"""
This file finds duplicated packages and gathers the URLs for them
"""
import sys
import os
import csv
import logging
import pytest
from pathlib import Path

utils_module_path = Path().resolve() / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/url_finder.log")

url_finder_module_path = Path().resolve() / "url_finder"
sys.path.append(str(url_finder_module_path))
from url_finder import URLFinder

# Set input and output files, inizialize variables
metrics_input_file = "../output/metrics_output/metrics.csv"
urls_input_file = "../output/url_finder_final.csv"
urls_output_file = "../output/url_finder_output/urls_with_duplicates.csv"
duplicates_output_file = "../output/url_finder_output/urls_duplicates.csv"
old_urls = []
urls = []
duplicates = []
old_urls_index = 0
start = 0

if start == 0:
    with open(urls_output_file, mode='w') as csv_file:
        urls_writer = csv.writer(csv_file, delimiter=';')
        urls_writer.writerow(["Package name", "Old URL", "Useless", "Metadata URL", "PyPI URL", "OSSGadget URL", "Final URL", "Accuracy", "Different"])
    with open(duplicates_output_file, mode='w') as csv_file:
        urls_writer = csv.writer(csv_file, delimiter=';')
        urls_writer.writerow(["Duplicated package name", "Old GitHub URL"])

# Open urls csv file
with open(urls_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > 0: old_urls.append(row)
        line_count += 1

# Open metrics csv file
with open(metrics_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count > start:
            package_name = row[0]

            # If the packages is already present, append the row as it is,
            # otherwise get the URLs
            if package_name == old_urls[old_urls_index][0]:
                urls.append(old_urls[old_urls_index])
                with open(urls_output_file, mode='a') as csv_file:
                    urls_writer = csv.writer(csv_file, delimiter=';')
                    urls_writer.writerow(old_urls[old_urls_index])
                old_urls_index += 1
            else:
                useless = False
                url_finder = URLFinder(package_name)

                # use three different sources to gather the URL
                old_url = URLFinder.normalize_url(row[2])
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

                if old_url == final_url: different = False
                else: different = True

                urls.append([package_name, old_url, useless, metadata_url, pypi_url, ossgadget_url, final_url, accuracy, different])
                duplicates.append([package_name, old_url])

                with open(urls_output_file, mode='a') as csv_file:
                    urls_writer = csv.writer(csv_file, delimiter=';')
                    urls_writer.writerow([package_name, old_url, useless, metadata_url, pypi_url, ossgadget_url, final_url, accuracy, different])
                with open(duplicates_output_file, mode='a') as csv_file:
                    urls_writer = csv.writer(csv_file, delimiter=';')
                    urls_writer.writerow([package_name, old_url])

        if len(urls) % 100 == 0 and line_count > start: 
            logger.info(f"Total old rows: {len(old_urls)}, Duplicates inserted: {len(duplicates)}, Total URLs rows: {len(urls)}")
        line_count += 1

# Print out the results and store the information into a csv file
logger.info(f"Total old rows: {len(old_urls)}, Duplicates inserted: {len(duplicates)}, Total URLs rows: {len(urls)}")
#with open(urls_output_file, mode='w') as csv_file:
#    urls_writer = csv.writer(csv_file, delimiter=';')
#    urls_writer.writerow(["Package name", "Old URL", "Useless", "Metadata URL", "PyPI URL", "OSSGadget URL", "Final URL", "Accuracy", "Different"])
#    for i in range(0, len(urls)):
#        urls_writer.writerow(urls[i])
#with open(duplicates_output_file, mode='w') as csv_file:
#    urls_writer = csv.writer(csv_file, delimiter=';')
#    urls_writer.writerow(["Duplicated package name"])
#    for i in range(0, len(duplicates)):
#        urls_writer.writerow(duplicates[i])