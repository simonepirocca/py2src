#!/bin/bash

INPUT=../output/vulns_output/packages_with_vuln_commit.csv
START=1
END=120
i=0

cd ../../../cloned_packages
while IFS=';' read -r package_name clone_url
do
    if [ $i -ge $START ]
    then
        git clone -n $clone_url 
        echo "******* $i. $package_name CLONED ********"
    fi

    i=$((i+1))
    if [ $i -gt $END ]
    then 
        break
    fi
done < $INPUT
