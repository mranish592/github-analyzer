# GitHub Analyzer

GitHub Analyzer is a tool that analyzes GitHub users' profiles to generate detailed experience and quality metrics based on their commit history. It provides insights into programming languages used, frameworks adopted, and code quality metrics through SonarQube integration.

## Overview

The analyzer works by:
1. Fetching a user's commits through the GitHub Search API
2. Analyzing each commit for experience metrics (languages, frameworks, lines of code)
3. Performing quality analysis using SonarQube
4. Aggregating metrics to provide comprehensive insights

## Architecture

The project consists of:

- **Backend (Python/FastAPI)**
  - GitHub API integration for fetching user data
  - Local Git operations for commit analysis
  - SonarQube integration for code quality metrics
  - MongoDB for caching analysis results

- **Frontend (TypeScript/React)**
  - User interface for submitting analysis requests
  - Visualization of metrics and results

## Setup and Installation

### Prerequisites

1. Python 3.8+
2. Node.js 16+
3. MongoDB
4. SonarQube Server
5. SonarScanner

### SonarQube Setup

1. Install SonarQube:
   - Follow the [official SonarQube installation guide](https://docs.sonarqube.org/latest/setup/install-server/)
   - Start the SonarQube server following the guide for your operating system
   - Access SonarQube at `http://localhost:9000` (default credentials: admin/admin)

2. Install SonarScanner:
   - Follow the [official SonarScanner installation guide](https://docs.sonarqube.org/latest/analyzing-source-code/scanners/sonarscanner/)
   - Ensure the scanner is properly added to your system's PATH

### Project Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/github-analyzer.git
   cd github-analyzer
   ```

2. Set up backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

3. Set up frontend:
   ```bash
   cd frontend
   npm install
   ```

4. Configure environment variables:
   ```bash
   # Backend .env
   GITHUB_ACCESS_TOKEN=your_github_token
   SONARQUBE_URL=http://localhost:9000
   SONARQUBE_TOKEN=your_sonar_token
   MONGO_CONNECTION_STRING=mongodb://localhost:27017
   MONGO_DB_NAME=github_metrics
   ```

5. Start the services:
   ```bash
   # Start backend
   cd backend
   uvicorn app.main:app --reload

   # Start frontend
   cd frontend
   npm start
   ```

## API Endpoints

### Analyze User
```
GET /api/analyze/{username}
Query Parameters:
  - skip_quality_metrics: boolean (optional)
```

## Technical Details

### Language and Framework Detection

- **Language Detection**: The system identifies programming languages based on file extensions and content patterns
- **Framework Detection**: Frameworks are identified through:
  - Package manager files (package.json, requirements.txt, etc.)
  - Framework-specific configuration files
  - Common import patterns in the code

### Analysis Optimization

1. **Commit Filtering**:
   - Commits without supported languages are skipped
   - Binary files and generated code are excluded
   - Duplicate commits (in case of merges) are handled appropriately

2. **Caching**:
   - Analysis results are cached in MongoDB
   - Subsequent requests for the same commit hash return cached results

3. **Quality Metrics**:
   - Code quality analysis is optional and can be skipped
   - SonarQube analysis is performed on a per-commit basis
   - Metrics include:
     - Code smells
     - Bugs
     - Vulnerabilities
     - Duplicated code
     - Complexity
     - Test coverage

### Experience Metrics

Experience metrics are calculated based on:
- Lines of code per language
- Framework usage frequency
- Commit frequency and recency
- Code complexity and quality trends

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Your chosen license] 