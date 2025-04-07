from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

@dataclass
class ExperienceMetrics:
    lines_of_code: dict[str, int]
    first_commit_timestamp: dict[str, datetime]
    last_commit_timestamp: dict[str, datetime]

@dataclass
class CommitExperienceMetrics:
    lines_of_code: dict[str, int]
    timestamp: datetime

@dataclass
class QualityMetrics:
    bugs: dict[str, int]
    code_smells: dict[str, int]
    cognitive_complexity: dict[str, int]
    complexity: dict[str, float]
    coverage: dict[str, float]
    ncloc: dict[str, int]
    reliability_rating: dict[str, float]
    security_rating: dict[str, float]
    sqale_rating: dict[str, float]
    duplicated_lines_density: dict[str, float]
    vulnerabilities: dict[str, int]
    
@dataclass
class CommitQualityMetrics:
    timestamp: datetime
    bugs: dict[str, int]
    code_smells: dict[str, int]
    cognitive_complexity: dict[str, int]
    complexity: dict[str, float]
    coverage: dict[str, float]
    ncloc: dict[str, int]
    reliability_rating: dict[str, float]
    security_rating: dict[str, float]
    sqale_rating: dict[str, float]
    duplicated_lines_density: dict[str, float]
    vulnerabilities: dict[str, int]

@dataclass
class FileQualityMetrics:
    file_path: str
    bugs: int | None
    code_smells: int | None
    cognitive_complexity: int | None
    complexity: float | None
    coverage: float | None
    ncloc: int | None
    reliability_rating: float | None
    security_rating: float | None
    sqale_rating: float | None
    duplicated_lines_density: float | None
    vulnerabilities: int | None

@dataclass
class FileInfo:
    file_path: str
    file_extension: str
    line_count: int
    char_count: int
    additions: int
    deletions: int
    language: Optional[str] = None
    frameworks: Optional[list[str]] = None
    content: Optional[str] = None

@dataclass
class CommitDetails:
    hash: str
    message: str
    timestamp: datetime
    files: dict[str, FileInfo]
    repo_url: str

@dataclass
class RepoDetails:
    url: str
    name: str
    languages: list[str] = None
    frameworks: list[str] = None
    commits: list[CommitDetails] = None

@dataclass
class User:
    username: str
    name: str
    repos: list[RepoDetails]

class AnalyzeResponse(BaseModel):
    username: str = Field(..., title="Github username", description="The username of the github profile to analyze")
    name: str = Field(..., title="Name", description="The name of the github profile")
    message: str = Field(..., title="Message", description="Analysis of the github profile")
    experience_metrics: ExperienceMetrics = Field(..., title="Experience Metrics", description="The experience metrics of the github profile")
    quality_metrics: QualityMetrics = Field(..., title="Quality Metrics", description="The quality metrics of the github profile")

    