import json
import glob
import os

result = {}
json_dir = os.path.abspath("../data/intermediate/")
for f in glob.glob("{}/*.json".format(json_dir)):
    with open(f) as infile:
        temp_dict = json.load(infile)
        for k, v in temp_dict.items():
            #result.setdefault(k, []).append(v)
            result.setdefault(k, v)

with open(os.path.abspath("../data/final/merged_pypi_github_urls.json"), "w") as outfile:
    json.dump(result, outfile)
