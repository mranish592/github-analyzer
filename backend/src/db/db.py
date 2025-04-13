from pymongo import MongoClient
from datetime import datetime
from typing import Optional, Dict, Any, List
from src.utils.logging_util import logging_util

from core.models import CommitExperienceMetrics, CommitQualityMetrics

class MongoDB:
    def __init__(self, connection_string: str, db_name: str):
        self.logger = logging_util.get_logger(__name__)
        self.logger.info(f"Initializing MongoDB connection to database: {db_name}")
        
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        
        # Collections
        self.commit_experience_metrics = self.db["commit_experience_metrics"]
        self.commit_quality_metrics = self.db["commit_quality_metrics"]
        
        # Create indexes
        self.logger.info("Creating indexes for collections")
        self.commit_experience_metrics.create_index("commit_hash")
        self.commit_quality_metrics.create_index("commit_hash")
    
    # Experience Metrics Functions
    def find_commit_experience_metrics(self, commit_hash: str) -> Optional[CommitExperienceMetrics]:
        """Find commit experience metrics by commit hash."""
        self.logger.debug(f"Finding experience metrics for commit: {commit_hash}")
        result = self.commit_experience_metrics.find_one({
            "commit_hash": commit_hash
        })
        
        if not result:
            self.logger.debug(f"No experience metrics found for commit: {commit_hash}")
            return None
            
        return CommitExperienceMetrics(
            skills=set(result.get("skills", [])),
            lines_of_code=result.get("lines_of_code", {}),
            timestamp=result["timestamp"],
            repo_url=result["repo_url"]
        )
    
    def save_commit_experience_metrics(self, 
                                      repo_url: str, 
                                      commit_hash: str, 
                                      metrics: CommitExperienceMetrics) -> str:
        """Save commit experience metrics. If exists, update it."""
        existing = self.commit_experience_metrics.find_one({
            "commit_hash": commit_hash
        })
        
        data = {
            "commit_hash": commit_hash,
            "repo_url": repo_url,
            "skills": list(metrics.skills),  # Convert set to list for MongoDB
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
    def find_commit_quality_metrics(self, commit_hash: str) -> Optional[CommitQualityMetrics]:
        """Find commit quality metrics by commit hash."""
        result = self.commit_quality_metrics.find_one({
            "commit_hash": commit_hash
        })
        
        if not result:
            return None
            
        return CommitQualityMetrics(
            timestamp=result["timestamp"],
            skills=set(result.get("skills", [])),
            bugs=result.get("bugs", {}),
            code_smells=result.get("code_smells", {}),
            complexity=result.get("complexity", {}),
            vulnerabilities=result.get("vulnerabilities", {}),
            coverage=result.get("coverage", {}),
            duplicated_lines_density=result.get("duplicated_lines_density", {}),
            reliability_rating=result.get("reliability_rating", {}),
            security_rating=result.get("security_rating", {}),
            maintainability_rating=result.get("maintainability_rating", {})
        )
    
    def save_commit_quality_metrics(self, 
                                   repo_url: str, 
                                   commit_hash: str, 
                                   metrics: CommitQualityMetrics) -> str:
        """Save commit quality metrics. If exists, update it."""
        existing = self.commit_quality_metrics.find_one({
            "commit_hash": commit_hash
        })
        
        data = {
            "commit_hash": commit_hash,
            "repo_url": repo_url,
            "timestamp": metrics.timestamp,
            "skills": list(metrics.skills),  # Convert set to list for MongoDB
            "bugs": metrics.bugs,
            "code_smells": metrics.code_smells,
            "complexity": metrics.complexity,
            "vulnerabilities": metrics.vulnerabilities,
            "coverage": metrics.coverage,
            "duplicated_lines_density": metrics.duplicated_lines_density,
            "reliability_rating": metrics.reliability_rating,
            "security_rating": metrics.security_rating,
            "maintainability_rating": metrics.maintainability_rating,
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
