import hashlib
import requests
from urllib.request import urlopen
from tqdm import tqdm

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

MD5SUMS = [
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

OUTPUT_MD5SUM = "569624e1c96872933e3e46be15f7e53e"




if __name__ == '__main__':
    btgzs = BigTGZStreamer([URL+f for f in FILES], MD5SUMS, BIGTGZ, OUTPUT_MD5SUM)
    btgzs.get()
