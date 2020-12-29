import sys
import os
import csv
import logging
import pytest
import json
from urllib.request import Request, urlopen
from datetime import date
from pathlib import Path

url_finder_module_path = Path().resolve().parent / "src" / "url_finder"
sys.path.append(str(url_finder_module_path))
from url_finder import URLFinder

get_metrics_module_path = Path().resolve().parent / "src" / "metrics"
sys.path.append(str(get_metrics_module_path))
from get_metrics import GetMetrics
from metrics import Metrics

utils_module_path = Path().resolve().parent / "src" / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/metrics.log")

github_token = "put_here_a_valid_github_token"

# Test the gathering of all GitHub metrics, using GetMetrics class
def test_all_metrics_gathering():
    package_name = 'urllib3'
    github_url = 'https://github.com/urllib3/urllib3'
    ms = GetMetrics(package_name, github_url)

    metrics = ms.get_metrics()
    # Numbers are changing constantly
    assert metrics == [2514, '2020-12-26', 31, 52, 132, 735, 100, 29, 243, 444259, 4034]

# Test single GitHub metrics gathering, using Metrics class
def test_get_open_issues_success():
    package_name = 'urllib3'
    github_url = 'https://github.com/urllib3/urllib3'
    pkg = Metrics(package_name, github_url)

    open_issues = pkg.get_link_span_metric_from_github_repo("issues")
    assert open_issues == 132

def test_get_open_issues_fail():
    package_name = 'lxml'
    github_url = 'https://github.com/lxml/lxml'
    pkg = Metrics(package_name, github_url)

    open_issues = pkg.get_link_span_metric_from_github_repo("issues")
    assert open_issues == ""

def test_get_closed_issues_success():
    package_name = 'urllib3'
    github_url = 'https://github.com/urllib3/urllib3'
    pkg = Metrics(package_name, github_url)

    closed_issues = pkg.get_closed_issues_from_github_repo()
    assert closed_issues == 735

def test_get_closed_issues_fail():
    package_name = 'lxml'
    github_url = 'https://github.com/lxml/lxml'
    pkg = Metrics(package_name, github_url)

    closed_issues = pkg.get_closed_issues_from_github_repo()
    assert closed_issues == ""

def test_get_commits_success():
    package_name = 'urllib3'
    github_url = 'https://github.com/urllib3/urllib3'
    pkg = Metrics(package_name, github_url)

    commits = pkg.get_commits_from_github_repo()
    assert commits == 3507

def test_get_commits_fail():
    package_name = 'importlib-metadata'
    github_url = 'https://github.com/importlib-metadata/importlib-metadata'
    pkg = Metrics(package_name, github_url)

    commits = pkg.get_commits_from_github_repo()
    assert commits == ""

def test_get_releases_success():
    package_name = 'urllib3'
    github_url = 'https://github.com/urllib3/urllib3'
    pkg = Metrics(package_name, github_url)

    releases = pkg.get_link_span_metric_from_github_repo("releases")
    assert releases == 64

def test_get_releases_fail():
    package_name = 'virtualenv-clone'
    github_url = 'https://github.com/edwardgeorge/virtualenv-clone'
    pkg = Metrics(package_name, github_url)

    releases = pkg.get_link_span_metric_from_github_repo("releases")
    assert releases == ""

def test_get_tags_success():
    package_name = 'six'
    github_url = 'https://github.com/benjaminp/six'
    pkg = Metrics(package_name, github_url)

    releases = pkg.get_tags_from_github_repo()
    assert releases == 24

def test_get_tags_fail():
    package_name = 'virtualenv-clone'
    github_url = 'https://github.com/edwardgeorge/virtualenv-clone'
    pkg = Metrics(package_name, github_url)

    releases = pkg.get_tags_from_github_repo()
    assert releases == ""

def test_get_contributors_success():
    package_name = 'urllib3'
    github_url = 'https://github.com/urllib3/urllib3'
    pkg = Metrics(package_name, github_url)

    contributors = pkg.get_link_span_metric_from_github_repo("graphs/contributors")
    assert contributors == 243

