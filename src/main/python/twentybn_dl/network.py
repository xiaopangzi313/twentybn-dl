import os.path as op
import hashlib
from collections import namedtuple
import pprint
from multiprocessing.pool import Pool
from concurrent.futures import ProcessPoolExecutor
from urllib.request import urlopen
import atexit
import signal

import requests
import sh
from tqdm import tqdm

DEFAULT_BLOCKSIZE = 1024 * 8

DOWNLOAD_FAILURE = 0
DOWNLOAD_SUCCESS = 1
DOWNLOAD_UNNEEDED = 2
DownloadResult = namedtuple('DownloadResult', ['result', 'filename', 'reason'])


class ContentLengthNotSupportedException(Exception):
    pass


class BigTGZStreamer(object):

    def __init__(self,
                 input_urls,
                 input_urls_md5sums,
                 output_file,
                 output_md5sum,
                 blocksize=DEFAULT_BLOCKSIZE,
                 ):
        self.input_urls = input_urls
        self.input_urls_md5sums = input_urls_md5sums
        self.output_file = output_file
        self.output_md5sum = output_md5sum
        self.blocksize = blocksize

    def total_blocks_and_bytes(self):
        total_blocks, total_bytes = 0, 0
        for u in self.input_urls:
            head_response_headers = requests.head(u).headers
            if 'Content-Length' not in head_response_headers:
                m = "The url: '{}' doesn't support the 'Content-Length' field.".format(u)
                raise ContentLengthNotSupportedException(m)
            else:
                remote_size = int(head_response_headers['Content-Length'])
            total_bytes += remote_size
            num_blocks, last_block_size = divmod(remote_size, self.blocksize)
            total_blocks += num_blocks
            if last_block_size:
                total_blocks += 1
        return total_blocks, total_bytes

    def stream_to_file(self, url, md5sum, file_pointer, file_checksum, pbar):
        url_pointer = urlopen(url)
        url_checksum = hashlib.md5()
        while True:
            block = url_pointer.read(self.blocksize)
            if not block:
                break
            file_pointer.write(block)
            url_checksum.update(block)
            file_checksum.update(block)
            pbar.update(len(block))
        if url_checksum.hexdigest() != md5sum:
            raise Exception

    def get(self):
        with open(self.output_file, 'wb') as output_pointer:
            output_checksum = hashlib.md5()
            total_blocks, total_bytes = self.total_blocks_and_bytes()
            pbar = tqdm(total=total_bytes,
                        unit='bytes',
                        ncols=80,
                        unit_scale=True,
                        )
            for url, md5 in zip(self.input_urls, self.input_urls_md5sums):
                self.stream_to_file(url, md5, output_pointer, output_checksum, pbar)
            if output_checksum.hexdigest() != self.output_md5sum:
                raise Exception
            else:
                print("Final checksum matches!")


class ParallelChunkDownloader(object):

    def __init__(self, urls, md5sums, output_files,
                 blocksize=DEFAULT_BLOCKSIZE):
        self.urls = urls
        self.md5sums = md5sums
        self.output_files = output_files
        self.blocksize = blocksize

    def urlretrieve(self, url, md5sum, filename):
        url_pointer = urlopen(url)
        url_checksum = hashlib.md5()
        with open(filename, 'wb') as file_pointer:
            while True:
                block = url_pointer.read(self.blocksize)
                if not block:
                    break
                file_pointer.write(block)
                url_checksum.update(block)
            if url_checksum.hexdigest() != md5sum:
                raise Exception

    @staticmethod
    def needs_download(url, filepath):
        if not op.exists(filepath):
            return True
        else:
            response = requests.head(url)
            remote_size = int(response.headers['Content-Length'])
            local_size = op.getsize(filepath)
            if remote_size > local_size:
                return True
            else:
                return False

    def download_chunk(self, url_md5sum_filepath):
        url, md5sum, filepath = url_md5sum_filepath
        try:
            needs_dl = self.needs_download(url, filepath)
            if needs_dl:
                print("Downloading: '{}'".format(filepath))
                self.urlretrieve(url, md5sum, filepath)
                return DownloadResult(DOWNLOAD_SUCCESS, filepath, None)
            else:
                print("Not Downloading: '{}'".format(filepath))
                return DownloadResult(DOWNLOAD_UNNEEDED, filepath, None)
        except Exception as e:
            return DownloadResult(DOWNLOAD_FAILURE, filepath, repr(e))

    def download_chunks(self, max_workers=30):
        print('Will now download chunks.')
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            result = list(executor.map(self.download_chunk,
                                       zip(self.urls,
                                           self.md5sums,
                                           self.output_files)))
        DownloadResultProcessor.process_and_print(result)


class ExecutorResultProcessor(object):

    def __init__(self,
                 possible_results,
                 failure_index,
                 result_descriptions
                 ):
        assert len(possible_results) == len(result_descriptions)
        self.possible_results = possible_results
        self.failure_index = failure_index
        self.result_descriptions = result_descriptions

    def process_and_print(self, results):
        counts, failures = self.process_results(results)
        self.print_processed_results(counts, failures)
        return len(failures) != 0

    def process_results(self, results):
        counts = {i: 0 for i in self.possible_results}
        failures = []
        for r in results:
            counts[r.result] += 1
            if r.result == self.failure_index:
                failures.append(r)
        return counts, failures

    def print_processed_results(self, counts, failures):
        for p, d in zip(self.possible_results, self.result_descriptions):
            print('{}: {}'.  format(d, counts[p]))
        if failures:
            print('Failures:')
            print(pprint.pformat(failures))


DownloadResultProcessor = ExecutorResultProcessor(
        (DOWNLOAD_FAILURE, DOWNLOAD_SUCCESS, DOWNLOAD_UNNEEDED),
        DOWNLOAD_FAILURE,
        ('Total failures', 'Total downloads', 'Total unneeded'),
)


class WGETDownloader(object):

    def __init__(self, urls, base):
        self.urls = urls
        self.base = base

    def get(self, url):
        print("Downloading: '{}'".format(url))
        try:
            process = sh.wget('-q',
                              '-c',
                              '--tries=3',
                              url,
                              _cwd=self.base,
                              _bg=True)

            def kill():
                try:
                    process.kill()
                except:
                    pass
            atexit.register(kill)
            process.wait()
            return DownloadResult(DOWNLOAD_SUCCESS, url, None)
        except Exception as e:
            return DownloadResult(DOWNLOAD_FAILURE, url, repr(self.e))

    def download_chunks(self, max_workers=5):
        print('Will now download chunks.')
        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        executor = Pool(max_workers)
        signal.signal(signal.SIGINT, original_sigint_handler)
        try:
            r = executor.map_async(self.get, self.urls)
            result = list(r.get(43200))
            DownloadResultProcessor.process_and_print(result)
        except KeyboardInterrupt:
            executor.terminate()
        else:
            executor.close()
        executor.join()
