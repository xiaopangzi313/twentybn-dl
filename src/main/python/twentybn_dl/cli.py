"""twentybn-dl

Usage:
    twentybn-dl [options] list
    twentybn-dl [options] get-chunks [<dataset>...]
    twentybn-dl [options] md5-chunks [<dataset>...]
    twentybn-dl [options] extract-chunks [<dataset>...]
    twentybn-dl [options] remove-tmp [<dataset>...]
    twentybn-dl [options] obtain [<dataset>...]


Subcommands:
    get-chunks : Download bigtgz chunks.
    md5-chunks : Check the md5 sums for the chunks.
    extract-chunks: Extract chunk file(s).
    remove-tmp: Remove all temporary files.
    obtain: Download, extract and remove temporary files.


Options:
   -s --storage=STORAGE  Storage location for datasets
   -u --base-url=URL     Base URL for downloads

"""
import os
import readline
import os.path as op
from docopt import docopt

from .datasets import DATASETS_AVAILABLE
from .defaults import DEFAULT_STORAGE, DEFAULT_BASE_URL


def get_chunks(d):
    print("Will now get chunks for: '{}'".format(d.name))
    d.get_chunks()


def md5_chunks(d):
    print("Will check md5 sums for chunks for: '{}'".format(d.name))
    ok = d.check_chunk_md5sum()
    if not ok:
        raise Exception("Some files failed their md5sum check, "
                        "please see above and delete them manually.")


def extract_chunks(d):
    print("Will now extract chunks for: '{}'".format(d.name))
    d.extract_chunks()


def remove_tmp(d):
        print("Will now remove temporary files for  for: '{}'".format(d.name))
        d.remove_tmp()


def normalize_storage_argument(storage):
    if storage:
        return (op.join(os.getcwd(), storage)
                if not op.isabs(storage)
                else storage)
    else:
        return DEFAULT_STORAGE


def read_storage_path_from_prompt():
    readline.set_completer_delims(' \t\n')
    readline.parse_and_bind("tab: complete")
    choice = input('Set storage directory [Enter for "%s"]: ' % DEFAULT_STORAGE)
    return choice or DEFAULT_STORAGE


def validate_storage_path(storage_path):
    if not os.path.isdir(storage_path):
        print('Directory "%s" doesn\'t exist. Using default directory.' % storage_path)
        return False
    else:
        return True


def main():
    arguments = docopt(__doc__)
    dsets = arguments['<dataset>'] or DATASETS_AVAILABLE.keys()
    dsets = [DATASETS_AVAILABLE[d] for d in dsets]
    base_url = arguments['--base-url'] or DEFAULT_BASE_URL
    if not arguments['list']:
        # allow for setting the storage path via args or prompt
        storage = normalize_storage_argument(arguments['--storage']) if arguments['--storage'] else read_storage_path_from_prompt()
        if not validate_storage_path(storage):
            storage = DEFAULT_STORAGE
        print("Using: '{}' as storage.".format(storage))
        for d in dsets:
            d.base_url = base_url
            d._storage = storage

    if arguments['list']:
        print('Available datasets:')
        for d in dsets:
            print(d.pformat())
    if arguments['get-chunks']:
        for d in dsets:
            get_chunks(d)
    if arguments['md5-chunks']:
        for d in dsets:
            md5_chunks(d)
    if arguments['extract-chunks']:
        for d in dsets:
            extract_chunks(d)
    if arguments['remove-tmp']:
        for d in dsets:
            remove_tmp(d)
    if arguments['obtain']:
        for d in dsets:
            get_chunks(d)
            md5_chunks(d)
            extract_chunks(d)
            remove_tmp(d)

# Unused bigtgz stuff
#    twentybn-dl get-bigtgz [<dataset>...]
#    twentybn-dl md5-bigtgz [<dataset>...]
#    twentybn-dl extract-bigtgz [<dataset>...]
#    twentybn-dl concat-chunks [<dataset>...]
#    get-bigtgz : Download bigtgz file(s).
#    md5-bigtgz: Check md5 sum for the bigtg z file(s).
#    extract-bigtgz: Extract the bigtgz file(s).
#    concat-chunks: Concatenate chunks into bigtgz.
#    if arguments['get-bigtgz']:
#        for d in dsets:
#            print("Will now get bigtgz for: '{}'".format(d.name))
#            d.get_bigtgz()
#    if arguments['extract-bigtgz']:
#        for d in dsets:
#            print("Will now extract bigtgz for: '{}'".format(d.name))
#            d.extract_bigtgz()
