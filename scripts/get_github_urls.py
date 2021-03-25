"""
This file gets the GitHub URL from different sources
"""
import sys
import os
import csv
import json
import pytest
import logging
from pathlib import Path

from ..src.url_finder import URLFinder
from ..src.utils import log_function_output
#logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filepath="../logs/url_finder.log")
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.INFO, log_filepath="../logs/url_finder.log")

# Set source, output and range
input_file = "../output/url_finder_final.csv"
output_file = "../output/url_finder_output/github_urls_from_diff_sources.csv"
start = 1
count = 500
end = start + count

# Inizialize variables
urls = []

if start == 1: 
    with open(output_file, mode='w') as csv_file:
        urls_writer = csv.writer(csv_file, delimiter=';')
        urls_writer.writerow(["Package name", "OSSGadget PyPI URL", "OSSGadget GitHub URL", "Metadata URL", "Homepage URL", "PyPI URL", "PyPI 2 URL", "Statistics URL", "Readthedocs URL", "PyPI badge URL"])

# Open old urls csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            package_name = row[0]
            finder = URLFinder(package_name)

            ossgadget_pypi_url = finder.find_ossgadget_url("pypi")
            ossgadget_github_url = finder.find_ossgadget_url("github")
            #metadata_url = finder.find_github_url_from_homepage_metadata()
            #homepage_url = finder.find_github_url_from_homepage_webpage()
            #pypi_url = finder.find_github_url_from_pypi_webpage()
            metadata_url = finder.mode_1()
            homepage_url = finder.mode_2()
            pypi_url = finder.mode_3()
            pypi_2_url = finder.find_github_url_from_pypi_page()
            statistics_url = finder.find_github_url_from_pypi_statistics()
            readthedocs_url = finder.find_github_url_from_readthedocs()
            pypi_badge_url = finder.find_github_url_from_pypi_badge()

            urls.append([package_name, ossgadget_pypi_url, ossgadget_github_url, metadata_url, homepage_url, pypi_url, pypi_2_url, statistics_url, readthedocs_url, pypi_badge_url])

        if len(urls) % 50 == 0 and line_count > start: 
            logger.info(f"rows: {len(urls)}")
            with open(output_file, mode='a') as csv_file:
                urls_writer = csv.writer(csv_file, delimiter=';')
                for i in range(0, len(urls)):
                    urls_writer.writerow(urls[i])
            urls = []

        line_count += 1
        if line_count >= end: break

# Store the information
#with open(output_file, mode='a') as csv_file:
#    urls_writer = csv.writer(csv_file, delimiter=';')
#    urls_writer.writerow(["Package name", "OSSGadget PyPI URL", "OSSGadget GitHub URL", "Metadata URL", "Homepage URL", "PyPI URL", "PyPI 2 URL", "Statistics URL", "Readthedocs URL", "GitHub badge URL"])
#    for i in range(0, len(urls)):
#        urls_writer.writerow(urls[i])
