from gitingest import ingest, ingest_async

from config import Config
class GitIngestUtil:
    def __init__(self):
        self.max_file_size = 50 * 1024

    # async def ingest(self, repo_url):
    #     summary, tree, content = await ingest_async(repo_url, max_file_size=self.max_file_size)
    #     return summary, tree
    
    async def get_file_structure(self, repo_url) -> str:
        summary, tree, content = await ingest_async(repo_url, max_file_size=self.max_file_size)
        return tree
    
    async def get_file_structure_and_content(self, repo_url):
        """
        Parameters
        ----------
        repo_url : str
        
        Returns
        -------
        Tuple[summary: str, tree: str, content: str]
        """
        summary, tree, content = await ingest_async(repo_url, max_file_size=self.max_file_size)
        return summary, tree, content

git_ingest_util = GitIngestUtil()

# max_file_size = 50 * 1024 
# repo_url = 'https://github.com/mranish592/simple-drive'
# summary, tree, content = ingest(repo_url, max_file_size=max_file_size)
# print(summary)
# print(tree)
# print(content)

