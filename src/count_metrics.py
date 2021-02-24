"""
This file get all the missing metrics for each repo
"""
import sys
import os
import csv
import json
import pytest
import logging
from pathlib import Path

utils_module_path = Path().resolve() / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/metrics.log")

# Set source, output and range
input_file = "../output/metrics_final.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
empty_cells = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
not_empty_cells = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
missing_github_url = 0
complete_rows = 0
semi_complete_rows = 0
useless_rows = 0
tot_packages = 0

# Open old metrics csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= 1:
            complete_row = True
            semi_complete_row = True
            useless_row = True

            for i in range(0, 14):
                if row[i] != "" and i in [3, 4, 5, 6, 7, 8, 10, 11, 12, 13]: useless_row = False
                if row[i] == "":
                    empty_cells[i] += 1
                    complete_row = False
                    if i in [1, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13]: semi_complete_row = False
                else: not_empty_cells[i] += 1
 
            if complete_row: complete_rows += 1
            if semi_complete_row: semi_complete_rows += 1
            if useless_row: useless_rows += 1
            tot_packages += 1

        line_count += 1
        if line_count >= end: break

# Print out the information
logger.info(f"Tot packages: {tot_packages}, Complete rows: {complete_rows}, Semi-complete rows: {semi_complete_rows}, Useless rows: {useless_rows}")
logger.info(f"Empty cells: {empty_cells}")
logger.info(f"NOT Empty cells: {not_empty_cells}")