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

def test_find_github_url_using_ossgadget_success():
    package_name = "urllib3"
    finder = URLFinder(package_name=package_name)
    url_found = finder.find_github_url_from_ossgadget()
    logger.info("Package: {}, URL: {}".format(package_name, url_found))
    assert url_found == "https://github.com/urllib3/urllib3"

def test_find_github_url_using_ossgadget_fail():
    # TODO: Writing a test to demonstrate a failure case that ossgadget cannot find the Github url
    assert url_found == ""

