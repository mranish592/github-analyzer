from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

@dataclass
class ExperienceMetrics:
    lines_of_code: int
    first_commit_timestamp: datetime
    last_commit_timestamp: datetime
    repos: set[str]

@dataclass
class OverallExperienceMetrics:
    skills: dict[str, ExperienceMetrics]

@dataclass
class CommitExperienceMetrics:
    skills: set[str]
    lines_of_code: dict[str, int]
    timestamp: datetime
    repo_url: str

@dataclass
class QualityMetrics:
    bugs_per_commit: float | None
    code_smells_per_commit: float | None
    complexity_per_commit: float | None
    vulnerabilities_per_commit: float | None
    code_coverage: float | None
    duplicated_lines_density: float | None
    reliability_rating: str | None
    security_rating: str | None
    maintainability_rating: str | None

@dataclass
class OverallQualityMetrics:
    skills: dict[str, QualityMetrics]

@dataclass
class CommitQualityMetrics:
    timestamp: datetime
    skills: set[str]
    bugs: dict[str, int]
    code_smells: dict[str, int]
    complexity: dict[str, int]
    vulnerabilities: dict[str, int]
    coverage: dict[str, float]
    duplicated_lines_density: dict[str, float]
    reliability_rating: dict[str, float]
    security_rating: dict[str, float]
    maintainability_rating: dict[str, float]

@dataclass
class FileQualityMetrics:
    file_path: str
    bugs: int | None
    code_smells: int | None
    complexity: int | None
    vulnerabilities: int | None
    coverage: float | None
    duplicated_lines_density: float | None
    reliability_rating: float | None
    security_rating: float | None
    maintainability_rating: float | None
    

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
    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    commits: list[CommitDetails] = field(default_factory=list)

@dataclass
class User:
    username: str
    name: str
    repos: list[RepoDetails]

@dataclass
class AnalysisStatus:
    total_commits: int
    analyzed_commits: int
    analysis_completed: bool

class AnalyzeResponse(BaseModel):
    username: str = Field(..., title="Github username", description="The username of the github profile to analyze")
    name: str = Field(..., title="Name", description="The name of the github profile")
    message: str = Field(..., title="Message", description="Analysis of the github profile")
    experience_metrics: OverallExperienceMetrics | None = Field(None, title="Experience Metrics", description="The experience metrics of the github profile")
    quality_metrics: OverallQualityMetrics | None = Field(None, title="Quality Metrics", description="The quality metrics of the github profile")

class SubmitAnalysisResponse(BaseModel):
    username: str = Field(..., title="Github username", description="The username of the github profile to analyze")
    analysis_id: str = Field(..., title="Analysis ID", description="The id of the analysis")
    # total_commits: int = Field(..., title="Total commits", description="The total number of commits in the analysis")
    name: str = Field(..., title="Name", description="The name of the github profile")

class StatusResponse(BaseModel):
    analysis_id: str = Field(..., title="Analysis ID", description="The id of the analysis")
    status: AnalysisStatus = Field(..., title="Analysis status", description="The status of the analysis")