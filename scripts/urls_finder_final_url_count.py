"""
This file creates the ground proof for validating URL finder sources
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
logger = log_function_output(file_level=logging.INFO, console_level=logging.INFO, log_filepath="../logs/url_finder.log")

# Set source and range
input_file = "../output/url_finder_final.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
positions = {0: 0, 1: 8, 2: 3, 3: 2, 4: 7, 5: 6, 6: 1, 7: 9, 8: 10}
final_urls = 0

# Open urls info csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            package_name = row[0]
            badge_url = row[8]
            homepage_url = row[3]
            metadata_url = row[2]
            page_conservative_url = row[4]
            page_majority_url = row[5]
            readthedocs_url = row[7]
            statistics_url = row[6]
            ossgadget_url = row[1]
            mode_url = row[16]
            final_url = "" #ModeThanOss

            if mode_url != "" and (mode_url == page_conservative_url or mode_url == page_majority_url):
                new_mode_urls = {}
                old_mode_url = mode_url
                for j in range(1, 6):
                    tmp_url = row[positions[j]]
                    if tmp_url != "":
                        if tmp_url in new_mode_urls: new_mode_urls[tmp_url] += 1
                        else: new_mode_urls[tmp_url] = 1

                occ_mode_url = 0
                mode_url = ""
                for url in new_mode_urls:
                    count = new_mode_urls[url]
                    if count > occ_mode_url:
                        occ_mode_url = count
                        mode_url = url
                row[9] = mode_url
                #logger.info(f"{line_count}. Mode URL: {old_mode_url} --> {mode_url}")

            final_url = mode_url
            if mode_url == "" and ossgadget_url != "": final_url = ossgadget_url

            if final_url != "": final_urls += 1

        line_count += 1
        if line_count >= end: break

# Print out the information
logger.info(f"---------------------------- rows 4000 ---------------------------------")
logger.info(f"Final URLs: {final_urls}")
logger.info(f"---------------------------------------------------------------------------")