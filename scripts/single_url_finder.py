"""
This file get the GitHub URL a package, using three sources, and the related accuracy
"""
import sys
import os
import csv
import logging
import pytest
from pathlib import Path

url_finder_module_path = Path().resolve() / "url_finder"
sys.path.append(str(url_finder_module_path))
from url_finder import URLFinder

utils_module_path = Path().resolve() / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/url_finder.log")

# set the package name and initialize the object
package_name = 'urllib3'
url_finder = URLFinder(package_name)

# use three different sources to gather the URL
metadata_url = url_finder.find_github_url_from_metadata()
pypi_url = url_finder.find_github_url_from_pypi_page()
ossgadget_url = url_finder.find_github_url_from_ossgadget()

# all urls are empty
final_url = ""
accuracy = "0%"

# all urls are equal
if metadata_url == pypi_url and pypi_url == ossgadget_url:
    final_url = metadata_url
    accuracy = "100%"
else:
    # at least two urls are equal
    if metadata_url == pypi_url or metadata_url == ossgadget_url:
        final_url = metadata_url
        accuracy = "66%"
    elif pypi_url == ossgadget_url:
        final_url = pypi_url
        accuracy = "66%"
    else:
        # at least one url is not empty
        if ossgadget_url != "":
            final_url = ossgadget_url
            accuracy = "33%"
        elif pypi_url != "":
            final_url = pypi_url
            accuracy = "33%"
        elif metadata_url != "":
            final_url = metadata_url
            accuracy = "33%"

#logger.info(f"{metadata_url}, {pypi_url}, {ossgadget_url}")
logger.info(f"Package name: {package_name} --> GitHub url: {final_url} (Accuracy: {accuracy})")