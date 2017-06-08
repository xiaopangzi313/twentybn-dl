"""twentybn-dl

Usage:
    twentybn-dl get-chunks [<dataset>...]
    twentybn-dl md5-chunks [<dataset>...]
    twentybn-dl extract-chunks [<dataset>...]
    twentybn-dl remove-tmp [<dataset>...]
    twentybn-dl obtain [<dataset>...]

    twentybn-dl get-bigtgz [<dataset>...]
    twentybn-dl md5-bigtgz [<dataset>...]
    twentybn-dl extract-bigtgz [<dataset>...]
    twentybn-dl concat-chunks [<dataset>...]

Subcommands:
    get-chunks : Download bigtgz chunks.
    md5-chunks : Check the md5 sums for the chunks.
    extract-chunks: Extract chunk file(s).
    remove-tmp: Remove all temporary files.
    obtain: Download, extract and remove temporary files.

    get-bigtgz : Download bigtgz file(s).
    md5-bigtgz: Check md5 sum for the bigtg z file(s).
    extract-bigtgz: Extract the bigtgz file(s).
    concat-chunks: Concatenate chunks into bigtgz.

"""
from docopt import docopt

from twentybn_dl.datasets import DATASETS_AVAILABLE


def get_chunks(dsets):
    for d in dsets:
        print("Will now get chunks for: '{}'".format(d.name))
        d.get_chunks()


def md5_chunks(dsets):
    for d in dsets:
        print("Will check md5 sums for chunks for: '{}'".format(d.name))
        ok = d.check_chunk_md5sum()
        if not ok:
            raise Exception("Some files failed their md5sum check, "
                            "please see above and delete them manually.")


def extract_chunks(dsets):
    for d in dsets:
        print("Will now extract chunks for: '{}'".format(d.name))
        d.extract_chunks()


def remove_tmp(dsets):
    for d in dsets:
        print("Will now remove temporary files for  for: '{}'".format(d.name))
        d.remove_tmp()


def main():
    arguments = docopt(__doc__)
    dsets = arguments['<dataset>'] or DATASETS_AVAILABLE.keys()
    dsets = [DATASETS_AVAILABLE[d] for d in dsets]

    if arguments['get-chunks']:
        get_chunks(dsets)
    if arguments['md5-chunks']:
        md5_chunks()
    if arguments['extract-chunks']:
        extract_chunks(dsets)
    if arguments['remove_tmp']:
        remove_tmp()
    if arguments['obtain']:
        get_chunks(dsets)
        md5_chunks()
        extract_chunks(dsets)
        remove_tmp()

    if arguments['get-bigtgz']:
        for d in dsets:
            print("Will now get bigtgz for: '{}'".format(d.name))
            d.get_bigtgz()
    if arguments['extract-bigtgz']:
        for d in dsets:
            print("Will now extract bigtgz for: '{}'".format(d.name))
            d.extract_bigtgz()
