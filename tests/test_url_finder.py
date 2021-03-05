import sys
import os
import csv
import logging
import pytest
from pathlib import Path

from ..src.url_finder import URLFinder

#utils_module_path = Path().resolve().parent / "src" / "utils"
#sys.path.append(str(utils_module_path))
#from utils import log_function_output
from ..src.utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filepath="../logs/url_finder.log")

# PyPi page crawler tests
def test_find_github_url_from_pypi_page_success():
    package_name = "urllib3"
    finder = URLFinder(package_name=package_name)
    url_found = finder.find_github_url_from_pypi_page()
    logger.info("Package: {}, URL: {}".format(package_name, url_found))
    assert url_found == "https://github.com/urllib3/urllib3"

def test_find_github_url_from_homepage_metadata():
    package_name = "urllib3"
    finder = URLFinder(package_name=package_name)
    url_found = finder.find_github_url_from_homepage_metadata()
    logger.info("Package: {}, Homepage metadata URL: {}".format(package_name, url_found))
    assert url_found is None 


def test_find_github_url_from_codepage_metadata():
    package_name = "urllib3"
    finder = URLFinder(package_name=package_name)
    url_found = finder.find_github_url_from_codepage_metadata()
    logger.info("Package: {}, Codepage metadata URL: {}".format(package_name, url_found))
    assert url_found == "https://github.com/urllib3/urllib3"

def test_find_github_url_from_homepage_metadata_package_non_exist():
    package_name = "adsafdsafda"
    finder = URLFinder(package_name=package_name)
    url_found = finder.find_github_url_from_codepage_metadata()
    logger.info("Package: {}, Codepage metadata URL: {}".format(package_name, url_found))
    assert url_found is None 

def test_find_github_url_from_homepage_page():
    package_name = "urllib3"
    finder = URLFinder(package_name=package_name)
    url_found = finder.find_github_url_from_homepage_webpage()
    logger.info("Package: {}, Homepage webpage URL: {}".format(package_name, url_found))
    assert url_found is None 

def test_find_github_url_from_pypi_page():
    package_name = "urllib3"
    finder = URLFinder(package_name=package_name)
    url_found = finder.find_github_url_from_pypi_page()
    logger.info("Package: {}, PyPI webpage URL: {}".format(package_name, url_found))
    assert url_found is "https://github.com/urllib3/urllib3" 

def test_find_github_url_from_homepage_metadata_package_non_exist():
    package_name = "adsafdsafda"
    finder = URLFinder(package_name=package_name)
    url_found = finder.find_github_url_from_homepage_metadata()
    logger.info("Package: {}, Homepage metadata URL: {}".format(package_name, url_found))
    assert url_found is None 
