import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set
import os
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.import_detector import import_detector
from utils.logging_util import logging_util




@dataclass
class FileInfo:
    file_path: str
    file_extension: str
    line_count: int
    char_count: int
    additions: int
    deletions: int
    language: Optional[str] = None
    frameworks: Optional[list[str]] = None
    content: Optional[str] = None


class FileInfoFrameworkDetector:
    """
    Updates FileInfo objects with language and framework information
    based on file extension and content analysis.
    """
    
    # File extension to language mapping
    EXTENSION_TO_LANGUAGE = {
        # JavaScript/TypeScript
        "js": "JavaScript",
        "jsx": "JavaScript (React)",
        "ts": "TypeScript",
        "tsx": "TypeScript (React)",
        
        # Python
        "py": "Python",
        "pyi": "Python",
        "pyx": "Python (Cython)",
        
        # Go
        "go": "Go",
        
        # Rust
        "rs": "Rust",
        
        # Ruby
        "rb": "Ruby",
        "erb": "Ruby (ERB)",
        
        # PHP
        "php": "PHP",
        
        # Java
        "java": "Java",
        
        # Kotlin
        "kt": "Kotlin",
        "kts": "Kotlin",
        
        # C/C++
        "c": "C",
        "cpp": "C++",
        "cc": "C++",
        "h": "C/C++ Header",
        "hpp": "C++ Header",
        
        # C#
        "cs": "C#",
        
        # Swift
        "swift": "Swift",
        
        # HTML/CSS/Web
        "html": "HTML",
        "htm": "HTML",
        "css": "CSS",
        "scss": "SCSS",
        "sass": "Sass",
        "less": "Less",
        
        # Shell
        "sh": "Shell",
        "bash": "Bash",
        "zsh": "Zsh",
        
        # Dart
        "dart": "Dart",
        
        # Others
        "xml": "XML",
        "json": "JSON",
        "yaml": "YAML",
        "yml": "YAML",
        "md": "Markdown",
        "sql": "SQL",
        "r": "R",
        "pl": "Perl",
        "lua": "Lua",
        "ex": "Elixir",
        "exs": "Elixir",
        "erl": "Erlang",
        "scala": "Scala",
        "groovy": "Groovy",
        "clj": "Clojure",
        "fs": "F#",
    }
    
    # Import pattern regexes for different languages
    IMPORT_PATTERNS = {
        # JavaScript/TypeScript (.js, .jsx, .ts, .tsx)
        "JavaScript": [
            # ES6 imports
            r'import\s+(?:\*\s+as\s+\w+\s+from\s+|{\s*[^}]*\s*}\s+from\s+|[a-zA-Z0-9_$]+\s+from\s+)[\'"]([^\'"]+)[\'"]',
            # CommonJS require
            r'(?:const|let|var)\s+(?:\w+|\{[^}]*\})\s*=\s*require\([\'"]([^\'"]+)[\'"]\)',
            # Direct require
            r'require\([\'"]([^\'"]+)[\'"]\)'
        ],
        "TypeScript": [
            # Same as JavaScript
            r'import\s+(?:\*\s+as\s+\w+\s+from\s+|{\s*[^}]*\s*}\s+from\s+|[a-zA-Z0-9_$]+\s+from\s+)[\'"]([^\'"]+)[\'"]',
            r'(?:const|let|var)\s+(?:\w+|\{[^}]*\})\s*=\s*require\([\'"]([^\'"]+)[\'"]\)',
            r'require\([\'"]([^\'"]+)[\'"]\)'
        ],
        
        # Python (.py)
        "Python": [
            # Regular imports
            r'import\s+([a-zA-Z0-9_.]+)',
            # From imports
            r'from\s+([a-zA-Z0-9_.]+)\s+import'
        ],
        
        # Java (.java)
        "Java": [
            r'import\s+([^;]+);'
        ],
        
        # Kotlin (.kt)
        "Kotlin": [
            r'import\s+([^;]+)'
        ],
        
        # Go (.go)
        "Go": [
            r'import\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+\(\s*(?:[\'"][^\'"]+[\'"][\s\n]*)*\)'
        ],
        
        # Rust (.rs)
        "Rust": [
            r'use\s+([^;{]+)',
            r'extern\s+crate\s+([^;]+)'
        ],
        
        # PHP (.php)
        "PHP": [
            r'use\s+([^;]+);',
            r'namespace\s+([^;]+);',
            r'require(?:_once)?\s*\([\'"]([^\'"]+)[\'"]\)'
        ],
        
        # Ruby (.rb)
        "Ruby": [
            r'require\s+[\'"]([^\'"]+)[\'"]',
            r'require_relative\s+[\'"]([^\'"]+)[\'"]',
            r'include\s+([A-Z][a-zA-Z0-9:]*)'
        ],
        
        # Dart (.dart)
        "Dart": [
            r'import\s+[\'"]([^\'"]+)[\'"]\s*;'
        ],
        
        # C# (.cs)
        "C#": [
            r'using\s+([^;]+);'
        ]
    }
    
    # Framework-specific import patterns
    FRAMEWORK_IMPORTS = {
        # JavaScript/TypeScript
        "React": ["react", "react-dom", "react-router", "redux", "react-redux"],
        "Vue": ["vue", "vue-router", "vuex", "vuetify", "@vue/"],
        "Angular": ["@angular/", "angular", "ng-"],
        "Next.js": ["next", "next/router", "next/link", "next/image"],
        "Express": ["express", "express-session", "body-parser", "import express from 'express';", "express from"],
        "NestJS": ["@nestjs/"],
        "jQuery": ["jquery", "$"],
        "D3.js": ["d3"],
        "Three.js": ["three"],
        "Jest": ["jest", "@testing-library/"],
        
        # Python
        "Django": ["django", "django.db", "django.contrib", "django.urls"],
        "Flask": ["flask", "flask_", "flask."],
        "FastAPI": ["fastapi", "pydantic", "starlette"],
        "Pandas": ["pandas", "numpy"],
        "Pytest": ["pytest"],
        "SQLAlchemy": ["sqlalchemy"],
        "PyTorch": ["torch", "torchvision"],
        "TensorFlow": ["tensorflow", "tf."],
        "Streamlit": ["streamlit"],
        
        # Java
        "Spring": ["org.springframework", "springframework"],
        "Hibernate": ["org.hibernate", "javax.persistence", "jakarta.persistence"],
        "JUnit": ["org.junit", "junit."],
        "Mockito": ["org.mockito", "mockito"],
        
        # Go
        "Gin": ["github.com/gin-gonic/gin", "gin"],
        "Echo": ["github.com/labstack/echo", "echo"],
        "Fiber": ["github.com/gofiber/fiber", "fiber"],
        "GORM": ["gorm.io/gorm", "gorm"],
        "Cobra": ["github.com/spf13/cobra"],
        
        # Rust
        "Rocket": ["rocket", "rocket::"],
        "Actix": ["actix_web", "actix::"],
        "Tokio": ["tokio", "tokio::"],
        "Serde": ["serde", "serde_json"],
        "Axum": ["axum"],
        
        # PHP
        "Laravel": ["Illuminate\\", "Laravel\\"],
        "Symfony": ["Symfony\\", "symfony"],
        "WordPress": ["wp_", "WP_"],
        
        # Ruby
        "Rails": ["Rails", "ActiveRecord", "ActionController", "ActionView"],
        "Sinatra": ["Sinatra", "sinatra"],
        
        # C#
        "ASP.NET": ["Microsoft.AspNetCore", "System.Web"],
        "Entity Framework": ["Microsoft.EntityFrameworkCore", "System.Data.Entity"],
        "LINQ": ["System.Linq"],
        
        # Mobile/Flutter
        "Flutter": ["flutter", "material.dart", "widgets.dart"],
        "React Native": ["react-native", "ReactNative"],
        
        # Kotlin
        "Ktor": ["io.ktor", "ktor", "io.ktor.server", "io.ktor.server.plugins", "io.ktor.server.application.*"]

    }
    
    def __init__(self):
        """Initialize the framework detector with TF-IDF vectorizer."""
        self.logger = logging_util.get_logger(__name__)
        # Prepare corpus for TF-IDF
        self.framework_docs = {}
        
        # Create a document for each framework
        for framework, imports in self.FRAMEWORK_IMPORTS.items():
            self.framework_docs[framework] = " ".join(imports)
        
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(analyzer='word', 
                                         token_pattern=r'[a-zA-Z0-9_\-./]+',
                                         min_df=1)
        
        # Fit the vectorizer with framework documents
        corpus = list(self.framework_docs.values())
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        
        # Get framework names in the same order as the matrix
        self.framework_names = list(self.framework_docs.keys())
    
    def detect_language(self, file_info: FileInfo) -> str:
        """
        Determine the programming language based on file extension.
        
        Args:
            file_info: FileInfo object
            
        Returns:
            Detected language name
        """
        # Use file extension to determine language
        ext = file_info.file_extension.lower()
        
        # Handle special cases where the extension might not be enough
        if ext in [".js", ".jsx", ".ts", ".tsx"]:
            # Check for React in JSX/TSX files
            if ext in [".jsx", ".tsx"] or (file_info.content and 
                     ("import React" in file_info.content or 
                      "from 'react'" in file_info.content or 
                      'from "react"' in file_info.content)):
                if ext in [".ts", ".tsx"]:
                    return "TypeScript (React)"
                else:
                    return "JavaScript (React)"
            elif ext in [".ts", ".tsx"]:
                return "TypeScript"
            else:
                return "JavaScript"
        
        # For other languages, use the simple mapping
        return self.EXTENSION_TO_LANGUAGE.get(ext, "Unknown")
    
    def extract_imports(self, file_info: FileInfo) -> Set[str]:
        """
        Extract import statements from file content.
        
        Args:
            file_info: FileInfo object with content
            
        Returns:
            Set of imported module names
        """
        if not file_info.content:
            return set()
        
        imports = set()
        language = self.detect_language(file_info)
        
        # Get base language without framework specification
        base_language = language.split(" ")[0]  # e.g., "JavaScript (React)" -> "JavaScript"
        
        # Apply language-specific import patterns
        for pattern in self.IMPORT_PATTERNS.get(base_language, []):
            matches = re.findall(pattern, file_info.content)
            imports.update(matches)
        
        # Handle special case for multi-import Go files
        if base_language == "Go" and "import (" in file_info.content:
            # Extract imports between import ( and )
            import_blocks = re.findall(r'import\s+\((.*?)\)', file_info.content, re.DOTALL)
            for block in import_blocks:
                # Extract individual imports
                go_imports = re.findall(r'[\'"]([^\'"]+)[\'"]', block)
                imports.update(go_imports)
        
        return imports
    
    def detect_frameworks(self, file_info: FileInfo) -> List[str]:
        """
        Detect frameworks used in a file based on import statements.
        
        Args:
            file_info: FileInfo object
            
        Returns:
            List of detected frameworks
        """
        # print('detect_frameworks', file_info.file_path)
        if not file_info.content:
            return []
        
        # Extract imports from file content
        imports = import_detector.find_imports_for_language(file_info.content, file_info.language)

        if not imports:
            return []
        
        # Create a document from the imports
        import_doc = " ".join(imports)
        
        # Transform the import document to TF-IDF vector
        import_vector = self.vectorizer.transform([import_doc])
        
        # Calculate cosine similarity with each framework
        similarities = cosine_similarity(import_vector, self.tfidf_matrix)[0]
        
        # Get frameworks with similarity above threshold
        threshold = 0.1
        frameworks = [
            self.framework_names[i]
            for i in range(len(self.framework_names))
            if similarities[i] > threshold
        ]
        
        # Add special case detection based on file content patterns
        lang = self.detect_language(file_info)
        content = file_info.content.lower()
        
        # React detection for JS/TS files
        if "javascript" in lang.lower() or "typescript" in lang.lower():
            if "react" not in [f.lower() for f in frameworks]:
                if ("import react" in content or 
                    "from 'react'" in content or 
                    'from "react"' in content or
                    "react.component" in content or
                    "usestate" in content or 
                    "useeffect" in content):
                    frameworks.append("React")
        
        # Django detection for Python files
        if lang == "Python" and "Django" not in frameworks:
            if ("from django" in content or 
                "import django" in content or
                "models.model" in content or
                "class meta:" in content and "class" in content and "models." in content):
                frameworks.append("Django")
        
        return frameworks
    
    def process_file_info(self, file_info: FileInfo) -> FileInfo:
        """
        Process FileInfo object to detect language and frameworks.
        
        Args:
            file_info: FileInfo object to process
            
        Returns:
            Updated FileInfo object with language and frameworks fields
        """
        # Update language field
        # file_info.language = self.detect_language(file_info)
        
        # Update frameworks field
        file_info.frameworks = self.detect_frameworks(file_info)
        
        return file_info


