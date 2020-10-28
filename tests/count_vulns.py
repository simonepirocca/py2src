"""
This file get all the missing metrics for each repo
"""
import sys
import os
import csv
from array import *
import logging
logging.basicConfig(filename="log.log", level=logging.INFO)

def test_count_vulns():

    start = 1 # DO NOT consider header line
    count = 1280
    end = start + count

    input_csv = "../vulns_output/snyk_pip_vulns.csv"

    packages = []
    not_empty_cells = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    complete_rows = 0
    tot_packages = 0
    tot_vulns = 0
    line_count = 0

    with open(input_csv) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            if line_count >= start:

                complete_row = True
                for i in range(0, 9):
                    if row[i+5] == "": complete_row = False
                    else: not_empty_cells[i] += 1

                if complete_row: complete_rows += 1

                duplicated = False
                package = row[3]
                if package != "":
                    for j in range (0, tot_packages):
                        if package == packages[j]:
                            duplicated = True
                            break
                if not duplicated:
                    packages.append(package)
                    tot_packages += 1

                tot_vulns += 1

            line_count += 1
            if line_count >= end: break

    logging.info(f"Tot vulns: {tot_vulns}, Tot packages: {tot_packages}, Complete rows: {complete_rows}")
    logging.info(f"Not empty cells: {not_empty_cells}")
    logging.info(f"-------------------------------------------------------------------------------------------------------------")
