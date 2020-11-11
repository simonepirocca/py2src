"""
This file correlate commit link of a vulnerability with the relative package name and directory
"""
import sys
import os
import csv
from urllib.request import Request, urlopen
sys.path.append(os.path.abspath("../src/"))
import logging
logging.basicConfig(filename="log.log", level=logging.INFO)


def test_find_package_from_vuln():
    package_names = []
    package_dirs = []
    commit_packages = []

    with open('../vulns_output/packages_with_vuln_commit.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:

                package_name = row[0]
                clone_url = row[1]
                package_dir = clone_url.split("/")[-1]
                package_dir = package_dir.replace(".git", "")

                if not os.path.isdir("../cloned_packages/" + package_dir):
                    logging.info(f"Package '{package_name}' is not in directory {package_dir}'")
                else:
                    package_names.append(package_name)
                    package_dirs.append(package_dir)

            line_count += 1

    n = len(package_names)  

    with open('../vulns_output/matching_vulns_unique_commit.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:

                id = row[0]
                name = row[4]
                commit_url = row[8]
                commit_hash = commit_url.split("/")[-1]
                hashtag_index = commit_hash.find("#")
                if hashtag_index != -1: commit_hash = commit_hash[:hashtag_index]
                package_index = searchStr(package_names, name, 0, n-1)

                if package_index != -1 and commit_hash != "":
                    commit_packages.append([id, name, package_dirs[package_index], commit_hash])
                else: logging.info(f"Commit'{commit_hash}' is not related to package '{name}' or is empty")

            line_count += 1

    logging.info(f"Commits: {len(commit_packages)}")
    logging.info(f"First commit: {commit_packages[0]}")

    with open("../vulns_output/clone_dir_from_commit_hash.csv", mode='w') as csv_file:
        vulns_writer = csv.writer(csv_file, delimiter=';')
        #vulns_writer.writerow(['ID', 'Package name', 'Clone dir', 'Commit hash'])
        for i in range(0, len(commit_packages)):
            vulns_writer.writerow(commit_packages[i])

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
