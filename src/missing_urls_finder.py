"""
This file get the missing GitHub URLs out of a list
"""
import sys
import os
import csv
import pytest

input_csv = "../output/url_finder_output/github_urls.csv"
output_csv = "../output/url_finder_output/missing_urls.csv"
    # Open the URL file
    with open(input_csv) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            # row = [package_name, github_url, accuracy, pypi_downloads]
            github_url = row[1]
            if github_url == "":
                # Write the package name into the missing urls file, if URL is empty 
                with open(output_csv, mode='a') as missing_csv:
                    packages_writer = csv.writer(missing_csv, delimiter=';')
                    packages_writer.writerow([row[0]])