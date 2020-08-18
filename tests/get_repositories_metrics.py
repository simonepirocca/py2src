"""
This file get all the needed repositories and extract the related metrics
"""
import sys
import os
import json
import csv
from urllib.request import Request, urlopen
sys.path.append(os.path.abspath("../src/"))
from metrics import Metrics


def test_get_repositories():
    # Set source and range
    pypi_repos_json = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-365-days.json"
    start = 91
    count = 10
    end = start + count

    if start == 1:
        with open('../metrics_output/metrics.csv', mode='w') as packages:
            packages_writer = csv.writer(packages, delimiter=';')
            packages_writer.writerow(['package_name', 'pypi_downloads', 'github_url', 'stars',\
 'last_commit', 'commit_freq', 'release_freq', 'open_issues', 'closed_issues', 'api_closed_issues', 'avg_days_to_close_issue', 'contributors',\
 'dep_repos', 'dep_pkgs', 'libraries_io_url', 'sourcerank', 'dep_repos', 'dep_pkgs'])

    with urlopen(pypi_repos_json) as response:
        repos = json.loads(response.read().decode())["rows"]
        for i in range(start, end):
            package_name = repos[i-1]["project"]
            downloads = repos[i-1]["download_count"]
            Metrics.get_repo_metrics(package_name, downloads)

