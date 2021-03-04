"""
This file get the GitHub URL a list of packages (JSON file), using three sources, and the related accuracy
"""
import json
import sys
import os
import csv
import logging
import pytest
from urllib.request import Request, urlopen
from pathlib import Path

url_finder_module_path = Path().resolve() / "url_finder"
sys.path.append(str(url_finder_module_path))
from url_finder import URLFinder

# Set source, output and range
pypi_repos_json = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-365-days.json"
output_file = "../output/url_finder_output/github_urls.csv"
start = 1
count = 10
end = start + count
urls = []

# Open and decode the JSON file
with urlopen(pypi_repos_json) as response:
    packages = json.loads(response.read().decode())["rows"]

    # Analyse each row in the range
    for i in range(start, end):
        # Get package name and downloads from the row
        package_name = packages[i-1]["project"]
        downloads = packages[i-1]["download_count"]

        url_finder = URLFinder(package_name)

        # use three different sources to gather the URL
        metadata_url = url_finder.find_github_url_from_metadata()
        pypi_url = url_finder.find_github_url_from_pypi_page()
        ossgadget_url = url_finder.find_github_url_from_ossgadget()

        # all urls are empty
        final_url = ""
        accuracy = "0%"
    
        # all urls are equal
        if metadata_url != "" and metadata_url == pypi_url and pypi_url == ossgadget_url:
            final_url = metadata_url
            accuracy = "100%"
        else:
            # at least two urls are equal
            if metadata_url != "" and (metadata_url == pypi_url or metadata_url == ossgadget_url):
                final_url = metadata_url
                accuracy = "66%"
            elif pypi_url != "" and pypi_url == ossgadget_url:
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
        urls.append([package_name, final_url, accuracy, downloads])

# Store the urls
with open(output_file, mode='w') as csv_file:
    urls_writer = csv.writer(csv_file, delimiter=';')
    urls_writer.writerow(["Package name", "GitHub URL", "Accuracy", "PyPi downloads"])
    for i in range(0, len(urls)):
        urls_writer.writerow(urls[i])
