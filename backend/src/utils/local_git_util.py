from config import Config
from core.models import CommitDetails, FileInfo
import git
import os
import shutil
from utils.logging_util import logging_util

EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

class LocalGitUtil:
    def __init__(self):
        self.logger = logging_util.get_logger(__name__)

    def get_commit_details(self, repo_path, commit_hash, commit_details: CommitDetails) -> CommitDetails | None:
        """
        Retrieves commit details including file changes.

        Args:
            repo_path (str): Path to the local Git repository.
            commit_hash (str): The commit hash to inspect.

        Returns:
            dict: A dictionary containing commit details.
        """
        
        try:
            repo = git.Repo(repo_path)
            commit = repo.commit(commit_hash)

            if len(commit.parents) > 0:
                parent_commit_sha = commit.parents[0].hexsha
            else:
                parent_commit_sha = EMPTY_TREE_SHA
            
            file_stats = {}
            numstat = repo.git.diff(parent_commit_sha, commit.hexsha, numstat=True)

            for line in numstat.strip().split('\n'):
                if line:
                    additions, deletions, file_path = line.split('\t')
                    # Convert to integers, handling special cases
                    additions = int(additions) if additions != '-' else 0
                    deletions = int(deletions) if deletions != '-' else 0
                    
                    file_stats[file_path] = {'additions': additions, 'deletions': deletions}

            # Print the stats for each file
            # for file_path, stats in file_stats.items():
            #     print(f"File: {file_path}")
            #     print(f"  Additions: {stats['additions']}")
            #     print(f"  Deletions: {stats['deletions']}")


            if(len(commit.parents) == 0):
                parent_commit = commit
                commit = None
            else:
                parent_commit = commit.parents[0]

            for diff in parent_commit.diff(commit):  # None means against the parent commit
                change_type = diff.change_type
                if change_type == "R":
                    continue
                # print(diff.change_type, diff.a_path, diff.b_path, diff.a_mode, diff.b_mode)
                additions = 0
                deletions = 0
                content = ""
                if diff.b_blob:
                        content = diff.b_blob.data_stream.read().decode('utf-8', errors='ignore')

                additions = file_stats[diff.b_path]['additions']
                deletions = file_stats[diff.b_path]['deletions']
                content = content
                line_count = content.count('\n')
                char_count = len(content)
                file_info = FileInfo(
                    file_path=diff.b_path, 
                    file_extension=diff.b_path.split('.')[-1], 
                    line_count=line_count, 
                    char_count=char_count, 
                    additions=additions, 
                    deletions=deletions, 
                    content=content)
                commit_details.files.update({diff.b_path: file_info})

            return commit_details

        except git.InvalidGitRepositoryError:
            self.logger.error(f"Error: Invalid Git repository at {repo_path}")
            return None
        except git.BadName:
            self.logger.error(f"Error: Invalid commit hash {commit_hash}")
            return None
        
    def clone_repo(self, repo_url) -> str | None:
        # --- START MODIFICATION ---
        # Check if the destination path exists
        base_dir = Config.BASE_DIR
        repo_path = repo_url.replace("https://github.com/", base_dir + "/")
        clone_url = repo_url + ".git"
        if os.path.exists(repo_path):
            self.logger.info(f"Directory '{repo_path}' already exists. Removing it...")
            try:
                # Use shutil.rmtree to remove the directory and all its contents
                shutil.rmtree(repo_path)
                self.logger.info(f"Successfully removed directory '{repo_path}'.")
            except OSError as e:
                # Handle potential errors during removal (e.g., permissions)
                self.logger.error(f"Error removing directory '{repo_path}': {e}")
                return None # Cannot proceed if removal fails
        # --- END MODIFICATION ---
        repo = git.Repo.clone_from(clone_url, repo_path)
        return repo_path

    def checkout_commit(self, repo_path, commit_hash):
        repo = git.Repo(repo_path)
        repo.git.checkout(commit_hash)
        return repo
    
    def delete_repo(self, repo_path):
        shutil.rmtree(repo_path)

local_git_util = LocalGitUtil()
# Example usage (assuming you have cloned the repo):
if __name__ == "__main__":
    # repo_path = "/Users/anish/projects/github-analyzer/backend/local_repo_dir/sample"  # Replace with your repo path
    base_dir = "/Users/anish/projects/github-analyzer/backend/local_repo_dir/base"
    commit_hash = "cc6010a948eb2dc8d227d21c6ad440e3f83c4017"  # Replace with the commit hash
    user_name = "mranish592"
    github_url = f"https://github.com/{user_name}/simple-drive.git"
    repo_path = github_url.replace("https://github.com/", base_dir + "/").replace(".git", "")

    # commit_data = local_git_util.get_commit_details(repo_path, commit_hash)
    # if commit_data:
    #     print(commit_data.id)
    #     print(commit_data.timestamp)
    #     print(commit_data.message)
    #     for file in commit_data.files:
    #         print(file.path)
    #         print(file.additions)
    #         print(file.deletions)
    #         if file.path == 'backend/simple-drive/src/main/kotlin/Config.kt':
                # print(file.content)
    repo = local_git_util.clone_repo("https://github.com/mranish592/simple-drive.git", repo_path)
    print(repo)
    repo = local_git_util.checkout_commit(repo_path, commit_hash)
    print(repo)
# if commit_data:

    # print(commit_data)