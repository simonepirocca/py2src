"""
This file looks at the pyupio vulnerabilities, from a JSON file
"""
import sys
import os
import json
import logging
import pytest
from pathlib import Path

utils_module_path = Path().resolve() / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/vulns.log")

# Set source
pypi_repos_json = "../inputs/insecure_full.json"
tot_packages = -1
tot_vulns = 0
total_cve = 0

# Open the JSON file
with open(pypi_repos_json) as json_file:
    data = json.load(json_file)
    # Analyse each row
    for package in data:
        # Increase the number of packages and update the number of vulnerabilities
        tot_packages += 1
        vulns = data[package]
        tot_vulns += len(vulns)
        if tot_packages > 0:
            # Scan each vulnerability of a particular package
            for vuln in vulns:
                # For each vulnerability, check all the parameters
                for info in vuln:
                    # Check if there is a vulnerability with additional information
                    if info != "advisory" and info != "cve" and info != "id" and info != "specs" and info != "v":
                        logger.info(f"{vuln}")
                    # Update the counter for CVE if it is specified for that vulnerability
                    if info == "cve" and vuln[info] != None: total_cve += 1

logger.info(f"PYUPIO VULNS --> Packages: {tot_packages}, Vulns: {tot_vulns}, CVE: {total_cve}")
