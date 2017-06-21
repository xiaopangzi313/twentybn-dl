from pybuilder.core import use_plugin, init, Author
from pybuilder.vcs import count_travis

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin("filter_resources")


name = "twentybn-dl"
default_task = "publish"
version = count_travis()
summary = "TwentyBN public dataset downloader"
authors = [Author("Valentin Haenel", "valentin.haenel@twentybn.com"),
           Author("Ingo Bax", "ingo.bax@twentybn.com"),
           ]

requires_python = ">=3.4"


@init
def set_properties(project):
    project.set_property('coverage_break_build', False)
    project.depends_on('requests')
    project.depends_on('tqdm')
    project.depends_on('docopt')
    project.depends_on('sh')
    project.get_property('filter_resources_glob').extend(
        ['**/twentybn_dl/__init__.py'])
