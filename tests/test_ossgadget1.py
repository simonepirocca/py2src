import sys
import os
import logging
import subprocess
import pytest
from pathlib import Path

utils_module_path = Path().resolve().parent / "src" / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output

logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="log_test.log")
def test():
    package_name = "urllib3"
    command = ["docker", "run", "-it", "ossgadget:latest", "/bin/bash", "-c", "./oss-find-source/bin/Debug/netcoreapp3.1/oss-find-source pkg:pypi/" + package_name]
    result = subprocess.run(command, stdout=subprocess.PIPE)
    url = result.stdout.decode('utf-8')
    logger.info(f"{url}")
