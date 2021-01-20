"""
This file check differences between old and new way to find GitHub urls
"""
import json
import sys
import os
import csv
import logging
import pytest
from urllib.request import Request, urlopen
from pathlib import Path

utils_module_path = Path().resolve() / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/url_finder.log")

url_finder_module_path = Path().resolve() / "url_finder"
sys.path.append(str(url_finder_module_path))
from url_finder import URLFinder

# Set source, output and range
input_file = "../output/metrics_final.csv"
output_file = "../output/url_finder_output/github_urls.csv"
start = 1
count = 4000
end = start + count
urls = []

total_packages = 0
useless_urls = 0
different_urls = 0
different_not_empty_urls = 0
different_useless_urls = 0
different_not_empty_useless_urls = 0
accuracy_0 = 0
accuracy_33 = 0
accuracy_66 = 0
accuracy_100 = 0

#with open(output_file, mode='w') as csv_file:
#    urls_writer = csv.writer(csv_file, delimiter=';')
#    urls_writer.writerow(["Package name", "Old GitHub URL", "Useless", "New GitHub URL", "Accuracy", "Different"])

# Open matching packages csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            # Get package name and old GitHub URL from the row
            package_name = row[0]
            old_github_url = URLFinder.normalize_url(row[2])

            # Check if it is a 'useless' row
            useless = True
            for i in range(3, 14):
                if row[i] != "":
                    useless = False
                    break
            if useless == True: useless_urls += 1

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


            different_url = False
            if old_github_url != final_url:
                different_url = True
                different_urls += 1
                if useless == True: different_useless_urls += 1
                if final_url != "":
                    different_not_empty_urls += 1
                    if useless == True: different_not_empty_useless_urls += 1
            urls.append([package_name, old_github_url, useless, final_url, accuracy, different_url])


            if different_url == "True":
                different_urls += 1
                if final_url != "":
                    different_not_empty_urls += 1
                    if useless == "True": different_not_empty_useless_urls += 1
                if useless == "True": different_useless_urls += 1

            if accuracy == "0%": accuracy_0 += 1
            elif accuracy == "33%": accuracy_33 += 1
            elif accuracy == "66%": accuracy_66 += 1
            elif accuracy == "100%": accuracy_100 += 1

            total_packages += 1

        #if len(urls) % 100 == 0 and line_count > start: 
        #    logger.info(f"{len(urls)} rows red")
        #    with open(output_file, mode='a') as csv_file:
        #        urls_writer = csv.writer(csv_file, delimiter=';')
        #        for i in range((len(urls)-100), len(urls)): urls_writer.writerow(urls[i])

        line_count += 1
        if line_count > end: break

# Print out the number of (useless) different GitHub urls and 
# Store the urls
logger.info(f"Total packages: {total_packages}, Useless rows: {useless_urls}")
logger.info(f"Different URLs: {different_urls}, Different useless URLs: {different_useless_urls}")
logger.info(f"Different NOT EMPTY URLs: {different_not_empty_urls}, Different NOT EMPTY useless URLs: {different_not_empty_useless_urls}")
logger.info(f"Accuracy 0%: {accuracy_0}, Accuracy 33%: {accuracy_33}, Accuracy 66%: {accuracy_66}, Accuracy 100%: {accuracy_100}")
with open(output_file, mode='w') as csv_file:
    urls_writer = csv.writer(csv_file, delimiter=';')
    urls_writer.writerow(["Package name", "Old GitHub URL", "Useless", "New GitHub URL", "Accuracy", "Different"])
    for i in range(0, len(urls)):
        urls_writer.writerow(urls[i])
