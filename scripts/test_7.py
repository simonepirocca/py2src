"""
This file fix the metrics related to the URLs gathered
"""
import json
import sys
import os
import csv
import logging
import pytest
import random
from pathlib import Path

from ..src.utils import log_function_output
#logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filepath="../logs/url_finder.log")
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.INFO, log_filepath="../logs/url_finder.log")

# Set source and range
urls_input_file = "../output/url_finder_final.csv"
ground_truth_input_file = "../output/url_finder_output/github_urls_ground_proof.csv"
output_file = "../output/url_finder_output/ground_truth_validation_45.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
tot_packages = 0
set_1 = [] # OSSGadget == ILSGadget != ModeURL
set_2 = [] # OSSGadet != ILSGadget == ModeURL
set_3 = [] # OSSGadget == ModeURL
packages_dict = {}
final_packages = []
final_set = []

# Open urls csv file
with open(ground_truth_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            #row = ["Package name", "OSSGadget GitHub URL", "Metadata URL", "Homepage URL", "PyPI URL", "PyPI 2 URL", "Statistics URL", "Readthedocs URL", "PyPI badge URL", "Final URL", "Real URL"]

            package_name = row[0]
            ossgadget_url = row[1]
            mode_url = row[9]
            ils_url = row[10]

            new_row = [package_name, row[8], row[3], row[2], row[4], row[5], row[7], row[6], ossgadget_url, mode_url, ils_url]

            if ossgadget_url == ils_url and ils_url != mode_url and ils_url != "":
                set_1.append(package_name)
                packages_dict[package_name] = new_row
            elif ossgadget_url != ils_url and ils_url == mode_url and ils_url != "":
                set_2.append(package_name)
                packages_dict[package_name] = new_row
            elif ossgadget_url == mode_url and ossgadget_url != "":
                set_3.append(package_name)
                packages_dict[package_name] = new_row

            tot_packages += 1

        line_count += 1
        if line_count >= end: break

random.shuffle(set_1)
random.shuffle(set_2)
random.shuffle(set_3)

for i in range(0, 15):
    final_packages.append(set_1[i])
    final_packages.append(set_2[i])
    final_packages.append(set_3[i])

final_packages.sort()

for package in final_packages:
    final_set.append(packages_dict[package])

# Print out the information and store the new values into the file
logger.info(f"------------------------------------------ rows: {tot_packages} -----------------------------------------")
logger.info(f"Set 1: {len(set_1)}, Set 2: {len(set_2)}, Set 3: {len(set_3)}")
logger.info(f"Final set lenght: {len(final_set)}")
logger.info(f"Final set: {final_set}")
logger.info(f"--------------------------------------------------------------------------------------------")

with open(output_file, mode='w') as csv_file:
    urls_writer = csv.writer(csv_file, delimiter=';')
    urls_writer.writerow(['Package name', 'Badge URL', 'Homepage URL', 'Metadata URL', 'Page Cons. URL',\
 'Page Major. URL', 'Readthedocs URL', 'Statistics URL', 'OSSGadget URL', 'Mode URL', 'ILSGadget URL'])
    for i in range(0, len(final_set)):
        urls_writer.writerow(final_set[i])