def test_get_contributors_fail():
    package_name = 'argparse'
    github_url = 'https://github.com/thomaswaldmann/argparse'
    pkg = Metrics(package_name, github_url)

    contributors = pkg.get_link_span_metric_from_github_repo("graphs/contributors")
    assert contributors == ""

def test_get_dependents_url_success():
    package_name = 'urllib3'
    github_url = 'https://github.com/urllib3/urllib3'
    pkg = Metrics(package_name, github_url)

    dependents_url = pkg.get_dependent_url_from_github_repo()
    assert dependents_url == "https://github.com/urllib3/urllib3/network/dependents?package_id=UGFja2FnZS01MjY4MDQ4Mw%3D%3D"

def test_get_dependents_url_fail():
    package_name = 'pytzdata'
    github_url = 'https://github.com/sdispater/pytzdata'
    pkg = Metrics(package_name, github_url)

    dependents_url = pkg.get_dependent_url_from_github_repo()
    assert dependents_url == ""

def test_get_dep_repos_success():
    package_name = 'urllib3'
    github_url = 'https://github.com/urllib3/urllib3'
    dependents_url = "https://github.com/urllib3/urllib3/network/dependents?package_id=UGFja2FnZS01MjY4MDQ4Mw%3D%3D"
    pkg = Metrics(package_name, github_url)

    dep_repos = pkg.get_dependent_from_github_repo(dependents_url, "dependent_type=REPOSITORY")
    assert dep_repos == 444259

def test_get_dep_repos_fail():
    package_name = 'pytzdata'
    github_url = 'https://github.com/sdispater/pytzdata'
    dependents_url = ""
    pkg = Metrics(package_name, github_url)

    dep_repos = pkg.get_dependent_from_github_repo(dependents_url, "dependent_type=REPOSITORY")
    assert dep_repos == ""

def test_get_dep_packages_success():
    package_name = 'urllib3'
    github_url = 'https://github.com/urllib3/urllib3'
    dependents_url = "https://github.com/urllib3/urllib3/network/dependents?package_id=UGFja2FnZS01MjY4MDQ4Mw%3D%3D"
    pkg = Metrics(package_name, github_url)

    dep_packages = pkg.get_dependent_from_github_repo(dependents_url, "dependent_type=PACKAGE")
    assert dep_packages == 4035

def test_get_dep_packages_fail():
    package_name = 'pytzdata'
    github_url = 'https://github.com/sdispater/pytzdata'
    dependents_url = ""
    pkg = Metrics(package_name, github_url)

    dep_packages = pkg.get_dependent_from_github_repo(dependents_url, "dependent_type=PACKAGE")
    assert dep_packages == ""

def test_get_created_at_success():
    package_name = 'urllib3'
    github_url = 'https://github.com/urllib3/urllib3'
    github_url_parts = github_url.split("/")
    parts = len(github_url_parts)

    github_json_url = "https://api.github.com/repos/" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1]
    api_req = Request(github_json_url)
    api_req.add_header('Authorization', 'token ' + github_token)
    try:
        github_json = json.loads(urlopen(api_req).read().decode())
        created_at = github_json["created_at"][:10]
    except Exception:
        created_at = ""

    assert created_at == "2011-09-18"

def test_get_created_at_fail():
    package_name = 'future'
    github_url = 'https://github.com/future/future'
    github_url_parts = github_url.split("/")
    parts = len(github_url_parts)

    github_json_url = "https://api.github.com/repos/" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1]
    api_req = Request(github_json_url)
    api_req.add_header('Authorization', 'token ' + github_token)
    try:
        github_json = json.loads(urlopen(api_req).read().decode())
        created_at = github_json["created_at"][:10]
    except Exception:
        created_at = ""

    assert created_at == ""

