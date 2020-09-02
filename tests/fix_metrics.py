"""
This file get all the missing metrics for each repo
"""
import sys
import os
import csv
import json
from array import *
from datetime import date
from urllib.request import Request, urlopen
sys.path.append(os.path.abspath("../src/"))
from package import Package
import logging
logging.basicConfig(filename="log.log", level=logging.INFO)

def test_fix_metrics():

    start = 1
    count = 4000
    end = start + count

    input_csv = "../metrics_output/metrics_final_with_tags_and_0.csv"
    output_csv = "../metrics_output/test.csv"

    packages = []
    empty_cells = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    missing_github_url = 0
    complete_rows = 0
    tot_packages = 0
    duplicates = 0
    line_count = 0
        
    with open(input_csv) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            if line_count >= start:
                duplicated = False

                github_url = row[2]
                libraries_io_url = row[14]
            #    if github_url != "":
            #        for i in range (0, tot_packages):
            #            if row[2] == packages[i][2]:
            #                duplicated = True
            #                duplicates += 1
            #                break

                if not duplicated:
                    complete_row = True
                    metrics = []
                    for i in range(0, 18):
                        if row[i] == "" or row[i] == "0": 
                            if i == 2: missing_github_url += 1
                            if i == 10 and row[9] != "" and row[9] != "0": metrics.append(0)
                            elif row[i] == "0" and i != 0 and i != 2 and i != 4 and i != 14: metrics.append(0)
                            #if i == 10 and row[9] != "" and row[9] != "0": metrics.append(1)
                            #elif row[i] == "0" and i != 0 and i != 2 and i != 4 and i != 14: metrics.append(1)

             #               elif github_url != "":
             #                   if "#" in github_url: 
             #                       to_delete_index = github_url.index("#")
             #                       github_url = github_url[:to_delete_index]
             #                   github_url_parts = github_url.split("/")
             #                   parts = len(github_url_parts)
             #                   github_token = "a_valid_github_token"
             #                   package_name = row[0]
             #                   pkg = Package(package_name)

             #                   if i == 4: 
             #                       commits_json_url = "https://api.github.com/repos/" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1] + "/commits"
             #                       api_req = Request(commits_json_url)
             #                       api_req.add_header('Authorization', 'token ' + github_token)
             #                       try:
             #                           commits_json = json.loads(urlopen(api_req).read().decode())
             #                           last_commit = commits_json[0]["commit"]["author"]["date"][:10]
             #                           with open('../metrics_output/json/commits/' + package_name + '.json', 'w') as json_file:
             #                               json.dump(commits_json, json_file)
             #                       except Exception:
             #                           last_commit = ""
             #                           empty_cells[i] += 1
             #                           complete_row = False
             #                       metrics.append(last_commit)

             #                   elif i == 5:
             #                       commits = pkg.get_commits2_from_github_repo(github_url).strip()
             #                       if commits == "": 
             #                           empty_cells[i] += 1
             #                           complete_row = False
             #                           metrics.append("")
             #                       else:
             #                           commits = convert_to_number(commits)
             #                           commit_freq = 0
             #                           github_json_url = "https://api.github.com/repos/" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1]
             #                           api_req = Request(github_json_url)
             #                           api_req.add_header('Authorization', 'token ' + github_token)
             #                           try:
             #                               github_json = json.loads(urlopen(api_req).read().decode())
             #                               created_at = github_json["created_at"][:10]

             #                               total_months = 0
             #                               if created_at != "":
             #                                   today_date = date.today().strftime('%Y-%m-%d')
             #                                   total_months = (int(today_date[:4]) - int(created_at[:4])) * 12 + (int(today_date[5:7]) - int(created_at[5:7]))
             #                               if total_months != 0:
             #                                   commit_freq = int(int(commits) / total_months)
             #                               with open('../metrics_output/json/generic_data/' + package_name + '.json', 'w') as json_file:
             #                                   json.dump(github_json, json_file)
             #                           except Exception as error:
             #                               commit_freq = ""
             #                               empty_cells[i] += 1
             #                               complete_row = False
             #                           metrics.append(commit_freq)

             #                   if i == 6:
             #                       releases = pkg.get_tags_from_github_repo(github_url).strip()
             #                       if releases == "": 
             #                           empty_cells[i] += 1
             #                           complete_row = False
             #                           metrics.append("")
             #                       else:
             #                           releases = convert_to_number(releases)
             #                           release_freq = 0
             #                           github_json_url = "https://api.github.com/repos/" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1]
             #                           api_req = Request(github_json_url)
             #                           api_req.add_header('Authorization', 'token ' + github_token)
             #                           try:
             #                               github_json = json.loads(urlopen(api_req).read().decode())
             #                               created_at = github_json["created_at"][:10]

             #                               total_days = 0
             #                               if created_at != "":
             #                                   today_date = date.today().strftime('%Y-%m-%d')
             #                                   total_days = (int(today_date[:4]) - int(created_at[:4])) * 365 + (int(today_date[5:7]) - int(created_at[5:7])) * 30 + (int(today_date[8:]) - int(created_at[8:]))
             #                               if total_days != 0:
             #                                   release_freq = int(total_days / int(releases))
             #                               with open('../metrics_output/json/generic_data/' + package_name + '.json', 'w') as json_file:
             #                                   json.dump(github_json, json_file)
             #                           except Exception as error:
             #                               release_freq = str(error)
             #                               empty_cells[i] += 1
             #                               complete_row = False
             #                           metrics.append(release_freq)

             #                   elif i == 6:
             #                       releases = pkg.get_link_span_metric_from_github_repo(github_url, "releases").strip()
             #                       if releases == "": 
             #                           empty_cells[i] += 1
             #                           complete_row = False
             #                           metrics.append("")
             #                       else:
             #                           releases = convert_to_number(releases)
             #                           release_freq = 0
             #                           github_json_url = "https://api.github.com/repos/" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1]
             #                           api_req = Request(github_json_url)
             #                           api_req.add_header('Authorization', 'token ' + github_token)
             #                           try:
             #                               github_json = json.loads(urlopen(api_req).read().decode())
             #                               created_at = github_json["created_at"][:10]

             #                               total_days = 0
             #                               if created_at != "":
             #                                   today_date = date.today().strftime('%Y-%m-%d')
             #                                   total_days = (int(today_date[:4]) - int(created_at[:4])) * 365 + (int(today_date[5:7]) - int(created_at[5:7])) * 30 + (int(today_date[8:]) - int(created_at[8:]))
             #                               if total_days != 0:
             #                                   release_freq = int(int(releases) / total_days)
             #                               with open('../metrics_output/json/generic_data/' + package_name + '.json', 'w') as json_file:
             #                                   json.dump(github_json, json_file)
             #                           except Exception as error:
             #                               release_freq = str(error)
             #                               empty_cells[i] += 1
             #                               complete_row = False
             #                           metrics.append(release_freq)

             #                   elif i == 7:
             #                       open_issues = pkg.get_link_span_metric_from_github_repo(github_url, "issues").strip()
             #                       if open_issues == "": 
             #                           empty_cells[i] += 1
             #                           complete_row = False
             #                           metrics.append("")
             #                       else: metrics.append(convert_to_number(open_issues))

             #                   elif i == 8:
             #                       issues_url = pkg.get_issues_url_from_github_repo(github_url).strip()
             #                       closed_issues = pkg.get_closed_issues_from_github_repo(issues_url).strip()
             #                       if closed_issues == "": 
             #                           empty_cells[i] += 1
             #                           complete_row = False
             #                           metrics.append("")
             #                       else: metrics.append(convert_to_number(closed_issues))

             #                   elif i == 9:
             #                       api_closed_issues = 0
             #                       sum_closed_days = 0
             #                       avg_close_issue_days = ""
             #                       issue_json_url = "https://api.github.com/search/issues?q=repo:" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1] + "%20is:issue%20is:closed&per_page=100"
             #                       api_req = Request(issue_json_url)
             #                       api_req.add_header('Authorization', 'token ' + github_token)            

             #                       try:
             #                           issue_json = json.loads(urlopen(api_req).read().decode())
             #                           with open('../metrics_output/json/closed_issues/' + package_name + '.json', 'w') as json_file:
             #                               json.dump(issue_json, json_file)
             #                       except Exception as error:
             #                           empty_cells[i] += 1
             #                           complete_row = False
             #                           metrics.append(error)
             #                       else:
             #                           total_count = int(issue_json["total_count"])
             #                           for i in range(len(issue_json["items"])):
             #                               try:
             #                                   created_date = issue_json["items"][i]["created_at"][:10]
             #                                   closed_date = issue_json["items"][i]["closed_at"][:10]
             #                               except TypeError as error:
             #                                   api_closed_issues = error
             #                                   created_date = ""
             #                                   closed_date = ""

             #                               if created_date != "" and closed_date != "":
             #                                   close_days = (int(closed_date[:4]) - int(created_date[:4])) * 365 + (int(closed_date[5:7]) - int(created_date[5:7])) * 30 + (int(closed_date[8:]) - int(created_date[8:]))
             #                                   sum_closed_days = sum_closed_days + close_days
             #                                   api_closed_issues = api_closed_issues + 1

             #                           if api_closed_issues > 0:
             #                               avg_close_issue_days = int(sum_closed_days / api_closed_issues)
             #                           else:
             #                               empty_cells[i] += 1
             #                               complete_row = False
             #                           metrics.append(api_closed_issues) 

             #                       elif i == 10:
             #                       api_closed_issues = 0
             #                       sum_closed_days = 0
             #                       avg_close_issue_days = ""
             #                       issue_json_url = "https://api.github.com/search/issues?q=repo:" + github_url_parts[parts-2] + "/" + github_url_parts[parts-1] + "%20is:issue%20is:closed&per_page=100"
             #                       api_req = Request(issue_json_url)
             #                       api_req.add_header('Authorization', 'token ' + github_token)            

             #                       try:
             #                           issue_json = json.loads(urlopen(api_req).read().decode())
             #                           with open('../metrics_output/json/closed_issues/' + package_name + '.json', 'w') as json_file:
             #                               json.dump(issue_json, json_file)
             #                       except Exception as error:
             #                           empty_cells[i] += 1
             #                           complete_row = False
             #                           metrics.append(error)
             #                       else:
             #                           total_count = int(issue_json["total_count"])
             #                           for i in range(len(issue_json["items"])):
             #                               try:
             #                                   created_date = issue_json["items"][i]["created_at"][:10]
             #                                   closed_date = issue_json["items"][i]["closed_at"][:10]
             #                               except TypeError as error:
             #                                   avg_close_issue_days = error
             #                                   created_date = ""
             #                                   closed_date = ""

             #                               if created_date != "" and closed_date != "":
             #                                   close_days = (int(closed_date[:4]) - int(created_date[:4])) * 365 + (int(closed_date[5:7]) - int(created_date[5:7])) * 30 + (int(closed_date[8:]) - int(created_date[8:]))
             #                                   sum_closed_days = sum_closed_days + close_days
             #                                   api_closed_issues = api_closed_issues + 1

             #                           if api_closed_issues > 0:
             #                               avg_close_issue_days = int(sum_closed_days / api_closed_issues)
             #                           else:
             #                               empty_cells[i] += 1
             #                               complete_row = False
             #                           metrics.append(avg_close_issue_days) 

             #                   elif i == 11:
             #                       contributors = pkg.get_link_span_metric_from_github_repo(github_url, "graphs/contributors").strip()
             #                       if contributors == "": 
             #                           empty_cells[i] += 1
             #                           complete_row = False
             #                           metrics.append("")
             #                       else: metrics.append(convert_to_number(contributors))

             #                   elif i == 12:
             #                       dependents_url = pkg.get_dependent_url_from_github_repo(github_url).strip() 
             #                       dep_repos = pkg.get_dependent_from_github_repo(dependents_url, "dependent_type=REPOSITORY").strip()
             #                       if dep_repos == "": 
             #                           empty_cells[i] += 1
             #                           complete_row = False
             #                           metrics.append("")
             #                       else: metrics.append(convert_to_number(dep_repos))

             #                   if i == 13:
             #                       dependents_url = pkg.get_dependent_url_from_github_repo(github_url).strip() 
             #                       dep_packages = pkg.get_dependent_from_github_repo(dependents_url, "dependent_type=PACKAGE").strip()
             #                       if dep_packages == "": 
             #                           empty_cells[i] += 1
             #                           complete_row = False
             #                           metrics.append("")
             #                       else: metrics.append(convert_to_number(dep_packages))

             #                   else:
             #                       empty_cells[i] += 1
             #                       complete_row = False
             #                       metrics.append("")
                            else:
                                empty_cells[i] += 1
                                complete_row = False
                                metrics.append("")
                        else: 
                            if i not in [0, 2, 4, 14]: 
                                metrics.append(convert_to_number(row[i]))
                            else: metrics.append(row[i])

                    packages.append(metrics)
                    if complete_row: complete_rows += 1
                    tot_packages += 1

            line_count += 1
            if line_count >= end: break

    logging.info(f"Count: {line_count - start}, Duplicated: {duplicates}, Tot packages: {tot_packages}, Complete rows: {complete_rows}, Missing GitHub urls: {missing_github_url}")
    logging.info(f"Empty cells: {empty_cells}")
    logging.info(f"First package: {packages[0][0]}")
    logging.info(f"Last package: {packages[tot_packages-1][0]}")
    logging.info(f"-------------------------------------------------------------------------------------------------------------")

    with open(output_csv, mode='w') as metrics_csv:
        packages_writer = csv.writer(metrics_csv, delimiter=';')
        packages_writer.writerow(['package_name', 'pypi_downloads', 'github_url', 'stars',\
 'last_commit', 'commit_freq', 'release_freq', 'open_issues', 'closed_issues', 'api_closed_issues', 'avg_days_to_close_issue', 'contributors',\
 'dep_repos', 'dep_pkgs', 'libraries_io_url', 'sourcerank', 'dep_repos', 'dep_pkgs'])

        for i in range(0, tot_packages):
            packages_writer.writerow(packages[i])

def convert_to_number(n: str):
    if "," in n: return int(n.replace(",", ""))
    if "K" in n:
        if "." in n:
            dot_index = n.index(".")
            k_index = n.index("K")
            decimals = k_index - dot_index - 1
            if decimals == 1: return int(n.replace(".", "").replace("K", "")) * 100
            elif decimals == 2: return int(n.replace(".", "").replace("K", "")) * 10
        return int(n.replace("K", "")) * 1000
    if "k" in n:
        if "." in n:
            dot_index = n.index(".")
            k_index = n.index("k")
            decimals = k_index - dot_index - 1
            if decimals == 1: return int(n.replace(".", "").replace("k", "")) * 100
            elif decimals == 2: return int(n.replace(".", "").replace("k", "")) * 10
        return int(n.replace("k", "")) * 1000
    return int(n)