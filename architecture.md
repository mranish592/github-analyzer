# GitHub Analyzer Architecture

## Overview

GitHub Analyzer is a system designed to analyze GitHub profiles by extracting metrics from users' commit history. The architecture follows a client-server model with a clear separation between the frontend user interface and the backend analysis engine.

### High-Level Architecture

The system consists of:

1. **Frontend**: A React/TypeScript application that provides the user interface
2. **Backend**: A FastAPI/Python service that performs the analysis
3. **External Services**: GitHub API, SonarQube, and MongoDB

## Request Flow

When a username is received, the following high-level steps are taken:

1. **Username Input**
   - User submits a GitHub username through the frontend
   - Frontend makes an API call to the backend

2. **Initial Processing**
   - Backend receives the request through the `/api/analyze/{username}` or `/api/submit/{username}` endpoint
   - System fetches basic user information from GitHub API
   - A unique analysis ID is generated for tracking

3. **Repository Analysis**
   - System retrieves the user's repositories 
   - For each repository, commits are analyzed either synchronously or asynchronously

4. **Metrics Extraction**
   - Each commit is processed to extract:
     - Experience metrics (languages, frameworks, lines of code)
     - Quality metrics through SonarQube integration (optional)
   - Metrics are aggregated across all commits

5. **Result Delivery**
   - Analyzed data is formatted and returned to the frontend
   - Results are cached in MongoDB for future requests
   - Frontend displays visualizations and summaries of the analysis

## Deep Dive: Architecture Components

### Core Services

The system is organized around several key services:

1. **Analysis Service**: Manages the analysis workflow, handling both synchronous and asynchronous analysis requests.

2. **Ingestion Service**: Responsible for fetching and processing repository data from GitHub.

3. **Skill Identification Service**: Analyzes code to identify programming languages and frameworks used.

4. **Metrics Extraction Service**: Calculates statistics like lines of code, contribution frequency, and other metrics.

5. **Scoring Service**: Evaluates the quality and experience metrics to provide insights.

### Key Components

#### GitHub Integration

The `GithubUtil` class provides an abstraction over the GitHub API, allowing the system to:
- Fetch user profiles
- List repositories
- Access commit history
- Monitor API rate limits to prevent throttling

#### Local Git Operations

The `LocalGitUtil` handles operations that require direct access to git repositories:
- Cloning repositories
- Checking out specific commits
- Extracting file changes between commits
- Analyzing commit content in detail

#### Framework Detection

The framework detection system identifies technologies used in each file:
- Maps file extensions to programming languages
- Uses pattern matching to identify frameworks and libraries
- Associates skills with each commit and aggregates them

#### Quality Analysis

The `QualityScan` component integrates with SonarQube to perform code quality analysis:
- Runs SonarScanner on repository snapshots
- Captures metrics like code smells, bugs, and vulnerabilities
- Supports both SonarQube server and SonarCloud modes

#### Metrics Aggregation

The `MetricsUtil` aggregates data across multiple commits:
- Calculates experience duration for each skill
- Tracks first and last usage of each technology
- Summarizes lines of code contributions per language and framework

#### Data Persistence

MongoDB is used to store analysis results:
- Caches commit-level metrics to avoid redundant processing
- Tracks analysis status for asynchronous operations
- Enables historical comparison of metrics

### API Endpoints

The FastAPI backend exposes several endpoints:
- `/api/analyze/{username}`: Performs a synchronous analysis
- `/api/submit/{username}`: Initiates an asynchronous analysis
- Status endpoints to track progress of long-running analyses
