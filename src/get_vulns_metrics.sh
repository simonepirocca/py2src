#!/bin/bash

CLONE_DIR=$1
INPUT=../../tmp/tmp_vulns.csv
START=1
i=0
vulns=0
avg_package_time_interval=0
commit_year=""
commit_month=""
commit_day=""
release_year=""
release_month=""
release_day=""
time_interval=0
release_date=""
release_type=""
severity_L=0
severity_M=0
severity_H=0
major_v=0
minor_v=0
patch_v=0
median_pkg_severity=""
median_pkg_release_type=""
if [[ ! -z "$CLONE_DIR" ]]
then
    cd ../cloned_repos
    if [ -d "./$CLONE_DIR" ]
    then
        cd $CLONE_DIR
        while IFS=';' read -r severity commit_hash 
        do
            if [ $i -ge $START ]
            then
                commit_hash=${commit_hash::-1}
                releases_string=$(git tag --contains ${commit_hash} 2>&1)
                if [[ ! $releases_string == *"error:"* ]]
                then
                    commit_date_command=$(git show -s --format=%ci ${commit_hash} 2>&1)
                    if [[ ! $commit_date_command == *"fatal:"* ]]
                    then
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
                        if [ ! -z "$commit_date" ]
                        then
                            tags=0
                            tmp_release_type=""
                            tmp_real_tag=""
                            for tmp_tag in $releases_string
                            do
                                official_tag=0
                                IFS='.' read -ra tmp_tag_parts <<< "$tmp_tag"
                                tmp_tag_parts_number=${#tmp_tag_parts[@]}
                                if [ $tmp_tag_parts_number -eq 3 ]
                                then
                                    tmp_major=${tmp_tag_parts[0]}
                                    tmp_minor=${tmp_tag_parts[1]}
                                    tmp_patch=${tmp_tag_parts[2]}

                                    tmp_major_start_index=0
                                    tmp_major_len=${#tmp_major}
                                    while [ $tmp_major_start_index -lt $tmp_major_len ]
                                    do
                                        tmp_tmp_major=${tmp_major:tmp_major_start_index}
                                        if [[ "$tmp_tmp_major" == +([0-9]) ]]; then break; fi
                                        tmp_major_start_index=$((tmp_major_start_index+1))
                                    done
                                    if [ $tmp_major_start_index -eq $tmp_major_len ]; then tmp_major=""; else tmp_major=$tmp_tmp_major; fi

                                    if [[ "$tmp_minor" != +([0-9]) ]]; then tmp_minor=""; fi

                                    if [[ "$tmp_patch" != +([0-9]) ]] 
                                    then
                                        tmp_patch_len=${#tmp_patch}
                                        tmp_patch_end_index=$tmp_patch_len
                                        while [ $tmp_patch_end_index -gt 0 ]
                                        do
                                            tmp_tmp_patch=${tmp_patch:0:tmp_patch_end_index}
                                            if [[ "$tmp_tmp_patch" == +([0-9]) ]]; then break; fi
                                            tmp_patch_end_index=$((tmp_patch_end_index-1))
                                        done
                                        if [ $tmp_patch_end_index -eq 0 ]; then tmp_patch=""
                                        else
                                            if [ ${tmp_patch:tmp_patch_end_index:1} == "+" ]; then tmp_patch=$tmp_tmp_patch
                                            else tmp_patch=""; fi
                                        fi
                                    fi

                                    if ! [ -z "$tmp_major" -o -z "$tmp_minor"  -o -z "$tmp_patch" ]
                                    then 
                                        official_tag=1
                                        tmp_real_tag="$tmp_major.$tmp_minor.$tmp_patch"
                                        if [ $tmp_patch != "0" ]; then tmp_release_type="patch"
                                        elif [ $tmp_minor != "0" ]; then tmp_release_type="minor"
                                        else tmp_release_type="major"; fi
                                    fi
                                fi
                                if [ $official_tag -eq 1 ]
                                then
                                    release_date_command=$(git show -s --format=%ci ${tmp_tag} 2>&1)
                                    if [[ ! $release_date_command == *"fatal:"* ]]
                                    then
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
                                        if [ ! -z "$tmp_release_date" ]
                                        then
                                            year_interval=$(( (release_year - commit_year) * 365 ))
                                            month_interval=$(( (release_month - commit_month) * 30 ))
                                            day_interval=$(( release_day - commit_day ))
                                            tmp_time_interval=$(( year_interval+month_interval+day_interval ))

                                            if [ $tags -eq 0 ] || [ $tmp_time_interval -lt $time_interval ]
                                            then 
                                                release_type=$tmp_release_type
                                                release_date=$tmp_release_date
                                                time_interval=$tmp_time_interval
                                                tag=$tmp_real_tag
                                            fi
                                            tags=$((tags+1))
                                        fi
                                    fi
                                fi
                            done

                            if [ $tags -gt 0 ]
                            then
                                if [ "$severity" == "L" ]; then severity_L=$((severity_L+1))
                                elif [ "$severity" == "M" ]; then severity_M=$((severity_M+1))
                                else severity_H=$((severity_H+1)); fi
                                if [ "$release_type" == "major" ]; then major_v=$((major_v+1))
                                elif [ "$release_type" == "minor" ]; then minor_v=$((minor_v+1))
                                else patch_v=$((patch_v+1)); fi
                                vulns=$((vulns+1))
                                avg_package_time_interval=$((avg_package_time_interval+time_interval))
                            fi
                        fi
                    fi
                fi
            fi
            i=$((i+1))
        done < $INPUT
        if [ $vulns -gt 0 ]
        then 
            if [ $severity_L -ge $severity_M ] && [ $severity_L -ge $severity_H ]; then median_pkg_severity="L"
            elif [ $severity_M -ge $severity_L ] && [ $severity_M -ge $severity_H ]; then median_pkg_severity="M"
            else median_pkg_severity="H"; fi

            if [ $major_v -ge $minor_v ] && [ $major_v -ge $patch_v ]; then median_pkg_release_type="major"
            elif [ $minor_v -ge $major_v ] && [ $minor_v -ge $patch_v ]; then median_pkg_release_type="minor"
            else median_pkg_release_type="patch"; fi

            avg_package_time_interval=$((avg_package_time_interval / vulns))
            echo ";$vulns;$median_pkg_severity;$median_pkg_release_type;$avg_package_time_interval;"
        fi
    fi
fi
