from core.models import CommitDetails, FileInfo, RepoDetails, User
from github import Github, Auth
import github
from github.NamedUser import NamedUser
from github.AuthenticatedUser import AuthenticatedUser
import json
import base64

from typing import Union
from config import Config

class GithubUtil:
    def __init__(self):
        # using an access token
        self.auth = Auth.Token(Config.GITHUB_ACCESS_TOKEN)
        self.github = Github(auth=self.auth)
    
    def get_user(self, username: str) -> NamedUser:
        return self.github.get_user(username)
    
    def get_repositories_for_username(self, username: str):
        user = self.github.get_user(username)
        repos = user.get_repos()
        return [Config.GITHUB_REPO_BASE_URL + repo.full_name for repo in repos]

    def get_repositories_for_user(self, user: User):
        github_user = self.github.get_user(user.username)
        repos = github_user.get_repos()
        user.name = github_user.name
        return [Config.GITHUB_REPO_BASE_URL + repo.full_name for repo in repos]
    
    def print_rate_limit(self):
        print("rate_limit", self.github.get_rate_limit())
    
   
    def get_commits_for_user(self, username: str) -> list[RepoDetails]:
        commits = self.github.search_commits(query=f"author:{username}")
        repos_details = dict[str, RepoDetails]()
        all_commits = list[CommitDetails]()
        count = 0
        for commit in commits:
            # print(commit.commit.message, commit.repository.url, commit.sha)
            if(commit.repository.full_name != "mranish592/simple-drive"):
                continue
            count += 1
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
    def get_language(self, file_extension: str) -> str:
        language_mapping = {
            "py": "Python",
            "js": "JavaScript",
            "ts": "TypeScript",
            "java": "Java",
            "cpp": "C++",
            "html": "HTML",
            "css": "CSS",
            "kt": "Kotlin",
        }
        return language_mapping.get(file_extension, None)
github_util = GithubUtil()

# Example usage:
if __name__ == "__main__":
    github_util = GithubUtil()
    username = "mranish592"
    user = github_util.get_user(username)
    # user = Github(auth=github_util.auth).get_user()
    # github_util.print_rate_limit()
    # repos = github_util.get_repositories_for_username(username)
    github_util.print_rate_limit()
    # print(repos)

    # commits = github_util.get_user_commits(username)
    # for commit in commits:
    #     print("commit", commit.message)
    #     for file in commit.files:
    #         print("file :: path", file.path)
    #         print("file :: language", file.language)
    all_commits, repos = github_util.test(username)
    # print(all_commits)
    print(repos)
    print(len(repos))
    print(len(all_commits))
    github_util.print_rate_limit()
    github_util.close()

    