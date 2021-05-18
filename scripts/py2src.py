"""
This file get the GitHub URL, related factors and vulnerabilities data from a list of PYPI packages
"""
import sys
import os
import csv
import logging
import json
import pytest
from datetime import datetime

from ..src.get_github_url import GetFinalURL
from ..src.get_github_factors import GetMetrics
from ..src.utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.INFO, log_filepath="../logs/log.log")

# Set source, output and range
packages_json = "../inputs/packages.json"
urls_file = "../output/urls.csv"
factors_file = "../output/factors.csv"
vulns_file = "../output/vulns.csv"

# Inizialize arrays
stored_urls = {}
stored_factors = {}
stored_vulns = {}
ts = round(datetime.now().timestamp())

# Open the stored URLs file
with open(urls_file) as urls_csv_file:
    urls_reader = csv.reader(urls_csv_file, delimiter=';')
    line_count = 0
    for row in urls_reader:
        if line_count > 0: stored_urls[row[0]] = row
        line_count += 1

# Open the stored factors file
with open(factors_file) as factors_csv_file:
    factors_reader = csv.reader(factors_csv_file, delimiter=';')
    line_count = 0
    for row in factors_reader:
        if line_count > 0: stored_factors[row[0]] = row
        line_count += 1

# Open the stored vulns file
with open(vulns_file) as vulns_csv_file:
    vulns_reader = csv.reader(vulns_csv_file, delimiter=';')
    line_count = 0
    for row in vulns_reader:
        if line_count > 0: stored_vulns[row[0]] = row
        line_count += 1

# Open and decode the JSON input file
with open(packages_json) as json_file:
    json_data = json.load(json_file)
    if "rows" in json_data: packages = json_data["rows"]
    else: packages = json_data["packages"]

    for element in packages:
        # Get package name (and PyPI downloads) from the row
        pypi_downloads = ""
        if "rows" in json_data:
            package_name = element["project"]
            pypi_downloads = element["download_count"]
        else: package_name = element["name"]

        # If the package is already stored and its age is no more than 1 month
        if package_name in stored_urls and (ts - int(stored_urls[package_name][3]) < 2500000): 
            package_url = stored_urls[package_name]
            if package_name in stored_factors: package_factors = stored_factors[package_name]
            else: package_factors = "No GitHub URL found"
            if package_name in stored_vulns: package_vulns = stored_vulns[package_name]
            else: package_vulns = "No vulnerabilities found"

        else:
            # Get GitHub URL associated to the package
            gfu = GetFinalURL(package_name)
            url_data = gfu.get_final_url()
            github_url = url_data[0]
            score = url_data[1]

            package_url = [package_name, github_url, score, ts]
            stored_urls[package_name] = package_url

            if github_url != "":
                # Get the metrics
                ms = GetMetrics(package_name, github_url)
                factors_data = ms.get_metrics()
                # Put the metrics into the storage array
                package_factors = [package_name, pypi_downloads]
                for factor in factors_data: package_factors.append(factor)
                stored_factors[package_name] = package_factors
            else: package_factors = "No GitHub URL found"

        package_vulns = "No vulnerabilities found"
        #TODO: vulnerabilities data gathering

        logger.info(f"'{package_name}' URL data: {package_url}")
        logger.info(f"'{package_name}' Factors data: {package_factors}")
        logger.info(f"'{package_name}' Vulns data: {package_vulns}")

# Update URLs data
with open(urls_file, mode='w') as urls_csv_file:
    urls_writer = csv.writer(urls_csv_file, delimiter=';')
    urls_writer.writerow(['Package name', 'Final URL', 'Reliability score', 'Timestamp'])
    for pkg in stored_urls: urls_writer.writerow(stored_urls[pkg])

with open(factors_file, mode='w') as factors_csv_file:
    factors_writer = csv.writer(factors_csv_file, delimiter=';')
    factors_writer.writerow(['Package name', 'PyPI downloads', 'Dependent repos', 'Stars', 'Contributors', 'Open issues',\
 'Closed issues', 'Open/Closed issues', 'Commit frequency', 'Release frequency', 'Time to close issue', 'License'])
    for pkg in stored_factors: factors_writer.writerow(stored_factors[pkg])

with open(vulns_file, mode='w') as vulns_csv_file:
    vulns_writer = csv.writer(vulns_csv_file, delimiter=';')
    vulns_writer.writerow(['Package name', 'Total vulns', 'Analysed vulns', 'AVG Time to release fix', 'AVG Release type', 'AVG Severity'])
    for pkg in stored_vulns: vulns_writer.writerow(stored_vulns[pkg])
