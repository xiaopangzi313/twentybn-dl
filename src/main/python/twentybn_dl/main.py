#!/usr/bin/env python
import os
import os.path as op
from urllib.parse import urljoin
from urllib.request import urlretrieve
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pool
from collections import namedtuple, Counter
import pprint
import tarfile
import hashlib

import requests
from tqdm import tqdm


HTTP_ENDPOINT_BASE = "https://s3-eu-west-1.amazonaws.com/20bn-public-datasets/"
DOWNLOAD_TARGET_BASE = op.expandvars('$HOME/20bn-datasets')

DOWNLOAD_FAILURE = 0
DOWNLOAD_SUCCESS = 1
DOWNLOAD_UNNEEDED = 2
DownloadResult = namedtuple('DownloadResult', ['result', 'filename', 'reason'])


class MissingChunksException(Exception):
    pass


class MissingBigTGZException(Exception):
    pass


class MD5Mismatch(Exception):
    pass


def md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


class Dataset(object):
    """ Dataset on S3 accessible via HTTP. """

    def __init__(self, name, version, chunks, md5sums, bigtgz_md5sum, count):
        self.name = name
        self.version = version
        self.chunks = chunks
        self.md5sums = md5sums
        self.bigtgz_md5sum = bigtgz_md5sum
        self.count = count
        self.tmp_dir = op.join(DOWNLOAD_TARGET_BASE, 'tmp')
        self.final_dir = op.join(
            DOWNLOAD_TARGET_BASE,
            "20bn-{}-{}".format(self.name, self.version)
        )
        self.big_tgz = op.join(
            self.tmp_dir,
            "20bn-{}-{}.tgz".format(self.name, self.version)
        )
        self.tar_dir = op.join(
            self.tmp_dir,
            "20bn-{}-{}".format(self.name, self.version)
        )
        self.ensure_directories_exist()

    def ensure_directories_exist(self):
        os.makedirs(self.tmp_dir, exist_ok=True)

    def ensure_chunks_exist(self):
        for c in self.chunks:
            chunk_path = op.join(self.tmp_dir, c)
            if not op.isfile(chunk_path):
                message = "Chunk: '{}' is missing!".format(chunk_path)
                raise MissingChunksException(message)

    def ensure_chunk_md5sums_match(self):
        for c, m in zip(self.chunks, self.md5sums):
            chunk_path = op.join(self.tmp_dir, c)
            expected = m
            received = md5(chunk_path)
            if received != expected:
                m = "MD5 Mismatch detected for: '{}'".format(chunk_path)
                MD5Mismatch(m)
            else:
                print("MD5 match for: '{}'".format(chunk_path))

    def ensure_bigtgz_exists(self):
        if not op.isfile(self.big_tgz):
            m = "Big TGZ: '{}' is missing".format(self.big_tgz)
            raise MissingBigTGZException(m)

    def ensure_bigtgz_md5sum_match(self):
        expected = self.bigtgz_md5sum
        received = md5(self.big_tgz)
        if received != expected:
            m = "MD5 Mismatch detected for: '{}'".format(self.big_tgz)
            MD5Mismatch(m)
        else:
            print("MD5 match for: '{}'".format(self.big_tgz))

    def url(self, filename):
        full_path = op.join(self.name, self.version, filename)
        return urljoin(HTTP_ENDPOINT_BASE, full_path)

    @property
    def urls(self):
        return [self.url(f) for f in self.chunks]

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

    def download_chunk(self, url_filename):
        url, filename = url_filename
        try:
            filepath = op.join(self.tmp_dir, filename)
            needs_dl = self.needs_download(url, filepath)
            if needs_dl:
                print("Downloading: '{}'".format(filename))
                urlretrieve(url, filepath)
                return DownloadResult(DOWNLOAD_SUCCESS, filename, None)
            else:
                print("Not Downloading: '{}'".format(filename))
                return DownloadResult(DOWNLOAD_UNNEEDED, filename, None)
        except Exception as e:
            return DownloadResult(DOWNLOAD_FAILURE, filename, repr(e))

    def download_chunks(self, max_workers=30):
        print('Will now download chunks.')
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            result = list(executor.map(self.download_chunk,
                                       zip(self.urls, self.chunks)))
        DownloadResultProcessor.process_and_print(result)

    def concat_chunks(self, keep=True, read_chunk_size=65536):
        self.ensure_chunks_exist()
        print('Will now concatenate chunks.')
        with open(self.big_tgz, 'wb') as target:
            for f in self.chunks:
                chunk_path = op.join(self.tmp_dir, f)
                with open(chunk_path, 'rb') as source:
                    print("Now appending: '{}'".format(f))
                    while True:
                        read_bytes = source.read(read_chunk_size)
                        target.write(read_bytes)
                        if len(read_bytes) < read_chunk_size:
                            break

    def extract_bigtgz(self):
        print('Will extract the big tgz.')
        self.ensure_bigtgz_exists()

        with tqdm(total=self.count, unit='records') as pbar:
            def callback(members):
                for tarinfo in members:
                    pbar.update(1)
                    yield tarinfo
            with tarfile.open(self.big_tgz, 'r|gz') as tar:
                tar.extractall(path=self.tmp_dir, members=callback(tar))

    def extract_record_tar(self, tar_path):
        try:
            with tarfile.open(tar_path, 'r|') as tar:
                tar.extractall(self.final_dir)
            return 1
        except Exception as e:
            return 0

    def extract_record_tars(self, max_workers=30):
        print('Will extract the record tars.')
        os.makedirs(self.final_dir, exist_ok=True)
        tar_files = [op.join(self.tar_dir, t)
                     for t in os.listdir(self.tar_dir)]
        p = Pool(30)
        result = p.map(self.extract_record_tar,  tqdm(tar_files, unit='records'), chunksize=5)
        print(Counter(result))


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

