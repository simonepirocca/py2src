"""
This file add some metrics to the URLs gathered
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
wrong_urls_input_file = "../output/url_finder_output/github_urls_to_check.csv"
input_file = "../output/url_finder_output/github_urls_from_diff_sources_2.csv"
all_output_file = "../output/url_finder_output/github_urls_all_to_check.csv"
remaining_output_file = "../output/url_finder_output/github_urls_remaining_to_check.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
checked_urls = []
all_to_check_urls = []
not_checked_urls = []

# Open wrong urls csv file
with open(wrong_urls_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start: checked_urls.append(row[0])
        line_count += 1
        if line_count >= end: break

# Open urls csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            package_name = row[0]
            ossgadget_url = row[1]
            ossgadget_position = row[15]
            final_url = row[16]
            urls_similarity = row[22]

            if ossgadget_position == "FP":
                all_to_check_urls.append([package_name, ossgadget_url, final_url, "OSSGadget URL FP"])
                if package_name not in checked_urls: not_checked_urls.append([package_name, ossgadget_url, final_url, "OSSGadget URL FP"])
            elif ossgadget_position == "FP(?)":
                all_to_check_urls.append([package_name, ossgadget_url, final_url, "OSSGadget URL FP maybe"])
                if package_name not in checked_urls: not_checked_urls.append([package_name, ossgadget_url, final_url, "OSSGadget URL FP maybe"])
            elif urls_similarity != "Equal":
                all_to_check_urls.append([package_name, ossgadget_url, final_url, urls_similarity])
                if package_name not in checked_urls: not_checked_urls.append([package_name, ossgadget_url, final_url, urls_similarity])

        #if len(urls) % 500 == 0 and line_count > start: logger.info(f"rows: {len(urls)}")
        line_count += 1
        if line_count >= end: break

# Print out the information and store the new values into the file
logger.info(f"----------------------------------------------- rows {start}-{end-1} -----------------------------------------------------------")
logger.info(f"Total URLs to check: {len(all_to_check_urls)}, Not checked yet: {len(not_checked_urls)}")
logger.info(f"-------------------------------------------------------------------------------------------------------------------------")
with open(all_output_file, mode='w') as csv_file:
    urls_writer = csv.writer(csv_file, delimiter=';')
    urls_writer.writerow(["Package name", "OSSGadget URL", "Final URL", "Motivation"])
    for i in range(0, len(all_to_check_urls)):
        urls_writer.writerow(all_to_check_urls[i])
with open(remaining_output_file, mode='w') as csv_file:
    urls_writer = csv.writer(csv_file, delimiter=';')
    urls_writer.writerow(["Package name", "OSSGadget URL", "Final URL", "Motivation"])
    for i in range(0, len(not_checked_urls)):
        urls_writer.writerow(not_checked_urls[i])