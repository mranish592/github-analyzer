from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel, Field

@dataclass
class Metrics:
    lines_of_code: dict[str, int]

@dataclass
class ParsedFile:
    file_name: str
    file_extension: str
    line_count: int
    char_count: int
    language: Optional[str] = None

@dataclass
class Repo:
    url: str
    file_structure: Optional[str] = None
    parsed_files: Optional[list[ParsedFile]] = None
    languages: Optional[list[str]] = None
    frameworks: Optional[list[str]] = None
    metrics: Optional[Metrics] = None
@dataclass
class User:
    username: str
    repos: list[Repo]

class AnalyzeResponse(BaseModel):
    username: str = Field(..., title="Github username", description="The username of the github profile to analyze")
    name: str = Field(..., title="Name", description="The name of the github profile")
    message: str = Field(..., title="Message", description="Analysis of the github profile")
    languages: list = Field(..., title="Languages", description="The languages of the github profile")
    frameworks: list = Field(..., title="Frameworks", description="The frameworks of the github profile")
    repos: list = Field(..., title="Repositories", description="The repositories of the github profile")
    metrics: Metrics = Field(..., title="Metrics", description="The metrics of the github profile")

    