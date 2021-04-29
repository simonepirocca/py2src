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
input_file = "../output/url_finder_output/github_urls_ground_proof.csv"
output_file = "../output/url_finder_output/github_urls_ground_truth_no_pages.csv"
start = 1
count = 400
end = start + count

# Inizialize variables
urls = []
positions = {0: 0, 1: 8, 2: 3, 3: 2, 4: 7, 5: 6, 6: 1, 7: 9, 8: 10}
tps = [0, 0, 0, 0, 0, 0, 0, 0]
fps = [0, 0, 0, 0, 0, 0, 0, 0]
tns = [0, 0, 0, 0, 0, 0, 0, 0]
fns = [0, 0, 0, 0, 0, 0, 0, 0]
accuracy = [0, 0, 0, 0, 0, 0, 0, 0]
precision = [0, 0, 0, 0, 0, 0, 0, 0]
recall = [0, 0, 0, 0, 0, 0, 0, 0]
f1_score = [0, 0, 0, 0, 0, 0, 0, 0]

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
            mode_url = row[9]
            final_url = "" #ModeThanOss
            real_url = row[10]

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
                logger.info(f"{line_count}. Mode URL: {old_mode_url} --> {mode_url}")

            final_url = mode_url
            if mode_url == "" and ossgadget_url != "": final_url = ossgadget_url

            urls_row = []
            urls_row.append(package_name)
            for i in range(1, 8):
                tmp_url = row[positions[i]]
                urls_row.append(tmp_url)
                if tmp_url == "":
                    if real_url == "": tns[i-1] += 1
                    else: fns[i-1] += 1
                else:
                    if real_url == tmp_url: tps[i-1] += 1
                    else: fps[i-1] += 1

            urls_row.append(final_url)
            if final_url == "":
                if real_url == "": tns[7] += 1
                else: fns[7] += 1
            else:
                if real_url == final_url: tps[7] += 1
                else: fps[7] += 1

            urls_row.append(real_url)
            urls.append(urls_row)

        line_count += 1
        if line_count >= end: break

beta = 0.4
for i in range(0, 8):
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
with open(output_file, mode='w') as csv_file:
    urls_writer = csv.writer(csv_file, delimiter=';')
    urls_writer.writerow(["Package name", "Badge URL", "Homepage URL", "Metadata URL",\
 "Readthedocs URL", "Statistics URL", "OSSGadget URL", "Mode URL", "Final URL", "Real URL"])
    for i in range(0, len(urls)):
        urls_writer.writerow(urls[i])