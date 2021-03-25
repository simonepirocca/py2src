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
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.INFO, log_filepath="../logs/url_finder.log")

# Set source and range
wrong_already_checked_urls_input_file = "../output/url_finder_output/wrong_33_package_urls.csv"
all_already_checked_urls_input_file = "../output/url_finder_output/github_urls_to_check.csv"
to_check_urls_input_file = "../output/url_finder_output/github_urls_remaining_to_check.csv"
urls_info_input_file = "../output/url_finder_output/github_urls_from_diff_sources_2.csv"
output_file = "../output/url_finder_output/github_urls_ground_proof.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
wrong_already_checked_urls = {}
all_already_checked_urls = {}
to_check_urls = {}
urls = []
tps = [0, 0, 0, 0, 0, 0, 0, 0, 0]
fps = [0, 0, 0, 0, 0, 0, 0, 0, 0]
tns = [0, 0, 0, 0, 0, 0, 0, 0, 0]
fns = [0, 0, 0, 0, 0, 0, 0, 0, 0]
accuracy = [0, 0, 0, 0, 0, 0, 0, 0, 0]
precision = [0, 0, 0, 0, 0, 0, 0, 0, 0]
recall = [0, 0, 0, 0, 0, 0, 0, 0, 0]
f1_score = [0, 0, 0, 0, 0, 0, 0, 0, 0]

# Open wrong already checked urls csv file
with open(wrong_already_checked_urls_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start: wrong_already_checked_urls[row[0]] = row[2]
        line_count += 1
        if line_count >= end: break

# Open all already checked urls csv file
with open(all_already_checked_urls_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start: all_already_checked_urls[row[0]] = row[1]
        line_count += 1
        if line_count >= end: break

# Open to check urls csv file
with open(to_check_urls_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start: to_check_urls[row[0]] = row[4]
        line_count += 1
        if line_count >= end: break

# Open urls info csv file
with open(urls_info_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            package_name = row[0]

            real_url = "CONTINUE"
            if package_name in wrong_already_checked_urls: real_url = wrong_already_checked_urls[package_name]
            elif package_name in all_already_checked_urls: real_url = all_already_checked_urls[package_name]
            elif package_name in to_check_urls: real_url = to_check_urls[package_name]

            if real_url != "CONTINUE":

                urls_row = []
                urls_row.append(package_name)
                for i in range(1, 9):
                    urls_row.append(row[i])
                    if row[i] == "":
                        if real_url == "": tns[i-1] += 1
                        else: fns[i-1] += 1
                    else:
                        if real_url == row[i]: tps[i-1] += 1
                        else: fps[i-1] += 1

                urls_row.append(row[16])
                if row[16] == "":
                    if real_url == "": tns[8] += 1
                    else: fns[8] += 1
                else:
                    if real_url == row[16]: tps[8] += 1
                    else: fps[8] += 1

                urls_row.append(real_url)
                urls.append(urls_row)

        #if len(urls) % 500 == 0 and line_count > start: logger.info(f"rows: {len(urls)}")
        line_count += 1
        if line_count >= end: break
beta = 0.4
for i in range(0, 9):
    acc_number = round(100 * (float(tps[i] + tns[i]) / float(tps[i] + tns[i] + fps[i] + fns[i])))
    accuracy[i] = str(acc_number) + "%"

    prec_number = float(tps[i]) / float(tps[i] + fps[i])
    precision[i] = str(round(100 * prec_number)) + "%"

    rec_number = float(tps[i]) / float(tps[i] + fns[i])
    recall[i] = str(round(100 * rec_number)) + "%"

    f1_number_num = (1 + beta * beta) * tps[i]
    f1_number_den = ((1 + beta * beta) * tps[i]) + (beta * beta * fns[i]) + fps[i]
    f1_number = float(f1_number_num) / float(f1_number_den)
    f1_score[i] = str(round(100 * f1_number)) + "%"

# Print out the information and store the new values into the file
logger.info(f"---------------------------- rows {len(urls)} ---------------------------------")
logger.info(f"TPs: {tps}, FPs: {fps}")
logger.info(f"TNs: {tns}, FNs: {fns}")
logger.info(f"Precision: {precision}, Recall: {recall}")
logger.info(f"Accuracy: {accuracy}, F1 Score: {f1_score}")
logger.info(f"---------------------------------------------------------------------------")
#with open(output_file, mode='w') as csv_file:
#    urls_writer = csv.writer(csv_file, delimiter=';')
#    urls_writer.writerow(["Package name", "OSSGadget URL", "Metadata URL", "Homepage URL", "PyPI URL", "PyPI 2 URL",\
# "Statistics URL", "Readthedocs URL", "PyPI badge URL", "Final URL", "Real URL"])
#    for i in range(0, len(urls)):
#        urls_writer.writerow(urls[i])