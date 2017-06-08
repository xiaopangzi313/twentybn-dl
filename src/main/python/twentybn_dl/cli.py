"""twentybn-dl

Usage:
    twentybn-dl get-bigtgz [<dataset>...]
    twentybn-dl get-chunks [<dataset>...]
    twentybn-dl md5-bigtgz [<dataset>...]
    twentybn-dl md5-chunks [<dataset>...]
    twentybn-dl extract-bigtgz [<dataset>...]
    twentybn-dl extract-chunks [<dataset>...]
    twentybn-dl concat-chunks [<dataset>...]
    twentybn-dl fetch [<dataset>...]
    twentybn-dl remove-tmp [<dataset>...]

Subcommands:
    get-bigtgz : Download bigtgz file(s).
    get-chunks : Download bigtgz chunks.
    md5-chunks : Check the md5 sums for the chunks.
    extract-bigtgz: Extract the bigtgz file(s).
    extract-chunks: Extract chunk file(s).
    concat-chunks: Concatenate chunks into bigtgz
    fetch: Download and extract the bigtgz file(s).
    remove-tmp: Remove all temporary files.

"""
import sys

from docopt import docopt

from twentybn_dl.datasets import DATASETS_AVAILABLE


def remove_tmp(dsets):
    for d in dsets:
        print("Will now remove temporary files for  for: '{}'".format(d.name))
        d.remove_tmp()


def main():
    EXIT = 0
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
    if arguments['md5-chunks']:
        for d in dsets:
            print("Will check md5 sums for chunks for: '{}'".format(d))
            s = DATASETS_AVAILABLE[d]
            ok = s.check_chunk_md5sum()
            if not ok:
                print("Some files failed their md5sum check, please see above and delete them manually.")
                EXIT = 1
    if arguments['fetch']:
        for d in dsets:
            print("Will get and extract bigtgz for: '{}'".format(d))
            s = DATASETS_AVAILABLE[d]
            s.get_bigtgz()
            s.extract_bigtgz()
    if arguments['remove-tmp']:
        remove_tmp([DATASETS_AVAILABLE[d] for d in dsets])

    sys.exit(EXIT)