#def test_find_github_url_from_pypi_page_wrong():
#    package_name = "ninja"
#    finder = URLFinder(package_name=package_name)
#    url_found = finder.find_github_url_from_pypi_page()
#    logger.info("Package: {}, URL: {}".format(package_name, url_found))
#    assert url_found == "https://github.com/scikit-build/ninja-python-distributions"
#
#def test_find_github_url_from_pypi_page_fail():
#    package_name = "python-dateutil"
#    finder = URLFinder(package_name=package_name)
#    url_found = finder.find_github_url_from_pypi_page()
#    logger.info("Package: {}, URL: {}".format(package_name, url_found))
#    assert url_found == ""
#
## OSSGadget tests
#def test_find_github_url_using_ossgadget_success():
#    package_name = "urllib3"
#    finder = URLFinder(package_name=package_name)
#    url_found = finder.find_github_url_from_ossgadget()
#    logger.info("Package: {}, URL: {}".format(package_name, url_found))
#    assert url_found == "https://github.com/urllib3/urllib3"
#
#def test_find_github_url_using_ossgadget_wrong():
#    package_name = "statistics"
#    finder = URLFinder(package_name=package_name)
#    url_found = finder.find_github_url_from_ossgadget()
#    logger.info("Package: {}, URL: {}".format(package_name, url_found))
#    assert url_found == "https://github.com/python/cpython"
#
#def test_find_github_url_using_ossgadget_fail():
#    package_name = "pkg_test_fail"
#    finder = URLFinder(package_name=package_name)
#    url_found = finder.find_github_url_from_ossgadget()
#    logger.info("Package: {}, URL: {}".format(package_name, url_found))
#    assert url_found == ""
#
## Metadata tests
#def test_find_github_url_from_metadata_success():
#    package_name = "urllib3"
#    finder = URLFinder(package_name=package_name)
#    url_found = finder.find_github_url_from_metadata()
#    logger.info("Package: {}, URL: {}".format(package_name, url_found))
#    assert url_found == "https://github.com/urllib3/urllib3"
#
#def test_find_github_url_from_metadata_wrong():
#    package_name = "cffi"
#    finder = URLFinder(package_name=package_name)
#    url_found = finder.find_github_url_from_metadata()
#    logger.info("Package: {}, URL: {}".format(package_name, url_found))
#    assert url_found == "https://github.com/python-cffi/release-doc"
#
#def test_find_github_url_from_metadata_fail():
#    package_name = "python-dateutil"
#    finder = URLFinder(package_name=package_name)
#    url_found = finder.find_github_url_from_metadata()
#    logger.info("Package: {}, URL: {}".format(package_name, url_found))
#    assert url_found == ""
#
## Static methods tests
#def test_not_redirected_github_url():
#    url = "https://github.com/kmike/dawg-python"
#    real_url = URLFinder.real_github_url(url)
#    logger.info("URL: {}, Real URL: {}".format(url, real_url))
#    assert real_url == "https://github.com/pytries/dawg-python"
#
#def test_redirected_github_url():
#    url = "https://github.com/urllib3/urllib3"
#    real_url = URLFinder.real_github_url(url)
#    logger.info("URL: {}, Real URL: {}".format(url, real_url))
#    assert real_url == "https://github.com/urllib3/urllib3"
#
## Metrics tests
#def test_check_pypi_statistics_success():
#    package_name = "urllib3"
#    final_github_url = "https://github.com/urllib3/urllib3"
#    finder = URLFinder(package_name=package_name)
#    finder.set_github_url(final_github_url)
#    statistics_url = finder.check_pypi_statistics()
#    logger.info("Final URL: {}, Stat URL: {}".format(final_github_url, statistics_url))
#    assert statistics_url == True
#
#def test_check_pypi_statistics_fail():
#    package_name = "future"
#    final_github_url = "https://github.com/pythoncharmers/python-future"
#    finder = URLFinder(package_name=package_name)
#    finder.set_github_url(final_github_url)
#    statistics_url = finder.check_pypi_statistics()
#    logger.info("Final URL: {}, Stat URL: {}".format(final_github_url, statistics_url))
#    assert statistics_url == False
#
#def test_get_pypi_description_success():
#    package_name = "websocket"
#    finder = URLFinder(package_name=package_name)
#    description = finder.get_pypi_descr().replace("\n","")
#    logger.info("Description: {}".format(description))
#    assert description == "UNKNOWN"
#
#def test_get_github_description_success():
#    package_name = "six"
#    final_url = "https://github.com/benjaminp/six"
#    finder = URLFinder(package_name=package_name)
#    finder.set_github_url(final_url)
#    description = finder.get_github_descr().replace("\n","")
#    logger.info("Description: {}".format(description))
#    assert description == "Six is a Python 2 and 3 compatibility library.  It provides utility functionsfor smoothing over the differences between the Python versions with the goal ofwriting Python code that is compatible on both Python versions.  See thedocumentation for more information on what is provided.Six supports Python 2.7 and 3.3+.  It is contained in only one Pythonfile, so it can be easily copied into your project. (The copyright and licensenotice must be retained.)Online documentation is at https://six.readthedocs.io/.Bugs can be reported to https://github.com/benjaminp/six.  The code can alsobe found there."
#
#def test_check_readthedocs_success():
#    package_name = "urllib3"
#    final_url = "https://github.com/urllib3/urllib3"
#    finder = URLFinder(package_name=package_name)
#    finder.set_github_url(final_url)
#    readthedocs_link = finder.check_readthedocs()
#    logger.info("Readthedocs link: {}".format(readthedocs_link))
#    assert readthedocs_link == True
#
#def test_check_readthedocs_fail():
#    package_name = "future"
#    final_url = "https://github.com/pythoncharmers/python-future"
#    finder = URLFinder(package_name=package_name)
#    finder.set_github_url(final_url)
#    readthedocs_link = finder.check_readthedocs()
#    logger.info("Readthedocs link: {}".format(readthedocs_link))
#    assert readthedocs_link == False
#
#def test_check_github_badge_success():
#    package_name = "pathlib-mate"
#    final_url = "https://github.com/machu-gwu/pathlib_mate-project"
#    finder = URLFinder(package_name=package_name)
#    finder.set_github_url(final_url)
#    github_badge = finder.check_github_badge()
#    logger.info("GitHub badge: {}".format(github_badge))
#    assert github_badge == True
#
#def test_check_travis_badge_success():
#    package_name = "twitter"
#    final_url = "https://github.com/sixohsix/twitter"
#    finder = URLFinder(package_name=package_name)
#    finder.set_github_url(final_url)
#    travis_badge = finder.check_github_badge()
#    logger.info("Travis badge: {}".format(travis_badge))
#    assert travis_badge == True
#
#def test_check_github_badge_fail():
#    package_name = "urllib3"
#    final_url = "https://github.com/urllib3/urllib3"
#    finder = URLFinder(package_name=package_name)
#    finder.set_github_url(final_url)
#    badge = finder.check_github_badge()
#    logger.info("GitHub badge: {}".format(badge))
#    assert badge == False
#
#def test_check_pypi_badge_success():
#    package_name = "urllib3"
#    final_url = "https://github.com/urllib3/urllib3"
#    finder = URLFinder(package_name=package_name)
#    finder.set_github_url(final_url)
#    badge = finder.check_pypi_badge()
#    logger.info("PyPI badge: {}".format(badge))
#    assert badge == True
#
#def test_check_pypi_badge_fail():
#    package_name = "pytz"
#    final_url = "https://github.com/stub42/pytz"
#    finder = URLFinder(package_name=package_name)
#    finder.set_github_url(final_url)
#    badge = finder.check_pypi_badge()
#    logger.info("PyPI badge: {}".format(badge))
#    assert badge == False
#
#def test_check_python_lang_high_perc():
#    package_name = "urllib3"
#    final_url = "https://github.com/urllib3/urllib3"
#    finder = URLFinder(package_name=package_name)
#    finder.set_github_url(final_url)
#    python_lang = finder.check_python_lang()
#    logger.info("Python language: {}".format(python_lang))
#    assert python_lang == "99.8%"
#
#def test_check_python_lang_low_perc():
#    package_name = "pytz"
#    final_url = "https://github.com/stub42/pytz"
#    finder = URLFinder(package_name=package_name)
#    finder.set_github_url(final_url)
#    python_lang = finder.check_python_lang()
#    logger.info("Python language: {}".format(python_lang))
#    assert python_lang == "16.3%"
#
#def test_check_python_lang_0_perc():
#    package_name = "websocket"
#    final_url = "https://github.com/duguying/websocket"
#    finder = URLFinder(package_name=package_name)
#    finder.set_github_url(final_url)
#    python_lang = finder.check_python_lang()
#    logger.info("Python language: {}".format(python_lang))
#    assert python_lang == "0%"
#
#def test_check_python_lang_fail():
#    package_name = "testresources"
#    final_url = "https://github.com/testresources/testresources"
#    finder = URLFinder(package_name=package_name)
#    finder.set_github_url(final_url)
#    python_lang = finder.check_python_lang()
#    logger.info("Python language: {}".format(python_lang))
#    assert python_lang == "0%"
