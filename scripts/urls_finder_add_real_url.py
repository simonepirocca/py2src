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
input_file = "../output/url_finder_output/github_urls_from_diff_sources_2.csv"
output_file = "../output/url_finder_output/github_urls_from_diff_sources_3.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
urls = []
weights = [53, 67, 23, 46, 63, 31, 58]
total_weight = 341
diff_from_ossgadget = 0
real_diff_from_ossgadget = 0
diff_from_final = 0
no_confidence = 0
low_confidence = 0
high_but_fp = 0
no_confidence_threshold = 10
trusted_confidence_threshold = 35
confidence_mean = 0

# Open urls csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            # Get URLs coming from different sources
            package_name = row[0]
            ossgadget_url = row[1]
            final_url = row[16]

            real_urls = {}

            for i in range(2, 9):
                tmp_url = row[i]
                if tmp_url != "":
                    if tmp_url in real_urls: real_urls[tmp_url] += weights[i-2]
                    else: real_urls[tmp_url] = weights[i-2]

            confidence = 0
            real_url = ""
            for url in real_urls:
                count = real_urls[url]
                if count > confidence:
                    confidence = count
                    real_url = url

            if real_url == "": confidence = 100
            else: confidence = round(100 * (float(confidence) / float(total_weight)))

            if real_url == "":
                lev_dist_text = ""
                similarity = ""
                descr_dist_text = ""
                github_badge = ""
                python_lang = ""
                other_languages = ""
                real_url_position = ""
            elif real_url == final_url and row[23] != "":
                lev_dist_text = row[23]
                similarity = row[24]
                descr_dist_text = row[25]
                github_badge = row[26]
                python_lang = row[27]
                other_languages = row[28]
                real_url_position = row[29]
            elif real_url == ossgadget_url and row[9] != "":
                lev_dist_text = row[9]
                similarity = row[10]
                descr_dist_text = row[11]
                github_badge = row[12]
                python_lang = row[13]
                other_languages = row[14]
                real_url_position = row[15]
            else:
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
                github_badge = finder.check_pypi_badge()
                python_lang = finder.check_python_lang()
                other_languages = finder.get_other_lang()

                matching_metrics = 0
                real_url_position = ""

                if lev_dist_text != "":
                    lev_distance = lev_dist_text.split("/")[0]
                    if lev_distance == "0" or lev_distance == "1" or similarity == "Substring": matching_metrics += 1

                if descr_dist_text != "":
                    descr_distance = float(descr_dist_text.split("/")[0])
                    descr_len = float(descr_dist_text.split("/")[1])
                    dist_len_rel = 0
                    if descr_len != 0: dist_len_rel = round(float(descr_distance / descr_len), 3)
                    if dist_len_rel < 0.5: matching_metrics += 1

                if github_badge == "True" or github_badge == True: real_url_position = "TP"

                perc = 0
                if python_lang != "": perc = float(python_lang[:-1])
                if perc > 50: matching_metrics += 1
                elif perc == 0 and other_languages != "": real_url_position = "FP"

                if real_url_position == "":
                    if matching_metrics == 3: real_url_position = "TP(?)"
                    elif matching_metrics == 0: real_url_position = "FP(?)"

            if real_url != ossgadget_url:
                diff_from_ossgadget += 1
                if ossgadget_url != "":
                    real_diff_from_ossgadget += 1
                    logger.info(f"{line_count}. '{package_name}': OSSGadget '{ossgadget_url}' --> Real '{real_url}'")
            if real_url != final_url:
                diff_from_final += 1
                logger.info(f"{line_count}. '{package_name}': Final '{final_url}' --> Real '{real_url}'")

            if confidence < 10 and "FP" in real_url_position:
                real_url = ""
                no_confidence += 1
                logger.info(f"{line_count}. '{package_name}' has NO confidence: {confidence}%")
            elif confidence < 35: low_confidence += 1
            elif "FP" in real_url_position: high_but_fp += 1

            confidence_text = str(confidence) + "%"
            confidence_mean += confidence

            # Append urls information
            tmp_row = []
            for i in range(0, 30): tmp_row.append(row[i])
            tmp_row.append(real_url)
            tmp_row.append(confidence_text)
            tmp_row.append(lev_dist_text)
            tmp_row.append(similarity)
            tmp_row.append(descr_dist_text)
            tmp_row.append(github_badge)
            tmp_row.append(python_lang)
            tmp_row.append(other_languages)
            tmp_row.append(real_url_position)
            urls.append(tmp_row)

        #if len(urls) % 500 == 0 and line_count > start: logger.info(f"rows: {len(urls)}")
        line_count += 1
        if line_count >= end: break

confidence_mean = str(round(float(confidence_mean)/(float(len(urls))))) + "%"
# Print out the information and store the new values into the file
logger.info(f"----------------------------------------------- rows {len(urls)} -----------------------------------------------------------")
logger.info(f"Confidence mean: {confidence_mean}, NO confidence: {no_confidence}, LOW confidence: {low_confidence}, HIGH conf. but FP: {high_but_fp}")
logger.info(f"Diff. from OSSGadget URL: {diff_from_ossgadget} (Real: {real_diff_from_ossgadget}), Diff. from Final URL: {diff_from_final}")
logger.info(f"--------------------------------------------------------------------------------------------")
with open(output_file, mode='w') as csv_file:
    urls_writer = csv.writer(csv_file, delimiter=';')
    urls_writer.writerow(["Package name", "OSSGadget URL", "Metadata URL", "Homepage URL", "PyPI URL", "PyPI 2 URL", "Statistics URL", "Readthedocs URL", "PyPI badge URL",\
 "Names Lev. dist.", "Names Similarity", "Descr. Lev. dist.", "GitHub badge", "Python lang. perc.", "Other languages", "OSSGadget position",\
 "Final URL", "Occ. final URL", "Second URL", "Occ. second URL", "Third URL", "Occ. third URL", "URLs similarity",\
 "Names Lev. dist.", "Names Similarity", "Descr. Lev. dist.", "GitHub badge", "Python lang. perc.", "Other languages", "Final URL position", "Real URL", "Confidence",\
 "Names Lev. dist.", "Names Similarity", "Descr. Lev. dist.", "GitHub badge", "Python lang. perc.", "Other languages", "Real URL position"])
    for i in range(0, len(urls)):
        urls_writer.writerow(urls[i])