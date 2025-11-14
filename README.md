# Git Dumper

A tool for dumping exposed .git directories from websites

**For use in authorized security testing and CTF challenges only**

## Installation

### Method 1: Direct Python Usage

```bash
pip3 install -r requirements.txt
chmod +x git_dumper.py
```

```bash
# Basic usage
python3 git_dumper.py http://target.com/.git ./output

# Or
python3 git_dumper.py https://example.com ./dump
```

### Method 2: Using Docker

```bash
# Build image
docker build -t git-dumper .
```

### Using Docker

```bash
# Method 1: Docker run
docker run --rm -v $(pwd)/output:/app/output git-dumper http://target.com/.git

# View help
docker run --rm git-dumper --help
```

## Post-Dump Steps

After dumping the .git directory, you can extract the original files:

```bash
cd output
git checkout -- .
```

Or view commit history:

```bash
cd output
git log
git show <commit-hash>
```

## Features

- Download basic .git files (HEAD, config, index, etc.)
- Download refs and logs
- Download git objects from refs and index file
- Support for both HTTP and HTTPS

## Legal Notice

This tool is created for educational purposes and authorized security testing only.
Using this tool against systems you do not have permission to access is illegal.
