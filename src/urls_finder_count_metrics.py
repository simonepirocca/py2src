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

utils_module_path = Path().resolve() / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/url_finder.log")

# Set source and range
input_file = "../output/url_finder_final.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
lev_dist_0 = 0
name_substring = 0
true_stats = 0
low_descr_dist = 0
true_readthedocs = 0
true_github_badge = 0
true_pypi_badge = 0
high_python_lang = 0
complete_rows_1 = [0, 0, 0, 0, 0, 0, 0, 0]
complete_rows_2 = [0, 0, 0, 0, 0, 0, 0, 0]

# Open urls csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            # Get accuracy and three GitHub URLs with the final one from the row
            package_name = row[0]
            old_url = row[1]
            useless = row[2]
            metadata_url = row[3]
            pypi_url = row[4]
            ossgadget_url = row[5]
            final_url = row[6]
            accuracy = row[7]
            different = row[8]

            # Get metrics
            lev_dist_text = row[9]
            similarity = row[10]
            statistics_url = row[11]
            descr_dist_text = row[12]
            readthedocs_link = row[13]
            github_badge = row[14]
            pypi_badge = row[15]
            python_lang = row[16]

            matching_metrics = 0

            lev_distance = lev_dist_text.split("/")[0]
            if lev_distance == "0": lev_dist_0 += 1
            if similarity == "Substring": name_substring += 1
            if similarity == "Substring" or lev_distance == "0": matching_metrics += 1

            if statistics_url == "True":
                true_stats += 1
                matching_metrics += 1

            descr_distance = float(descr_dist_text.split("/")[0])
            descr_len = float(descr_dist_text.split("/")[1])
            dist_len_rel = 0
            if descr_len != 0: dist_len_rel = round(float(descr_distance / descr_len), 3)
            if dist_len_rel < 0.5:
                low_descr_dist += 1
                matching_metrics += 1

            if readthedocs_link == "True":
                true_readthedocs += 1
                matching_metrics += 1

            if github_badge == "True":
                true_github_badge += 1
                matching_metrics += 1

            if pypi_badge == "True":
                true_pypi_badge += 1
                matching_metrics += 1

            # Get Python language on GitHub page
            perc = float(python_lang[:-1])
            if perc > 50: 
                high_python_lang += 1
                matching_metrics += 1

            complete_rows_1[matching_metrics] += 1
            for i in range(0, matching_metrics+1): complete_rows_2[i] += 1

        #if len(urls) % 100 == 0 and line_count > start: logger.info(f"rows: {len(urls)}")
        line_count += 1
        if line_count >= end: break

# Print out the information and store the new values into the file
logger.info(f"------------------------------------------ rows {start}-{end-1} -------------------------------------------")
logger.info(f"Complete rows 1: {complete_rows_1}, Complete rows 2: {complete_rows_2}")
logger.info(f"Package name Lev. distance 0: {lev_dist_0}, Package name SUB: {name_substring}, Statistics: {true_stats}, Low descriptions Lev. distance: {low_descr_dist}")
logger.info(f"Readthedocs.io: {true_readthedocs}, GitHub/Travis badge: {true_github_badge}, PyPI badge: {true_pypi_badge}, High Python lang. perc.: {high_python_lang}")
logger.info(f"-------------------------------------------------------------------------------------------------------------------------")