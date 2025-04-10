import subprocess
import os
import tempfile
import config
from core.models import FileQualityMetrics
import requests
from config import Config
from utils.local_git_util import local_git_util
from utils.github_util import github_util

class QualityScan:
    def __init__(self):
        pass
    
    def analyze_commit_files(self, commit_hash, repo_path):

        # Create a temp directory for the files
        if Config.SONAR_CLOUD_TOKEN is not None and Config.SONAR_CLOUD_TOKEN != "":
            cmd = [
                "sonar-scanner",
                f'-Dsonar.projectKey=commit_{commit_hash}',
                f'-Dsonar.projectName=Commit Analysis {commit_hash}',
                f'-Dsonar.projectVersion=1.0', # Identify analysis by commit
                f'-Dsonar.sources={repo_path}', # Scan current directory (the temp dir)
                f'-Dsonar.organization={Config.SONAR_CLOUD_ORGANIZATION}',
                f'-Dsonar.token={Config.SONAR_CLOUD_TOKEN}',
                f'-Dsonar.login={Config.SONAR_CLOUD_TOKEN}',
            ]
        else:
            cmd = [
                "sonar-scanner",
                f'-Dsonar.projectKey=commit_{commit_hash}',
                f'-Dsonar.projectName=Commit Analysis {commit_hash}',
                f'-Dsonar.projectVersion=1.0', # Identify analysis by commit
                f'-Dsonar.sources={repo_path}', # Scan current directory (the temp dir)
                f'-Dsonar.host.url={Config.SONARQUBE_URL}',
                f'-Dsonar.token={Config.SONARQUBE_TOKEN}',
                # f'-Dsonar.inclusions={inclusions}',
                f'-Dsonar.sourceEncoding=UTF-8',
                f'-Dsonar.scm.disabled=true' # Good practice for this workflow
            ]

        
        # Run SonarScanner
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        return result.stdout, result.stderr

    def get_quality_metrics_for_files(self, temp_repo_dir_path: str, commit_hash: str, excluded_files: list[str]) -> list[FileQualityMetrics]:
        # Get the quality metrics for the file
        url = f"{Config.SONARQUBE_URL}/api/measures/component_tree"
        metrics = [
            "bugs", "vulnerabilities", "code_smells",
            "reliability_rating", "security_rating", "sqale_rating",
            "coverage", "duplicated_lines_density","complexity" 
        ]

        params = {
            "component": f"commit_{commit_hash}",
            "metricKeys": ",".join(metrics),
            "qualifiers": "FIL",
            "strategy": "leaves",
            "ps": 500
        }
        headers = {}
        if Config.SONAR_CLOUD_TOKEN is not None and Config.SONAR_CLOUD_TOKEN != "":
            headers["Authorization"] = f"Bearer {Config.SONAR_CLOUD_TOKEN}"
        else:
            headers["Authorization"] = f"Bearer {Config.SONARQUBE_USER_TOKEN}"
        response = requests.get(url,  params=params, headers=headers)
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.text}")
        result = response.json()
        file_metrics = list[FileQualityMetrics]()
        
        for component in result.get("components", []):
            # Only process files (not directories)
            if component["qualifier"] != "FIL":
                continue
            # print(component)
            file_path = component["path"].replace(temp_repo_dir_path, "")
            if file_path in excluded_files:
                continue

            file_quality_metrics = FileQualityMetrics(file_path, None, None, None, None, None, None, None, None, None)
            # Extract metrics for this file
            for measure in component.get("measures", []):
                if measure["metric"] == "bugs":
                    file_quality_metrics.bugs = measure["value"]
                elif measure["metric"] == "vulnerabilities":
                    file_quality_metrics.vulnerabilities = measure["value"]
                elif measure["metric"] == "code_smells":
                    file_quality_metrics.code_smells = measure["value"]
                elif measure["metric"] == "duplicated_lines_density":
                    file_quality_metrics.duplicated_lines_density = measure["value"]
                elif measure["metric"] == "coverage":
                    file_quality_metrics.coverage = measure["value"]
                elif measure["metric"] == "sqale_rating":
                    file_quality_metrics.maintainability_rating = measure["value"]
                elif measure["metric"] == "reliability_rating":
                    file_quality_metrics.reliability_rating = measure["value"]
                elif measure["metric"] == "security_rating":
                    file_quality_metrics.security_rating = measure["value"]
                elif measure["metric"] == "complexity":
                    file_quality_metrics.complexity = measure["value"]
                                        
            file_metrics.append(file_quality_metrics)
            
        return file_metrics

quality_scan = QualityScan()
