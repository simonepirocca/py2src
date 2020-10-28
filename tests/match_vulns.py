"""
This file finds the vulnerabilities related to already known packages
"""
import sys
import os
import csv
from urllib.request import Request, urlopen
sys.path.append(os.path.abspath("../src/"))
import logging
logging.basicConfig(filename="log.log", level=logging.INFO)


def test_match_packages():
    packages = []
    package_names = []
    matching_vulns = []
    matching_packages = []
    tot_matching_packages = 0

    with open('../metrics_output/packages_asc.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:

                package_name = row[0]
                github_url = row[1]
                pypi_downloads = row[2]
                dep_repos = row[3]
                dep_pkgs = row[4]

                package_names.append(package_name)
                packages.append([package_name, github_url, pypi_downloads, dep_repos, dep_pkgs])

            line_count += 1

    n = len(package_names)  

    with open('../vulns_output/snyk_pip_vulns.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:

                name = row[3]
                package_index = searchStr(package_names, name, 0, n-1)

                if package_index != -1:
                    matching_vulns.append(row)

                    duplicated = False
                    for j in range (0, tot_matching_packages):
                        if name == matching_packages[j]:
                            duplicated = True
                            break
                    if not duplicated:
                        matching_packages.append(name)
                        tot_matching_packages += 1

            line_count += 1

    logging.info(f"Matching vulns: {len(matching_vulns)}, Matching packages: {tot_matching_packages}")

    with open("../vulns_output/matching_vulns.csv", mode='w') as csv_file:
        vulns_writer = csv.writer(csv_file, delimiter=';')
        vulns_writer.writerow(['Severity', 'Name', 'Vulnerability_url', 'Package', 'Versions', 'CVE', 'GitHub Advisory', \
'GitHub Commit', 'GitHub Release', 'GitHub Release Tag', 'GitHub Additional Information', 'GitHub PR', 'GitHub Issue', 'NVD'])

        for i in range(0, len(matching_vulns)):
            vulns_writer.writerow(matching_vulns[i])

    with open("../vulns_output/matching_packages.csv", mode='w') as csv_file:
        vulns_writer = csv.writer(csv_file, delimiter=';')
        for i in range(0, len(matching_packages)):
            vulns_writer.writerow([matching_packages[i]])

def compareStrings(str1, str2):  
   
    i = 0 
    if len(str1) <= len(str2): max_len = len(str1)
    else: max_len = len(str2)
    while i < max_len - 1 and str1[i] == str2[i]:  
        i += 1 
    if str1[i] > str2[i]:  
        return -1 
  
    return str1[i] < str2[i] 
   
# Main function to find string location  
def searchStr(arr, string, first, last):  
   
    if first > last: 
        return -1 
  
    # Move mid to the middle  
    mid = (last + first) // 2 
  
    # If mid is empty , find closet non-empty string  
    if len(arr[mid]) == 0:  
       
        # If mid is empty, search in both sides of mid  
        # and find the closest non-empty string, and  
        # set mid accordingly.  
        left, right = mid - 1, mid + 1 
        while True:  
           
            if left < first and right > last:  
                return -1
                  
            if right <= last and len(arr[right]) != 0:  
                mid = right  
                break 
               
            if left >= first and len(arr[left]) != 0:  
                mid = left  
                break 
               
            right += 1 
            left -= 1
  
    # If str is found at mid  
    if compareStrings(string, arr[mid]) == 0:  
        return mid  
  
    # If str is greater than mid  
    if compareStrings(string, arr[mid]) < 0:  
        return searchStr(arr, string, mid+1, last)  
  
    # If str is smaller than mid  
    return searchStr(arr, string, first, mid-1)  
