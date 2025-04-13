from collections import defaultdict
from config import Config
from core.models import CommitDetails, CommitExperienceMetrics, CommitQualityMetrics, ExperienceMetrics, OverallExperienceMetrics, OverallQualityMetrics, QualityMetrics
from utils.quality_scan import quality_scan
import datetime
from utils.logging_util import logging_util


class MetricsUtil:
    def __init__(self):
        self.logger = logging_util.get_logger(__name__)
        pass

    def get_experience_metrics(self, commit_details: CommitDetails, exclude_files: list) -> CommitExperienceMetrics:
        commit_additions = 0
        experience_metrics = CommitExperienceMetrics(
            skills=set(), 
            lines_of_code={}, 
            timestamp=commit_details.timestamp, 
            repo_url=commit_details.repo_url
        )
        
        for file_path, file in commit_details.files.items():
            if file.file_path in exclude_files:
                continue
            file_additions = file.additions
            language = file.language
            if language is None or language == 'Unknown':
                continue
            skills = [language]
            frameworks = file.frameworks
            if frameworks:
                for framework in frameworks:
                    skills.append(framework)
            for skill in skills:
                if(experience_metrics.lines_of_code.get(skill, 0) == 0):
                    experience_metrics.lines_of_code[skill] = 0
                experience_metrics.lines_of_code[skill] += file_additions
                experience_metrics.skills.add(skill)
        return experience_metrics
    
    def get_quality_metrics(self, commit_details: CommitDetails, exclude_files: list, repo_path: str) -> CommitQualityMetrics | None:
        success, error = quality_scan.analyze_commit_files(commit_details.hash, repo_path)
        if error:
            self.logger.error(error)
            return None
        
        if not success:
            self.logger.info("Analysis failed or results not available")
            return None

        code_quality_per_file = quality_scan.get_quality_metrics_for_files(Config.BASE_DIR, commit_details.hash, [])
        
        commit_quality_metrics = CommitQualityMetrics(
            skills=set(),
            timestamp=commit_details.timestamp,
            bugs={},
            code_smells={},
            complexity={},
            coverage={},
            maintainability_rating={},
            reliability_rating={},
            security_rating={},
            duplicated_lines_density={},
            vulnerabilities={}
        )
        
        # Track file counts per language for calculating averages
        coverage_language_count = defaultdict(int)
        duplicated_lines_density_language_count = defaultdict(int)
        security_rating_language_count = defaultdict(int)
        reliability_rating_language_count = defaultdict(int)
        maintainability_rating_language_count = defaultdict(int)
        for file_quality_metrics in code_quality_per_file:
            file_info = commit_details.files.get(file_quality_metrics.file_path)
            if file_info is None:
            #     print('file_info is None', file_quality_metrics.file_path, commit_details.files)
                continue
            language = file_info.language
            if language is None or language == 'Unknown':
                continue
            
            skills = [language]
            frameworks = file_info.frameworks
            if frameworks:
                for framework in frameworks:
                    skills.append(framework)
            
            # Initialize metrics dictionaries
            for skill in skills:
                if skill not in commit_quality_metrics.bugs and file_quality_metrics.bugs is not None:
                    commit_quality_metrics.bugs[skill] = 0
                if skill not in commit_quality_metrics.code_smells and file_quality_metrics.code_smells is not None:
                    commit_quality_metrics.code_smells[skill] = 0
                if skill not in commit_quality_metrics.complexity and file_quality_metrics.complexity is not None:
                    commit_quality_metrics.complexity[skill] = 0
                if skill not in commit_quality_metrics.vulnerabilities and file_quality_metrics.vulnerabilities is not None:
                    commit_quality_metrics.vulnerabilities[skill] = 0
                if skill not in commit_quality_metrics.coverage and file_quality_metrics.coverage is not None:
                    commit_quality_metrics.coverage[skill] = 0.0
                if skill not in commit_quality_metrics.duplicated_lines_density and file_quality_metrics.duplicated_lines_density is not None:
                    commit_quality_metrics.duplicated_lines_density[skill] = 0.0
                if skill not in commit_quality_metrics.reliability_rating and file_quality_metrics.reliability_rating is not None:
                    commit_quality_metrics.reliability_rating[skill] = 0.0
                if skill not in commit_quality_metrics.security_rating and file_quality_metrics.security_rating is not None:
                    commit_quality_metrics.security_rating[skill] = 0.0
                if skill not in commit_quality_metrics.maintainability_rating and file_quality_metrics.maintainability_rating is not None:
                    commit_quality_metrics.maintainability_rating[skill] = 0.0
            
            
            # Sum metrics
            for skill in skills:
                if file_quality_metrics.bugs is not None:
                    commit_quality_metrics.bugs[skill] += int(file_quality_metrics.bugs)
                if file_quality_metrics.code_smells is not None:
                    commit_quality_metrics.code_smells[skill] += int(file_quality_metrics.code_smells)
                if file_quality_metrics.complexity is not None:
                    commit_quality_metrics.complexity[skill] += int(file_quality_metrics.complexity)
                if file_quality_metrics.vulnerabilities is not None:
                    commit_quality_metrics.vulnerabilities[skill] += int(file_quality_metrics.vulnerabilities)
                if file_quality_metrics.coverage is not None:
                    commit_quality_metrics.coverage[skill] += float(file_quality_metrics.coverage)
                    coverage_language_count[skill] += 1
                if file_quality_metrics.duplicated_lines_density is not None:
                    commit_quality_metrics.duplicated_lines_density[skill] += float(file_quality_metrics.duplicated_lines_density)
                    duplicated_lines_density_language_count[skill] += 1
            
                if file_quality_metrics.reliability_rating is not None:
                    commit_quality_metrics.reliability_rating[skill] += float(file_quality_metrics.reliability_rating)
                    reliability_rating_language_count[skill] += 1
                if file_quality_metrics.security_rating is not None:
                    commit_quality_metrics.security_rating[skill] += float(file_quality_metrics.security_rating)
                    security_rating_language_count[skill] += 1
                if file_quality_metrics.maintainability_rating is not None:
                    commit_quality_metrics.maintainability_rating[skill] += float(file_quality_metrics.maintainability_rating)
                    maintainability_rating_language_count[skill] += 1

        
        # Calculate averages for float metrics and round to 1 decimal place
        for skill in set(coverage_language_count.keys()) | set(reliability_rating_language_count.keys()) | set(security_rating_language_count.keys()) | set(maintainability_rating_language_count.keys()) | set(duplicated_lines_density_language_count.keys()):
            if skill in commit_quality_metrics.coverage and coverage_language_count[skill] > 0:
                commit_quality_metrics.coverage[skill] = round(commit_quality_metrics.coverage[skill] / coverage_language_count[skill], 1)
            if skill in commit_quality_metrics.reliability_rating and reliability_rating_language_count[skill] > 0:
                commit_quality_metrics.reliability_rating[skill] = round(commit_quality_metrics.reliability_rating[skill] / reliability_rating_language_count[skill], 1)
            if skill in commit_quality_metrics.security_rating and security_rating_language_count[skill] > 0:
                commit_quality_metrics.security_rating[skill] = round(commit_quality_metrics.security_rating[skill] / security_rating_language_count[skill], 1)
            if skill in commit_quality_metrics.maintainability_rating and maintainability_rating_language_count[skill] > 0:
                commit_quality_metrics.maintainability_rating[skill] = round(commit_quality_metrics.maintainability_rating[skill] / maintainability_rating_language_count[skill], 1)
            if skill in commit_quality_metrics.duplicated_lines_density and duplicated_lines_density_language_count[skill] > 0:
                commit_quality_metrics.duplicated_lines_density[skill] = round(commit_quality_metrics.duplicated_lines_density[skill] / duplicated_lines_density_language_count[skill], 1)

            commit_quality_metrics.timestamp = commit_details.timestamp
            commit_quality_metrics.skills.add(skill)
        
        return commit_quality_metrics

    def get_overall_experience_metrics(self, experience_metrics: dict[str, CommitExperienceMetrics]):
        overall_experience_metrics = OverallExperienceMetrics(skills={})
        for commit_hash, commit_experience_metrics in experience_metrics.items():
            timestamp = commit_experience_metrics.timestamp
            
            # Convert to timezone-aware if it's naive
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
            
            for skill, lines_of_code in commit_experience_metrics.lines_of_code.items():
                if skill is None:
                    continue 
                if skill not in overall_experience_metrics.skills:
                    overall_experience_metrics.skills[skill] = ExperienceMetrics(
                        lines_of_code=lines_of_code, 
                        first_commit_timestamp=timestamp, 
                        last_commit_timestamp=timestamp, 
                        repos=set([commit_experience_metrics.repo_url]))
                else:
                    overall_experience_metrics.skills[skill].lines_of_code += lines_of_code
                    overall_experience_metrics.skills[skill].repos.add(commit_experience_metrics.repo_url)
                    if timestamp < overall_experience_metrics.skills[skill].first_commit_timestamp:
                        overall_experience_metrics.skills[skill].first_commit_timestamp = timestamp
                    if timestamp > overall_experience_metrics.skills[skill].last_commit_timestamp:
                        overall_experience_metrics.skills[skill].last_commit_timestamp = timestamp
                
        return overall_experience_metrics
    
    def get_overall_quality_metrics(self, quality_metrics: dict[str, CommitQualityMetrics]) -> OverallQualityMetrics:
        overall_quality_metrics = OverallQualityMetrics(skills={})
        
        # Track metrics for calculating averages
        metrics_count = defaultdict(lambda: defaultdict(int))
        
        # First, collect all skills across all commits
        all_skills = set()
        for commit_hash, commit_quality_metrics in quality_metrics.items():
            all_skills.update(commit_quality_metrics.bugs.keys())
            all_skills.update(commit_quality_metrics.code_smells.keys())
            all_skills.update(commit_quality_metrics.complexity.keys())
            all_skills.update(commit_quality_metrics.vulnerabilities.keys())
            all_skills.update(commit_quality_metrics.coverage.keys())
            all_skills.update(commit_quality_metrics.duplicated_lines_density.keys())
            all_skills.update(commit_quality_metrics.reliability_rating.keys())
            all_skills.update(commit_quality_metrics.security_rating.keys())
            all_skills.update(commit_quality_metrics.maintainability_rating.keys())
        
        # Initialize all skills with None values
        for skill in all_skills:
            overall_quality_metrics.skills[skill] = QualityMetrics(
                bugs_per_commit=None,
                code_smells_per_commit=None,
                complexity_per_commit=None,
                vulnerabilities_per_commit=None,
                code_coverage=None,
                duplicated_lines_density=None,
                reliability_rating=None,
                security_rating=None,
                maintainability_rating=None
            )
        skill_bugs = defaultdict(int)
        skill_code_smells = defaultdict(int)
        skill_complexity = defaultdict(int)
        skill_vulnerabilities = defaultdict(int)
        skill_coverage = defaultdict(float)
        skill_duplicated_lines_density = defaultdict(float)
        skill_reliability_rating = defaultdict(float)
        skill_security_rating = defaultdict(float)
        skill_maintainability_rating = defaultdict(float)
        # Process each metric type separately
        total_commits = defaultdict(int)
        for commit_hash, commit_quality_metrics in quality_metrics.items():
            # Process bugs
            for skill in commit_quality_metrics.bugs.keys():
                skill_bugs[skill] += commit_quality_metrics.bugs[skill]
            for skill in commit_quality_metrics.code_smells.keys():
                skill_code_smells[skill] += commit_quality_metrics.code_smells[skill]
            for skill in commit_quality_metrics.complexity.keys():
                skill_complexity[skill] += commit_quality_metrics.complexity[skill]
            for skill in commit_quality_metrics.vulnerabilities.keys():
                skill_vulnerabilities[skill] += commit_quality_metrics.vulnerabilities[skill]
            for skill in commit_quality_metrics.coverage.keys():
                skill_coverage[skill] += commit_quality_metrics.coverage[skill]
            for skill in commit_quality_metrics.duplicated_lines_density.keys():
                skill_duplicated_lines_density[skill] += commit_quality_metrics.duplicated_lines_density[skill]
            for skill in commit_quality_metrics.reliability_rating.keys():
                skill_reliability_rating[skill] += commit_quality_metrics.reliability_rating[skill]
            for skill in commit_quality_metrics.security_rating.keys():
                skill_security_rating[skill] += commit_quality_metrics.security_rating[skill]
            for skill in commit_quality_metrics.maintainability_rating.keys():
                skill_maintainability_rating[skill] += commit_quality_metrics.maintainability_rating[skill]
            for skill in commit_quality_metrics.skills:
                total_commits[skill] += 1
        for skill in all_skills:
            if total_commits[skill] == 0:
                continue
            overall_quality_metrics.skills[skill].bugs_per_commit = round(skill_bugs[skill] / total_commits[skill], 1)
            overall_quality_metrics.skills[skill].code_smells_per_commit = round(skill_code_smells[skill] / total_commits[skill], 1)
            overall_quality_metrics.skills[skill].complexity_per_commit = round(skill_complexity[skill] / total_commits[skill], 1)
            overall_quality_metrics.skills[skill].vulnerabilities_per_commit = int(skill_vulnerabilities[skill] / total_commits[skill])
            overall_quality_metrics.skills[skill].code_coverage = round(skill_coverage[skill] / total_commits[skill], 1)
            overall_quality_metrics.skills[skill].duplicated_lines_density = round(skill_duplicated_lines_density[skill] / total_commits[skill], 1)
            overall_quality_metrics.skills[skill].reliability_rating = self._convert_rating_to_letter(skill_reliability_rating[skill] / total_commits[skill])
            overall_quality_metrics.skills[skill].security_rating = self._convert_rating_to_letter(skill_security_rating[skill] / total_commits[skill])
            overall_quality_metrics.skills[skill].maintainability_rating = self._convert_rating_to_letter(skill_maintainability_rating[skill] / total_commits[skill])
            
        return overall_quality_metrics

    def _convert_rating_to_letter(self, rating: float) -> str:
        """Convert a numeric rating (1-5) to a letter rating (A-E)"""
        if rating <= 1.5:
            return "A"
        elif rating <= 2.5:
            return "B"
        elif rating <= 3.5:
            return "C"
        elif rating <= 4.5:
            return "D"
        else:
            return "E"

metrics_util = MetricsUtil()