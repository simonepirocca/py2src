import subprocess
import csv

f = open("../../output/metrics_output/wrong_urls.csv", "w")
f.write("package_name;ossgadget_url;old_url\n")
f.close()

i = 0
with open("../../output/metrics_output/metrics_with_urls_added.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    for row in csv_reader:
        if i > 0:
            package_name = row[0]
            command1 = ["docker", "run", "-it", "ossgadget:latest", "/bin/bash", "-c", "./oss-find-source/bin/Debug/netcoreapp3.1/oss-find-source pkg:pypi/" + package_name]
            result1 = subprocess.run(command1, stdout=subprocess.PIPE)
            url1 = result1.stdout.decode('utf-8')
            if "No repositories were found after searching metadata." in url1:
                command2 = ["docker", "run", "-it", "ossgadget:latest", "/bin/bash", "-c", "./oss-find-source/bin/Debug/netcoreapp3.1/oss-find-source pkg:github/" + package_name + "/" + package_name]
                result2 = subprocess.run(command2, stdout=subprocess.PIPE)
                url2 = result2.stdout.decode('utf-8')
                if "No repositories were found after searching metadata." in url2: url = "URL Not Found"
                else:
                    start = url2.index("h")
                    url = url2.split(" ")[0][start:]
            else: 
                start = url1.index("h")
                url = url1.split(" ")[0][start:]
            old_url = row[2].lower().replace("https", "http")
            if url.lower().replace("https", "http") != old_url:
                f = open("../../output/metrics_output/wrong_urls.csv", "a")
                f.write(package_name + ";" + url + ";" + old_url + "\n")
                f.close()
        i += 1