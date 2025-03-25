import asyncio
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from config import Config
from utils.gitingest_util import git_ingest_util

class LangchainUtil: 
    def __init__(self):
        self.groq_api_key = Config.GROQ_API_KEY
        self.model = "llama3-70b-8192"
        self.chat = ChatGroq(groq_api_key=self.groq_api_key, temperature=0,  model_name=self.model)
        
    
    async def get_languages_and_frameworks(self, repo_url) -> tuple[list[str], list[str]]:
        system_prompt = """
            You are an expert in reviewing and understanding code. 
            You can identify languages and framworks used in a codebase.
            Based on the file structure and content, you can provide insights on the codebase.
            If you're not sure about the frame, don't mention it. Do not halucinate.
            You give out responses in a json format with two json arrays: languages and frameworks.
            Like below: 
            {{
                "languages": ["Python", "JavaScript"],
                "frameworks": ["Django", "React"]
            }}
        """
        input_prompt_base = """
        Based on the file strucutre and content, what languages and frameworks are used in this codebase?\n
        """
        human = "{text}"
        prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", human)])
        chain = prompt | self.chat
        file_structure = await git_ingest_util.get_file_structure(repo_url)
        input_prompt = input_prompt_base + file_structure
        response = await chain.ainvoke({"text" : input_prompt})
        response_json = json.loads(response.content)
        return response_json["languages"], response_json["frameworks"]

langchain_util = LangchainUtil()
repo_url = "https://github.com/mranish592/simple-drive"
response = asyncio.run(langchain_util.get_languages_and_frameworks(repo_url))
print(response)