# Example usage
def process_files(file_infos: List[FileInfo]) -> List[FileInfo]:
    """
    Process a list of FileInfo objects to detect languages and frameworks.
    
    Args:
        file_infos: List of FileInfo objects
        
    Returns:
        Updated list of FileInfo objects
    """
    detector = FileInfoFrameworkDetector()
    
    for file_info in file_infos:
        detector.process_file_info(file_info)
    
    return file_infos

framework_detector = FileInfoFrameworkDetector()

# Example of how to use this code
if __name__ == "__main__":
    # Create some example FileInfo objects
    files = [
        FileInfo(
            file_path="app.js",
            file_extension="js",
            line_count=100,
            char_count=3000,
            additions=50,
            deletions=10,
            content="""
                import React from 'react';
                import ReactDOM from 'react-dom';
                import { BrowserRouter } from 'react-router-dom';
                import App from './App';
                
                ReactDOM.render(
                  <BrowserRouter>
                    <App />
                  </BrowserRouter>,
                  document.getElementById('root')
                );
            """
        ),
        FileInfo(
            file_path="models.py",
            file_extension="py",
            line_count=200,
            char_count=5000,
            additions=100,
            deletions=20,
            content="""
                from django.db import models
                from django.contrib.auth.models import User
                
                class Product(models.Model):
                    name = models.CharField(max_length=100)
                    price = models.DecimalField(max_digits=10, decimal_places=2)
                    description = models.TextField()
                    created_at = models.DateTimeField(auto_now_add=True)
                    
                    def __str__(self):
                        return self.name
                    
                    class Meta:
                        ordering = ['-created_at']
            """
        ),
        FileInfo(
            file_path="server.go",
            file_extension="go",
            line_count=150,
            char_count=4000,
            additions=80,
            deletions=5,
            content="""
                package main
                
                import (
                    "github.com/gin-gonic/gin"
                    "net/http"
                    "database/sql"
                    _ "github.com/lib/pq"
                )
                
                func main() {
                    router := gin.Default()
                    
                    router.GET("/api/users", getUsers)
                    router.POST("/api/users", createUser)
                    
                    router.Run(":8080")
                }
                
                func getUsers(c *gin.Context) {
                    c.JSON(http.StatusOK, gin.H{
                        "message": "This is the users endpoint",
                    })
                }
            """
        )
    ]
    
    # Process the files
    processed_files = process_files(files)
    
    # Print results
    for file in processed_files:
        print(f"File: {file.file_path}")
        print(f"Language: {file.language}")
        print(f"Frameworks: {file.frameworks}")
        print("---")