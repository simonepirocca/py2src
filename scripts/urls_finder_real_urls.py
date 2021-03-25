"""
This file returns the real URL
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
checked_urls_input_file = "../output/url_finder_output/github_urls_ground_proof.csv"
input_file = "../output/url_finder_output/github_urls_from_diff_sources_3.csv"
output_file = "../output/url_finder_output/github_urls_real_urls.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
urls = []
checked_urls = {}
different = 0
diff_weight_empty = 0
diff_real_empty = 0
different1 = 0
diff_weight_empty1 = 0
diff_real_empty1 = 0
different2 = 0
diff_weight_empty2 = 0
diff_real_empty2 = 0

# Open checked urls csv file
with open(checked_urls_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start: checked_urls[row[0]] = row[10]
        line_count += 1
        if line_count >= end: break

# Open urls csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            # Get URLs coming from different sources
            package_name = row[0]
            ossgadget_url = row[1]
            major_url = row[16]
            weight_url = row[30]

            if package_name in checked_urls:
                real_url = checked_urls[package_name]
                if weight_url != real_url:
                    different += 1
                    if weight_url == "": diff_weight_empty += 1
                    elif real_url == "": diff_real_empty += 1

                if major_url != real_url:
                    different1 += 1
                    if major_url == "": diff_weight_empty1 += 1
                    elif real_url == "": diff_real_empty1 += 1

                if ossgadget_url != real_url:
                    different2 += 1
                    if ossgadget_url == "": diff_weight_empty2 += 1
                    elif real_url == "": diff_real_empty2 += 1
            else: real_url = weight_url

            tmp_row = []
            for i in range(0, 39): tmp_row.append(row[i])
            tmp_row.append(real_url)
            urls.append(tmp_row)

        line_count += 1
        if line_count >= end: break

# Print out the information and store the new values into the file
logger.info(f"----------------------------------------------- rows {len(urls)} -----------------------------------------------------------")
logger.info(f"Different: {different}, Different (Weight empty): {diff_weight_empty}, Different (Real empty): {diff_real_empty}")
logger.info(f"Different1: {different1}, Different1 (Majow empty): {diff_weight_empty1}, Different1 (Real empty): {diff_real_empty1}")
logger.info(f"Different1: {different2}, Different2 (OSSGadget empty): {diff_weight_empty2}, Different1 (Real empty): {diff_real_empty2}")
logger.info(f"--------------------------------------------------------------------------------------------")
#with open(output_file, mode='w') as csv_file:
#    urls_writer = csv.writer(csv_file, delimiter=';')
#    urls_writer.writerow(["Package name", "OSSGadget URL", "Metadata URL", "Homepage URL", "PyPI URL", "PyPI 2 URL", "Statistics URL", "Readthedocs URL", "PyPI badge URL",\
# "Names Lev. dist.", "Names Similarity", "Descr. Lev. dist.", "GitHub badge", "Python lang. perc.", "Other languages", "OSSGadget position",\
# "Major URL", "Occ. final URL", "Second URL", "Occ. second URL", "Third URL", "Occ. third URL", "URLs similarity",\
# "Names Lev. dist.", "Names Similarity", "Descr. Lev. dist.", "GitHub badge", "Python lang. perc.", "Other languages", "Major URL position", "Weight URL", "Confidence",\
# "Names Lev. dist.", "Names Similarity", "Descr. Lev. dist.", "GitHub badge", "Python lang. perc.", "Other languages", "Weight URL position", "Real URL"])
#    for i in range(0, len(urls)):
#        urls_writer.writerow(urls[i])