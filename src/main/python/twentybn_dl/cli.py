"""twentybn-dl

Usage:
    twentybn-dl get-bigtgz [<dataset>...]
    twentybn-dl get-chunks [<dataset>...]
    twentybn-dl extract-bigtgz [<dataset>...]
    twentybn-dl extract-chunks [<dataset>...]
    twentybn-dl fetch [<dataset>...]

Subcommands:
    get-bigtgz : Download bigtgz file(s).
    get-chunks : Download bigtgz chunks.
    extract-bigtgz: Extract the bigtgz file(s).
    fetch: Download and extract the bigtgz file(s).

"""

from docopt import docopt

from twentybn_dl.datasets import DATASETS_AVAILABLE


def main():
    arguments = docopt(__doc__)
    dsets = arguments['<dataset>'] or DATASETS_AVAILABLE.keys()

    if arguments['get-bigtgz']:
        for d in dsets:
            print("Will now get bigtgz for: '{}'".format(d))
            s = DATASETS_AVAILABLE[d]
            s.get_bigtgz()
    if arguments['get-chunks']:
        for d in dsets:
            print("Will now get chunks for: '{}'".format(d))
            s = DATASETS_AVAILABLE[d]
            s.get_chunks()
    if arguments['extract-bigtgz']:
        for d in dsets:
            print("Will now extract bigtgz for: '{}'".format(d))
            s = DATASETS_AVAILABLE[d]
            s.extract_bigtgz()
    if arguments['extract-chunks']:
        for d in dsets:
            print("Will now extract chunks for: '{}'".format(d))
            s = DATASETS_AVAILABLE[d]
            s.extract_chunks()
    if arguments['fetch']:
        for d in dsets:
            print("Will get and extract bigtgz for: '{}'".format(d))
            s = DATASETS_AVAILABLE[d]
            s.get_bigtgz()
            s.extract_bigtgz()
