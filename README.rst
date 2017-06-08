===========
twentybn-dl
===========

About
=====

Twenty Billion Neurons public dataset downloader.

Install
=======

There are many ways to setup a Python environment for installation. Here we
outline an approach using *virtualenvironment*. Note: this package does not
support legacy Python and will only work with Python 3.x

The following will setup a virtualenvironment and activate it:

.. code::

    python -m venv twentybn-dl
    source twentybn-dl/bin/activate

Then, install the package using:

.. code::

    pip install twentybn-dl

Usage
=====

.. code::

    twentybn-dl

    Usage:
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
       -u --base-url=URL     Base URL for donwloads

Example
=======

To download, extract and remove temporary files for the *jester* dataset, use:

.. code::

    $ twentybn-dl obtain jester
    ...

Details
=======

By default, the Datasets will be downloaded to ``$HOME/20bn-datasets``. Any
temporary files will reside in a ``tmp`` directory in that directory.

So, for example, the following will contain the directories, each of which
represent a video that was split into JPG images:

.. code::

    ~/20bn-datasets/20bn-jester-v1

Whereas the following contains any temporary files, e.g. chunk files:

.. code::

    ~/20bn-datasets/tmp/


License
=======

Copyright (c) 2016 Twenty Billion Neurons GmbH, Berlin, Germany

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
