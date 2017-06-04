"""twentybn-dl

Usage:
    twentybn-dl get [<dataset>...]

Subcommands:
    get : Download bigtgz file(s).

"""

from docopt import docopt


def main():
    arguments = docopt(__doc__)
    print(arguments)
