from core.models import User
from utils.langchain_util import langchain_util

class IdentifySkills:
    def __init__(self):
        pass
    
    async def identify(self, user: User) -> User:
        print("Identifying skills") 
        for repo in user.repos:
            [languages, frameworks] = await langchain_util.get_languages_and_frameworks(repo)
            repo.languages = languages
            repo.frameworks = frameworks
        return user
        
identify_skills = IdentifySkills()