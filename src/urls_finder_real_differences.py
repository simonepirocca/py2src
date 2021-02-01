"""
This file check if different GitHub urls gathered redirects to the same one
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

# Set source and range
input_file = "../output/url_finder_output/github_urls.csv"
output_file = "../output/url_finder_output/github_urls_real_differences.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
accuracy_changed_33 = 0
accuracy_changed_66 = 0
redirections_33 = 0
redirections_66 = 0
no_different_33 = 0
no_different_66 = 0
urls = []

# Open matching packages csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            # Get accuracy and three GitHub URLs with the final one from the row
            package_name = row[0]
            old_url = row[1]
            useless = row[2]
            metadata_url = row[3]
            pypi_url = row[4]
            ossgadget_url = row[5]
            final_url = row[6]
            accuracy = row[7]
            different = row[8]

            if accuracy == "33%" and\
               ((metadata_url != "" and (pypi_url != "" or ossgadget_url != "")) or\
                (pypi_url != "" and (metadata_url != "" or ossgadget_url != "")) or\
                (ossgadget_url != "" and (pypi_url != "" or metadata_url != ""))):
                old_final_url = final_url
                url_redirection = False
                if metadata_url != "":
                    url_request = Request(metadata_url, headers={"User-Agent": "Mozilla/5.0"})
                    url_response = urlopen(url_request)
                    new_metadata_url = URLFinder.normalize_url(url_response.geturl())
                    if new_metadata_url != metadata_url:
                        redirections_33 += 1
                        logger.info(f"{line_count}. Redirection: metadata URL {metadata_url} --> {new_metadata_url}")
                        metadata_url = new_metadata_url
                        url_redirection = True

                if pypi_url != "":
                    url_request = Request(pypi_url, headers={"User-Agent": "Mozilla/5.0"})
                    url_response = urlopen(url_request)
                    new_pypi_url = URLFinder.normalize_url(url_response.geturl())
                    if new_pypi_url != pypi_url:
                        redirections_33 += 1
                        logger.info(f"{line_count}. Redirection: metadata URL {pypi_url} --> {new_pypi_url}")
                        pypi_url = new_pypi_url
                        url_redirection = True

                if ossgadget_url != "":
                    url_request = Request(ossgadget_url, headers={"User-Agent": "Mozilla/5.0"})
                    url_response = urlopen(url_request)
                    new_ossgadget_url = URLFinder.normalize_url(url_response.geturl())
                    if new_ossgadget_url != ossgadget_url:
                        redirections_33 += 1
                        logger.info(f"{line_count}. Redirection: metadata URL {ossgadget_url} --> {new_ossgadget_url}")
                        ossgadget_url = new_ossgadget_url
                        url_redirection = True

                if url_redirection == True:
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

                    if accuracy != "33%":
                        accuracy_changed_33 += 1
                        logger.info(f"{line_count}. Accuracy changed from 33% to {accuracy}")
                    if old_final_url != final_url:
                        logger.info(f"{line_count}. Redirection: final URL {old_final_url} --> {final_url}")
                        redirections_33 += 1
                        if old_url == final_url:
                            different = "False"
                            no_different_33 += 1
                            logger.info(f"{line_count}. Old and final URLs are NO MORE DIFFERENT")

            elif accuracy == "66%" and metadata_url != "" and pypi_url != "" and ossgadget_url != "":
                final_url_request = Request(final_url, headers={"User-Agent": "Mozilla/5.0"})
                final_url_response = urlopen(final_url_request)
                new_final_url = URLFinder.normalize_url(final_url_response.geturl())

                if metadata_url != final_url:
                    if metadata_url == new_final_url:
                        accuracy_changed_66 += 1
                        accuracy = "100%"
                        logger.info(f"{line_count}. Accuracy changed from 66% to 100%")
                    else:
                        url_request = Request(metadata_url, headers={"User-Agent": "Mozilla/5.0"})
                        url_response = urlopen(url_request)
                        new_metadata_url = URLFinder.normalize_url(url_response.geturl())
                        if new_metadata_url == new_final_url:
                            if new_metadata_url != metadata_url:
                                redirections_66 += 1
                                logger.info(f"{line_count}. Redirection: metadata URL {metadata_url} --> {new_metadata_url}")
                            accuracy_changed_66 += 1
                            accuracy = "100%"
                            logger.info(f"{line_count}. Accuracy changed from 66% to 100%")
                            metadata_url = new_final_url
                    if new_final_url != final_url:
                        logger.info(f"{line_count}. Redirection: final URL {final_url} --> {new_final_url}")
                        redirections_66 += 1
                        pypi_url = new_final_url
                        ossgadget_url = new_final_url
                        final_url = new_final_url
                        if old_url == final_url:
                            different = "False"
                            no_different_66 += 1
                            logger.info(f"{line_count}. Old and final URLs are NO MORE DIFFERENT")

                elif pypi_url != final_url:
                    if pypi_url == new_final_url:
                        accuracy_changed_66 += 1
                        logger.info(f"{line_count}. Accuracy changed from 66% to 100%")
                        accuracy = "100%"
                    else:
                        url_request = Request(pypi_url, headers={"User-Agent": "Mozilla/5.0"})
                        url_response = urlopen(url_request)
                        new_pypi_url = URLFinder.normalize_url(url_response.geturl())
                        if new_pypi_url == new_final_url:
                            if new_pypi_url != pypi_url:
                                redirections_66 += 1
                                logger.info(f"{line_count}. Redirection: pypi URL {pypi_url} --> {new_pypi_url}")
                            accuracy_changed_66 += 1
                            logger.info(f"{line_count}. Accuracy changed from 66% to 100%")
                            accuracy = "100%"
                            pypi_url = new_final_url
                    if new_final_url != final_url:
                        logger.info(f"{line_count}. Redirection: final URL {final_url} --> {new_final_url}")
                        redirections_66 += 1
                        metadata_url = new_final_url
                        ossgadget_url = new_final_url
                        final_url = new_final_url
                        if old_url == final_url:
                            different = "False"
                            no_different_66 += 1
                            logger.info(f"{line_count}. Old and final URLs are NO MORE DIFFERENT")

                elif ossgadget_url != final_url:
                    if ossgadget_url == new_final_url:
                        accuracy_changed_66 += 1
                        accuracy = "100%"
                        logger.info(f"{line_count}. Accuracy changed from 66% to 100%")
                    else:
                        url_request = Request(ossgadget_url, headers={"User-Agent": "Mozilla/5.0"})
                        url_response = urlopen(url_request)
                        new_ossgadget_url = URLFinder.normalize_url(url_response.geturl())
                        if new_ossgadget_url == new_final_url:
                            if new_ossgadget_url != ossgadget_url:
                                redirections_66 += 1
                                logger.info(f"{line_count}. Redirection: ossgadget URL {ossgadget_url} --> {new_ossgadget_url}")
                            accuracy_changed_66 += 1
                            accuracy = "100%"
                            logger.info(f"{line_count}. Accuracy changed from 66% to 100%")
                            ossgadget_url = new_final_url
                    if new_final_url != final_url:
                        logger.info(f"{line_count}. Redirection: final URL {final_url} --> {new_final_url}")
                        redirections_66 += 1
                        metadata_url = new_final_url
                        pypi_url = new_final_url
                        final_url = new_final_url
                        if old_url == final_url:
                            different = "False"
                            no_different_66 += 1
                            logger.info(f"{line_count}. Old and final URLs are NO MORE DIFFERENT")

            urls.append([package_name, old_url, useless, metadata_url, pypi_url, ossgadget_url, final_url, accuracy, different])

        line_count += 1
        if line_count > end: break

# Print out the information and store the new values into the file
logger.info(f"33% redirections: {redirections_33}, 33% accuracy change: {accuracy_changed_33}, 33% no more different: {no_different_33}")
logger.info(f"66% redirections: {redirections_66}, 66% accuracy change (100%): {accuracy_changed_66}, 66% no more different: {no_different_66}")
with open(output_file, mode='w') as csv_file:
    urls_writer = csv.writer(csv_file, delimiter=';')
    urls_writer.writerow(["Package name", "Old URL", "Useless", "Metadata URL", "PyPI URL", "OSSGadget URL", "Final URL", "Accuracy", "Different"])
    for i in range(0, len(urls)):
        urls_writer.writerow(urls[i])