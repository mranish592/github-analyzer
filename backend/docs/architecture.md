# Low Level Architecture

### Classes
```python
class User:
    username: str
    repos: List[Repo]
```

```python
class Repo:
    file_structure: str
    parsed_files: List[ParsedFile]
    langauges: List[str]
    framworks: List[str]
    Metrics: List[Metric]
```

```python
class Metric:
    lines_of_code: Dict[str, int]
```

### Services
1. Ingestion
2. SkillIdentification
3. ExtractMetrics
4. Scoring

### Utils
1. File Ingestor
2. File Parser
3. LLM Util

