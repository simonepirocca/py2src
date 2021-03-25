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
tot_packages = 0
diff_urls_in_row = [0, 0, 0, 0, 0]
ossgadget_other_diff_tp = 0
ossgadget_other_diff_fp = 0
ossgadget_other_diff_tp_maybe = 0
ossgadget_other_diff_fp_maybe = 0
ossgadget_other_diff_empty = 0
ossgadget_diff_empty = 0
ossgadget_diff_other_empty = 0
ossgadget_diff_total = 0
# Open urls csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            #row = ["Package name", "OSSGadget URL", "Metadata URL", "Homepage URL", "PyPI URL", "PyPI 2 URL", "Statistics URL", "Readthedocs URL", "PyPI badge URL"]

            package_name = row[0]
            ossgadget_url = row[1]
            ossgadget_position = row[15]

            final_urls = {}

            for i in range(2, 9):
                tmp_url = row[i]
                if tmp_url != "":
                    if tmp_url in final_urls: final_urls[tmp_url] += 1
                    else: final_urls[tmp_url] = 1

            matching_urls = 0
            final_url = ""
            for url in final_urls:
                count = final_urls[url]
                if count > matching_urls: 
                    matching_urls = count
                    final_url = url

            if len(final_urls) == 3: logger.info(f"{line_count}. Diff 3 '{package_name}'")
            elif len(final_urls) == 4: logger.info(f"{line_count}. Diff 4 '{package_name}'")

            if final_url != ossgadget_url:
                ossgadget_diff_total += 1
                if ossgadget_url == "": ossgadget_diff_empty += 1
                elif final_url == "": ossgadget_diff_other_empty += 1
                if ossgadget_position == "TP": ossgadget_other_diff_tp += 1
                if ossgadget_position == "TP": ossgadget_other_diff_tp += 1
                elif ossgadget_position == "FP": ossgadget_other_diff_fp += 1
                elif ossgadget_position == "TP(?)": ossgadget_other_diff_tp_maybe += 1
                elif ossgadget_position == "FP(?)": ossgadget_other_diff_fp_maybe += 1
                else: ossgadget_other_diff_empty += 1

            diff_urls_in_row[len(final_urls)] += 1

            tot_packages += 1

        #if len(urls) % 100 == 0 and line_count > start: logger.info(f"rows: {len(urls)}")
        line_count += 1
        if line_count >= end: break

# Print out the information and store the new values into the file
logger.info(f"------------------------------------------ rows: {tot_packages} -----------------------------------------")
logger.info(f"Different URLs in a row: {diff_urls_in_row}")
logger.info(f"Different OSSGadget Total: {ossgadget_diff_total}, Different OSSGadget empty: {ossgadget_diff_empty}, Different other empty: {ossgadget_diff_other_empty}")
logger.info(f"Diff TP: {ossgadget_other_diff_tp}, Diff FP: {ossgadget_other_diff_fp}, Diff TP maybe: {ossgadget_other_diff_tp_maybe}, Diff FP maybe: {ossgadget_other_diff_fp_maybe}, Diff empty: {ossgadget_other_diff_empty}")
logger.info(f"--------------------------------------------------------------------------------------------")