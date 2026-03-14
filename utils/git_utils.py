import os
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict
import re

class GitUtils:
    """
    Git repository analysis utilities
    """
    
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.has_git = self._check_git()
    
    def _check_git(self):
        """Check if directory is a git repository"""
        git_path = os.path.join(self.repo_path, '.git')
        return os.path.exists(git_path)
    
    def _run_git_command(self, command):
        """Run git command safely"""
        if not self.has_git:
            return None
        
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception as e:
            print(f"Git command failed: {e}")
            return None
    
    def get_repo_info(self):
        """Get basic repository information"""
        if not self.has_git:
            return None
        
        info = {}
        
        # Get remote URL
        remote = self._run_git_command('git config --get remote.origin.url')
        if remote:
            info['remote_url'] = remote
        
        # Get current branch
        branch = self._run_git_command('git rev-parse --abbrev-ref HEAD')
        if branch:
            info['branch'] = branch
        
        # Get last commit
        last_commit = self._run_git_command('git log -1 --pretty=format:%h|%an|%ad|%s')
        if last_commit:
            parts = last_commit.split('|')
            if len(parts) == 4:
                info['last_commit'] = {
                    'hash': parts[0],
                    'author': parts[1],
                    'date': parts[2],
                    'message': parts[3]
                }
        
        # Get commit count
        count = self._run_git_command('git rev-list --count HEAD')
        if count:
            info['commit_count'] = int(count)
        
        # Get contributors count
        contributors = self._run_git_command('git shortlog -sn | wc -l')
        if contributors:
            info['contributors_count'] = int(contributors)
        
        # Get repository age
        first_commit = self._run_git_command('git log --reverse --format=%ad --date=iso | head -1')
        if first_commit:
            info['created_at'] = first_commit
        
        return info
    
    def get_commit_history(self, days=180, max_commits=1000):
        """Get commit history for specified period"""
        if not self.has_git:
            return []
        
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        command = f'git log --since="{since_date}" --format=%h|%an|%ad|%s --date=iso'
        output = self._run_git_command(command)
        
        if not output:
            return []
        
        commits = []
        for line in output.split('\n')[:max_commits]:
            if '|' in line:
                parts = line.split('|', 3)
                if len(parts) == 4:
                    commits.append({
                        'hash': parts[0],
                        'author': parts[1],
                        'date': parts[2],
                        'message': parts[3],
                        'timestamp': datetime.fromisoformat(parts[2].replace(' ', 'T'))
                    })
        
        return commits
    
    def get_file_history(self, filepath):
        """Get history of specific file"""
        if not self.has_git:
            return []
        
        command = f'git log --format=%h|%an|%ad|%s --date=iso -- {filepath}'
        output = self._run_git_command(command)
        
        if not output:
            return []
        
        history = []
        for line in output.split('\n'):
            if '|' in line:
                parts = line.split('|', 3)
                if len(parts) == 4:
                    history.append({
                        'hash': parts[0],
                        'author': parts[1],
                        'date': parts[2],
                        'message': parts[3]
                    })
        
        return history
    
    def get_code_churn(self, days=180):
        """Calculate code churn statistics"""
        if not self.has_git:
            return {}
        
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        command = f'git log --since="{since_date}" --numstat --format=%h'
        output = self._run_git_command(command)
        
        if not output:
            return {}
        
        churn = {
            'by_file': defaultdict(lambda: {'added': 0, 'deleted': 0, 'commits': 0}),
            'by_author': defaultdict(lambda: {'added': 0, 'deleted': 0, 'commits': 0}),
            'by_date': defaultdict(lambda: {'added': 0, 'deleted': 0, 'commits': 0}),
            'total': {'added': 0, 'deleted': 0, 'commits': 0}
        }
        
        current_commit = None
        
        for line in output.split('\n'):
            if '|' not in line and line.strip():
                # This is a commit line
                current_commit = line.strip()
                churn['total']['commits'] += 1
            elif line.strip() and current_commit:
                # This is a file change line
                parts = line.split('\t')
                if len(parts) == 3:
                    added = parts[0] if parts[0] != '-' else '0'
                    deleted = parts[1] if parts[1] != '-' else '0'
                    filename = parts[2]
                    
                    if added.isdigit() and deleted.isdigit():
                        added_int = int(added)
                        deleted_int = int(deleted)
                        
                        # Update file stats
                        churn['by_file'][filename]['added'] += added_int
                        churn['by_file'][filename]['deleted'] += deleted_int
                        churn['by_file'][filename]['commits'] += 1
                        
                        # Update totals
                        churn['total']['added'] += added_int
                        churn['total']['deleted'] += deleted_int
        
        return churn
    
    def get_contributors(self):
        """Get contributor statistics"""
        if not self.has_git:
            return []
        
        command = 'git shortlog -sn --all'
        output = self._run_git_command(command)
        
        if not output:
            return []
        
        contributors = []
        for line in output.split('\n'):
            if line.strip():
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    contributors.append({
                        'commits': int(parts[0]),
                        'name': parts[1]
                    })
        
        return contributors
    
    def get_bug_fixes(self, days=180):
        """Get bug fix commits"""
        commits = self.get_commit_history(days=days)
        
        bug_keywords = ['fix', 'bug', 'error', 'issue', 'hotfix', 'patch', 'resolve']
        
        bug_fixes = []
        for commit in commits:
            message_lower = commit['message'].lower()
            if any(keyword in message_lower for keyword in bug_keywords):
                bug_fixes.append(commit)
        
        return bug_fixes
    
    def get_file_at_commit(self, filepath, commit_hash):
        """Get file content at specific commit"""
        if not self.has_git:
            return None
        
        command = f'git show {commit_hash}:{filepath}'
        return self._run_git_command(command)
    
    def get_changed_files(self, commit_hash):
        """Get files changed in a commit"""
        if not self.has_git:
            return []
        
        command = f'git show --name-only --pretty=format: {commit_hash}'
        output = self._run_git_command(command)
        
        if output:
            return [f for f in output.split('\n') if f.strip()]
        return []
    
    def get_commit_diff(self, commit_hash):
        """Get diff for a commit"""
        if not self.has_git:
            return None
        
        command = f'git show {commit_hash}'
        return self._run_git_command(command)
    
    def get_branch_info(self):
        """Get information about branches"""
        if not self.has_git:
            return {}
        
        branches = {}
        
        # Get local branches
        local = self._run_git_command('git branch')
        if local:
            branches['local'] = [b.strip().replace('* ', '') for b in local.split('\n') if b.strip()]
        
        # Get remote branches
        remote = self._run_git_command('git branch -r')
        if remote:
            branches['remote'] = [b.strip() for b in remote.split('\n') if b.strip()]
        
        return branches
    
    def get_tags(self):
        """Get repository tags"""
        if not self.has_git:
            return []
        
        tags = self._run_git_command('git tag')
        if tags:
            return tags.split('\n')
        return []
    
    def generate_report(self):
        """Generate comprehensive git report"""
        if not self.has_git:
            return {'error': 'Not a git repository'}
        
        report = {
            'repo_info': self.get_repo_info(),
            'contributors': self.get_contributors(),
            'branches': self.get_branch_info(),
            'tags': self.get_tags(),
            'commit_history': self.get_commit_history(),
            'bug_fixes': self.get_bug_fixes(),
            'code_churn': self.get_code_churn(),
            'statistics': {}
        }
        
        # Calculate statistics
        commits = report['commit_history']
        if commits:
            report['statistics']['total_commits'] = len(commits)
            
            # Commits by author
            authors = defaultdict(int)
            for commit in commits:
                authors[commit['author']] += 1
            report['statistics']['commits_by_author'] = dict(authors)
            
            # Commits by date
            by_date = defaultdict(int)
            for commit in commits:
                date = commit['date'].split(' ')[0]
                by_date[date] += 1
            report['statistics']['commits_by_date'] = dict(by_date)
            
            # Bug fix ratio
            bug_count = len(report['bug_fixes'])
            report['statistics']['bug_fix_ratio'] = bug_count / len(commits) if commits else 0
        
        return report