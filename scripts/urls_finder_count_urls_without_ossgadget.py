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
input_file = "../output/url_finder_output/github_urls_from_diff_sources_2.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
complete_rows_1 = [0, 0, 0, 0, 0, 0, 0, 0]
complete_rows_2 = [0, 0, 0, 0, 0, 0, 0, 0]
equal_rows_1 = [0, 0, 0, 0, 0, 0, 0, 0]
equal_rows_2 = [0, 0, 0, 0, 0, 0, 0, 0]
not_empty = [0, 0, 0, 0, 0, 0, 0]
tp = [0, 0, 0, 0, 0, 0, 0]
fp = [0, 0, 0, 0, 0, 0, 0]
tot_packages = 0

# Open urls csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            package_name = row[0]
            final_url = row[16]

            not_empty_urls = 0
            right_urls = 0
            for i in range(2, 9):
                tmp_url = row[i]
                if tmp_url != "":
                    not_empty[i-2] += 1
                    not_empty_urls += 1
                    if tmp_url == final_url:
                        tp[i-2] += 1
                        right_urls += 1
                    else: fp[i-2] += 1

            complete_rows_1[not_empty_urls] += 1
            for i in range(0, not_empty_urls+1): complete_rows_2[i] += 1

            equal_rows_1[right_urls] += 1
            for i in range(0, right_urls+1): equal_rows_2[i] += 1

            tot_packages += 1

        #if len(urls) % 100 == 0 and line_count > start: logger.info(f"rows: {len(urls)}")
        line_count += 1
        if line_count >= end: break

# Print out the information
logger.info(f"------------------------------------------ rows: {tot_packages} -----------------------------------------")
logger.info(f"Complete rows 1: {complete_rows_1}, Complete rows 2: {complete_rows_2}")
logger.info(f"Equal rows 1: {equal_rows_1}, Equal rows 2: {equal_rows_2}")
logger.info(f"Not Empty: {not_empty}, TP: {tp}, FP: {fp}")
logger.info(f"--------------------------------------------------------------------------------------------")