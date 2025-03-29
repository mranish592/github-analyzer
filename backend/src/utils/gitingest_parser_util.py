from dataclasses import dataclass
from typing import Optional
from utils.gitingest_util import git_ingest_util

import asyncio

@dataclass
class ParsedFile:
    file_name: str
    file_extension: str
    line_count: int
    char_count: int
    language: Optional[str] = None


class GitIngestParserUtil: 
    def __init__(self):
        pass
    

    def parse(self, input) -> list[ParsedFile]:
        files_split = input.lstrip().split("================================================\n")[1:]
        total_files = len(files_split) // 2
        files = []
        for index in range(total_files):
            file_name = files_split[index * 2].split("File: ")[1].strip()
            file_extension = file_name.split(".")[-1]
            file_content = files_split[index * 2 + 1]
            line_count = file_content.count("\n")
            char_count = len(file_content)
            language = extension_to_language.get(file_extension, None)
            files.append(ParsedFile(file_name, file_extension, line_count, char_count, language))
        return files


extension_to_language = {
    "py": "Python",
    "js": "JavaScript",
    "ts": "TypeScript",
    "java": "Java",
    "c": "C",
    "cpp": "C++",
    "h": "C++",
    "cs": "C#",
    "go": "Go",
    "rb": "Ruby",
    "php": "PHP",
    "swift": "Swift",
    "kt": "Kotlin",
    "kts": "Kotlin",
    "rs": "Rust",
    "scala": "Scala",
    "pl": "Perl",
    "lua": "Lua",
    "sh": "Shell",
    "bash": "Shell",
    "ps1": "PowerShell",
    "r": "R",
    "dart": "Dart",
    "m": "Objective-C",
    "jl": "Julia",
    "f90": "Fortran",
    "f95": "Fortran",
    "f03": "Fortran",
    "f08": "Fortran",
    "f": "Fortran",
    "hs": "Haskell",
    "erl": "Erlang",
    "ex": "Elixir",
    "exs": "Elixir",
    "clj": "Clojure",
    "scm": "Scheme",
    "lisp": "Lisp",
    "asm": "Assembly",
    "s": "Assembly",
    "vb": "Visual Basic",
    "vba": "Visual Basic for Applications",
    "sql": "SQL",
    "groovy": "Groovy",
    "nim": "Nim",
    "zig": "Zig",
    "coffee": "CoffeeScript",
    "tsx": "TypeScript",
    "jsx": "JavaScript",
    "vue": "Vue",
    "svelte": "Svelte",
    "ipynb": "Jupyter Notebook",
    "mjs": "JavaScript",
    "cjs": "JavaScript",
    "pyspark": "Python",
    "tcl": "Tcl",
    "ada": "Ada",
    "pas": "Pascal",
    "cob": "COBOL",
}

gitingest_parser_util = GitIngestParserUtil()

async def main():
    repo_url = "https://github.com/mranish592/simple-drive"
    summary, tree, content= await git_ingest_util.get_file_structure_and_content(repo_url)
    print("got content of size: ", len(content))
    # print(content)
    files = gitingest_parser_util.parse(content) 
    for file in files:
        print(file)

if __name__ == "__main__":
    asyncio.run(main())