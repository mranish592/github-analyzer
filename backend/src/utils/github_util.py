from core.models import CommitDetails, FileInfo, RepoDetails, User
from github import Github, Auth
import github
from github.NamedUser import NamedUser
from github.AuthenticatedUser import AuthenticatedUser
import json
import base64

from typing import Union
from config import Config
from utils.logging_util import logging_util

class GithubUtil:
    def __init__(self):
        self.logger = logging_util.get_logger(__name__)
        # using an access token
        self.auth = Auth.Token(Config.GITHUB_ACCESS_TOKEN)
        self.github = Github(auth=self.auth)
    
    def get_user(self, username: str) -> Union[NamedUser, AuthenticatedUser, None]:
        if username is None:
            return None
        user =  self.github.get_user(username)
        if user is None:
            return None
        return user
    
    def get_repositories_for_username(self, username: str):
        user = self.github.get_user(username)
        repos = user.get_repos()
        return [Config.GITHUB_REPO_BASE_URL + repo.full_name for repo in repos]

    def get_repositories_for_user(self, user: User):
        if user is None or user.username is None:
            return []
            
        github_user = self.github.get_user(user.username)
        repos = github_user.get_repos()
        
        if github_user.name is not None:
            user.name = github_user.name
        return [Config.GITHUB_REPO_BASE_URL + repo.full_name for repo in repos]
    
    def print_rate_limit(self):
        rate_limit = self.github.get_rate_limit()
        self.logger.info(f"GitHub API rate limit: {rate_limit}")
    
   
    def get_commits_for_user(self, username: str) -> list[RepoDetails]:
        commits = self.github.search_commits(query=f"author:{username}")
        repos_details = dict[str, RepoDetails]()
        all_commits = list[CommitDetails]()
        # count = 0
        for commit in commits:
            # skip merge commits, merge commits have more than 1 parent
            if(len(commit._parents.value) > 1):
                # print('skipping merge commit', commit.sha, commit.commit.message, 'parents', commit._parents.value, len(commit._parents.value))
                continue
            # print(commit.commit.message, commit.repository.url, commit.sha)
            # if(commit.repository.full_name != "mranish592/simple-drive"):
                # continue
            # count += 1
            # if count > 3:
            #     break
            
            repo_detail = RepoDetails(
                url=Config.GITHUB_REPO_BASE_URL + commit.repository.full_name,
                name=commit.repository.name,
                languages=[],
                frameworks=[],
                commits=[]
            )
            repos_details.update({commit.repository.url: repo_detail})
            commit_details = CommitDetails(
                repo_url=commit.repository.url,
                hash=commit.sha,
                message=commit.commit.message,
                timestamp=commit.commit.author.date,
                files=dict[str, FileInfo]()
            )
            all_commits.append(commit_details)
        
        for commit in all_commits:
            repo_detail = repos_details[commit.repo_url]
            repo_detail.commits.append(commit)

        return list(repos_details.values())
        
    def close(self):
        self.github.close()
        
github_util = GithubUtil()

    