SOMETHING_SOMETHING_CUNKS = [
    '20bn-something-something-v1-aa',
    '20bn-something-something-v1-ab',
    '20bn-something-something-v1-ac',
    '20bn-something-something-v1-ad',
    '20bn-something-something-v1-ae',
    '20bn-something-something-v1-af',
    '20bn-something-something-v1-ag',
    '20bn-something-something-v1-ah',
    '20bn-something-something-v1-ai',
    '20bn-something-something-v1-aj',
    '20bn-something-something-v1-ak',
    '20bn-something-something-v1-al',
    '20bn-something-something-v1-am',
    '20bn-something-something-v1-an',
    '20bn-something-something-v1-ao',
    '20bn-something-something-v1-ap',
    '20bn-something-something-v1-aq',
    '20bn-something-something-v1-ar',
    '20bn-something-something-v1-as',
    '20bn-something-something-v1-at',
    '20bn-something-something-v1-au',
    '20bn-something-something-v1-av',
    '20bn-something-something-v1-aw',
    '20bn-something-something-v1-ax',
    '20bn-something-something-v1-ay',
    '20bn-something-something-v1-az',
    '20bn-something-something-v1-ba',
    '20bn-something-something-v1-bb',
    '20bn-something-something-v1-bc',
    '20bn-something-something-v1-bd',
    '20bn-something-something-v1-be'
]

SOMETHING_SOMETHING_MD5SUMS = [
    '76e2b0cd4493252f68cfffc5adbdb5c9',
    '5b590c2bb7eb862faf447bf50a54af73',
    '97a77b180621616cbbe6252173b77044',
    'f7d34505236076b0884101f47a1136a1',
    'b87d92d8ee519be6bdfe1399816f6d15',
    '9c85a5c1d9b6345dd0405751436367df',
    'f42db2e29b15633031fec3fd17708fa1',
    '94a6bacf75cd0f537e33adcf6781660e',
    '51928a7e709e6a546dec9e942662cf19',
    '8c4702a179d77f1966b6cafc50ad82b0',
    '12235aab429ffa9fbda1bc02ec308e1e',
    '4801d94550b66be3e3e6c59afd34848a',
    '3220ca7120f8994e6fd3864c9eef47cf',
    '331ba5aca48e7aeffa1edd517e5da16e',
    '934f9ee42e7573ee34fa7b2ada0f6675',
    '317fbfb7e7ccccbed9bcefe258c9e2ea',
    'f4105ea9f29fb4e83407e81cf73f0902',
    'fd2066184fc934a955371b063c8ab80a',
    '0bbb74ca5205ee7f82fa6913ff8c3ee4',
    '9f9e6e51494ec2fd27682450ae748324',
    'cf0d745933cc786853b5404aba335b09',
    '27fca5d0eeef1d82e844169b078f3c65',
    'd28d3e12477e47edf1b31b21c15409e2',
    '7ddccdf32c884578eae0d9e1610eaa75',
    '08a42a3fe1edbffa4e4a943603f1a6ab',
    'a2f944b576f2e8a887f7f0314ad1b908',
    'a17d29faf4fdb2eda84554d0138f8d3c',
    'ea1cacdd569960beaf7e4083ac4f2bd7',
    '73f9fef480c60d19539ef9227261e060',
    'cc58710e4c7bc38ffd6ab6d4166bd169',
    '071a8919da2a5b8582424dbc9679f7c4',
]
SOMETHING_SOMETHING_BIGTGZ_MD5SUM = "569624e1c96872933e3e46be15f7e53e"
SomethingSomething = Dataset('something-something',
                             'v1',
                             SOMETHING_SOMETHING_CUNKS,
                             SOMETHING_SOMETHING_MD5SUMS,
                             SOMETHING_SOMETHING_BIGTGZ_MD5SUM,
                             134636)

