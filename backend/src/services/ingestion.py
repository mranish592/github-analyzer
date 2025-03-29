from core.models import Repo, User
from utils.gitingest_parser_util import gitingest_parser_util
from utils.github_util import github_util
from utils.gitingest_util import git_ingest_util

class Ingestion:
    def __init__(self):
        pass
    
    async def ingest(self, username: str) -> User: 
        print("Ingesting")
        repo_urls = github_util.get_repositories_for_username(username)
        user = User(username=username, repos=[])
        count = 0
        for repo_url in repo_urls:
            summary, tree, content = await git_ingest_util.get_file_structure_and_content(repo_url)
            print("ingested", repo_url)
            repo = Repo(url=repo_url)
            repo.file_structure = tree
            repo.parsed_files = gitingest_parser_util.parse(content)
            user.repos.append(repo)
            print("parsed", repo_url, "count", count)
            count += 1
        return user
        print("Ingested")
    
ingestion = Ingestion()