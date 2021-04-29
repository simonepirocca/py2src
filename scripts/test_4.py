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
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.INFO, log_filepath="../logs/url_finder.log")

# Set source and range
input_file = "../output/url_finder_final.csv"
start = 1
count = 4000
end = start + count

# Inizialize variables
tp = [0, 0, 0]
fp = [0, 0, 0]
tpm = [0, 0, 0]
fpm = [0, 0, 0]

# Open urls csv file
with open(input_file) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count >= start:
            # Get URLs coming from different sources
            package_name = row[0]
            ossgadget_url = row[1]
            ossgadget_quality = row[15]
            major_url = row[16]
            major_quality = row[29]
            weight_url = row[30]
            weight_quality = row[38]

            if ossgadget_quality == "TP": tp[0] += 1
            elif ossgadget_quality == "TP(?)": tpm[0] += 1
            elif ossgadget_quality == "FP(?)": fpm[0] += 1
            elif ossgadget_quality == "FP": fp[0] += 1

            if major_url == ossgadget_url:
                if ossgadget_quality == "TP": tp[1] += 1
                elif ossgadget_quality == "TP(?)": tpm[1] += 1
                elif ossgadget_quality == "FP(?)": fpm[1] += 1
                elif ossgadget_quality == "FP": fp[1] += 1
            else:
                if major_quality == "TP": tp[1] += 1
                elif major_quality == "TP(?)": tpm[1] += 1
                elif major_quality == "FP(?)": fpm[1] += 1
                elif major_quality == "FP": fp[1] += 1

            if weight_url == ossgadget_url:
                if ossgadget_quality == "TP": tp[2] += 1
                elif ossgadget_quality == "TP(?)": tpm[2] += 1
                elif ossgadget_quality == "FP(?)": fpm[2] += 1
                elif ossgadget_quality == "FP": fp[2] += 1
            elif weight_url == major_url:
                if major_quality == "TP": tp[2] += 1
                elif major_quality == "TP(?)": tpm[2] += 1
                elif major_quality == "FP(?)": fpm[2] += 1
                elif major_quality == "FP": fp[2] += 1
            else:
                if weight_url == "TP": tp[2] += 1
                elif weight_url == "TP(?)": tpm[2] += 1
                elif weight_url == "FP(?)": fpm[2] += 1
                elif weight_url == "FP": fp[2] += 1

        line_count += 1
        if line_count >= end: break

# Print out the information and store the new values into the file
logger.info(f"--------------------------------------------------------------------------------------------")
logger.info(f"TP: {tp}, TPM: {tpm}, FPM: {fpm}, FP: {fp},")
logger.info(f"--------------------------------------------------------------------------------------------")