#!/bin/bash

INPUT=../output/vulns_output/clone_dir_from_pr_commit_hash.csv
VULNS_OUTPUT=../output/vulns_output/pr_vulns_time_interval.csv
PACKAGE_OUTPUT=../output/vulns_output/package_time_interval_for_pr_vulns.csv
ERRORS_LOG=../../output/vulns_output/errors_for_pr_hashes.txt
START=1
END=1000
i=0
vulns=0
avg_package_time_interval=0
current_package=""
current_dir=""
commit_year=""
commit_month=""
commit_day=""
release_year=""
release_month=""
release_day=""
time_interval=0
release_date=""

if [ -f "$ERRORS_LOG" ]; then rm ../$ERRORS_LOG; fi
cd ../../../cloned_packages
echo "Vuln ID;Package name;Clone dir;Commit hash;Release;Commit date;Release date;Time interval" > $VULNS_OUTPUT
echo "Package name;Clone dir;Tot vulns with commit;Avg time interval" > $PACKAGE_OUTPUT

while IFS=';' read -r id package_name clone_dir commit_url commit_hash 
do
    if [ $i -ge $START ]
    then
        if [ $i -eq $START ]
        then
            cd $clone_dir
            current_package=$package_name
            current_dir=$clone_dir
        fi
        if [ "$clone_dir" != "$current_dir" ]
        then
            if [ ! -d "../$clone_dir" ]; then echo "'$clone_dir' doeans't exists." >> $ERRORS_LOG
            else
                if [ $vulns -gt 0 ]
                then 
                    avg_package_time_interval=$((avg_package_time_interval / vulns))
                    echo "$current_package;$current_dir;$vulns;$avg_package_time_interval" >> ../$PACKAGE_OUTPUT
                fi
                cd ../$clone_dir
                current_package=$package_name
                current_dir=$clone_dir
                vulns=0
                avg_package_time_interval=0
            fi
        fi
        commit_hash=${commit_hash::-1}
        releases_string=$(git tag --contains ${commit_hash} 2>&1)
        if [[ $releases_string == *"error:"* ]]; then echo "ID '$id' doesn't belong to '$current_package'." >> $ERRORS_LOG
        else
            commit_date_command=$(git show -s --format=%ci ${commit_hash} 2>&1)
            if [[ $commit_date_command == *"fatal:"* ]]; then echo "ID '$id' doesn't have a commit date." >> $ERRORS_LOG
            else
                commit_date=""
                for item1 in $commit_date_command
                do
                    IFS='-' read -ra tmp_commit_date_parts <<< "$item1"
                    tmp_parts_number=${#tmp_commit_date_parts[@]}
                    if [ $tmp_parts_number -eq 3 ]
                    then
                        tmp_commit_year=${tmp_commit_date_parts[0]}
                        tmp_commit_month=${tmp_commit_date_parts[1]}
                        tmp_commit_day=${tmp_commit_date_parts[2]}
                        if [[ ${#tmp_commit_year} -eq 4 && ${#tmp_commit_month} -eq 2 && ${#tmp_commit_day} -eq 2 ]]
                        then
                            commit_date=$item1
                            commit_year=$(expr $tmp_commit_year + 0)
                            commit_month=$(expr $tmp_commit_month + 0)
                            commit_day=$(expr $tmp_commit_day + 0)
                            break
                        fi
                    fi
                done
                if [ -z "$commit_date" ]; then echo "ID '$id' doesn't have a commit date." >> $ERRORS_LOG
                else
                    tags=0
                    for tmp_tag in $releases_string
                    do
                        release_date_command=$(git show -s --format=%ci ${tmp_tag} 2>&1)
                        if [[ $release_date_command == *"fatal:"* ]]; then echo "ID '$id' doesn't have a release date for version '$tmp_tag'." >> $ERRORS_LOG
                        else
                            tmp_release_date=""
                            for item2 in $release_date_command
                            do
                                IFS='-' read -ra tmp_release_date_parts <<< "$item2"
                                tmp_parts_number=${#tmp_release_date_parts[@]}
                                if [ $tmp_parts_number -eq 3 ]
                                then
                                    tmp_release_year=${tmp_release_date_parts[0]}
                                    tmp_release_month=${tmp_release_date_parts[1]}
                                    tmp_release_day=${tmp_release_date_parts[2]}
                                    if [[ ${#tmp_release_year} -eq 4 && ${#tmp_release_month} -eq 2 && ${#tmp_release_day} -eq 2 ]]
                                    then
                                        tmp_release_date=$item2
                                        release_year=$(expr $tmp_release_year + 0)
                                        release_month=$(expr $tmp_release_month + 0)
                                        release_day=$(expr $tmp_release_day + 0)
                                        break
                                    fi
                                fi
                            done
                            if [ -z "$tmp_release_date" ]; then echo "'$tmp_tag' of ID '$id' doesn't have a release date." >> $ERRORS_LOG
                            else
                                year_interval=$(( (release_year - commit_year) * 365 ))
                                month_interval=$(( (release_month - commit_month) * 30 ))
                                day_interval=$(( release_day - commit_day ))
                                tmp_time_interval=$(( year_interval+month_interval+day_interval ))

                                if [ $tags -eq 0 ] || [ $tmp_time_interval -lt $time_interval ]
                                then 
                                    release_date=$tmp_release_date
                                    time_interval=$tmp_time_interval
                                    tag=$tmp_tag
                                fi
                                tags=$((tags+1))
                            fi
                        fi
                    done

                    if [ $tags -gt 0 ]
                    then
                        echo "$id;$package_name;$clone_dir;$commit_hash;$tag;$commit_date;$release_date;$time_interval" >> ../$VULNS_OUTPUT
                        vulns=$((vulns+1))
                        avg_package_time_interval=$((avg_package_time_interval+time_interval))
                    else echo "$id doesn't have any release date associated." >> $ERRORS_LOG
                    fi
                fi
            fi
        fi
    fi

    i=$((i+1))
    if [ $i -gt $END ]
    then 
        break
    fi
done < $INPUT

if [ $vulns -gt 0 ]
then 
    avg_package_time_interval=$((avg_package_time_interval / vulns))
    echo "$current_package;$current_dir;$vulns;$rows;$avg_package_time_interval" >> ../$PACKAGE_OUTPUT
fi
