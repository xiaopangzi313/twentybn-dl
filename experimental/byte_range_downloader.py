import requests
from tqdm import tqdm
import multiprocessing

url = "https://s3-eu-west-1.amazonaws.com/20bn-public-datasets/something-something/v1/20bn-something-something-v1-aa"

blob_size = 4096
remote_size = int(requests.head(url).headers['Content-Length'])

total_blobs, last_blob_size = divmod(remote_size, blob_size)
print(total_blobs, last_blob_size)

s = requests.Session()


def get_blob(index):
    start = index*blob_size
    end = start+blob_size-1
    return get(url, start, end)


def get_last_blob(total_blobs, last_blob_size):
    start = total_blobs*blob_size
    end = start + last_blob_size
    return get(url, start, end)


def get(url, start, end):
    headers = {"Range": "bytes={}-{}".format(start, end)}  # first 100 bytes
    resp = s.get(url, headers=headers)
    return resp.content



#d = b"".join(map(get_blob, tqdm(range(total_blobs))))
#l = get_last_blob(total_blobs, last_blob_size)
p = multiprocessing.Pool(256)
d = list(p.map(get_blob, tqdm(range(total_blobs)), chunksize=32))

