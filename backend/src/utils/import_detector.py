import logging # Optional: for logging parsing issues

# --- Keyword Definitions (Required for the specified language) ---
# Define keywords that typically start an import/dependency line
# Using tuples: (keyword_to_check, extraction_method_hint)
# More specific prefixes should come first in the list for a language.
IMPORT_START_KEYWORDS = {
    "Python": [
        ('from ', 'python_from'), # 'from module import ...'
        ('import ', 'python_import'), # 'import module'
    ],
    "Java": [
        ('import ', 'java_style'), # 'import package.name;'
    ],
    "Kotlin": [
        ('import ', 'kotlin_style'), # 'import package.name' (no semicolon needed)
    ],
    "JavaScript": [
        ('import ', 'js_import'), # 'import ... from 'module'' or 'import 'module''
        ('require(', 'js_require'), # E.g., const x = require('module')
    ],
    "TypeScript": [ # Often similar to JavaScript for basic imports
        ('import ', 'js_import'),
        ('require(', 'js_require'),
    ],
    "Go": [
        ('import "', 'go_quoted'), # Only handles single 'import "path"'
        # Note: Go's multi-line `import (...)` blocks are harder without more context/parsing
    ],
    "Rust": [
        ('use ', 'rust_use'), # 'use path::to::item;' or 'use path::{...};'
        ('extern crate ', 'rust_extern_crate'), # 'extern crate crate_name;'
    ],
    "PHP": [
        ('use ', 'php_use'), # 'use Namespace\Class;'
        ('require_once(', 'php_require'),
        ('require(', 'php_require'),
    ],
    "Ruby": [
        ('require_relative ', 'ruby_require'), # 'require_relative 'path''
        ('require ', 'ruby_require'), # 'require 'gem_name''
        ('include ', 'ruby_include'), # 'include ModuleName'
    ],
    "Dart": [
        ('import ', 'dart_import'), # 'import 'package:path/path.dart';'
    ],
    "C#": [
        ('using ', 'csharp_using'), # 'using Namespace;'
    ]
    # Add other languages or refine patterns as needed
}

