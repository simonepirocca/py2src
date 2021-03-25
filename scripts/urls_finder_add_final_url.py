"""
This file add some metrics to the URLs gathered
"""
import json
import sys
import os
import csv
import logging
import pytest
from pathlib import Path

from ..src.url_finder import URLFinder
from ..src.utils import log_function_output
#logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filepath="../logs/url_finder.log")
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.INFO, log_filepath="../logs/url_finder.log")

src_module_path = Path().resolve().parent / "src" / "levenshtein_distance"
sys.path.append(str(src_module_path))
from string_distance import StringDistance

# Set source and range
input_file = "../output/url_finder_output/github_urls_from_diff_sources.csv"
output_file = "../output/url_finder_output/github_urls_from_diff_sources_1.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
urls = []
diff_urls_in_row = [0, 0, 0, 0, 0]
ossgadget_other_diff_tp = 0
ossgadget_other_diff_fp = 0
ossgadget_other_diff_tp_maybe = 0
ossgadget_other_diff_fp_maybe = 0
ossgadget_other_diff_empty = 0
ossgadget_diff_empty = 0
ossgadget_diff_other_empty = 0
ossgadget_diff_total = 0
ossgadget_equal_to_final_url = 0
ossgadget_equal_to_second_url = 0
ossgadget_equal_to_third_url = 0

if start == 1: 
    with open(output_file, mode='w') as csv_file:
        urls_writer = csv.writer(csv_file, delimiter=';')
        urls_writer.writerow(["Package name", "OSSGadget URL", "Metadata URL", "Homepage URL", "PyPI URL", "PyPI 2 URL", "Statistics URL", "Readthedocs URL", "PyPI badge URL",\
 "Names Lev. dist.", "Names Similarity", "Descr. Lev. dist.", "GitHub badge", "Python lang. perc.", "Other languages", "OSSGadget position",\
 "Final URL", "Occ. final URL", "Second URL", "Occ. second URL", "Third URL", "Occ. third URL", "URLs similarity"])

# Open urls csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            # Get URLs coming from different sources
            package_name = row[0]
            ossgadget_url = row[1]
            ossgadget_position = row[15]

            final_urls = {}

            for i in range(2, 9):
                tmp_url = row[i]
                if tmp_url != "":
                    if tmp_url in final_urls: final_urls[tmp_url] += 1
                    else: final_urls[tmp_url] = 1

            occ_final_url = 0
            final_url = ""
            for url in final_urls:
                count = final_urls[url]
                if count > occ_final_url:
                    occ_final_url = count
                    final_url = url

            occ_second_url = 0
            second_url = ""
            for url in final_urls:
                if url != final_url:
                    count = final_urls[url]
                    if count > occ_second_url:
                        occ_second_url = count
                        second_url = url

            occ_third_url = 0
            third_url = ""
            for url in final_urls:
                if url != final_url and url != second_url:
                    count = final_urls[url]
                    if count > occ_third_url:
                        occ_third_url = count
                        third_url = url

            if final_url == ossgadget_url:
                ossgadget_equal_to_final_url += 1
                ossgadget_final_url_similarity = "Equal"
            else:
                if second_url == ossgadget_url and second_url != "":
                    ossgadget_final_url_similarity = "Equal to second URL"
                    ossgadget_equal_to_second_url += 1
                    logger.info(f"{line_count}. Equal to second URL '{package_name}'")
                elif third_url == ossgadget_url and third_url != "":
                    ossgadget_final_url_similarity = "Equal to third URL"
                    ossgadget_equal_to_third_url += 1
                    logger.info(f"{line_count}. Equal to third URL '{package_name}'")
                else:
                    ossgadget_final_url_similarity = "Different"
                    ossgadget_diff_total += 1
                if ossgadget_url == "": ossgadget_diff_empty += 1
                elif final_url == "": ossgadget_diff_other_empty += 1
                if ossgadget_position == "TP" and final_url != "": ossgadget_other_diff_tp += 1
                if ossgadget_position == "TP" and final_url != "": ossgadget_other_diff_tp += 1
                elif ossgadget_position == "FP" and final_url != "": ossgadget_other_diff_fp += 1
                elif ossgadget_position == "TP(?)" and final_url != "": ossgadget_other_diff_tp_maybe += 1
                elif ossgadget_position == "FP(?)" and final_url != "": ossgadget_other_diff_fp_maybe += 1
                elif ossgadget_position == "" and final_url != "": ossgadget_other_diff_empty += 1

            diff_urls_in_row[len(final_urls)] += 1

            # Append urls information
            tmp_row = []
            for i in range(0, 16): tmp_row.append(row[i])
            tmp_row.append(final_url)
            tmp_row.append(occ_final_url)
            tmp_row.append(second_url)
            tmp_row.append(occ_second_url)
            tmp_row.append(third_url)
            tmp_row.append(occ_third_url)
            tmp_row.append(ossgadget_final_url_similarity)
            urls.append(tmp_row)

        #if len(urls) % 500 == 0 and line_count > start: logger.info(f"rows: {len(urls)}")
        line_count += 1
        if line_count >= end: break

# Print out the information and store the new values into the file
logger.info(f"----------------------------------------------- rows {start}-{end-1} -----------------------------------------------------------")
logger.info(f"Different URLs in a row: {diff_urls_in_row}")
logger.info(f"Equal to final URL: {ossgadget_equal_to_final_url}, Equal to second URL: {ossgadget_equal_to_second_url}, Equal to third URL: {ossgadget_equal_to_third_url}, Different OSSGadget Total: {ossgadget_diff_total}, Different OSSGadget empty: {ossgadget_diff_empty}, Different other empty: {ossgadget_diff_other_empty}")
logger.info(f"Diff TP: {ossgadget_other_diff_tp}, Diff FP: {ossgadget_other_diff_fp}, Diff TP maybe: {ossgadget_other_diff_tp_maybe}, Diff FP maybe: {ossgadget_other_diff_fp_maybe}, Diff empty: {ossgadget_other_diff_empty}")
logger.info(f"--------------------------------------------------------------------------------------------")
with open(output_file, mode='a') as csv_file:
    urls_writer = csv.writer(csv_file, delimiter=';')
#    urls_writer.writerow(["Package name", "OSSGadget URL", "Metadata URL", "Homepage URL", "PyPI URL", "PyPI 2 URL", "Statistics URL", "Readthedocs URL", "PyPI badge URL",\
# "Names Lev. dist.", "Names Similarity", "Descr. Lev. dist.", "GitHub badge", "Python lang. perc.", "Other languages", "OSSGadget position",\
# "Final URL", "Occ. final URL", "Second URL", "Occ. second URL", "Third URL", "Occ. third URL", "URLs similarity"])
    for i in range(0, len(urls)):
        urls_writer.writerow(urls[i])