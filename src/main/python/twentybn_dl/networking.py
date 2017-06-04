import hashlib
import requests
from urllib.request import urlopen
from tqdm import tqdm

DEFAULT_BLOCKSIZE = 1024 * 8


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
