from collections import defaultdict
from core.models import Metrics, User
class ExtractMetrics:
    def __init__(self):
        pass
    
    async def extract(self, user: User) -> User: 
        print("Extracting metrics")
        for repo in user.repos:
            lines_of_code = defaultdict(int)
            for file in repo.parsed_files:
                lines_of_code[file.language] += file.line_count
            repo.metrics = Metrics(lines_of_code=lines_of_code)
            print("repo:", repo.url, "metrics:", repo.metrics)
        return user
        
extract_metrics = ExtractMetrics()        
        