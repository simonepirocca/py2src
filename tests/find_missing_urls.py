"""
This file write all the packages with missing GitHub url
"""
import sys
import os
import csv

def test_find_missing_urls():

    input_csv = "../metrics_output/metrics_final_with_tags_and_0.csv"
    output_csv = "../metrics_output/missing_urls.csv"

    with open(input_csv) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            if row[2] == "":
                with open(output_csv, mode='a') as missing_csv:
                    packages_writer = csv.writer(missing_csv, delimiter=';')
                    packages_writer.writerow([row[0]])
