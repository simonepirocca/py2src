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
input_file = "../output/url_finder_output/github_urls_from_diff_sources_1.csv"
output_file = "../output/url_finder_output/github_urls_from_diff_sources_2.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
urls = []
diff_packages = 0
tp = 0
fp = 0
tp_maybe = 0
fp_maybe = 0
tp_tp = 0
tp_fp = 0
fp_tp = 0
fp_fp = 0

if start == 1: 
    with open(output_file, mode='w') as csv_file:
        urls_writer = csv.writer(csv_file, delimiter=';')
        urls_writer.writerow(["Package name", "OSSGadget URL", "Metadata URL", "Homepage URL", "PyPI URL", "PyPI 2 URL", "Statistics URL", "Readthedocs URL", "PyPI badge URL",\
 "Names Lev. dist.", "Names Similarity", "Descr. Lev. dist.", "GitHub badge", "Python lang. perc.", "Other languages", "OSSGadget position",\
 "Final URL", "Occ. final URL", "Second URL", "Occ. second URL", "Third URL", "Occ. third URL", "URLs similarity",\
 "Names Lev. dist.", "Names Similarity", "Descr. Lev. dist.", "GitHub badge", "Python lang. perc.", "Other languages", "Final URL position"])

# Open urls csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            # Get URLs coming from different sources
            package_name = row[0]
            ossgadget_position = row[15]
            final_url = row[16]
            urls_similarity = row[22]

            lev_dist_text = ""
            similarity = ""
            descr_dist_text = ""
            github_badge = ""
            python_lang = ""
            other_languages = ""
            final_url_position = ""
            if urls_similarity != "Equal" and final_url != "":
                diff_packages += 1
                finder = URLFinder(package_name)
                finder.set_github_url(final_url)

                if final_url[-1] != "/": url_package_name = final_url.split("/")[-1]
                else: url_package_name = final_url.split("/")[-2]

                # Calculate Levenshtein distance and similarity between package names
                lev_distance = StringDistance().lev_distances_raw_strs(url_package_name, package_name)
                len1 = len(url_package_name)
                len2 = len(package_name)
                if len1 > len2: max_lev_dist = len1
                else: max_lev_dist = len2
                lev_dist_text = str(lev_distance) + "/" + str(max_lev_dist)

                similarity = "Different"
                if url_package_name == package_name: similarity = "Equal"
                elif url_package_name in package_name or package_name in url_package_name: similarity = "Substring"

                # Check Levenshtein distance between PyPI and GitHub descriptions
                pypi_descr = finder.get_pypi_descr().replace("\n","")
                github_descr = finder.get_github_descr().replace("\n","")
                descr_distance = StringDistance().lev_distances_raw_strs(pypi_descr, github_descr)
                len1 = len(pypi_descr)
                len2 = len(github_descr)
                if len1 > len2: max_descr_dist = len1
                else: max_descr_dist = len2
                descr_dist_text = str(descr_distance) + "/" + str(max_descr_dist)

                # Get PyPI badge, Python and other languages on GitHub page
                github_badge = finder.check_pypi_badge()
                python_lang = finder.check_python_lang()
                other_languages = finder.get_other_lang()

                matching_metrics = 0

                if lev_dist_text != "":
                    lev_distance = lev_dist_text.split("/")[0]
                    if lev_distance == "0" or lev_distance == "1" or similarity == "Substring": matching_metrics += 1

                if descr_dist_text != "":
                    descr_distance = float(descr_dist_text.split("/")[0])
                    descr_len = float(descr_dist_text.split("/")[1])
                    dist_len_rel = 0
                    if descr_len != 0: dist_len_rel = round(float(descr_distance / descr_len), 3)
                    if dist_len_rel < 0.5: matching_metrics += 1

                if github_badge == "True" or github_badge == True:
                    final_url_position = "TP"
                    tp += 1

                perc = 0
                if python_lang != "": perc = float(python_lang[:-1])
                if perc > 50: matching_metrics += 1
                elif perc == 0 and other_languages != "":
                    final_url_position = "FP"
                    fp += 1

                if final_url_position == "":
                    if matching_metrics == 3:
                        final_url_position = "TP(?)"
                        tp_maybe += 1
                    elif matching_metrics == 0:
                        final_url_position = "FP(?)"
                        fp_maybe += 1

                if ossgadget_position == "TP" and final_url_position == "TP":
                    tp_tp += 1
                    logger.info(f"{line_count}. TP --> TP: '{package_name}'")
                elif ossgadget_position == "TP" and final_url_position == "FP":
                    tp_fp += 1
                    logger.info(f"{line_count}. TP --> FP: '{package_name}'")
                elif ossgadget_position == "FP" and final_url_position == "TP":
                    fp_tp += 1
                    logger.info(f"{line_count}. FP --> TP: '{package_name}'")
                elif ossgadget_position == "FP" and final_url_position == "FP":
                    fp_fp += 1
                    logger.info(f"{line_count}. FP --> FP: '{package_name}'")

            # Append urls information
            tmp_row = []
            for i in range(0, 23): tmp_row.append(row[i])
            tmp_row.append(lev_dist_text)
            tmp_row.append(similarity)
            tmp_row.append(descr_dist_text)
            tmp_row.append(github_badge)
            tmp_row.append(python_lang)
            tmp_row.append(other_languages)
            tmp_row.append(final_url_position)
            urls.append(tmp_row)

        if len(urls) % 500 == 0 and line_count > start: logger.info(f"rows: {len(urls)}")
        line_count += 1
        if line_count >= end: break

# Print out the information and store the new values into the file
logger.info(f"----------------------------------------------- rows {start}-{end-1} -----------------------------------------------------------")
logger.info(f"Different packages: {diff_packages}")
logger.info(f"TP: {tp}, FP: {fp}, TP maybe: {tp_maybe}, FP maybe: {fp_maybe}")
logger.info(f"TP --> TP: {tp_tp}, TP --> FP: {tp_fp}, FP --> TP: {fp_tp}, FP --> FP: {fp_fp}")
logger.info(f"-------------------------------------------------------------------------------------------------------------------------")
with open(output_file, mode='a') as csv_file:
    urls_writer = csv.writer(csv_file, delimiter=';')
#    urls_writer.writerow(["Package name", "OSSGadget URL", "Metadata URL", "Homepage URL", "PyPI URL", "PyPI 2 URL", "Statistics URL", "Readthedocs URL", "PyPI badge URL",\
# "Names Lev. dist.", "Names Similarity", "Descr. Lev. dist.", "GitHub badge", "Python lang. perc.", "Other languages", "OSSGadget position",\
# "Final URL", "Occ. final URL", "Second URL", "Occ. second URL", "Third URL", "Occ. third URL", "URLs similarity",\
# "Names Lev. dist.", "Names Similarity", "Descr. Lev. dist.", "GitHub badge", "Python lang. perc.", "Other languages", "Final URL position"])
    for i in range(0, len(urls)):
        urls_writer.writerow(urls[i])