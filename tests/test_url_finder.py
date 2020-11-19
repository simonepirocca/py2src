import sys
import os
sys.path.append(os.path.abspath('../src/'))

from url_finder import URLFinder

def test_initialization():
    pkg = URLFinder(package_name='urllib3')
    assert isinstance(pkg, URLFinder)

def test_find_github_url():
    finder = URLFinder(package_name='urllib3')
    github_url = finder.find_github_url()
    assert github_url == "https://github.com/urllib3/urllib3"