def test_get_stars_success():
    package_name = 'urllib3'
    github_url = 'https://github.com/urllib3/urllib3'
    github_url_parts = github_url.split("/")
    parts = len(github_url_parts)

    github_json_url = "https://api.github.com/repos/" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1]
    api_req = Request(github_json_url)
    api_req.add_header('Authorization', 'token ' + github_token)
    try:
        github_json = json.loads(urlopen(api_req).read().decode())
        stars = github_json["stargazers_count"]
        if stars != "": stars = Metrics.convert_to_number(str(stars))
    except Exception:
        stars = ""

    assert stars == 2514

def test_get_stars_fail():
    package_name = 'future'
    github_url = 'https://github.com/future/future'
    github_url_parts = github_url.split("/")
    parts = len(github_url_parts)

    github_json_url = "https://api.github.com/repos/" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1]
    api_req = Request(github_json_url)
    api_req.add_header('Authorization', 'token ' + github_token)
    try:
        github_json = json.loads(urlopen(api_req).read().decode())
        stars = github_json["stargazers_count"]
        if stars != "": stars = Metrics.convert_to_number(str(stars))
    except Exception:
        stars = ""

    assert stars == ""

def test_get_last_commit_success():
    package_name = 'urllib3'
    github_url = 'https://github.com/urllib3/urllib3'
    github_url_parts = github_url.split("/")
    parts = len(github_url_parts)

    commits_json_url = "https://api.github.com/repos/" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1] + "/commits"
    api_req = Request(commits_json_url)
    api_req.add_header('Authorization', 'token ' + github_token)
    try:
        commits_json = json.loads(urlopen(api_req).read().decode())
        last_commit = commits_json[0]["commit"]["author"]["date"][:10]
    except Exception:
        last_commit = ""

    assert last_commit == "2020-12-26"

def test_get_last_commit_fail():
    package_name = 'petname'
    github_url = 'https://github.com/petname/petname'
    github_url_parts = github_url.split("/")
    parts = len(github_url_parts)

    commits_json_url = "https://api.github.com/repos/" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1] + "/commits"
    api_req = Request(commits_json_url)
    api_req.add_header('Authorization', 'token ' + github_token)
    try:
        commits_json = json.loads(urlopen(api_req).read().decode())
        last_commit = commits_json[0]["commit"]["author"]["date"][:10]
    except Exception:
        last_commit = ""

    assert last_commit == ""

def test_get_commit_frequency_success():
    package_name = 'urllib3'
    github_url = 'https://github.com/urllib3/urllib3'
    created_at = "2011-09-18"
    commits = 3507
    commit_frequency = ""

    total_months = 0
    if created_at != "":
        today_date = date.today().strftime('%Y-%m-%d')
        total_months = (int(today_date[:4]) - int(created_at[:4])) * 12 + (int(today_date[5:7]) - int(created_at[5:7]))
    if total_months != 0 and commits != "":                
        commit_frequency = int(int(commits) / total_months)

    assert commit_frequency == 31

def test_get_commit_frequency_fail():
    package_name = 'petname'
    github_url = 'https://github.com/petname/petname'
    created_at = ""
    commits = ""
    commit_frequency = ""

    total_months = 0
    if created_at != "":
        today_date = date.today().strftime('%Y-%m-%d')
        total_months = (int(today_date[:4]) - int(created_at[:4])) * 12 + (int(today_date[5:7]) - int(created_at[5:7]))
    if total_months != 0 and commits != "":                
        commit_frequency = int(int(commits) / total_months)

    assert commit_frequency == ""

def test_get_release_frequency_success():
    package_name = 'urllib3'
    github_url = 'https://github.com/urllib3/urllib3'
    created_at = "2011-09-18"
    releases = 64
    release_frequency = ""

    total_days = 0
    if created_at != "":
        today_date = date.today().strftime('%Y-%m-%d')
        total_days = (int(today_date[:4]) - int(created_at[:4])) * 365 + (int(today_date[5:7]) - int(created_at[5:7])) * 30 + (int(today_date[8:]) - int(created_at[8:]))
    if total_days != 0 and releases != "":                
        release_frequency = int(total_days / int(releases))

    assert release_frequency == 52

