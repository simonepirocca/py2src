"""
This file counts the number of unique packages and vulnerabilities present in a CSV file,
together with the number of occurrencies for each type of information regarding vulnerabilities
"""
import sys
import os
import csv
import logging
import pytest
from pathlib import Path

from ..src.utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.INFO, log_filepath="../logs/vulns.log")

# Set input file and range
input_csv = "../output/vulns_output/snyk_pip_vulns.csv"
start = 1 # DO NOT consider header line
count = 4000
end = start + count

# Inizialize variables
packages = []
not_empty_cells = [0, 0, 0, 0, 0, 0, 0, 0, 0]
complete_rows = 0
tot_packages = 0
tot_vulns = 0
line_count = 0

# Open the CSV file and read each line within the range
with open(input_csv) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    for row in csv_reader:
        if line_count >= start:

            # Check whether an information about the vulnerability is present or not;
            # in case it's present, update the related counter
            complete_row = True
            for i in range(0, 9):
                if row[i+5] == "": complete_row = False
                else: not_empty_cells[i] += 1
            # If the vulnerability holds all the information, update the counter
            if complete_row: complete_rows += 1

            # Put the related package in a list, checking if that name already exists
            duplicated = False
            package = row[3]
            if package != "":
                for j in range (0, tot_packages):
                    if package == packages[j]:
                        duplicated = True
                        break
            if not duplicated:
                packages.append(package)
                tot_packages += 1

            tot_vulns += 1

        line_count += 1
        #if line_count >= end: break

# Print out the total number of unique packages and vulnerabilities,
# together with the number of occurrencies for each type of information
logger.info(f"Tot vulns: {tot_vulns}, Tot packages: {tot_packages}, Complete rows: {complete_rows}")
logger.info(f"Not empty cells: {not_empty_cells}")
logger.info(f"-------------------------------------------------------------------------------------------------------------")
