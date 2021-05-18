# py2src: Automatic Identification of Source Code Repositories and Factors for Selecting New PyPI Packages

### Description
*py2src* is a Python based tool that can be used by developers for the selection of new PyPI libraries, as well as by normal users needing to download such packages. 

Starting from a package name, *py2src* first tries to retrieve the URL of the associated GitHub repository, looking at different sources present in the PyPI page, as well as exploiting the OSSGadget tool.

If a GitHub repository is found, it calculates a reliability score for the returned URL, going from -4 to 4.

Secondly, the tool goes through the GitHub repository looking at the adoption and popularity factors that developers suggest to be important while deciding to implement such dependency or not.

Finally, it also crawls the Snyk Database looking for vulnerabilities affecting such package, analysing average severity, type of release and time to release the fix of each vulnerability.

Information of packages are stored into an internal database, in order to reduce the time to return the information for already extracted packages. 

Whenever a given package is already stored, if is not outdated (data retrieved no more than 1 months ago), the tool returns directly the stored information, otherwise information about such package will be refreshed.

### Requirements
To run/test the entire project, the following tools are needed
* Linux 18.04 or higher
* Python (>= 3.6.9) [Guide here] (https://askubuntu.com/questions/865554/how-do-i-install-python-3-6-using-apt-get)
* [Pipenv] (https://pipenv-fork.readthedocs.io/en/latest/install.html) for dependency management
* OSSGadget [Docker image] (https://github.com/microsoft/OSSGadget/#docker-image), to ensure the complete functionality of the URL finder component

### Download and Installation
1. Clone the repository into the PATH_TO_TOOL directory
2. Set a valid GitHub Token in the beginning of *PATH_TO_TOOL/src/get_github_factors.py* file
3. Install the dependencies
```console
foo@bar:~/py2src$ pipenv install
Installing dependencies from Pipfile.lock (XXX)…
[Progreesing bar here]
To activate this project's virtualenv, run pipenv shell.
Alternatively, run a command inside the virtualenv with pipenv run.
foo@bar:~/py2src$ pipenv shell
(py2src)foo@bar:~/py2src$ 
```
4. Run tests
```console
(py2src)foo@bar:~/py2src$ cd tests
(py2src)foo@bar:~/py2src/tests$ pytest test_url_finder.py
(py2src)foo@bar:~/py2src/tests$ pytest test_factors.py
(py2src)foo@bar:~/py2src/tests$ pytest test_vulns.py
```

### Usage
1. Create the *PATH_TO_TOOL/inputs/packages.json* file containing the needed PyPI packages, following one of the two structurs described in the two examaple files. If packages are extracted directly from the [Top PyPI Packages] (https://hugovk.github.io/top-pypi-packages/) page, just change the name or select a subset of those packages, following the *example_1.json* file. Otherwise, if only the name of the packages are known, follow the *example_2.json* file
2. Launch the tool 
```console
foo@bar:~/py2src$ pipenv shell
(py2src)foo@bar:~/py2src$ cd scripts
(py2src)foo@bar:~/py2src/tests$ pytest py2src.py
```
5. Results will be stored in *PATH_TO_TOOL/logs/log.log* file. The process may require some minutes for each package, if not already stored in the database.