def test_get_release_frequency_fail():
    package_name = 'petname'
    github_url = 'https://github.com/petname/petname'
    created_at = ""
    releases = ""
    release_frequency = ""

    total_days = 0
    if created_at != "":
        today_date = date.today().strftime('%Y-%m-%d')
        total_days = (int(today_date[:4]) - int(created_at[:4])) * 365 + (int(today_date[5:7]) - int(created_at[5:7])) * 30 + (int(today_date[8:]) - int(created_at[8:]))
    if total_days != 0 and releases != "":                
        release_frequency = int(total_days / int(releases))

    assert release_frequency == ""

def test_get_avg_close_issue_days_success():
    package_name = 'urllib3'
    github_url = 'https://github.com/urllib3/urllib3'
    github_url_parts = github_url.split("/")
    parts = len(github_url_parts)
    avg_close_issue_days = ""

    # Calculate 'avg_close_issue_days' metric by inspecting most 100 recent closed issues
    i = 0
    api_closed_issues = 0
    sum_closed_days = 0
    issue_json_url = "https://api.github.com/search/issues?q=repo:" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1] + "%20is:issue%20is:closed&per_page=100"
    api_req = Request(issue_json_url)
    api_req.add_header('Authorization', 'token ' + github_token)            
    # Get the json of closed issues using GitHub API
    try:
        issue_json = json.loads(urlopen(api_req).read().decode())
    except Exception:
        avg_close_issue_days = ""
    else:
        for i in range(len(issue_json["items"])):
            try:
                # Get creation and close date for each issue
                created_date = issue_json["items"][i]["created_at"][:10]
                closed_date = issue_json["items"][i]["closed_at"][:10]
            except TypeError:
                created_date = ""
                closed_date = ""
            # Calculate for each issue the elapsed days
            if created_date != "" and closed_date != "":
                close_days = (int(closed_date[:4]) - int(created_date[:4])) * 365 + (int(closed_date[5:7]) - int(created_date[5:7])) * 30 + (int(closed_date[8:]) - int(created_date[8:]))
                sum_closed_days = sum_closed_days + close_days
                api_closed_issues = api_closed_issues + 1
        # Compute the average
        if api_closed_issues > 0:
            avg_close_issue_days = int(sum_closed_days / api_closed_issues)
        else: api_closed_issues = ""

    assert avg_close_issue_days == 29

def test_get_avg_close_issue_days_fail():
    package_name = 'crc16'
    github_url = 'https://github.com/gennady/pycrc16'
    github_url_parts = github_url.split("/")
    parts = len(github_url_parts)
    avg_close_issue_days = ""

    # Calculate 'avg_close_issue_days' metric by inspecting most 100 recent closed issues
    i = 0
    api_closed_issues = 0
    sum_closed_days = 0
    issue_json_url = "https://api.github.com/search/issues?q=repo:" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1] + "%20is:issue%20is:closed&per_page=100"
    api_req = Request(issue_json_url)
    api_req.add_header('Authorization', 'token ' + github_token)            
    # Get the json of closed issues using GitHub API
    try:
        issue_json = json.loads(urlopen(api_req).read().decode())
    except Exception:
        avg_close_issue_days = ""
    else:
        for i in range(len(issue_json["items"])):
            try:
                # Get creation and close date for each issue
                created_date = issue_json["items"][i]["created_at"][:10]
                closed_date = issue_json["items"][i]["closed_at"][:10]
            except TypeError:
                created_date = ""
                closed_date = ""
            # Calculate for each issue the elapsed days
            if created_date != "" and closed_date != "":
                close_days = (int(closed_date[:4]) - int(created_date[:4])) * 365 + (int(closed_date[5:7]) - int(created_date[5:7])) * 30 + (int(closed_date[8:]) - int(created_date[8:]))
                sum_closed_days = sum_closed_days + close_days
                api_closed_issues = api_closed_issues + 1
        # Compute the average
        if api_closed_issues > 0:
            avg_close_issue_days = int(sum_closed_days / api_closed_issues)
        else: api_closed_issues = ""

    assert avg_close_issue_days == ""
