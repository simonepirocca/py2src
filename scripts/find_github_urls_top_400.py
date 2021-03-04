import os
import json
import sys
sys.path.append(os.path.abspath('../src/'))
from url_finder import URLFinder
from tqdm import tqdm
import json
import multiprocessing
import time

pypi_github_urls = {}
top_4000_json_file = os.path.abspath("../data/raw/top-pypi-packages-365-days.json")

with open(top_4000_json_file) as fp:
    data_json = json.load(fp)
    packages = [project["project"] for project in data_json["rows"]]

def worker(package_name: str, pypi_github_urls = None):
    tries = 5
    i = 0
    while i < tries:
        finder = URLFinder(package_name=package_name)
        github_url = finder.find_github_url()
        if github_url:
            break
        else:
            time.sleep(5)
            i = i + 1
            
    #pypi_github_urls[package_name] = github_url
    return github_url

#manager = multiprocessing.Manager()
#pypi_github_urls = manager.dict()
pypi_github_urls = {}
number_of_processors = 4
pool = multiprocessing.Pool(processes=number_of_processors)

for package in tqdm(packages[3600:3768]):
    #pool.apply_async(worker, args=(package, pypi_github_urls))
    pypi_github_urls[package] = worker(package)

#pool.close()
#pool.join()

import pdb; pdb.set_trace()
result_path = os.path.abspath("../data/intermediate/pypi_github_urls.json")
with open(result_path, "w") as fp:
    json.dump(pypi_github_urls, fp)

