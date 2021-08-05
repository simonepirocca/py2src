'''
This class collects metrics from a Github repository
'''

from dataclasses import dataclass


@dataclass
class GithubMetrics:
    url: str # Repo URL 

    def get_license() -> str:
        # Do something here
        return 

    def get_num_stars() -> int:
        # Do something here
        return

    def get_repo_ages_in_days() -> int:
        # Do something here
        return 

    def get_num_dependent_repos() -> int:
        # Do something here
        return

    def get_num_stargazers() -> int:
        # Do something here
        return

    def get_num_contributors() -> int:
        # Do something here
        return

    def get_num_open_issues() -> int:
        # Do something here
        return


