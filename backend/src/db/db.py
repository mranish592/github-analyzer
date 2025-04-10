from pymongo import MongoClient
from datetime import datetime
from typing import Optional, Dict, Any, List

from core.models import CommitExperienceMetrics, CommitQualityMetrics

class MongoDB:
    def __init__(self, connection_string: str, db_name: str):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        
        # Collections
        self.commit_experience_metrics = self.db["commit_experience_metrics"]
        self.commit_quality_metrics = self.db["commit_quality_metrics"]
    
    # Experience Metrics Functions
    def find_commit_experience_metrics(self, commit_hash: str, repo_url: str) -> Optional[CommitExperienceMetrics]:
        """Find commit experience metrics by commit hash and repo URL."""
        result = self.commit_experience_metrics.find_one({
            "commit_hash": commit_hash,
            "repo_url": repo_url
        })
        
        if not result:
            return None
            
        return CommitExperienceMetrics(
            lines_of_code=result["lines_of_code"],
            timestamp=result["timestamp"]
        )
    
    def save_commit_experience_metrics(self, 
                                      commit_hash: str, 
                                      repo_url: str, 
                                      metrics: CommitExperienceMetrics) -> str:
        """Save commit experience metrics. If exists, update it."""
        existing = self.commit_experience_metrics.find_one({
            "commit_hash": commit_hash,
            "repo_url": repo_url
        })
        
        data = {
            "commit_hash": commit_hash,
            "repo_url": repo_url,
            "lines_of_code": metrics.lines_of_code,
            "timestamp": metrics.timestamp,
            "updated_at": datetime.utcnow()
        }
        
        if existing:
            self.commit_experience_metrics.update_one(
                {"_id": existing["_id"]},
                {"$set": data}
            )
            return str(existing["_id"])
        else:
            data["created_at"] = datetime.utcnow()
            result = self.commit_experience_metrics.insert_one(data)
            return str(result.inserted_id)
    
    # Quality Metrics Functions
    def find_commit_quality_metrics(self, commit_hash: str, repo_url: str) -> Optional[CommitQualityMetrics]:
        """Find commit quality metrics by commit hash and repo URL."""
        result = self.commit_quality_metrics.find_one({
            "commit_hash": commit_hash,
            "repo_url": repo_url
        })
        
        if not result:
            return None
            
        return CommitQualityMetrics(
            timestamp=result["timestamp"],
            bugs=result["bugs"],
            code_smells=result["code_smells"],
            cognitive_complexity=result["cognitive_complexity"],
            complexity=result["complexity"],
            coverage=result["coverage"],
            ncloc=result["ncloc"],
            reliability_rating=result["reliability_rating"],
            security_rating=result["security_rating"],
            sqale_rating=result["sqale_rating"],
            duplicated_lines_density=result["duplicated_lines_density"],
            vulnerabilities=result["vulnerabilities"]
        )
    
    def save_commit_quality_metrics(self, 
                                   commit_hash: str, 
                                   repo_url: str, 
                                   metrics: CommitQualityMetrics) -> str:
        """Save commit quality metrics. If exists, update it."""
        existing = self.commit_quality_metrics.find_one({
            "commit_hash": commit_hash,
            "repo_url": repo_url
        })
        
        data = {
            "commit_hash": commit_hash,
            "repo_url": repo_url,
            "timestamp": metrics.timestamp,
            "bugs": metrics.bugs,
            "code_smells": metrics.code_smells,
            "cognitive_complexity": metrics.cognitive_complexity,
            "complexity": metrics.complexity,
            "coverage": metrics.coverage,
            "ncloc": metrics.ncloc,
            "reliability_rating": metrics.reliability_rating,
            "security_rating": metrics.security_rating,
            "sqale_rating": metrics.sqale_rating,
            "duplicated_lines_density": metrics.duplicated_lines_density,
            "vulnerabilities": metrics.vulnerabilities,
            "updated_at": datetime.utcnow()
        }
        
        if existing:
            self.commit_quality_metrics.update_one(
                {"_id": existing["_id"]},
                {"$set": data}
            )
            return str(existing["_id"])
        else:
            data["created_at"] = datetime.utcnow()
            result = self.commit_quality_metrics.insert_one(data)
            return str(result.inserted_id)
    
    # Additional helper functions
    def get_commit_metrics_by_date_range(self, 
                                        repo_url: str, 
                                        start_date: datetime, 
                                        end_date: datetime) -> Dict[str, List]:
        """Get both experience and quality metrics for commits in a date range."""
        experience_metrics = list(self.commit_experience_metrics.find({
            "repo_url": repo_url,
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }).sort("timestamp", 1))
        
        quality_metrics = list(self.commit_quality_metrics.find({
            "repo_url": repo_url,
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }).sort("timestamp", 1))
        
        return {
            "experience_metrics": experience_metrics,
            "quality_metrics": quality_metrics
        }
