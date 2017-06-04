import requests
from urllib.request import urlopen
from tqdm import tqdm

BLOCKSIZE = 1024 * 8
URL = "https://s3-eu-west-1.amazonaws.com/20bn-public-datasets/something-something/v0/"
BIGTGZ = "20bn-something-something-v1.tgz"
FILES = [
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


def get_total_blocks_and_bytes():
    total_blocks = 0
    total_bytes = 0
    for f in FILES:
        remote_size = int(requests.head(URL+f).headers['Content-Length'])
        total_bytes += remote_size
        num_blocks, last_block_size = divmod(remote_size, BLOCKSIZE)
        total_blocks += num_blocks
        if last_block_size:
            total_blocks += 1
    return total_blocks, total_bytes


def stream_to_file(url, file_pointer, pbar):
    url_pointer = urlopen(url)
    while True:
        block = url_pointer.read(BLOCKSIZE)
        if not block:
            break
        file_pointer.write(block)
        pbar.update(len(block))


with open(BIGTGZ, 'wb') as fp:
    total_blocks, total_bytes = get_total_blocks_and_bytes()
    pbar = tqdm(total=total_bytes, unit='bytes', ncols=80, unit_scale=True)
    for f in FILES:
        stream_to_file(URL+f, fp, pbar)
