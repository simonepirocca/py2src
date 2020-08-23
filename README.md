# research_project
Research project about the verification of factors that influence the usage of Python dependencies

## Metric description

### GitHub metrics (taken from https://docs.github.com/en/github/getting-started-with-github/github-glossary) 
- Stars (got using github api, see 'metrics_output/json/generic_data'): The number of GitHub users that displayed an appreciation for the repository. Stars are a manual way to rank the popularity of projects.
- Last commit (got using github api, see 'metrics_output/json/commits'): The date of the last commit
- Commit frequency (got from GitHub webpage using a crawler): The average number of commits per months
- Release frequency (got from GitHub webpage using a crawler): The average number days between two releases
- Open issues (got from GitHub webpage using a crawler): The total number of issues linked to the repository that are still open, thus not addressed yet.
- Closed issues (got from GitHub webpage using a crawler): The total number of issues linked to the repository that have been resolved.
- Average time to close an issue (got using github api, see 'metrics_output/json/closed_issues'): The average time elapsed between the creation of an issue and when it has been resolved.
- Contributors (got from GitHub webpage using a crawler): The number of GitHub users who don’t have collaborator access to a repository but have contributed to a project and had a pull request they opened merged into the repository.
- Dependent repositories (got from GitHub webpage using a crawler): A GitHub repository which have the current repo as dependency.
- Dependent packages (got from GitHub webpage using a crawler): A GitHub project which have the current repo as dependency

### Libraries.io metrics (taken from https://libraries.io/data and https://docs.libraries.io/overview.html) 
- SourceRank (got from Libraries.io webpage using a crawler): A score of the repository, from 0 to 30, based on code, community, distribution, documentation and usage.
- Dependent packages (got from Libraries.io webpage using a crawler): The number of packages that have the repository as dependency
- Dependent repositories (got from Libraries.io webpage using a crawler): The number of repositories that have the repository as dependency

### PyPi metrics
- Downloads (got from https://hugovk.github.io/top-pypi-packages/top-pypi-packages-365-days.json): the number of users that downloaded the repository from PyPi
