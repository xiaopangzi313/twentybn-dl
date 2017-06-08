import os
import os.path as op
from urllib.parse import urljoin

from .network import BigTGZStreamer, ParallelChunkDownloader, WGETDownloader
from .extract import extract_bigtgz, extract_chunks
from .utils import md5


class MissingChunksException(Exception):
    pass


class MissingBigTGZException(Exception):
    pass


class TwentyBNDatasetSchema(object):

    def __init__(self,
                 name=None,
                 version=None,
                 size=None,
                 jpegs=None,
                 chunks=None,
                 chunk_md5sums=None,
                 bigtgz_md5sum=None,
                 base_url=None,
                 storage=None,
                 ):
        self.name = name
        self.version = version
        self.size = size
        self.jpegs = jpegs
        self.chunks = chunks
        self.chunk_md5sums = chunk_md5sums
        self.bigtgz_md5sum = bigtgz_md5sum
        self.base_url = base_url
        self._storage = storage

    def ensure_directories_exist(self):
        os.makedirs(self.storage, exist_ok=True)
        os.makedirs(self.tmpdir, exist_ok=True)

    @property
    def tmpdir(self):
        tmpdir = op.join(self.storage, 'tmp')
        os.makedirs(tmpdir, exist_ok=True)
        return tmpdir

    @property
    def storage(self):
        os.makedirs(self._storage, exist_ok=True)
        return self._storage

    @property
    def bigtgz(self):
        return op.join(self.tmpdir,
                       "20bn-{}-{}.tgz".format(self.name, self.version))

    def url(self, filename):
        full_path = op.join(self.name, self.version, filename)
        return urljoin(self.base_url, full_path)

    @property
    def urls(self):
        return [self.url(f) for f in self.chunks]

    @property
    def chunk_paths(self):
        return [op.join(self.tmpdir, c) for c in self.chunks]

    def get_bigtgz(self):
        bigtgz_streamer = BigTGZStreamer(
            self.urls,
            self.chunk_md5sums,
            self.bigtgz,
            self.bigtgz_md5sum,
        )
        bigtgz_streamer.get()

    def get_chunks(self):
        downloader = WGETDownloader(self.urls, self.tmpdir)
        downloader.download_chunks()

    def ensure_chunks_exist(self):
        for c in self.chunk_paths:
            if not op.isfile(c):
                message = "Chunk: '{}' is missing!".format(c)
                raise MissingChunksException(message)

    def check_chunk_md5sum(self):
        ok = True
        for c, m in zip(self.chunk_paths, self.chunk_md5sums):
            if md5(c) == m:
                print("MD5 sum matches for: '{}'".format(c))
            else:
                print("MD5 sum mismatch for: '{}'".format(c))
                ok = False
        return ok

    def ensure_bigtgz_exists(self):
        if not op.isfile(self.big_tgz):
            m = "Big TGZ: '{}' is missing".format(self.big_tgz)
            raise MissingBigTGZException(m)

    def extract_bigtgz(self):
        extract_bigtgz(self.bigtgz, self.size + self.jpegs, self.storage)

    def extract_chunks(self):
        self.ensure_chunks_exist()
        extract_chunks(self.chunk_paths, self.jpegs, self.storage)

    def remove_tmp(self):
        for c in self.chunk_paths:
            print("Removing: '{}'".format(c))
            os.remove(c)