class ImportDetector:
    # --- Helper Function for Name Extraction ---
    def __init__(self):
        pass

    def _extract_module_name(self, line, keyword, method):
        """
        Helper function to extract the module name based on the language convention.
        This is a simplified parser, may not cover all edge cases.
        (Implementation details are the same as the previous answer)
        """
        try:
            payload = line[len(keyword):].strip()
            if not payload: return None

            # Python
            if method == 'python_from':
                parts = payload.split()
                if parts: return parts[0].split('.')[0]
            elif method == 'python_import':
                parts = payload.split()
                if parts: return parts[0].split(',')[0].strip().split('.')[0]
            # Java / C#
            elif method == 'java_style' or method == 'csharp_using':
                return payload.split(';')[0].strip()
            # Kotlin
            elif method == 'kotlin_style':
                return payload
            # JavaScript / TypeScript Import
            elif method == 'js_import':
                last_s_quote = payload.rfind("'")
                last_d_quote = payload.rfind('"')
                if last_s_quote == -1 and last_d_quote == -1:
                    first_s_quote = payload.find("'")
                    first_d_quote = payload.find('"')
                    if first_s_quote != -1:
                        end_quote = payload.find("'", first_s_quote + 1)
                        if end_quote != -1: return payload[first_s_quote+1:end_quote]
                    if first_d_quote != -1:
                        end_quote = payload.find('"', first_d_quote + 1)
                        if end_quote != -1: return payload[first_d_quote+1:end_quote]
                    return None
                elif last_s_quote > last_d_quote:
                    start_quote = payload.rfind("'", 0, last_s_quote)
                    if start_quote != -1: return payload[start_quote + 1 : last_s_quote]
                else:
                    start_quote = payload.rfind('"', 0, last_d_quote)
                    if start_quote != -1: return payload[start_quote + 1 : last_d_quote]
            # JavaScript / TypeScript / PHP Require
            elif method == 'js_require' or method == 'php_require':
                end_paren = payload.find(')')
                if end_paren == -1: return None
                content_in_parens = payload[:end_paren].strip()
                if len(content_in_parens) > 1:
                    if content_in_parens.startswith("'") and content_in_parens.endswith("'"): return content_in_parens[1:-1]
                    if content_in_parens.startswith('"') and content_in_parens.endswith('"'): return content_in_parens[1:-1]
            # Go
            elif method == 'go_quoted':
                end_quote = payload.find('"')
                if end_quote != -1: return payload[:end_quote]
            # Rust Use
            elif method == 'rust_use':
                term_semi = payload.find(';')
                term_brace = payload.find('{')
                end = len(payload)
                if term_semi != -1: end = min(end, term_semi)
                name_part = payload[:end].strip()
                if term_brace != -1 and term_brace < end: name_part = name_part[:term_brace].strip()
                return name_part.split('::')[0].strip()
            # Rust Extern Crate
            elif method == 'rust_extern_crate':
                return payload.split(';')[0].strip()
            # PHP Use
            elif method == 'php_use':
                term_semi = payload.find(';')
                term_brace = payload.find('{')
                end = len(payload)
                if term_semi != -1: end = min(end, term_semi)
                name_part = payload[:end].strip()
                if term_brace != -1 and term_brace < end: name_part = name_part[:term_brace].strip()
                return name_part
            # Ruby Require
            elif method == 'ruby_require':
                payload = payload.strip()
                if len(payload) > 1:
                    if payload.startswith("'") and payload.endswith("'"): return payload[1:-1]
                    if payload.startswith('"') and payload.endswith('"'): return payload[1:-1]
            # Ruby Include
            elif method == 'ruby_include':
                parts = payload.split()
                if parts: return parts[0]
            # Dart Import
            elif method == 'dart_import':
                s_quote = payload.find("'")
                d_quote = payload.find('"')
                if s_quote == -1 and d_quote == -1: return None
                if s_quote != -1:
                    start_quote = s_quote
                    end_quote = payload.find("'", start_quote + 1)
                else:
                    start_quote = d_quote
                    end_quote = payload.find('"', start_quote + 1)
                if end_quote != -1: return payload[start_quote + 1 : end_quote].split(' ')[0]

        except Exception as e:
            # Log or print error if needed
            # print(f"Error parsing import line: '{line}' with keyword '{keyword}'. Error: {e}")
            return None
        return None # Default return if no specific logic matched or failed


    # --- Main Function ---
    def find_imports_for_language(self, file_content, language):
        """
        Finds import statements in the given file content for a specific language
        by checking line prefixes using predefined keywords for that language.

        Args:
            file_content (str): The source code content.
            language (str): The specific programming language (e.g., 'Python', 'Java').

        Returns:
            set: A set of unique imported module/package/library names found for that language.
                Returns an empty set if the language is not defined or no imports are found.
        """
        imports = set()

        # Get the list of (keyword, method) tuples *only* for the specified language
        language_keywords = IMPORT_START_KEYWORDS.get(language)

        if not language_keywords:
            # print(f"Warning: Import keywords not defined for language: {language}")
            return imports # Return empty set if language rules aren't defined

        lines = file_content.splitlines()

        for line in lines:
            stripped_line = line.strip()

            # Basic check to ignore empty lines and potentially simple comments
            if not stripped_line or stripped_line.startswith(('#', '//', '--', '/*')): # Add other common comment chars if needed
                continue

            # Check against the keywords *only* for the specified language
            for keyword, method in language_keywords:
                if stripped_line.startswith(keyword):
                    # Found a line starting with an import keyword for this language
                    module_name = self._extract_module_name(stripped_line, keyword, method)
                    if module_name:
                        imports.add(module_name)
                    # Once matched for this line, move to the next line
                    break

        return imports

# --- Example Usage ---
import_detector = ImportDetector()

if __name__ == "__main__":
    # 1. Known Language: Python
    python_code_sample = """
    import os
    from sys import argv
    import requests as r # Aliased import
    # import commented_out
    """
    python_imports = import_detector.find_imports_for_language(python_code_sample, "Python")
    print(f"Found Python imports: {python_imports}")
    # Expected: {'os', 'sys', 'requests'}

    # 2. Known Language: JavaScript
    javascript_code_sample = """
    // File: component.js
    import { Button } from '@mui/material';
    const fs = require('fs');
    import './local.css';
    """
    javascript_imports = import_detector.find_imports_for_language(javascript_code_sample, "JavaScript")
    print(f"Found JavaScript imports: {javascript_imports}")
    # Expected: {'@mui/material', 'fs', './local.css'}

    # 3. Known Language: Java
    java_code_sample = """
    package my.app;
    import java.io.File;
    import com.google.common.collect.Lists; // External library
    """
    java_imports = import_detector.find_imports_for_language(java_code_sample, "Java")
    print(f"Found Java imports: {java_imports}")
    # Expected: {'java.io.File', 'com.google.common.collect.Lists'}

    # 4. Unknown/Undefined Language
    some_other_code = """
    -- Lua example
    local socket = require("socket")
    -- This won't be processed unless Lua rules are added
    """
    other_imports = import_detector.find_imports_for_language(some_other_code, "Lua") # Assume Lua is not in IMPORT_START_KEYWORDS
    print(f"Found Lua imports: {other_imports}")
    # Expected: Warning message and empty set {}