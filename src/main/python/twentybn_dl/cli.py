"""twentybn-dl

Usage:
    twentybn-dl get [<dataset>...]
    twentybn-dl extract [<dataset>...]
    twentybn-dl fetch [<dataset>...]

Subcommands:
    get : Download bigtgz file(s).
    extract: Extract the bigtgz file(s).
    fetch: Download and extract the bigtgz file(s).

"""

from docopt import docopt

from twentybn_dl.datasets import DATASETS_AVAILABLE


def main():
    arguments = docopt(__doc__)
    dsets = arguments['<dataset>'] or DATASETS_AVAILABLE.keys()

    if arguments['get']:
        for d in dsets:
            print("Will now get bigtgz for: '{}'".format(d))
            s = DATASETS_AVAILABLE[d]
            s.get_bigtgz()
    if arguments['extract']:
        for d in dsets:
            print("Will now extract bigtgz for: '{}'".format(d))
            s = DATASETS_AVAILABLE[d]
            s.extract_bigtgz()
    if arguments['fetch']:
        for d in dsets:
            print("Will get and extract bigtgz for: '{}'".format(d))
            s = DATASETS_AVAILABLE[d]
            s.get_bigtgz()
            s.extract_bigtgz()
