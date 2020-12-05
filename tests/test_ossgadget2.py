import subprocess
package_name = "urllib3"
command = ["docker", "run", "-it", "ossgadget:latest", "/bin/bash", "-c", "./oss-find-source/bin/Debug/netcoreapp3.1/oss-find-source pkg:pypi/" + package_name]
result = subprocess.run(command, stdout=subprocess.PIPE)
url = result.stdout.decode('utf-8')
print(url)
