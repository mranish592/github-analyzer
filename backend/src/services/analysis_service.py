import uuid
import threading
from dataclasses import dataclass
from typing import Optional
from core.models import AnalysisStatus, CommitExperienceMetrics, ExperienceMetrics, OverallExperienceMetrics, OverallQualityMetrics, QualityMetrics
from db import db
from utils.framework_detector import framework_detector
from utils.metrics_util import metrics_util
from utils.skills_util import skills_util
from utils.local_git_util import local_git_util
from utils.github_util import github_util


@dataclass
class Submission:
    username: str
    name: str
    skip_quality_metrics: bool
    status: AnalysisStatus
    experience_metrics: Optional[ExperienceMetrics] = None
    quality_metrics: Optional[QualityMetrics] = None


class AnalysisService:
    def __init__(self):
        self.submissions = {}

    def submit_analysis(self, username: str, skip_quality_metrics: bool = False) -> tuple[str, str]:
        analysis_id = str(uuid.uuid4())
        print('submitting analysis for', username, 'with id', analysis_id)
        user = github_util.get_user(username)
        print('user', user)
        name = user.name if user.name is not None else username
        self.submissions[analysis_id] = Submission(
            username=username,
            name=name,
            skip_quality_metrics=skip_quality_metrics,
            status=AnalysisStatus(total_commits=0, analyzed_commits=0, analysis_completed=False)
        )
        
        # Start analysis in a separate thread
        thread = threading.Thread(
            target=self._run_analysis,
            args=(analysis_id, username, skip_quality_metrics)
        )
        thread.daemon = True
        thread.start()
        print('analysis submitted for', username, 'with id', analysis_id)
        return analysis_id, name
    
    def _run_analysis(self, analysis_id: str, username: str, skip_quality_metrics: bool):
        try:
            experience_metrics, quality_metrics = self.analyze(analysis_id, username, skip_quality_metrics)
            submission = self.submissions[analysis_id]
            submission.experience_metrics = experience_metrics
            submission.quality_metrics = quality_metrics
            submission.status.analysis_completed = True
        except Exception as e:
            print(f"Error analyzing {username}: {e}")
            # You might want to update status to indicate error
            self.submissions[analysis_id].status.analysis_completed = True
    
    def get_status(self, analysis_id: str) -> AnalysisStatus:
        return self.submissions[analysis_id].status
    
    def get_analysis(self, analysis_id: str):
        submission = self.submissions[analysis_id]
        return submission

    def analyze(self, analysis_id: str, username: str, skip_quality_metrics: bool = False) -> tuple[OverallExperienceMetrics | None, OverallQualityMetrics | None]:
        repos = github_util.get_commits_for_user(username)
        print('len(repos)', len(repos))
        
        # Update total commits count
        total_commits = sum(len(repo.commits) for repo in repos)
        self.submissions[analysis_id].status.total_commits = total_commits
        
        experience_metrics = {}
        quality_metrics = {}
        all_languages = set[str]()
        all_frameworks = set[str]()
        analyzed_commits = 0
        
        for repo in repos: 
            repo_path = local_git_util.clone_repo(repo.url)
            if repo_path is None:
                print('failed to clone repo', repo.url)
                continue
            for commit in repo.commits:
                analyzed_commits += 1
                self.submissions[analysis_id].status.analyzed_commits = analyzed_commits
                commit_experience_metrics = db.find_commit_experience_metrics(commit.hash)
                commit_quality_metrics = db.find_commit_quality_metrics(commit.hash)
                if commit_experience_metrics is not None and commit_quality_metrics is not None:
                    print('found exisiting metrics for commit', commit.hash)
                    print('repo', repo.url, 'commit', commit.hash, 'lines_of_code', commit_experience_metrics.lines_of_code)
                    print('repo', repo.url, 'commit', commit.hash, commit_quality_metrics)
                    experience_metrics.update({commit.hash: commit_experience_metrics})
                    quality_metrics.update({commit.hash: commit_quality_metrics})
                    continue
                
                local_git_util.checkout_commit(repo_path, commit.hash)
                commit_details = local_git_util.get_commit_details(repo_path, commit.hash, commit)
                if commit_details is None:
                    print('failed to get commit details for commit', commit.hash)
                    continue
                # print('\n\n',commit_details, '\n\n')
                commit_details, languages, frameworks = skills_util.identify_skills(commit_details)
                all_languages.update(languages)
                all_frameworks.update(frameworks)
                    
                if len(languages) == 0:
                    continue

                excluded_files = skills_util.identify_excluded_files(commit_details)
                # print('excluded_files', excluded_files)
                commit_experience_metrics = metrics_util.get_experience_metrics(commit_details, excluded_files)
                experience_metrics.update({commit.hash: commit_experience_metrics})
                db.save_commit_experience_metrics(repo.url, commit.hash, commit_experience_metrics)
                print('repo', repo.url, 'commit', commit.hash, 'lines_of_code', commit_experience_metrics.lines_of_code)
                if not skip_quality_metrics:
                    commit_quality_metrics = metrics_util.get_quality_metrics(commit_details, excluded_files, repo_path)
                    quality_metrics.update({commit.hash: commit_quality_metrics})
                    print('repo', repo.url, 'commit', commit.hash, commit_quality_metrics)
                    if commit_quality_metrics is not None:
                        db.save_commit_quality_metrics(repo.url, commit.hash, commit_quality_metrics)

            local_git_util.delete_repo(repo_path)

        overall_experience_metrics = metrics_util.get_overall_experience_metrics(experience_metrics)
        if not skip_quality_metrics:
            overall_quality_metrics = metrics_util.get_overall_quality_metrics(quality_metrics)
        else:
            overall_quality_metrics = None
        print('all_languages', all_languages)
        print('all_frameworks', all_frameworks)
        print('overall_experience_metrics', overall_experience_metrics)
        print('overall_quality_metrics', overall_quality_metrics)
        return overall_experience_metrics, overall_quality_metrics


analysis_service = AnalysisService()

if __name__ == "__main__":
    analysis_id, name = analysis_service.submit_analysis("mranish592", False)
    print(f"Analysis ID: {analysis_id}")
    print(f"Name: {name}")
    
    # Wait for analysis to complete
    import time
    while not analysis_service.get_status(analysis_id).analysis_completed:
        print("Waiting for analysis to complete...")
        time.sleep(5)
    
    # Get the results
    result = analysis_service.get_analysis(analysis_id)
    print("Experience metrics:", result.experience_metrics)
    print("Quality metrics:", result.quality_metrics)