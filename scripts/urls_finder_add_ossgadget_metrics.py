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
old_input_file = "../output/url_finder_final.csv"
input_file = "../output/url_finder_output/github_urls_from_diff_sources_copy.csv"
output_file = "../output/url_finder_output/github_urls_from_diff_sources.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
old_urls = []
urls = []
diff_packages = 0
tp = 0
fp = 0
tp_maybe = 0
fp_maybe = 0

# Open old urls csv file
with open(old_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            old_urls.append(row)
        line_count += 1
        if line_count >= end: break

if start == 1: 
    with open(output_file, mode='w') as csv_file:
        urls_writer = csv.writer(csv_file, delimiter=';')
        urls_writer.writerow(["Package name", "OSSGadget URL", "Metadata URL", "Homepage URL", "PyPI URL", "PyPI 2 URL", "Statistics URL", "Readthedocs URL", "PyPI badge URL",\
 "Names Lev. dist.", "Names Similarity", "Descr. Lev. dist.", "GitHub badge", "Python lang. perc.", "Other languages", "OSSGadget position"])

# Open urls csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            # Get URLs coming from different sources
            package_name = row[0]
            ossgadget_url = row[1]
            metadata_url = row[3]
            homepage_url = row[4]
            pypi_url = row[5]
            pypi_2_url = row[6]
            statistics_url = row[7]
            readthedocs_url = row[8]
            pypi_badge_url = row[9]

            old_final_url = old_urls[line_count-1][6]
            if ossgadget_url == "":
                lev_dist_text = ""
                similarity = ""
                descr_dist_text = ""
                github_badge = ""
                python_lang = ""
                other_languages = ""
            elif old_final_url == ossgadget_url:
                lev_dist_text = old_urls[line_count-1][9]
                similarity = old_urls[line_count-1][10]
                descr_dist_text = old_urls[line_count-1][12]
                github_badge = old_urls[line_count-1][15]
                python_lang = old_urls[line_count-1][16]
                other_languages = old_urls[line_count-1][17]
            else:
                diff_packages += 1
                finder = URLFinder(package_name)
                finder.set_github_url(ossgadget_url)

                if ossgadget_url[-1] != "/": url_package_name = ossgadget_url.split("/")[-1]
                else: url_package_name = ossgadget_url.split("/")[-2]

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

            ossgadget_position = ""
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
                ossgadget_position = "TP"
                tp += 1

            perc = 0
            if python_lang != "": perc = float(python_lang[:-1])
            if perc > 50: matching_metrics += 1
            elif perc == 0 and other_languages != "" and ossgadget_url != "":
                ossgadget_position = "FP"
                fp += 1

            if ossgadget_position == "" and ossgadget_url != "":
                if matching_metrics == 3:
                    ossgadget_position = "TP(?)"
                    tp_maybe += 1
                elif matching_metrics == 0:
                    ossgadget_position = "FP(?)"
                    fp_maybe += 1

            # Append urls information
            urls.append([package_name, ossgadget_url, metadata_url, homepage_url, pypi_url, pypi_2_url, statistics_url, readthedocs_url, pypi_badge_url,\
 lev_dist_text, similarity, descr_dist_text, github_badge, python_lang, other_languages, ossgadget_position])

        if len(urls) % 500 == 0 and line_count > start: logger.info(f"rows: {len(urls)}")
        line_count += 1
        if line_count >= end: break

# Print out the information and store the new values into the file
logger.info(f"----------------------------------------------- rows {start}-{end-1} -----------------------------------------------------------")
logger.info(f"Different packages: {diff_packages}")
logger.info(f"TP: {tp}, FP: {fp}, TP maybe: {tp_maybe}, FP maybe: {fp_maybe}")
logger.info(f"-------------------------------------------------------------------------------------------------------------------------")
with open(output_file, mode='a') as csv_file:
    urls_writer = csv.writer(csv_file, delimiter=';')
#    urls_writer.writerow(["Package name", "OSSGadget URL", "Metadata URL", "Homepage URL", "PyPI URL", "PyPI 2 URL", "Statistics URL", "Readthedocs URL", "PyPI badge URL",\
# "Names Lev. dist.", "Names Similarity", "Descr. Lev. dist.", "GitHub badge", "Python lang. perc.", "Other languages", "OSSGadget position"])
    for i in range(0, len(urls)):
        urls_writer.writerow(urls[i])