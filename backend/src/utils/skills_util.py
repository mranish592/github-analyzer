from core.models import CommitDetails, FileInfo
from utils.framework_detector import framework_detector

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

class SkillsUtil:
    def __init__(self):
        pass

    def identify_language(self, file: FileInfo) -> str | None:
        extension = file.file_extension
        return extension_to_language.get(extension.lower(), "Unknown")
    
    def identify_skills(self, commit_details: CommitDetails) -> tuple[CommitDetails, list[str], list[str]]:
        languages = set[str]()
        frameworks = set[str]()
        for file_path, file in commit_details.files.items():
            file.language = self.identify_language(file)
            if file.language is not None and file.language != "Unknown":
                languages.add(file.language)
        

        for file in commit_details.files.values():
            detected_frameworks = framework_detector.process_file_info(file).frameworks
            if len(detected_frameworks) > 0:
                # print('commit', commit_details.hash, 'file', file.file_path, 'detected_frameworks', detected_frameworks)
                frameworks.update(detected_frameworks)
                file.frameworks = detected_frameworks

        return commit_details, list(languages), list(frameworks)
    
    def identify_excluded_files(self, commit_details: CommitDetails) -> list[FileInfo]:
        return [file for _, file in commit_details.files.items() if file.language is None]
        # return [file for file in commit_details.files if file.language is None]


skills_util = SkillsUtil()
__all__ = ["skills_util"]