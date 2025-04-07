from core.models import ExperienceMetrics, QualityMetrics
from utils.metrics_util import metrics_util
from utils.skills_util import skills_util
from utils.local_git_util import local_git_util
from utils.github_util import github_util


class AnalysisService:
    def __init__(self):
        pass

    def analyze(self, username: str) -> tuple[ExperienceMetrics, QualityMetrics]:
        repos= github_util.get_commits_for_user(username)
        print('len(repos)', len(repos))
        experience_metrics = {}
        quality_metrics = {}
        for repo in repos: 
            repo_path = local_git_util.clone_repo(repo.url)
            for commit in repo.commits:
                local_git_util.checkout_commit(repo_path, commit.hash)
                commit_details = local_git_util.get_commit_details(repo_path, commit.hash, commit)
                # print('\n\n',commit_details, '\n\n')
                commit_details = skills_util.identify_skills(commit_details)
                excluded_files = skills_util.identify_excluded_files(commit_details)
                commit_experience_metrics = metrics_util.get_experience_metrics(commit_details, excluded_files)
                experience_metrics.update({commit.hash: commit_experience_metrics})
                print('repo', repo.url, 'commit', commit.hash, 'lines_of_code', commit_experience_metrics.lines_of_code)
                commit_quality_metrics = metrics_util.get_quality_metrics(commit_details, excluded_files, repo_path)
                print('repo', repo.url, 'commit', commit.hash, commit_quality_metrics)
                quality_metrics.update({commit.hash: commit_quality_metrics})

            local_git_util.delete_repo(repo_path)

        overall_experience_metrics = metrics_util.get_overall_experience_metrics(experience_metrics)
        overall_quality_metrics = metrics_util.get_overall_quality_metrics(quality_metrics)
        return overall_experience_metrics, overall_quality_metrics

analysis_service = AnalysisService()

if __name__ == "__main__":
    experience_metrics, quality_metrics = analysis_service.analyze("mranish592")
    print(experience_metrics)
    print(quality_metrics)