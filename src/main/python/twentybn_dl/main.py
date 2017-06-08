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
