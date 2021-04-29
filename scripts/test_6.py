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
input_file = "../output/url_finder_final.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
swap_dict = {0: 0, 1: 3, 2: 2, 3: 4, 4: 5, 5: 7, 6: 6, 7: 1}


tot_packages = 0
equal_cols_not_empty_1 = []
equal_cols_not_empty_2 = []
equal_cols_not_empty_3 = []
equal_cols_empty_1 = []
equal_cols_empty_2 = []
equal_cols_empty_3 = []
for i in range(0, 8):
    equal_cols_not_empty_1.append([0, 0, 0, 0, 0, 0, 0, 0])
    equal_cols_not_empty_2.append([0, 0, 0, 0, 0, 0, 0, 0])
    equal_cols_not_empty_3.append([0, 0, 0, 0, 0, 0, 0, 0])
    equal_cols_empty_1.append([0, 0, 0, 0, 0, 0, 0, 0])
    equal_cols_empty_2.append([0, 0, 0, 0, 0, 0, 0, 0])
    equal_cols_empty_3.append([0, 0, 0, 0, 0, 0, 0, 0])

# Open urls csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            #row = ["Package name", "OSSGadget GitHub URL", "Metadata URL", "Homepage URL", "PyPI URL", "PyPI 2 URL", "Statistics URL", "Readthedocs URL", "PyPI badge URL"]

            package_name = row[0]

            for i in range(0, 8):
                for j in range(0, 8):
                    if row[j+1] == row[i+1]:
                        if row[i+1] != "": equal_cols_not_empty_1[swap_dict[i]][swap_dict[j]] += 1
                        else: equal_cols_empty_1[swap_dict[i]][swap_dict[j]] += 1

            tot_packages += 1

        #if len(urls) % 100 == 0 and line_count > start: logger.info(f"rows: {len(urls)}")
        line_count += 1
        if line_count >= end: break

for i in range(0, 8):
    i_count_not_empty = equal_cols_not_empty_1[i][i]
    i_count_empty = equal_cols_empty_1[i][i]
    for j in range(0, 8):
        j_i_count_not_empty = equal_cols_not_empty_1[i][j]
        j_i_count_empty = equal_cols_empty_1[i][j]
        equal_cols_not_empty_2[i][j] = str(round(100 * (float(j_i_count_not_empty) / float(i_count_not_empty)))) + "%"
        equal_cols_not_empty_3[i][j] = str(round(100 * (float(j_i_count_not_empty) / float(4000)))) + "%"
        equal_cols_empty_2[i][j] = str(round(100 * (float(j_i_count_empty) / float(i_count_empty)))) + "%"
        equal_cols_empty_3[i][j] = str(round(100 * (float(j_i_count_empty) / float(4000)))) + "%"

# Print out the information and store the new values into the file
logger.info(f"------------------------------------------ rows: {tot_packages} -----------------------------------------")
logger.info(f"Equal cols NOT EMPTY TOT: {equal_cols_not_empty_1}")
logger.info(f"Equal cols NOT EMPTY ABS: {equal_cols_not_empty_2}")
logger.info(f"Equal cols NOT EMPTY ABS: {equal_cols_not_empty_3}")
logger.info(f"Equal cols EMPTY TOT: {equal_cols_empty_1}")
logger.info(f"Equal cols EMPTY REL: {equal_cols_empty_2}")
logger.info(f"Equal cols EMPTY ABS: {equal_cols_empty_3}")
logger.info(f"--------------------------------------------------------------------------------------------")