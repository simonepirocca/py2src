"""
This file get all the needed repositories and extract the related metrics
"""
import sys
import os
import json
import logging
logging.basicConfig(filename="../log.log", level=logging.INFO)

def test_count_vulns():
    # Set source
    pypi_repos_json = "../../inputs/insecure_full.json"
    tot_packages = -1
    tot_vulns = 0
    total_cve = 0

    with open(pypi_repos_json) as json_file:
        data = json.load(json_file)
        for package in data:
            tot_packages += 1
            vulns = data[package]
            tot_vulns += len(vulns)
            if tot_packages > 0:
                for vuln in vulns:
                    for info in vuln:
                        if info != "advisory" and info != "cve" and info != "id" and info != "specs" and info != "v":
                            logging.info(f"{vuln}")
                        if info == "cve" and vuln[info] != None: total_cve += 1
            #if tot_packages > 10: break

    logging.info(f"Packages: {tot_packages}, Vulns: {tot_vulns}, CVE: {total_cve}")
