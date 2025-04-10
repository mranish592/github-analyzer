from config import Config
from core.models import CommitDetails, CommitExperienceMetrics, CommitQualityMetrics, ExperienceMetrics, QualityMetrics
from utils.quality_scan import quality_scan
import datetime


class MetricsUtil:
    def __init__(self):
        pass

    def get_experience_metrics(self, commit_details: CommitDetails, exclude_files: list) -> CommitExperienceMetrics:
        commit_additions = 0
        experience_metrics = CommitExperienceMetrics(lines_of_code={}, timestamp=commit_details.timestamp)
        
        for file_path, file in commit_details.files.items():
            if file.file_path in exclude_files:
                continue
            file_additions = file.additions
            language = file.language
            frameworks = file.frameworks
            if(experience_metrics.lines_of_code.get(language, 0) == 0):
                experience_metrics.lines_of_code[language] = 0
            experience_metrics.lines_of_code[language] += file_additions
            if frameworks:
                for framework in frameworks:
                    if(experience_metrics.lines_of_code.get(framework, 0) == 0):
                        experience_metrics.lines_of_code[framework] = 0
                    experience_metrics.lines_of_code[framework] += file_additions
        return experience_metrics
    
    def get_quality_metrics(self, commit_details: CommitDetails, exclude_files: list, repo_path: str) -> CommitQualityMetrics:
        quality_metrics = {}
        analysis_result, error = quality_scan.analyze_commit_files(commit_details.hash, repo_path)
        if error:
            print(error)
            return quality_metrics
        # print(analysis_result)
        code_quality_per_file = quality_scan.get_quality_metrics_for_files(Config.BASE_DIR, commit_details.hash, [])
        # print('code_quality_per_file', code_quality_per_file)
        commit_quality_metrics = CommitQualityMetrics(
            timestamp=commit_details.timestamp,
            bugs={},
            code_smells={},
            cognitive_complexity={},
            complexity={},
            coverage={},
            ncloc={},
            reliability_rating={},
            security_rating={},
            sqale_rating={},
            duplicated_lines_density={},
            vulnerabilities={}
        )
        for file_quality_metrics in code_quality_per_file:
            file_info = commit_details.files.get(file_quality_metrics.file_path)
            if file_info is None:
            #     print('file_info is None', file_quality_metrics.file_path, commit_details.files)
                continue
            language = file_info.language
            frameworks = file_info.frameworks
            # all the metrics which is a float value, we need to take average of them. For all the metrics which is an int value, we need to take sum of them.
            
            if language not in commit_quality_metrics.bugs and file_quality_metrics.bugs is not None:
                commit_quality_metrics.bugs[language] = 0
            if language not in commit_quality_metrics.code_smells and file_quality_metrics.code_smells is not None:
                commit_quality_metrics.code_smells[language] = 0
            if language not in commit_quality_metrics.cognitive_complexity and file_quality_metrics.cognitive_complexity is not None:
                commit_quality_metrics.cognitive_complexity[language] = 0
            if language not in commit_quality_metrics.complexity and file_quality_metrics.complexity is not None:
                commit_quality_metrics.complexity[language] = 0.0
            if language not in commit_quality_metrics.coverage and file_quality_metrics.coverage is not None:
                commit_quality_metrics.coverage[language] = 0.0
            if language not in commit_quality_metrics.ncloc and file_quality_metrics.ncloc is not None:
                commit_quality_metrics.ncloc[language] = 0
            if language not in commit_quality_metrics.reliability_rating and file_quality_metrics.reliability_rating is not None:
                commit_quality_metrics.reliability_rating[language] = 0.0
            if language not in commit_quality_metrics.security_rating and file_quality_metrics.security_rating is not None:
                commit_quality_metrics.security_rating[language] = 0.0
            if language not in commit_quality_metrics.sqale_rating and file_quality_metrics.sqale_rating is not None:
                commit_quality_metrics.sqale_rating[language] = 0.0
            if language not in commit_quality_metrics.duplicated_lines_density and file_quality_metrics.duplicated_lines_density is not None:
                commit_quality_metrics.duplicated_lines_density[language] = 0.0
            if language not in commit_quality_metrics.vulnerabilities and file_quality_metrics.vulnerabilities is not None:
                commit_quality_metrics.vulnerabilities[language] = 0

            if file_quality_metrics.bugs is not None:
                commit_quality_metrics.bugs[language] += int(file_quality_metrics.bugs)
            if file_quality_metrics.code_smells is not None:
                commit_quality_metrics.code_smells[language] += int(file_quality_metrics.code_smells)
            if file_quality_metrics.complexity is not None:
                commit_quality_metrics.complexity[language] += float(file_quality_metrics.complexity)
            if file_quality_metrics.coverage is not None:
                commit_quality_metrics.coverage[language] += float(file_quality_metrics.coverage)
            if file_quality_metrics.ncloc is not None:
                commit_quality_metrics.ncloc[language] += int(file_quality_metrics.ncloc)
            if file_quality_metrics.reliability_rating is not None:
                commit_quality_metrics.reliability_rating[language] += float(file_quality_metrics.reliability_rating)
            if file_quality_metrics.security_rating is not None:
                commit_quality_metrics.security_rating[language] += float(file_quality_metrics.security_rating)
            if file_quality_metrics.sqale_rating is not None:
                commit_quality_metrics.sqale_rating[language] += float(file_quality_metrics.sqale_rating)
            if file_quality_metrics.duplicated_lines_density is not None:
                commit_quality_metrics.duplicated_lines_density[language] += float(file_quality_metrics.duplicated_lines_density)
            if file_quality_metrics.vulnerabilities is not None:
                commit_quality_metrics.vulnerabilities[language] += int(file_quality_metrics.vulnerabilities)
            
        return commit_quality_metrics

    def get_overall_experience_metrics(self, experience_metrics: dict[str, CommitExperienceMetrics]):
        overall_experience_metrics = ExperienceMetrics(lines_of_code={}, first_commit_timestamp={}, last_commit_timestamp={})
        print(len(experience_metrics))
        for commit_hash, commit_experience_metrics in experience_metrics.items():
            timestamp = commit_experience_metrics.timestamp
            
            # Convert to timezone-aware if it's naive
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
            
            for language, lines_of_code in commit_experience_metrics.lines_of_code.items():
                if language not in overall_experience_metrics.lines_of_code:
                    overall_experience_metrics.lines_of_code[language] = 0
                overall_experience_metrics.lines_of_code[language] += lines_of_code
                
                if language not in overall_experience_metrics.first_commit_timestamp:
                    overall_experience_metrics.first_commit_timestamp[language] = timestamp
                if language not in overall_experience_metrics.last_commit_timestamp:
                    overall_experience_metrics.last_commit_timestamp[language] = timestamp
                
                # Make sure stored timestamps are timezone-aware before comparing
                if overall_experience_metrics.first_commit_timestamp[language].tzinfo is None:
                    overall_experience_metrics.first_commit_timestamp[language] = overall_experience_metrics.first_commit_timestamp[language].replace(tzinfo=datetime.timezone.utc)
                if overall_experience_metrics.last_commit_timestamp[language].tzinfo is None:
                    overall_experience_metrics.last_commit_timestamp[language] = overall_experience_metrics.last_commit_timestamp[language].replace(tzinfo=datetime.timezone.utc)
                
                if timestamp < overall_experience_metrics.first_commit_timestamp[language]:
                    overall_experience_metrics.first_commit_timestamp[language] = timestamp
                if timestamp > overall_experience_metrics.last_commit_timestamp[language]:
                    overall_experience_metrics.last_commit_timestamp[language] = timestamp
        return overall_experience_metrics
    
    def get_overall_quality_metrics(self, quality_metrics: dict[str, CommitQualityMetrics]) -> QualityMetrics:
        overall_quality_metrics = QualityMetrics(
            bugs={},
            code_smells={},
            cognitive_complexity={},
            complexity={},
            coverage={},
            ncloc={},
            reliability_rating={},
            security_rating={},
            sqale_rating={},
            duplicated_lines_density={},
            vulnerabilities={}
        )
        for commit_hash, commit_quality_metrics in quality_metrics.items():
            for language, bugs in commit_quality_metrics.bugs.items():
                if language not in overall_quality_metrics.bugs and bugs is not None:
                    overall_quality_metrics.bugs[language] = 0
                if bugs is not None:
                    overall_quality_metrics.bugs[language] += bugs
            for language, code_smells in commit_quality_metrics.code_smells.items():
                if language not in overall_quality_metrics.code_smells and code_smells is not None:
                    overall_quality_metrics.code_smells[language] = 0
                if code_smells is not None:
                    overall_quality_metrics.code_smells[language] += code_smells
            for language, cognitive_complexity in commit_quality_metrics.cognitive_complexity.items():
                if language not in overall_quality_metrics.cognitive_complexity and cognitive_complexity is not None:
                    overall_quality_metrics.cognitive_complexity[language] = 0
                if cognitive_complexity is not None:
                    overall_quality_metrics.cognitive_complexity[language] += cognitive_complexity
            for language, complexity in commit_quality_metrics.complexity.items():
                if language not in overall_quality_metrics.complexity and complexity is not None:
                    overall_quality_metrics.complexity[language] = 0.0
                if complexity is not None:
                    overall_quality_metrics.complexity[language] += complexity
            for language, coverage in commit_quality_metrics.coverage.items():
                if language not in overall_quality_metrics.coverage and coverage is not None:
                    overall_quality_metrics.coverage[language] = 0.0
                if coverage is not None:
                    overall_quality_metrics.coverage[language] += coverage
            for language, ncloc in commit_quality_metrics.ncloc.items():
                if language not in overall_quality_metrics.ncloc and ncloc is not None:
                    overall_quality_metrics.ncloc[language] = 0
                if ncloc is not None:
                    overall_quality_metrics.ncloc[language] += ncloc
            for language, reliability_rating in commit_quality_metrics.reliability_rating.items():
                if language not in overall_quality_metrics.reliability_rating and reliability_rating is not None:
                    overall_quality_metrics.reliability_rating[language] = 0.0
                if reliability_rating is not None:
                    overall_quality_metrics.reliability_rating[language] += reliability_rating
            for language, security_rating in commit_quality_metrics.security_rating.items():
                if language not in overall_quality_metrics.security_rating and security_rating is not None:
                    overall_quality_metrics.security_rating[language] = 0.0
                if security_rating is not None:
                    overall_quality_metrics.security_rating[language] += security_rating
            for language, sqale_rating in commit_quality_metrics.sqale_rating.items():
                if language not in overall_quality_metrics.sqale_rating and sqale_rating is not None:
                    overall_quality_metrics.sqale_rating[language] = 0.0
                if sqale_rating is not None:
                    overall_quality_metrics.sqale_rating[language] += sqale_rating
            for language, duplicated_lines_density in commit_quality_metrics.duplicated_lines_density.items():
                if language not in overall_quality_metrics.duplicated_lines_density and duplicated_lines_density is not None:
                    overall_quality_metrics.duplicated_lines_density[language] = 0.0
                if duplicated_lines_density is not None:
                    overall_quality_metrics.duplicated_lines_density[language] += duplicated_lines_density
            for language, vulnerabilities in commit_quality_metrics.vulnerabilities.items():
                if language not in overall_quality_metrics.vulnerabilities and vulnerabilities is not None:
                    overall_quality_metrics.vulnerabilities[language] = 0
                if vulnerabilities is not None:
                    overall_quality_metrics.vulnerabilities[language] += vulnerabilities
        
        return overall_quality_metrics

metrics_util = MetricsUtil()