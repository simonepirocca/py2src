import sys
import os
import csv
import logging
logging.basicConfig(filename="../log.log", level=logging.INFO)
sys.path.append(os.path.abspath('../utils/'))
from url_finder import URLFinder

#def test_initialization():
#    pkg = URLFinder(package_name='urllib3')
#    assert isinstance(pkg, URLFinder)

#def test_find_github_url():
#    finder = URLFinder(package_name='urllib3')
#    github_url = finder.find_github_url()
#    assert github_url == "https://github.com/urllib3/urllib3"

def test_github_url_gathering():
    packages = []    
    with open('../../output/metrics_output/metrics_final.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                package_name = row[0]
                right_url = row[2]

                useless_row = True
                for i in range(3, 14):
                    if row[i] != "" and i in [3, 4, 5, 6, 7, 8, 10, 11, 12, 13]: 
                        useless_row = False
                        break

                other_url = URLFinder(package_name).find_github_url()
                packages.append([package_name, right_url, useless_row, other_url])

            line_count += 1

    with open('../../output/github_urls_output/urls_comparison.csv', mode='w') as urls_csv:
        packages_writer = csv.writer(urls_csv, delimiter=';')
        packages_writer.writerow(['Package name', 'Right URL', 'Useless', 'Old URL'])
        for i in range(0, len(packages)):
                packages_writer.writerow(packages[i])