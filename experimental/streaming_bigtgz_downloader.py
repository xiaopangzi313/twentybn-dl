from urllib.request import urlopen

URL = "https://s3-eu-west-1.amazonaws.com/20bn-public-datasets/something-something/v1/"
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


def stream_to_file(url, file_pointer):
    url_pointer = urlopen(url)
    blocksize = 1024 * 8
    while True:
        block = url_pointer.read(blocksize)
        if not block:
            break
        file_pointer.write(block)


with open(BIGTGZ, 'wb') as fp:
    for f in FILES:
        print(f)
        stream_to_file(URL+f, fp)
