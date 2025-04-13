FROM --platform=linux/arm64 python:3.11-slim

WORKDIR /app

# Install system dependencies including git, sonar-scanner, and Node.js
RUN apt-get update && apt-get install -y \
    git \
    wget \
    unzip \
    openjdk-17-jre \
    gnupg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && node --version \
    && npm --version

# Install SonarScanner for linux x86
RUN wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-7.0.2.4839-linux.zip \
    && unzip sonar-scanner-cli-7.0.2.4839-linux.zip \
    && mv sonar-scanner-7.0.2.4839-linux /opt/sonar-scanner \
    && ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner \
    && rm sonar-scanner-cli-7.0.2.4839-linux.zip

# # Install SonarScanner for ARM64/aarch64
# RUN wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-7.0.2.4839-linux-aarch64.zip \
#     && unzip sonar-scanner-cli-7.0.2.4839-linux-aarch64.zip \
#     && mv sonar-scanner-7.0.2.4839-linux-aarch64 /opt/sonar-scanner \
#     && ln -s /opt/sonar-scanner/bin/sonar-scanner /usr/local/bin/sonar-scanner \
#     && rm sonar-scanner-cli-7.0.2.4839-linux-aarch64.zip

# Copy requirements first for better caching
COPY requirements.txt .

# Create and use a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies in the virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for cloning repositories
# RUN mkdir -p /app/local_repo_dir/base
RUN mkdir -p /tmp/github-analyzer/base


# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app:/app/src
# ENV BASE_DIR=/app/local_repo_dir/base

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "main.py"]
