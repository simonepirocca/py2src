"""
This file get all the missing github url related to package names
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

    name = "urllib3"
    package_index = searchStr(package_names, name, 0, n-1)
    if package_index != -1:
        logging.info(f"{name} = {packages[package_index][0]}")
    else:
        logging.info(f"{name} not present")

def compareStrings(str1, str2):  
   
    i = 0 
    while i < len(str1) - 1 and str1[i] == str2[i]:  
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
