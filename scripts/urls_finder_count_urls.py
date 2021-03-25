"""
This file fix the metrics related to the URLs gathered
"""
import json
import sys
import os
import csv
import logging
import pytest
from pathlib import Path

from ..src.utils import log_function_output
#logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filepath="../logs/url_finder.log")
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.INFO, log_filepath="../logs/url_finder.log")

# Set source and range
input_file = "../output/url_finder_output/github_urls_from_diff_sources.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
complete_rows_1 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
complete_rows_2 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
equal_rows_1 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
equal_rows_2 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
not_empty = [0, 0, 0, 0, 0, 0, 0, 0, 0]
tot_packages = 0
ossgadget_github_pypi_empty = 0
useful_ossgadget_github = 0
ossgadget_empty = [0, 0, 0, 0, 0, 0, 0]
equal_to_ossgadget_rows_1 = [0, 0, 0, 0, 0, 0, 0, 0]
equal_to_ossgadget_rows_2 = [0, 0, 0, 0, 0, 0, 0, 0]
equal_to_ossgadget_not_empty = [0, 0, 0, 0, 0, 0, 0]
equal_cols_not_empty = []
for i in range(0, 8): equal_cols_not_empty.append([0, 0, 0, 0, 0, 0, 0, 0])
# Open urls csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            #row = ["Package name", "OSSGadget PyPI URL", "OSSGadget GitHub URL", "Metadata URL", "Homepage URL", "PyPI URL", "PyPI 2 URL", "Statistics URL", "Readthedocs URL", "PyPI badge URL"]
 
            package_name = row[0]

            final_url = {}
            not_empty_urls = 0
            equal_to_ossgadget_urls = 0

            if row[1] != "":
                equal_cols_not_empty[0][0] += 1
                not_empty[0] += 1
                not_empty_urls += 1
                final_url[row[1]] = 1
            if row[2] != "":
                not_empty[1] += 1
                if row[1] == "":
                    ossgadget_github_pypi_empty += 1
                    useful = True
                    for i in range(3, 10):
                        if row[i] != "":
                            useful = False
                            break
                    if useful == True: useful_ossgadget_github += 1

            for j in range(3, 10):
                if row[j] != "" and row[j] == row[1]: equal_cols_not_empty[0][j-2] += 1

            for i in range(3, 10):
                if row[1] != "" and row[1] == row[i]: equal_cols_not_empty[i-2][0] += 1
                for j in range(3, 10): 
                    if row[j] != "" and row[j] == row[i]: equal_cols_not_empty[i-2][j-2] += 1
                tmp_url = row[i]
                if tmp_url != "":
                    not_empty[i-1] += 1
                    not_empty_urls += 1
                    if tmp_url == row[1]:
                        equal_to_ossgadget_not_empty[i-3] += 1
                        equal_to_ossgadget_urls += 1
                    elif row[1] == "": ossgadget_empty[i-3] += 1
                    if tmp_url in final_url: final_url[tmp_url] += 1
                    else: final_url[tmp_url] = 1

            matching_urls = 0
            for url in final_url:
                count = final_url[url]
                if count > matching_urls: matching_urls = count

            complete_rows_1[not_empty_urls] += 1
            for i in range(0, not_empty_urls+1): complete_rows_2[i] += 1

            equal_rows_1[matching_urls] += 1
            for i in range(0, matching_urls+1): equal_rows_2[i] += 1

            equal_to_ossgadget_rows_1[equal_to_ossgadget_urls] += 1
            for i in range(0, equal_to_ossgadget_urls+1): equal_to_ossgadget_rows_2[i] += 1

            tot_packages += 1

        #if len(urls) % 100 == 0 and line_count > start: logger.info(f"rows: {len(urls)}")
        line_count += 1
        if line_count >= end: break

# Print out the information and store the new values into the file
logger.info(f"------------------------------------------ rows: {tot_packages} -----------------------------------------")
logger.info(f"Complete rows 1: {complete_rows_1}, Complete rows 2: {complete_rows_2}")
logger.info(f"Equal rows 1: {equal_rows_1}, Equal rows 2: {equal_rows_2}")
logger.info(f"Equal to OSSGadget rows 1: {equal_to_ossgadget_rows_1}, Equal to OSSGadget rows 2: {equal_to_ossgadget_rows_2}")
logger.info(f"Not Empty: {not_empty}, Equal to OSSGadget (not empty): {equal_to_ossgadget_not_empty}, OSSGadget empty: {ossgadget_empty}")
logger.info(f"Equal cols (not empty): {equal_cols_not_empty}")
logger.info(f"GitHub OSSGadget PyPI empty: {ossgadget_github_pypi_empty}, Useful OSSGadget GitHub: {useful_ossgadget_github}")
logger.info(f"--------------------------------------------------------------------------------------------")