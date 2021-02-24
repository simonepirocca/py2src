"""
This file separate duplicates (with the same GitHub URL) from the 4000 packages csv file
"""
import json
import sys
import os
import csv
import logging
import pytest
from urllib.request import Request, urlopen
from pathlib import Path

utils_module_path = Path().resolve() / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/url_finder.log")

# Set source and range
input_file = "../output/url_finder_output/github_urls_with_fixed_metrics_and_urls.csv"
empty_output_file = "../output/metrics_output/github_urls_no_url.csv"
duplicates_output_file = "../output/metrics_output/github_urls_duplicates.csv"
urls_output_file = "../output/metrics_output/github_urls_without_duplicates.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
empty = []
duplicates = []
urls = []
tot_empty = 0
tot_urls = 0
tot_duplicates = 0

# Open urls csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            # Get accuracy and three GitHub URLs with the final one from the row
            package_name = row[0]
            final_url = row[6]
            if final_url != "" and final_url[-1] == "/": final_url = final_url[:-1]

            duplicated = False
            for j in range (0, tot_urls):
                if final_url != "" and final_url == urls[j][1]:
                    duplicated = True
                    break
            if not duplicated:
                if final_url == "":
                    empty.append([package_name])
                    tot_empty += 1
                else:
                    urls.append([package_name, final_url])
                    tot_urls += 1
            else:
                duplicates.append([package_name, final_url])
                tot_duplicates += 1

        line_count += 1
        if line_count > end: break

# Print out and store the information
logger.info(f"Not duplicated URLs: {tot_urls}, Duplicated URLs: {tot_duplicates}, Empty: {tot_empty}")

with open(empty_output_file, mode='w') as csv_file:
    urls_writer = csv.writer(csv_file, delimiter=';')
    urls_writer.writerow(["Package name"])
    for i in range(0, len(empty)):
        urls_writer.writerow(empty[i])

with open(duplicates_output_file, mode='w') as csv_file:
    urls_writer = csv.writer(csv_file, delimiter=';')
    urls_writer.writerow(["Package name", "Final URL"])
    for i in range(0, len(duplicates)):
        urls_writer.writerow(duplicates[i])

with open(urls_output_file, mode='w') as csv_file:
    urls_writer = csv.writer(csv_file, delimiter=';')
    urls_writer.writerow(["Package name", "Final URL"])
    for i in range(0, len(urls)):
        urls_writer.writerow(urls[i])