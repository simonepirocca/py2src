import sys
import os
import csv
from urllib.parse import urlparse
import logging
logging.basicConfig(filename="../log.log", level=logging.INFO)

def test_find_diff_urls():
    total_useful = 0
    total_useless = 0
    diff_useful = 0
    diff_useless = 0
    diff_old_empty_useful = 0
    diff_old_empty_useless = 0

    with open('../../output/github_urls_output/different_urls.csv', mode='w') as urls_csv:
        packages_writer = csv.writer(urls_csv, delimiter=';')
        packages_writer.writerow(['Package name', 'Right URL', 'Useless', 'Old URL'])

    with open('../../output/github_urls_output/different_urls_NO_EMPTY.csv', mode='w') as urls_csv:
        packages_writer = csv.writer(urls_csv, delimiter=';')
        packages_writer.writerow(['Package name', 'Right URL', 'Useless', 'Old URL'])

    with open('../../output/github_urls_output/urls_comparing.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                package_name = row[0]
                right_url = row[1]
                right_url_path = urlparse(right_url).path.lower()
                right_url_path = right_url_path.replace(".git", "")
                useless = row[2]
                old_url = row[3]
                old_url_path = urlparse(old_url).path.lower()
                old_url_path = old_url_path.replace(".git", "")

                if useless == "False": total_useful += 1
                else: total_useless += 1

                if right_url_path != old_url_path:
                    if useless == "False": diff_useful += 1
                    else: diff_useless += 1

                    if old_url_path == "":
                        if useless == "False": diff_old_empty_useful += 1
                        else: diff_old_empty_useless += 1
                    else:
                        with open('../../output/github_urls_output/different_urls_NO_EMPTY.csv', mode='a') as urls_csv:
                            packages_writer = csv.writer(urls_csv, delimiter=';')
                            packages_writer.writerow([package_name, right_url, useless, old_url])

                    with open('../../output/github_urls_output/different_urls.csv', mode='a') as urls_csv:
                        packages_writer = csv.writer(urls_csv, delimiter=';')
                        packages_writer.writerow([package_name, right_url, useless, old_url])

            line_count += 1

    total_packages = line_count - 1

    logging.info(f"Total packages: {total_packages}, Total useful: {total_useful}, Total useless: {total_useless}, Different useful: {diff_useful},\
 Different useless: {diff_useless}, Different EMPTY useful: {diff_old_empty_useful}, Different EMPTY useless: {diff_old_empty_useless}")