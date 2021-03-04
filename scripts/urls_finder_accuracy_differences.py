"""
This file check differences between old and new ways to find GitHub urls
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

# Set source and range
#input_file = "../output/url_finder_output/urls_with_duplicates.csv"
input_file = "../output/url_finder_final.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
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
metadata_urls = 0
pypi_urls = 0
ossgadget_urls = 0
metadata_66_urls = 0
pypi_66_urls = 0
ossgadget_66_urls = 0
metadata_not_not_empty_66_urls = 0
pypi_not_not_empty_66_urls = 0
ossgadget_not_not_empty_66_urls = 0
metadata_not_66_urls = 0
pypi_not_66_urls = 0
ossgadget_not_66_urls = 0
metadata_33_urls = 0
pypi_33_urls = 0
ossgadget_33_urls = 0
metadata_not_33_urls = 0
pypi_not_33_urls = 0
ossgadget_not_33_urls = 0
metadata_33_right_urls = 0
pypi_33_right_urls = 0
ossgadget_33_right_urls = 0
metadata_33_right_other_not_empty_urls = 0
pypi_33_right_other_not_empty_urls = 0
ossgadget_33_right_other_not_empty_urls = 0
true_positives = [0, 0, 0]
false_positives = [0, 0, 0]
true_positives_unique_not_empty = [0, 0, 0]
false_positives_other_not_empty = [0, 0, 0]
false_positives_other_right = [0, 0, 0]

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

            if useless == "True": useless_urls += 1

            if metadata_url != "": metadata_urls += 1
            if pypi_url != "": pypi_urls += 1
            if ossgadget_url != "": ossgadget_urls += 1

            if accuracy == "66%":
                if final_url == metadata_url: metadata_66_urls += 1
                if final_url == pypi_url: pypi_66_urls += 1
                if final_url == ossgadget_url: ossgadget_66_urls += 1
                if metadata_url != final_url: 
                    metadata_not_66_urls += 1
                    if metadata_url != "": metadata_not_not_empty_66_urls += 1
                if pypi_url != final_url: 
                    pypi_not_66_urls += 1
                    if pypi_url != "": pypi_not_not_empty_66_urls += 1
                if ossgadget_url != final_url: 
                    ossgadget_not_66_urls += 1
                    if ossgadget_url != "": ossgadget_not_not_empty_66_urls += 1

            if accuracy == "33%":
                if metadata_url != "": 
                    metadata_33_urls += 1
                    if metadata_url != final_url: metadata_not_33_urls += 1
                    else:
                        metadata_33_right_urls += 1
                        if pypi_url != "" or ossgadget_url != "": metadata_33_right_other_not_empty_urls += 1
                if pypi_url != "": 
                    pypi_33_urls += 1
                    if pypi_url != final_url: pypi_not_33_urls += 1
                    else:
                        pypi_33_right_urls += 1
                        if metadata_url != "" or ossgadget_url != "": pypi_33_right_other_not_empty_urls += 1
                if ossgadget_url != "": 
                    ossgadget_33_urls += 1
                    if ossgadget_url != final_url: ossgadget_not_33_urls += 1
                    else:
                        ossgadget_33_right_urls += 1
                        if pypi_url != "" or metadata_url != "": ossgadget_33_right_other_not_empty_urls += 1

            if different == "True":
                different_urls += 1
                if useless == "True": different_useless_urls += 1
                if final_url != "":
                    different_not_empty_urls += 1
                    if useless == "True": different_not_empty_useless_urls += 1

            if accuracy == "0%": accuracy_0 += 1
            elif accuracy == "33%": accuracy_33 += 1
            elif accuracy == "66%": accuracy_66 += 1
            elif accuracy == "100%": accuracy_100 += 1

            if metadata_url != "":
                if metadata_url == final_url: 
                    true_positives[0] += 1
                    if pypi_url == "" and ossgadget_url == "": true_positives_unique_not_empty[0] += 1
                else:
                    false_positives[0] += 1
                    if pypi_url != "" or ossgadget_url != "": false_positives_other_not_empty[0] += 1
                    if pypi_url == final_url or ossgadget_url == final_url: false_positives_other_right[0] += 1

            if pypi_url != "":
                if pypi_url == final_url: 
                    true_positives[1] += 1
                    if metadata_url == "" and ossgadget_url == "": true_positives_unique_not_empty[1] += 1
                else:
                    false_positives[1] += 1
                    if ossgadget_url != "" or ossgadget_url != "": false_positives_other_not_empty[1] += 1
                    if ossgadget_url == final_url or ossgadget_url == final_url: false_positives_other_right[1] += 1

            if ossgadget_url != "":
                if ossgadget_url == final_url: 
                    true_positives[2] += 1
                    if pypi_url == "" and ossgadget_url == "": true_positives_unique_not_empty[2] += 1
                else:
                    false_positives[2] += 1
                    if pypi_url != "" or ossgadget_url != "": false_positives_other_not_empty[2] += 1
                    if pypi_url == final_url or ossgadget_url == final_url: false_positives_other_right[2] += 1

            total_packages += 1

        line_count += 1
        if line_count > end: break

# Print out the information
logger.info(f"Total packages: {total_packages}, Useless rows: {useless_urls}")
logger.info(f"Metadata URLs: {metadata_urls}, PyPI URLs: {pypi_urls}, OSSGadget URLs: {ossgadget_urls}")
logger.info(f"Different URLs: {different_urls}, Different useless URLs: {different_useless_urls}")
logger.info(f"Different NOT EMPTY URLs: {different_not_empty_urls}, Different NOT EMPTY useless URLs: {different_not_empty_useless_urls}")
logger.info(f"Accuracy 0%: {accuracy_0}, Accuracy 33%: {accuracy_33}, Accuracy 66%: {accuracy_66}, Accuracy 100%: {accuracy_100}")
logger.info(f"Metadata 66% URLs: {metadata_66_urls}, PyPI 66% URLs: {pypi_66_urls}, OSSGadget 66% URLs: {ossgadget_66_urls}")
logger.info(f"Metadata NOT 66% URLs: {metadata_not_66_urls}, PyPI NOT 66% URLs: {pypi_not_66_urls}, OSSGadget NOT 66% URLs: {ossgadget_not_66_urls}")
logger.info(f"Metadata NOT (NOT EMPTY) 66% URLs: {metadata_not_not_empty_66_urls}, PyPI NOT (NOT EMPTY) 66% URLs: {pypi_not_not_empty_66_urls}, OSSGadget NOT (NOT EMPTY) 66% URLs: {ossgadget_not_not_empty_66_urls}")
logger.info(f"Metadata 33% URLs: {metadata_33_urls}, PyPI 33% URLs: {pypi_33_urls}, OSSGadget 33% URLs: {ossgadget_33_urls}")
logger.info(f"Metadata NOT 33% URLs: {metadata_not_33_urls}, PyPI NOT 33% URLs: {pypi_not_33_urls}, OSSGadget NOT 33% URLs: {ossgadget_not_33_urls}")
logger.info(f"Metadata 33% right URLs: {metadata_33_right_urls}, PyPI 33% right URLs: {pypi_33_right_urls}, OSSGadget 33% right URLs: {ossgadget_33_right_urls}")
logger.info(f"Metadata 33% other not empty URLs: {metadata_33_right_other_not_empty_urls}, PyPI 33% other not empty URLs: {pypi_33_right_other_not_empty_urls}, OSSGadget 33% other not empty URLs: {ossgadget_33_right_other_not_empty_urls}")
logger.info(f"True Positives: {true_positives}, False Positives: {false_positives}")
logger.info(f"True Positives unique not empty: {true_positives_unique_not_empty}, False Positives other not empty: {false_positives_other_not_empty}, False positives other right: {false_positives_other_right}")
