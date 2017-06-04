import os
import os.path as op
from urllib.parse import urljoin

from .networking import BigTGZStreamer
from .extract import extract_bigtgz

DEFAULT_BASE_URL = "https://s3-eu-west-1.amazonaws.com/20bn-public-datasets/"
DEFAULT_STORAGE = op.expandvars('$HOME/20bn-datasets')


class TwentyBNDatasetSchema(object):

    def __init__(self,
                 name=None,
                 version=None,
                 size=None,
                 jpegs=None,
                 chunks=None,
                 chunk_md5sums=None,
                 bigtgz_md5sum=None,
                 base_url=DEFAULT_BASE_URL,
                 storage=DEFAULT_STORAGE,
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

    def get_bigtgz(self):
        bigtgz_streamer = BigTGZStreamer(
            self.urls,
            self.chunk_md5sums,
            self.bigtgz,
            self.bigtgz_md5sum,
        )
        bigtgz_streamer.get()

    def extract_bigtgz(self):
        extract_bigtgz(self.bigtgz, self.jpegs, self.storage)
