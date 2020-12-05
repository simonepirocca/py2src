import sys
import os
import csv
import logging
logging.basicConfig(filename="log.log", level=logging.INFO)
sys.path.append(os.path.abspath('../src/url_finder'))
from url_finder import URLFinder

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

    logging.info(f"{metadata_url}, {pypi_url}, {ossgadget_url}")
    logging.info(f"GitHub url: {final_url}, Accuracy: {accuracy}")