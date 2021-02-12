import sys
import os
import csv
import logging
import pytest
from pathlib import Path

url_finder_module_path = Path().resolve().parent / "src" / "url_finder"
sys.path.append(str(url_finder_module_path))
from url_finder import URLFinder

utils_module_path = Path().resolve().parent / "src" / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/url_finder.log")

# PyPi page crawler tests
def test_find_github_url_from_pypi_page_success():
    package_name = "urllib3"
    finder = URLFinder(package_name=package_name)
    url_found = finder.find_github_url_from_pypi_page()
    logger.info("Package: {}, URL: {}".format(package_name, url_found))
    assert url_found == "https://github.com/urllib3/urllib3"

def test_find_github_url_from_pypi_page_wrong():
    package_name = "ninja"
    finder = URLFinder(package_name=package_name)
    url_found = finder.find_github_url_from_pypi_page()
    logger.info("Package: {}, URL: {}".format(package_name, url_found))
    assert url_found == "https://github.com/scikit-build/ninja-python-distributions"

def test_find_github_url_from_pypi_page_fail():
    package_name = "python-dateutil"
    finder = URLFinder(package_name=package_name)
    url_found = finder.find_github_url_from_pypi_page()
    logger.info("Package: {}, URL: {}".format(package_name, url_found))
    assert url_found == ""

# OSSGadget tests
def test_find_github_url_using_ossgadget_success():
    package_name = "urllib3"
    finder = URLFinder(package_name=package_name)
    url_found = finder.find_github_url_from_ossgadget()
    logger.info("Package: {}, URL: {}".format(package_name, url_found))
    assert url_found == "https://github.com/urllib3/urllib3"

def test_find_github_url_using_ossgadget_wrong():
    package_name = "statistics"
    finder = URLFinder(package_name=package_name)
    url_found = finder.find_github_url_from_ossgadget()
    logger.info("Package: {}, URL: {}".format(package_name, url_found))
    assert url_found == "https://github.com/python/cpython"

def test_find_github_url_using_ossgadget_fail():
    package_name = "pkg_test_fail"
    finder = URLFinder(package_name=package_name)
    url_found = finder.find_github_url_from_ossgadget()
    logger.info("Package: {}, URL: {}".format(package_name, url_found))
    assert url_found == ""

# Metadata tests
def test_find_github_url_from_metadata_success():
    package_name = "urllib3"
    finder = URLFinder(package_name=package_name)
    url_found = finder.find_github_url_from_metadata()
    logger.info("Package: {}, URL: {}".format(package_name, url_found))
    assert url_found == "https://github.com/urllib3/urllib3"

def test_find_github_url_from_metadata_wrong():
    package_name = "cffi"
    finder = URLFinder(package_name=package_name)
    url_found = finder.find_github_url_from_metadata()
    logger.info("Package: {}, URL: {}".format(package_name, url_found))
    assert url_found == "https://github.com/python-cffi/release-doc"

def test_find_github_url_from_metadata_fail():
    package_name = "python-dateutil"
    finder = URLFinder(package_name=package_name)
    url_found = finder.find_github_url_from_metadata()
    logger.info("Package: {}, URL: {}".format(package_name, url_found))
    assert url_found == ""

# Static methods tests
def test_not_redirected_github_url():
    url = "https://github.com/kmike/dawg-python"
    real_url = URLFinder.real_github_url(url)
    logger.info("URL: {}, Real URL: {}".format(url, real_url))
    assert real_url == "https://github.com/pytries/dawg-python"

def test_redirected_github_url():
    url = "https://github.com/urllib3/urllib3"
    real_url = URLFinder.real_github_url(url)
    logger.info("URL: {}, Real URL: {}".format(url, real_url))
    assert real_url == "https://github.com/urllib3/urllib3"