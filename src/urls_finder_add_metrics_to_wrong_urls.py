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

utils_module_path = Path().resolve() / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/url_finder.log")

url_finder_module_path = Path().resolve() / "url_finder"
sys.path.append(str(url_finder_module_path))
from url_finder import URLFinder

src_module_path = Path().resolve().parent / "src" / "levenshtein_distance"
sys.path.append(str(src_module_path))
from string_distance import StringDistance

# Set source and range
wrong_urls_input_file = "../output/url_finder_output/wrong_33_package_urls.csv"
urls_input_file = "../output/url_finder_output/github_urls_with_fixed_metrics.csv"
output_file = "../output/url_finder_output/github_urls_with_fixed_metrics_and_urls.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
wrong_urls = {}
urls = []
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
updated_rows = 0

# Open wrong urls csv file
with open(wrong_urls_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= 1:
            package_name = row[0]
            old_url = row[1]
            right_url = row[2]
            wrong_urls[package_name] = right_url
        line_count += 1

if start == 1: 
    with open(output_file, mode='w') as csv_file:
        urls_writer = csv.writer(csv_file, delimiter=';')
        urls_writer.writerow(["Package name", "Old URL", "Useless", "Metadata URL", "PyPI URL", "OSSGadget URL", "Final URL", "Accuracy", "Different",\
 "Names Lev. dist.", "Names Similarity", "Statistics", "Descr. Lev. dist.", "Readthedocs", "GitHub badge", "PyPI badge", "Python lang. perc.", "Other languages"])

# Open urls csv file
with open(urls_input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:

            # Update information only if the package name contains a wrong URL
            package_name = row[0]
            if package_name in wrong_urls:

                # Get accuracy and three GitHub URLs with the final one from the row
                old_url = row[1]
                useless = row[2]
                metadata_url = row[3]
                pypi_url = row[4]
                ossgadget_url = row[5]
                row[6] = wrong_urls[package_name]
                final_url = row[6]
                accuracy = row[7]
                different = row[8]

                finder = URLFinder(package_name)
                if final_url != "": finder.set_github_url(final_url)

                # Insert URLs info into the row
                urls_row = []
                for i in range (0, 9): urls_row.append(row[i])

                if final_url == "": url_package_name = ""
                elif final_url[-1] != "/": url_package_name = final_url.split("/")[-1]
                else: url_package_name = final_url.split("/")[-2]

                matching_metrics = 0

                # Calculate Levenshtein distance and similarity between package names
                lev_distance = StringDistance().lev_distances_raw_strs(url_package_name, package_name)
                len1 = len(url_package_name)
                len2 = len(package_name)
                if lev_distance == 0:
                    lev_dist_0 += 1
                if len1 > len2: max_lev_dist = len1
                else: max_lev_dist = len2
                lev_dist_text = str(lev_distance) + "/" + str(max_lev_dist)
                urls_row.append(lev_dist_text)

                similarity = "Different"
                if url_package_name == package_name: similarity = "Equal"
                elif url_package_name in package_name or package_name in url_package_name: similarity = "Substring"
                if similarity == "Substring": name_substring += 1
                urls_row.append(similarity)

                if similarity == "Substring" or lev_distance == 0: matching_metrics += 1

                # Check GitHub statistics on PyPI page
                statistics_url = finder.check_pypi_statistics()
                if statistics_url == True:
                    true_stats += 1
                    matching_metrics += 1
                urls_row.append(statistics_url)

                # Check Levenshtein distance between PyPI and GitHub descriptions
                pypi_descr = finder.get_pypi_descr().replace("\n","")
                github_descr = finder.get_github_descr().replace("\n","")
                descr_distance = StringDistance().lev_distances_raw_strs(pypi_descr, github_descr)
                len1 = len(pypi_descr)
                len2 = len(github_descr)
                if len1 > len2: max_descr_dist = len1
                else: max_descr_dist = len2
                descr_dist_text = str(descr_distance) + "/" + str(max_descr_dist)
                dist_len_rel = 0
                if max_descr_dist != 0: dist_len_rel = round(float(descr_distance / max_descr_dist), 3)
                if dist_len_rel < 0.5:
                    low_descr_dist += 1
                    matching_metrics += 1
                urls_row.append(descr_dist_text)

                # Check readthedocs.io link
                readthedocs_link = finder.check_readthedocs()
                if readthedocs_link == True:
                    true_readthedocs += 1
                    matching_metrics += 1
                urls_row.append(readthedocs_link)

                # Get GitHub/Travis badge on PyPI page
                github_badge = finder.check_github_badge()
                if github_badge == True:
                    true_github_badge += 1
                    matching_metrics += 1
                urls_row.append(github_badge)

                # Get PyPI badge on GitHub page
                pypi_badge = finder.check_pypi_badge()
                if pypi_badge == True:
                    true_pypi_badge += 1
                    matching_metrics += 1
                urls_row.append(pypi_badge)

                # Get Python language on GitHub page
                python_lang = finder.check_python_lang()
                integer_index = python_lang.find(".")
                perc = 0
                if integer_index != -1:
                    perc = int(python_lang[:integer_index])
                if perc > 50:
                    high_python_lang += 1
                    matching_metrics += 1
                urls_row.append(python_lang)

                # Get other languages
                other_languages = finder.get_other_lang()
                urls_row.append(other_languages)

                complete_rows_1[matching_metrics] += 1
                for i in range(0, matching_metrics+1): complete_rows_2[i] += 1

                # Append urls row
                urls.append(urls_row)
                updated_rows += 1

                logger.info(f"{urls_row}")

            else: urls.append(row)

        if len(urls) % 100 == 0 and line_count > start: logger.info(f"rows: {len(urls)}")
        line_count += 1
        if line_count >= end: break

# Print out the information and store the new values into the file
logger.info(f"------------------------------------- rows {start}-{end-1} (Updated rows: {updated_rows}) ----------------------------------------------------------")
logger.info(f"Complete rows 1: {complete_rows_1}, Complete rows 2: {complete_rows_2}")
logger.info(f"Package name Lev. distance 0: {lev_dist_0}, Package name SUB: {name_substring}, Statistics: {true_stats}, Low descriptions Lev. distance: {low_descr_dist}")
logger.info(f"Readthedocs.io: {true_readthedocs}, GitHub/Travis badge: {true_github_badge}, PyPI badge: {true_pypi_badge}, High Python lang. perc.: {high_python_lang}")
logger.info(f"-------------------------------------------------------------------------------------------------------------------------")
with open(output_file, mode='a') as csv_file:
    urls_writer = csv.writer(csv_file, delimiter=';')
#    urls_writer.writerow(["Package name", "Old URL", "Useless", "Metadata URL", "PyPI URL", "OSSGadget URL", "Final URL", "Accuracy", "Different",\
# "Names Lev. dist.", "Names Similarity", "Statistics", "Descr. Lev. dist.", "Readthedocs", "GitHub badge", "PyPI badge", "Python lang. perc.", "Other languages"])
    for i in range(0, len(urls)):
        urls_writer.writerow(urls[i])