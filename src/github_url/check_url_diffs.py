"""
This file checks the differences between two different GitHub url gathering implementations
"""
import sys
import os
import csv
import logging
logging.basicConfig(filename="../log.log", level=logging.INFO)

def test_check_url_diffs():
    urls = {}
    useless = {}
    total_useful = 0
    diff_urls = 0
    diff_useful = 0
    diff_useless = 0
    missing_urls = 0
    equal_package_names = 0

    with open('../../output/metrics_output/metrics_final.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                package_name = row[0]
                github_url = row[2]
                urls[package_name] = github_url

                useless_row = True
                for i in range(3, 14):
                    if row[i] != "" and i in [3, 4, 5, 6, 7, 8, 10, 11, 12, 13]: 
                        useless_row = False
                        total_useful += 1
                        break

                useless[package_name] = useless_row

            line_count += 1

    total_urls = len(urls)

    with open('../../output/github_urls_output/different_urls.csv', mode='w') as urls_csv:
        packages_writer = csv.writer(urls_csv, delimiter=';')
        packages_writer.writerow(['Package name', 'Useless', 'Right URL', 'Old URL'])

    with open('../../output/github_urls_output/github_urls_old.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                package_name = row[1]
                old_url = row[2]

                if package_name not in urls: missing_urls += 1
                else:
                    equal_package_names += 1
                    if old_url != urls[package_name]:
                        if useless[package_name]: diff_useless += 1
                        else: diff_useful += 1

                        with open('../../output/github_urls_output/different_urls.csv', mode='a') as urls_csv:
                            packages_writer = csv.writer(urls_csv, delimiter=';')
                            packages_writer.writerow([package_name, useless[package_name], urls[package_name], old_url])

            line_count += 1

    diff_urls = diff_useful + diff_useless
    logging.info(f"Total urls: {total_urls}, Total useful: {total_useful}, Different urls: {diff_urls}, Different useful:\
 {diff_useful}, Different useless: {diff_useless}, Missing urls: {missing_urls}, Equal package names: {equal_package_names}")