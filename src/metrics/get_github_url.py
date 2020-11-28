"""
This file get all the missing github url related to package names
"""
import sys
import os
import csv
from urllib.request import Request, urlopen
sys.path.append(os.path.abspath("../utils/"))
from package import Package


def test_get_github_url():
    ids = []
    names = []
    urls = []

    with open('../../output/github_urls/top_4000_pypi_packages_old.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                id = row[0]
                package_name = row[1]
                github_url = row[2]
                if github_url == "":
                    github_url = Package(package_name).extract_github_url()

                ids.append(id)
                names.append(package_name)
                urls.append(github_url)

            line_count += 1

    with open('../output/github_urls/top_4000_pypi_packages_old.csv', mode='w') as packages:
        packages_writer = csv.writer(packages, delimiter=';')
        packages_writer.writerow(['0', 'Package', 'github_url'])

        for i in range(0, len(ids)):
            packages_writer.writerow([ids[i], names[i], urls[i]])
