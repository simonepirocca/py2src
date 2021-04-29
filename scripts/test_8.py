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
input_file = "../output/url_finder_output/github_urls_ground_truth_no_pages.csv"
start = 1
count = 400
end = start + count

# Inizialize variables
urls = []
equal_ossgadget_1 = [0, 0, 0, 0, 0, 0]
equal_mode_1 = [0, 0, 0, 0, 0, 0]
equal_final_1 = [0, 0, 0, 0, 0, 0]
equal_real_1 = [0, 0, 0, 0, 0, 0]
equal_ossgadget_2 = [0, 0, 0, 0, 0, 0]
equal_mode_2 = [0, 0, 0, 0, 0, 0]
equal_final_2 = [0, 0, 0, 0, 0, 0]
equal_real_2 = [0, 0, 0, 0, 0, 0]

# Open urls info csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            package_name = row[0]
            ossgadget_url = row[6]
            mode_url = row[7]
            final_url = row[8]
            real_url = row[9]

            equal_to_ossgadget = 0
            equal_to_mode = 0
            equal_to_final = 0
            equal_to_real = 0
            for i in range(1, 6):
                tmp_url = row[i]
                if tmp_url == ossgadget_url: equal_to_ossgadget += 1
                if tmp_url == mode_url: equal_to_mode += 1
                if tmp_url == final_url: equal_to_final += 1
                if tmp_url == real_url: equal_to_real += 1

            equal_ossgadget_1[equal_to_ossgadget] += 1
            for j in range(0, equal_to_ossgadget+1): equal_ossgadget_2[j] += 1

            equal_mode_1[equal_to_mode] += 1
            for j in range(0, equal_to_mode+1): equal_mode_2[j] += 1

            equal_final_1[equal_to_final] += 1
            for j in range(0, equal_to_final+1): equal_final_2[j] += 1

            equal_real_1[equal_to_real] += 1
            for j in range(0, equal_to_real+1): equal_real_2[j] += 1

        line_count += 1
        if line_count >= end: break

# Print out the information
logger.info(f"-------------------------------------------------------------")
logger.info(f"Equals to OSSGadget 1: {equal_ossgadget_1}, Equals to OSSGadget 2: {equal_ossgadget_2}")
logger.info(f"Equals to Mode 1: {equal_mode_1}, Equals to Mode 2: {equal_mode_2}")
logger.info(f"Equals to Final 1: {equal_final_1}, Equals to Final 2: {equal_final_2}")
logger.info(f"Equals to Real 1: {equal_real_1}, Equals to Real 2: {equal_real_2}")
logger.info(f"---------------------------------------------------------------------------")