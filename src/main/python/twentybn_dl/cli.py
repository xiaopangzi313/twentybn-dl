"""twentybn-dl

Usage:
    twentybn-dl get [<dataset>...]

Subcommands:
    get : Download bigtgz file(s).

"""

from docopt import docopt

from twentybn_dl.datasets import DATASETS_AVAILABLE


def main():
    arguments = docopt(__doc__)
    print(arguments)
    dsets = arguments['<dataset>'] or DATASETS_AVAILABLE
    if arguments['get']:
        for d in dsets.values():
            d.get_bigtgz()
