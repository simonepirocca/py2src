import sys
import os
import csv
import logging
import pytest
from pathlib import Path

vulns_module_path = Path().resolve().parent / "src" / "vulns"
sys.path.append(str(vulns_module_path))
from vulns import Vuln

utils_module_path = Path().resolve().parent / "src" / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/vulns.log")

# Test the crawling of all vulnerability information
def test_get_snyk_vuln_info():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-TENSORFLOWGPU-1020815"
    vuln_info = Vuln(vuln_url).get_snyk_vuln_info()
    assert vuln_info == ["CVE-2020-15266", "",\
 "https://github.com/tensorflow/tensorflow/pull/42143/commits/3ade2efec2e90c6237de32a19680caaa3ebc2845",\
 "", "", "", "", "https://github.com/tensorflow/tensorflow/issues/42129", ""]

# Test the crawling of a single vulnerability information
def test_get_cve_success():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-TENSORFLOWGPU-1020815"
    cve = Vuln(vuln_url).find_cve()
    assert cve == "CVE-2020-15266"

def test_get_cve_fail():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-DJANGOTWOFACTORAUTH-1014668"
    cve = Vuln(vuln_url).find_cve()
    assert cve == ""

def test_github_advisory_success():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-TENSORFLOWGPU-1013620"
    github_advisory = Vuln(vuln_url).find_ref_url("GitHub Advisory")
    assert github_advisory == "https://github.com/tensorflow/tensorflow/security/advisories/GHSA-w5gh-2wr2-pm6g"

def test_github_advisory_fail():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-TENSORFLOWGPU-1020815"
    github_advisory = Vuln(vuln_url).find_ref_url("GitHub Advisory")
    assert github_advisory == ""

def test_github_commit_success():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-TENSORFLOWGPU-1020820"
    github_commit = Vuln(vuln_url).find_ref_url("GitHub Commit")
    assert github_commit == "https://github.com/tensorflow/tensorflow/commit/eccb7ec454e6617738554a255d77f08e60ee0808"

def test_github_commit_fail():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-MATRIXSYNAPSE-1019356"
    github_release = Vuln(vuln_url).find_ref_url("GitHub Commit")
    assert github_release == ""

def test_github_release_success():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-MTPROTOPROXY-42170"
    github_release = Vuln(vuln_url).find_ref_url("GitHub Release")
    assert github_release == "https://github.com/alexbers/mtprotoproxy/releases"

def test_github_release_fail():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-PSDTOOLS-560316"
    github_commit = Vuln(vuln_url).find_ref_url("GitHub Release")
    assert github_commit == ""

def test_github_release_tag_success():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-FLASK-42185"
    github_release_tag = Vuln(vuln_url).find_ref_url("GitHub Release Tag")
    assert github_release_tag == "https://github.com/pallets/flask/releases/tag/0.12.3"

def test_github_release_tag_fail():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-TENSORFLOWCPU-1020821"
    github_release_tag = Vuln(vuln_url).find_ref_url("GitHub Release Tag")
    assert github_release_tag == ""

def test_github_add_inf_success():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-TENSORFLOWGPU-1013451"
    github_add_inf = Vuln(vuln_url).find_ref_url("GitHub Additional Information")
    assert github_add_inf == "https://github.com/advisories/GHSA-9mqp-7v2h-2382"

def test_github_add_inf_fail():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-TENSORFLOWCPU-1020814"
    github_add_inf = Vuln(vuln_url).find_ref_url("GitHub Additional Information")
    assert github_add_inf == ""

def test_github_pr_success():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-WEBSOCKETS-42181"
    github_pr = Vuln(vuln_url).find_ref_url("GitHub PR")
    assert github_pr == "https://github.com/aaugustin/websockets/pull/407"

def test_github_pr_fail():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-DJANGOTWOFACTORAUTH-1014668"
    github_pr = Vuln(vuln_url).find_ref_url("GitHub PR")
    assert github_pr == ""

def test_github_issue_success():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-EC2METADATA-569069"
    github_issue = Vuln(vuln_url).find_ref_url("GitHub Issue")
    assert github_issue == "https://github.com/adamchainz/ec2-metadata/issues/150"

def test_github_issue_fail():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-CARAVEL-40506"
    github_issue = Vuln(vuln_url).find_ref_url("GitHub Issue")
    assert github_issue == ""

def test_nvd_success():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-PRODUCTSCMFCORE-42090"
    nvd = Vuln(vuln_url).find_ref_url("NVD")
    assert nvd == "https://nvd.nist.gov/vuln/detail/CVE-2007-0240"

def test_nvd_fail():
    vuln_url = "https://snyk.io/vuln/SNYK-PYTHON-AIOHTTPSESSION-72728"
    nvd = Vuln(vuln_url).find_ref_url("NVD")
    assert nvd == ""

# Test the getting of PR link
def test_get_commit_link_from_pr_link_success():
    pr_url = "https://github.com/PyTorchLightning/pytorch-lightning/pull/2786"
    commit_url = Vuln(pr_url).get_commit_link_from_pr_link()
    if "https://" not in commit_url: commit_url = "https://github.com" + commit_url
    assert commit_url == "https://github.com/PyTorchLightning/pytorch-lightning/commit/96eb6ebacd5b8bba2dea4741355f576e8f1c6a16"

def test_get_commit_link_from_pr_link_fail():
    pr_url = "https://github.com/phihag/ipaddress/pull/56"
    commit_url = Vuln(pr_url).get_commit_link_from_pr_link()
    assert commit_url == ""