from github import Github, Auth
from github.NamedUser import NamedUser
from github.AuthenticatedUser import AuthenticatedUser
import json

from typing import Union
from config import Config

class GithubUtil:
    def __init__(self):
        # using an access token
        self.auth = Auth.Token(Config.GITHUB_ACCESS_TOKEN)
        self.github = Github(auth=self.auth)
    
    def get_user(self, username: str):
        return self.github.get_user(username)
    
    def get_repositories_for_username(self, username: str):
        user = self.github.get_user(username)
        print(type(user))
        repos = user.get_repos()
        # Return a list of full names of repositories
        return [repo.full_name for repo in repos]

    def get_repositories_for_user(self, user: Union[NamedUser, AuthenticatedUser]):
        repos = user.get_repos()
        return [Config.GITHUB_REPO_BASE_URL + repo.full_name for repo in repos]

    def close(self):
        self.github.close()

github_util = GithubUtil()

# Example usage:
if __name__ == "__main__":
    github_util = GithubUtil()
    username = "torvalds"
    user = github_util.get_user(username)
    # user = Github(auth=github_util.auth).get_user()
    repos = github_util.get_repositories_for_user(user)
    print(repos)
    github_util.close()

    