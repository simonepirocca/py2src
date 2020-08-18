## This file shows how to install and use the code extracting 

1. Install Python (>= 3.6.9) [Guide here](https://askubuntu.com/questions/865554/how-do-i-install-python-3-6-using-apt-get)
2. Install [Pipenv] (https://pipenv-fork.readthedocs.io/en/latest/install.html)
3. Install the dependencies
```console
foo@bar:~/research_project$ cd pypi_github/
foo@bar:~/research_project/pypi_github$ pipenv install
Installing dependencies from Pipfile.lock (XXX)…
[Progreesing bar here]
To activate this project's virtualenv, run pipenv shell.
Alternatively, run a command inside the virtualenv with pipenv run.
foo@bar:~/research_project/pypi_github$ pipenv shell
(pypi_github)foo@bar:~/research_project/pypi_github$ 
```
4. Run tests
```console
(pypi_github)foo@bar:~/research_project/pypi_github$ cd tests/
(pypi_github)foo@bar:~/research_project/pypi_github/tests$ pytest test_package_class.py
```
Results should be recored in the log.log file
```console
foo@bar:~/research_project/pypi_github/tests$ tail -f log.log
...
DEBUG:urllib3.connectionpool:https://github.com:443 "GET /urllib3/urllib3 HTTP/1.1" 200 None
INFO:root:Package: urllib3, Final url: https://github.com/urllib3/urllib3
```
