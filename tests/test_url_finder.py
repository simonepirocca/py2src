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

# Test the GitHub URL gathering of a package, using three sources
def test_github_url_gathering():
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

def test_find_missing_urls():
    input_csv = "../output/metrics_output/metrics_final_with_tags_and_0.csv"
    output_csv = "../output/metrics_output/missing_urls.csv"
    # Open the URL file
    with open(input_csv) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            github_url = row[2]
            if github_url == "":
                # Write the package name into the missing urls file, if URL is empty 
                with open(output_csv, mode='a') as missing_csv:
                    packages_writer = csv.writer(missing_csv, delimiter=';')
#                    packages_writer.writerow([row[0]])