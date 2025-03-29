from collections import defaultdict
import re
from core.models import Metrics, User, AnalyzeResponse

class ScoringEngine:
    def __init__(self):
        pass
    
    async def score(self, user: User) -> AnalyzeResponse: 
        print("Scoring")
        total_lines_of_code = defaultdict(int)
        languages = set()
        frameworks = set()
        for repo in user.repos:
            languages.update(repo.languages)
            frameworks.update(repo.frameworks)
            print("repo:", repo.url, "languages:", repo.languages, "frameworks:", repo.frameworks)
            for skill in repo.metrics.lines_of_code.keys():
                print("skill:", skill, "code:", repo.metrics.lines_of_code[skill])
                total_lines_of_code[skill] += repo.metrics.lines_of_code[skill]
        print("total_lines_of_code", total_lines_of_code)
        return AnalyzeResponse(
            username=user.username, 
            name="asdf", 
            repos= [repo.url for repo in user.repos], 
            languages=list(languages),
            frameworks=list(frameworks),
            message=f"Hello, {user.username}!, you have {len(user.repos)} public repos",
            metrics=Metrics(lines_of_code=total_lines_of_code)
        )

scoring_engine = ScoringEngine()