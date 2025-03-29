import asyncio
import json
from core.models import Repo
from langchain_text_splitters import Language
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from config import Config

class FileStructureAnalysis(BaseModel):
    languages: list[str] = Field(..., title="Languages", description="The languages of the codebase")
    frameworks: list[str] = Field(..., title="Frameworks", description="The frameworks of the codebase")
    files_required: list[str] = Field(..., title="Files Required", description="The files required for further analysis")


class LangchainUtil: 
    def __init__(self):
        self.groq_api_key = Config.GROQ_API_KEY
        self.model = "qwen-2.5-coder-32b"
        self.chat = ChatGroq(groq_api_key=self.groq_api_key, temperature=0,  model_name=self.model)
        self.output_parser = PydanticOutputParser(pydantic_object=FileStructureAnalysis)        
    
    async def get_languages_and_frameworks(self, repo: Repo) -> tuple[list[str], list[str]]:
        system_prompt = """
            Based on the file structure and content, provide insights on the codebase.
            If you're not sure about the framework, don't mention it. Do not halucinate.
            If you require more files in order to correctly identify the framworks and languages, please mention the files required with their full path.
            Always ask for additional files, as they are needed more often than not. Limiting the number of files you ask for to 5.
            Make sure you ask for enough files to be sure.
            You give out responses in a json format with two json arrays: languages, frameworks and files_required.
            Like below: 
            {{
                "languages": ["Python", "JavaScript"],
                "frameworks": ["Django", "React"],
                "files_required": ["backend/requirements.txt", "frontend/packange.json"]
            }}
        """
        input_prompt_base = """
        Based on the file structure and content, what languages and frameworks are used in this codebase?
        Tell me any files you reuqire further for analysis.\n\n
        """
        human = "{text}"
        prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", human)])
        chain = prompt | self.chat
        file_structure = repo.file_structure
        input_prompt = input_prompt_base + file_structure
        response = await chain.ainvoke({"text" : input_prompt})
        print(response)
        response_json = json.loads(response.content)
        languages = response_json["languages"]
        frameworks = response_json["frameworks"]
        files_required = response_json["files_required"]
        print("LangchainUtil :: Languages: ", languages, "Frameworks: ", frameworks, "Files Required: ", files_required)
        return (response_json["languages"], response_json["frameworks"])

langchain_util = LangchainUtil()
# repo_url = "https://github.com/mranish592/simple-drive"
# response = asyncio.run(langchain_util.get_languages_and_frameworks(repo_url))
# print(response)