import asyncio
import json
from time import sleep
from core.models import Repo

from langchain_text_splitters import Language
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.sequential import SequentialChain
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from utils.gitingest_parser_util import gitingest_parser_util
from utils.gitingest_util import git_ingest_util
from config import Config

class FileContent(BaseModel):
    """Represents the content of a file."""
    filename: str = Field(description="The name of the file.")
    content: str = Field(description="The full content of the file.")

class FileList(BaseModel):
            files: list[str] = Field(description="List of file paths")

class LanguageFrameworkOutput(BaseModel):
    """Represents the identified languages and frameworks."""
    languages: list[str] = Field(description="List of programming languages used.")
    frameworks: list[str] = Field(description="List of frameworks used.")


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
        file_structure_prompt = PromptTemplate(
            input_variables=["file_structure"],
            template="""Given the following file structure: {file_structure}. 
            Please identify the files most critical for determining the languages and frameworks used in the project.
            Limit the number of files to 2. Do not ask for files which might be very large.
            Return a JSON object with a "files" key containing an array of filenames relative to the base directory. Do not include any explanation.
            """,
        )
        # Example format: {{"files": ["path/to/file1", "path/to/file2"]}}
        file_content_parser = PydanticOutputParser(pydantic_object=FileList)
        file_content_chain = file_structure_prompt | self.chat | file_content_parser
        language_framework_prompt = PromptTemplate(
            input_variables=["file_contents"],
            template="""Given the following file contents:
            {file_contents} 
            and file structure: 
            {file_structure}
            Identify the programming languages, frameworks. Output the languages, frameworks in a structured format.
            Include all major development frameworks, Do not include build frameworks, only include major frameworks. 
            {format_instructions}
            """,
            partial_variables={"format_instructions": PydanticOutputParser(pydantic_object=LanguageFrameworkOutput).get_format_instructions()},
        )

        language_framework_parser = PydanticOutputParser(pydantic_object=LanguageFrameworkOutput)
        language_framework_chain = language_framework_prompt | self.chat | language_framework_parser

        file_structure: str | None = repo.file_structure
        # print("file_structure", file_structure)        
        file_list = file_content_chain.invoke({"file_structure": file_structure})
        # print("file_list", file_list)
        # print("Available files:", list(repo.parsed_files.keys()))

        file_contents = []
        for file_name in file_list.files:
            file = repo.parsed_files.get(file_name)
            if file is None:
                continue
            # Limit to first 2500 characters per file
            file_content = file.content[:1000] + "..." if len(file.content) > 1000 else file.content
            file_contents.append(f"fileName:{file_name}\nfileContent:\n{file_content}")
        languages_frameworks = language_framework_chain.invoke({"file_contents": file_contents, "file_structure": file_structure})
        print("repo", repo.url, "languages_frameworks", languages_frameworks)
        return [languages_frameworks.languages, languages_frameworks.frameworks]

langchain_util = LangchainUtil()
# async def main():
#     repo_url = "https://github.com/mranish592/simple-drive"
#     summary, tree, content = await git_ingest_util.get_file_structure_and_content(repo_url)
#     print("ingested", repo_url)
#     repo = Repo(url=repo_url)
#     repo.file_structure = tree
#     repo.parsed_files = gitingest_parser_util.parse(content)
#     langchain_util = LangchainUtil()
#     response = await langchain_util.get_languages_and_frameworks(repo)
#     print(response)

# asyncio.run(main())