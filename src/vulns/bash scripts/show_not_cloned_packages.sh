#!/bin/bash

INPUT=../output/vulns_output/packages_with_vuln_commit.csv
ERRORS=../output/vulns_output/not_cloned_packages.csv
START=1
END=120
i=0

cd ../../../cloned_packages
while IFS=';' read -r package_name clone_url
do
    if [ $i -ge $START ]
    then
        if [ ! -d "$package_name" ]
        then
            echo "$package_name not cloned."
            echo "$package_name" >> $ERRORS
        fi
    fi

    i=$((i+1))
    if [ $i -gt $END ]
    then 
        break
    fi
done < $INPUT
