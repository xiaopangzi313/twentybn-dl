"""twentybn-dl

Usage:
    twentybn-dl get [<dataset>...]
    twentybn-dl extract [<dataset>...]

Subcommands:
    get : Download bigtgz file(s).
    extract: Extract the bigtgz file(s).

"""

from docopt import docopt

from twentybn_dl.datasets import DATASETS_AVAILABLE


def main():
    arguments = docopt(__doc__)
    print(arguments)
    dsets = [DATASETS_AVAILABLE[k] for k in arguments['<dataset>']] \
        or DATASETS_AVAILABLE.values()

    if arguments['get']:
        for d in dsets.values():
            d.get_bigtgz()
    if arguments['extract']:
        for d in dsets.values():
            d.extract_bigtgz()
