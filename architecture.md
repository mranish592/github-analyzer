# GitHub Analyzer Architecture

## Overview

GitHub Analyzer is a system designed to analyze GitHub profiles by extracting metrics from users' commit history. 

### High-Level Architecture

The system consists of:

1. **Frontend**: A React/TypeScript application that provides the user interface
2. **Backend**: A FastAPI/Python service that performs the analysis
3. **External Services**: GitHub API, SonarQube, and MongoDB

## API Overview

The GitHub Analyzer exposes three main API endpoints that work together to process and deliver GitHub profile analysis:

1. **Submit Analysis API**
   - Endpoint: `/api/submit/{username}`
   - Purpose: Initiates the analysis process for a given GitHub username
   - Operation: Fetches basic user information from GitHub and generates a unique analysis ID
   - Returns: Analysis ID that can be used to track progress and retrieve results

2. **Status API**
   - Endpoint: `/api/status/{analysis_id}`
   - Purpose: Checks the progress of an ongoing analysis
   - Returns: Current status including total commits, analyzed commits, and completion flag

3. **Get Analysis Results API**
   - Endpoint: `/api/analysis/{analysis_id}`
   - Purpose: Retrieves the completed analysis results
   - Returns: Comprehensive metrics including experience and quality metrics
   - Condition: Only returns complete results when analysis is finished

This API structure allows for asynchronous processing of potentially lengthy analyses while providing immediate feedback to users.

## Analysis Flow

When a username is submitted for analysis, the system performs the following operations:

### 1. Commit Discovery
- The system queries the GitHub Search API to extract all commit hashes and repositories associated with the user
- This provides a comprehensive view of the user's contribution history across all their repositories

### 2. Repository Processing
For each repository containing user commits:
- The system clones the repository to the server
- For each commit:
  - Checks out the specific commit version
  - Identifies modified files and their changes

### 3. Language and Framework Detection
For each file in a commit:
- **Language Detection**: Determines the programming language based on file extension
- **Framework Detection**: 
  - Extracts import statements from the file
  - Converts these imports to vectors
  - Performs cosine similarity analysis against pre-computed framework import patterns
  - Identifies the most likely frameworks being used based on similarity scores

### 4. Metrics Collection
Two primary categories of metrics are collected:

#### Experience Metrics
- Lines of code added per language/framework
- Timestamp of each commit to track experience duration
- Repository diversity (number of different repositories worked on)

#### Quality Metrics
- Integrates with SonarQube for code quality analysis
- For each commit:
  - Runs SonarScanner on the repository at that commit point
  - Captures quality metrics such as code smells, bugs, and vulnerabilities
  - Filters results to focus only on files modified in that commit
  - Aggregates metrics at the file, commit, and overall levels

### 5. Data Storage
- All collected metrics are stored in MongoDB:
  - Commit-level metrics are cached to avoid recalculation
  - Experience metrics are organized by skill (language/framework)
  - Quality metrics are maintained at file, commit, and overall levels

## Optimization Strategies

The system implements several optimizations to improve performance and efficiency:

### 1. Commit Filtering
- PR commits are excluded to focus on substantial contributions
- Commits without modifications to actual code files are filtered out
- This reduces the number of commits that need detailed analysis

### 2. Caching
- MongoDB stores results of previously analyzed commits
- Before analyzing a commit, the system checks if metrics already exist
- This avoids redundant processing for repeat analyses or when analyzing multiple users with shared commits

### 3. Selective Quality Analysis
- Quality analysis (SonarQube scanning) is only performed on modified files
- This significantly reduces the processing time compared to analyzing entire repositories

### 4. Tiered Metric Storage
- Metrics are maintained at multiple levels:
  - File level: Tracking quality per file
  - Commit level: Aggregating metrics for each commit
  - Overall level: Providing summary statistics across the user's entire history