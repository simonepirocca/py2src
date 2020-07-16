"""
This file contains test cases for testing the Package class
"""
import sys
import os
sys.path.append(os.path.abspath("../src/"))
from package import Package
import logging
logging.basicConfig(filename="log.log", level=logging.DEBUG)


def test_get_json_url_urllib3():
    package_name = "urllib3"
    pkg = Package(package_name)
    json_url = pkg.json_url
    logging.info(f"Package: {package_name}, Json url: {json_url}")
    assert json_url == "https://pypi.org/pypi/urllib3/json"

def test_get_metadata_urllib3():
    package_name = "urllib3"
    pkg = Package(package_name)
    metadata = pkg.metadata_dict
    logging.info(f"Package: {package_name}, Metadata fields: {metadata.keys()}")
    assert metadata

def test_extract_homepage_urllib3():
    package_name = "urllib3"
    pkg = Package(package_name)
    homepage = pkg.extract_homepage()
    logging.info(f"Package: {package_name}, Homepage: {homepage}")
    assert homepage == "https://urllib3.readthedocs.io"

def test_extract_codepage_urllib3():
    package_name = "urllib3"
    pkg = Package(package_name)
    codepage = pkg.extract_codepage()
    logging.info(f"Package: {package_name}, Codepage: {codepage}")
    assert codepage == "https://github.com/urllib3/urllib3" 

def test_extract_urls_from_metadata_urllib3():
    package_name = "urllib3"
    pkg = Package(package_name)
    urls = pkg.extract_urls_from_metadata()
    logging.info(f"Package: {package_name}, first 3 urls: {urls[:2]}")
    assert len(urls) > 0 

def test_is_github_url_urllib3():
    github_url = "https://github.com/urllib3/urllib3/"
    is_github_url = Package("").is_github_url(github_url)
    logging.info(f"URL: {github_url}, is_github_url: {is_github_url}")
    assert is_github_url 

def test_extract_github_url_from_webpage():
    package_name = "urllib3"
    pkg = Package(package_name)
    homepage = pkg.extract_homepage()
    url = pkg.extract_github_url_from_webpage(homepage)
    logging.info(f"Package: {package_name}, Scraped url: {url}")
    assert url 

def test_get_final_url():
    package_name = "urllib3"
    pkg = Package(package_name)
    final_url = pkg.get_final_url()
    logging.info(f"Package: {package_name}, Final url: {final_url}")
    assert final_url == "https://github.com/urllib3/urllib3" 

