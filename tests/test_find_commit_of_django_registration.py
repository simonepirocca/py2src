from git import Repo 
import logging
import sys
from pathlib import Path
from tempfile import mkdtemp

utils_module_path = Path().resolve().parent / "src" / "utils"
sys.path.append(str(utils_module_path))
from utils import log_function_output
logger = log_function_output(file_level=logging.DEBUG, console_level=logging.DEBUG, log_filename="../logs/find_commits.log")


def test_find_commit_in_repo_find_online_but_not_local():
    # Specifying the Github repository url
    github_repo_url = "https://github.com/macropin/django-registration"

    # Commit id
    commit_id = "3a2e0182ff92cc8ce39a932e463cbac37e485afa"

    # Clone a directory into a temp directory; the directory is the input to the Repo class
    local_clone_dir = mkdtemp()
    repo = Repo.clone_from(github_repo_url, local_clone_dir)

    # Obtain the list of commits from the repository
    commits = (repo.iter_commits())
    commit_ids = [commit.hexsha for commit in commits]

    logger.info("Found commit {}".format(commit_id))
    assert commit_id in commit_ids
