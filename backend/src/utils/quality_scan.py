import subprocess
import os
import tempfile
import config
from core.models import FileQualityMetrics
import requests
from config import Config
from utils.local_git_util import local_git_util
from utils.github_util import github_util
import time

class QualityScan:
    def __init__(self):
        pass
    
    def analyze_commit_files(self, commit_hash, repo_path):
        """
        Analyzes commit files and waits for results to be available
        Returns:
            tuple: (success_status, error_message)
        """
        if Config.SONAR_CLOUD_TOKEN is not None and Config.SONAR_CLOUD_TOKEN != "":
            cmd = [
                "sonar-scanner",
                f'-Dsonar.projectKey=commit_{commit_hash}',
                f'-Dsonar.projectName=Commit Analysis {commit_hash}',
                f'-Dsonar.projectVersion=1.0',
                f'-Dsonar.sources={repo_path}',
                f'-Dsonar.organization={Config.SONAR_CLOUD_ORGANIZATION}',
                f'-Dsonar.token={Config.SONAR_CLOUD_TOKEN}',
                f'-Dsonar.login={Config.SONAR_CLOUD_TOKEN}',
            ]
        else:
            cmd = [
                "sonar-scanner",
                f'-Dsonar.projectKey=commit_{commit_hash}',
                f'-Dsonar.projectName=Commit Analysis {commit_hash}',
                f'-Dsonar.projectVersion=1.0',
                f'-Dsonar.sources={repo_path}',
                f'-Dsonar.host.url={Config.SONARQUBE_URL}',
                f'-Dsonar.token={Config.SONARQUBE_TOKEN}',
                f'-Dsonar.sourceEncoding=UTF-8',
                f'-Dsonar.scm.disabled=true',
            ]

        # Run SonarScanner
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            print(f"SonarQube scanner failed with exit code {result.returncode}")
            print(f"Error output:\n{result.stderr}")
            return None, result.stderr

        # Extract task ID from the output
        task_id = None
        for line in result.stdout.splitlines():
            if "INFO  More about the report processing at" in line:
                task_id = line.split("id=")[1].strip()
                print(f"Found task ID: {task_id}")
                break

        if not task_id:
            print("Could not find task ID in scanner output. Full output:")
            print(result.stdout)
            return None, "Could not find task ID in scanner output"

        # Wait for analysis to complete using CE API
        if not self._wait_for_task_completion(task_id):
            return None, "Analysis task did not complete successfully"

        return True, None

    def _wait_for_task_completion(self, task_id: str, max_retries: int = 5, delay: int = 1) -> bool:
        """
        Wait for analysis task to complete using CE API
        """
        headers = {
            "Authorization": f"Bearer {Config.SONAR_CLOUD_TOKEN if Config.SONAR_CLOUD_TOKEN else Config.SONARQUBE_TOKEN}"
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    f"{Config.SONARQUBE_URL}/api/ce/task",
                    params={"id": task_id},
                    headers=headers
                )
                
                if response.status_code == 200:
                    task_data = response.json()["task"]
                    status = task_data["status"]
                    
                    print(f"Analysis status: {status} (attempt {attempt + 1}/{max_retries})")
                    
                    if status == "SUCCESS":
                        return True
                    elif status in ["FAILED", "CANCELED"]:
                        print(f"Analysis failed with status: {status}")
                        return False
                    
                time.sleep(delay)
                
            except Exception as e:
                print(f"Error checking task status: {str(e)}")
                time.sleep(delay)
        
        return False

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
