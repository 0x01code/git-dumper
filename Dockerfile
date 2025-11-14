FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install git (needed for git operations after dump)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY git_dumper.py .

# Make script executable
RUN chmod +x git_dumper.py

# Entry point
ENTRYPOINT ["python", "/app/git_dumper.py"]

# Default help command
CMD ["--help"]
