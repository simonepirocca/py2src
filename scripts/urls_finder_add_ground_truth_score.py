"""
This file add the Real URL
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
input_file = "../output/url_finder_output/github_urls_ground_truth_no_pages.csv"
urls_input_file = "../output/url_finder_final.csv"
output_file = "../output/url_finder_output/github_urls_ground_truth_no_pages_with_score.csv"
start = 1
count = 400
end = start + count

# Inizialize variables
urls = []
all_urls = {}
scores = {-4: 0, -3: 0, -2: 0, -1: 0, 0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
empty_urls = 0
new_urls = 0

# Open wrong already checked urls csv file
with open(urls_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= 1: all_urls[row[0]] = row
        line_count += 1

# Open urls csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            # Get URLs coming from different sources
            package_name = row[0]
            real_url = row[9]

            if package_name not in all_urls: logger.info(f"{line_count}. '{package_name}' is not in the set of 4000 packages")
            else:
                old_ossgadget_url = all_urls[package_name][1]
                old_mode_url = all_urls[package_name][16]
                old_weight_url = all_urls[package_name][30]
                if real_url == "":
                    empty_urls += 1
                    lev_dist_text = ""
                    similarity = ""
                    descr_dist_text = ""
                    github_badge = ""
                    python_lang = ""
                    other_languages = ""
                elif real_url == old_ossgadget_url and all_urls[package_name][9] != "":
                    lev_dist_text = all_urls[package_name][9]
                    similarity = all_urls[package_name][10]
                    descr_dist_text = all_urls[package_name][11]
                    github_badge = all_urls[package_name][12]
                    python_lang = all_urls[package_name][13]
                    other_languages = all_urls[package_name][14]
                elif real_url == old_mode_url and all_urls[package_name][23] != "":
                    lev_dist_text = all_urls[package_name][23]
                    similarity = all_urls[package_name][24]
                    descr_dist_text = all_urls[package_name][25]
                    github_badge = all_urls[package_name][26]
                    python_lang = all_urls[package_name][27]
                    other_languages = all_urls[package_name][28]
                elif real_url == old_weight_url and all_urls[package_name][32] != "":
                    lev_dist_text = all_urls[package_name][32]
                    similarity = all_urls[package_name][33]
                    descr_dist_text = all_urls[package_name][34]
                    github_badge = all_urls[package_name][35]
                    python_lang = all_urls[package_name][36]
                    other_languages = all_urls[package_name][37]
                else:
                    new_urls += 1
                    logger.info(f"{line_count}. '{package_name}' have a new Real URL: '{real_url}'")
                    finder = URLFinder(package_name)
                    finder.set_github_url(real_url)

                    if real_url[-1] != "/": url_package_name = real_url.split("/")[-1]
                    else: url_package_name = real_url.split("/")[-2]

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
                    github_badge = str(finder.check_pypi_badge())
                    python_lang = finder.check_python_lang()
                    other_languages = finder.get_other_lang()

                if lev_dist_text != "":
                    lev_distance = lev_dist_text.split("/")[0]
                    if lev_distance == "0" or lev_distance == "1" or similarity == "Substring": score_1 = 1
                    else: score_1 = -1
                else: score_1 = 0

                if descr_dist_text != "":
                    descr_distance = float(descr_dist_text.split("/")[0])
                    descr_len = float(descr_dist_text.split("/")[1])
                    dist_len_rel = 0
                    if descr_len != 0: dist_len_rel = round(float(descr_distance / descr_len), 3)
                    if dist_len_rel < 0.5: score_2 = 1
                    else: score_2 = -1
                else: score_2 = 0

                if github_badge == "True": score_3 = 1
                elif github_badge == "False" or github_badge == "": score_3 = 0
                else: score_3 = -1

                perc = 0
                if python_lang == "": score_4 = 0
                elif python_lang != "0%": score_4 = 1
                else:
                    if other_languages == "": score_4 = 0
                    else: score_4 = -1

                score = score_1 + score_2 + score_3 + score_4

                # Append urls information
                tmp_row = []
                for i in range(0, 10): tmp_row.append(row[i])
                tmp_row.append(score_1)
                tmp_row.append(score_2)
                tmp_row.append(score_3)
                tmp_row.append(score_4)
                tmp_row.append(score)
                urls.append(tmp_row)

                scores[score] += 1

        if len(urls) % 50 == 0 and line_count > start: logger.info(f"rows: {len(urls)}")
        line_count += 1
        if line_count >= end: break

# Print out the information and store the new values into the file
logger.info(f"----------------------------------------------- rows {len(urls)} -----------------------------------------------------------")
logger.info(f"New URLs: {new_urls}, Empty URLs: {empty_urls}")
logger.info(f"Scores: {scores}")
logger.info(f"--------------------------------------------------------------------------------------------")
with open(output_file, mode='w') as csv_file:
    urls_writer = csv.writer(csv_file, delimiter=';')
    urls_writer.writerow(["Package name", "Badge URL", "Homepage URL", "Metadata URL",\
 "Readthedocs URL", "Statistics URL", "OSSGadget URL", "Mode URL", "Final URL", "Real URL",\
 "Names Similarity", "Descr. Lev. dist.", "GitHub badge", "Python lang. perc.", "Real URL Score"])
    for i in range(0, len(urls)):
        urls_writer.writerow(urls[i])