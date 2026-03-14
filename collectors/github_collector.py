import os
import git
import requests
import time
import re
from github import Github, GithubException
from github.GithubException import RateLimitExceededException
from datetime import datetime
import base64
import tempfile
import shutil

class GitHubCollector:
    """
    GitHub Repository Collector
    Searches, clones, and analyzes GitHub repositories
    """
    
    def __init__(self, token=None):
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.github = Github(self.token) if self.token else Github()
        self.rate_limit = self._check_rate_limit()
        
    def _check_rate_limit(self):
        """Check current rate limit status"""
        try:
            rate_limit = self.github.get_rate_limit()
            return {
                'core': {
                    'limit': rate_limit.core.limit,
                    'remaining': rate_limit.core.remaining,
                    'reset': rate_limit.core.reset
                },
                'search': {
                    'limit': rate_limit.search.limit,
                    'remaining': rate_limit.search.remaining,
                    'reset': rate_limit.search.reset
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def search_repositories(self, query, max_results=20, sort='stars', order='desc'):
        """
        Search for repositories matching query
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            sort: Sort field (stars, forks, updated)
            order: Sort order (desc, asc)
        
        Returns:
            List of repository information dictionaries
        """
        results = []
        
        try:
            print(f"🔍 Searching GitHub for: '{query}'")
            
            # Enhanced search query for AI/microservices projects
            search_queries = [
                query,
                f"{query} language:python",
                f"{query} language:javascript",
                f"{query} language:java",
                f"{query} language:go",
                f"{query} microservices",
                f"{query} machine-learning",
                f"{query} MLOps"
            ]
            
            repos = self.github.search_repositories(
                query=query,
                sort=sort,
                order=order
            )
            
            count = 0
            for repo in repos:
                if count >= max_results:
                    break
                    
                repo_info = self._extract_repo_info(repo)
                results.append(repo_info)
                count += 1
                
                print(f"  Found: {repo.full_name} ({repo.stargazers_count} ⭐)")
            
            print(f"✅ Found {len(results)} repositories")
            
        except RateLimitExceededException:
            print("⚠️ GitHub API rate limit exceeded. Please provide a token or try again later.")
            reset_time = self.rate_limit.get('core', {}).get('reset')
            if reset_time:
                wait_time = (reset_time - datetime.now()).total_seconds()
                print(f"   Rate limit resets in {int(wait_time/60)} minutes")
        
        except GithubException as e:
            print(f"❌ GitHub API error: {e}")
            
        return results
    
    def _extract_repo_info(self, repo):
        """Extract relevant information from repository object"""
        return {
            'id': repo.id,
            'name': repo.full_name,
            'full_name': repo.full_name,
            'description': repo.description,
            'url': repo.html_url,
            'clone_url': repo.clone_url,
            'ssh_url': repo.ssh_url,
            'homepage': repo.homepage,
            'stars': repo.stargazers_count,
            'forks': repo.forks_count,
            'watchers': repo.watchers_count,
            'language': repo.language,
            'topics': repo.get_topics(),
            'created_at': repo.created_at.isoformat() if repo.created_at else None,
            'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
            'pushed_at': repo.pushed_at.isoformat() if repo.pushed_at else None,
            'size': repo.size,
            'open_issues': repo.open_issues_count,
            'has_issues': repo.has_issues,
            'has_wiki': repo.has_wiki,
            'has_pages': repo.has_pages,
            'has_downloads': repo.has_downloads,
            'archived': repo.archived,
            'disabled': repo.disabled,
            'license': repo.license.name if repo.license else None,
            'default_branch': repo.default_branch,
            'owner': {
                'login': repo.owner.login,
                'type': repo.owner.type,
                'avatar_url': repo.owner.avatar_url
            }
        }
    
    def clone_repository(self, repo_url, target_path, branch=None, depth=1):
        """
        Clone a GitHub repository
        
        Args:
            repo_url: Repository URL (HTTPS or SSH)
            target_path: Local path to clone to
            branch: Branch to clone (None for default branch)
            depth: Shallow clone depth (1 for shallow, None for full)
        
        Returns:
            Dictionary with clone result information
        """
        result = {
            'success': False,
            'path': None,
            'branch': branch,
            'commit': None,
            'error': None
        }
        
        # Create target directory if it doesn't exist
        os.makedirs(target_path, exist_ok=True)
        
        try:
            print(f"📦 Cloning repository: {repo_url}")
            
            # Prepare clone arguments
            clone_args = {
                'url': repo_url,
                'to_path': target_path,
                'depth': depth
            }
            
            if branch:
                clone_args['branch'] = branch
            
            # Clone repository
            repo = git.Repo.clone_from(**clone_args)
            
            # Get clone information
            result['success'] = True
            result['path'] = target_path
            result['branch'] = repo.active_branch.name
            result['commit'] = repo.head.commit.hexsha
            result['commit_message'] = repo.head.commit.message.strip()
            result['commit_author'] = str(repo.head.commit.author)
            result['commit_date'] = repo.head.commit.committed_datetime.isoformat()
            
            print(f"✅ Repository cloned successfully")
            print(f"   Path: {target_path}")
            print(f"   Branch: {result['branch']}")
            print(f"   Commit: {result['commit'][:8]}")
            
        except git.GitCommandError as e:
            result['error'] = f"Git command failed: {e}"
            print(f"❌ {result['error']}")
            
        except Exception as e:
            result['error'] = f"Unexpected error: {e}"
            print(f"❌ {result['error']}")
            
        return result
    
    def get_repository_info(self, repo_url):
        """Get information about a repository without cloning"""
        # Parse owner and repo name from URL
        repo_info = self._parse_github_url(repo_url)
        
        if not repo_info:
            return {'error': 'Invalid repository URL'}
        
        try:
            repo = self.github.get_repo(f"{repo_info['owner']}/{repo_info['repo']}")
            
            return {
                'success': True,
                'info': self._extract_repo_info(repo),
                'readme': self._get_readme(repo),
                'languages': self._get_languages(repo),
                'contributors': self._get_contributors(repo),
                'releases': self._get_releases(repo)
            }
            
        except GithubException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_github_url(self, url):
        """Parse GitHub URL to extract owner and repo name"""
        # Pattern for GitHub URLs
        patterns = [
            r'github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?$',
            r'github\.com[/:]([^/]+)/([^/]+)$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return {
                    'owner': match.group(1),
                    'repo': match.group(2).replace('.git', '')
                }
        
        return None
    
    def _get_readme(self, repo):
        """Get README content from repository"""
        try:
            readme = repo.get_readme()
            content = base64.b64decode(readme.content).decode('utf-8')
            return {
                'name': readme.name,
                'path': readme.path,
                'content': content[:1000] + '...' if len(content) > 1000 else content
            }
        except:
            return None
    
    def _get_languages(self, repo):
        """Get language statistics from repository"""
        try:
            languages = repo.get_languages()
            total = sum(languages.values())
            
            # Calculate percentages
            lang_stats = {}
            for lang, bytes_count in languages.items():
                lang_stats[lang] = {
                    'bytes': bytes_count,
                    'percentage': round(bytes_count / total * 100, 1)
                }
            
            return lang_stats
        except:
            return {}
    
    def _get_contributors(self, repo, max_results=10):
        """Get top contributors from repository"""
        try:
            contributors = []
            for contributor in repo.get_contributors()[:max_results]:
                contributors.append({
                    'login': contributor.login,
                    'contributions': contributor.contributions,
                    'avatar_url': contributor.avatar_url
                })
            return contributors
        except:
            return []
    
    def _get_releases(self, repo, max_results=5):
        """Get recent releases from repository"""
        try:
            releases = []
            for release in repo.get_releases()[:max_results]:
                releases.append({
                    'tag': release.tag_name,
                    'name': release.title,
                    'published': release.published_at.isoformat() if release.published_at else None,
                    'prerelease': release.prerelease
                })
            return releases
        except:
            return []
    
    def search_by_topic(self, topics, max_results=20):
        """Search repositories by topic"""
        query = ' '.join([f'topic:{topic}' for topic in topics])
        return self.search_repositories(query, max_results)
    
    def search_ml_projects(self, max_results=20):
        """Search for ML/AI projects"""
        ml_queries = [
            'topic:machine-learning',
            'topic:deep-learning',
            'topic:tensorflow',
            'topic:pytorch',
            'topic:mlops',
            'topic:llm',
            'topic:generative-ai'
        ]
        
        all_results = []
        for query in ml_queries:
            results = self.search_repositories(query, max_results // len(ml_queries))
            all_results.extend(results)
        
        # Remove duplicates and sort by stars
        seen = set()
        unique_results = []
        for repo in all_results:
            if repo['id'] not in seen:
                seen.add(repo['id'])
                unique_results.append(repo)
        
        unique_results.sort(key=lambda x: x['stars'], reverse=True)
        
        return unique_results[:max_results]
    
    def search_microservices_projects(self, max_results=20):
        """Search for microservices projects"""
        ms_queries = [
            'topic:microservices',
            'topic:microservice',
            'topic:service-mesh',
            'topic:kubernetes',
            'topic:docker',
            'topic:istio'
        ]
        
        all_results = []
        for query in ms_queries:
            results = self.search_repositories(query, max_results // len(ms_queries))
            all_results.extend(results)
        
        # Remove duplicates and sort by stars
        seen = set()
        unique_results = []
        for repo in all_results:
            if repo['id'] not in seen:
                seen.add(repo['id'])
                unique_results.append(repo)
        
        unique_results.sort(key=lambda x: x['stars'], reverse=True)
        
        return unique_results[:max_results]
    
    def download_file(self, repo_url, file_path, target_path):
        """
        Download a specific file from a GitHub repository
        """
        repo_info = self._parse_github_url(repo_url)
        if not repo_info:
            return {'error': 'Invalid repository URL'}
        
        try:
            repo = self.github.get_repo(f"{repo_info['owner']}/{repo_info['repo']}")
            contents = repo.get_contents(file_path)
            
            if isinstance(contents, list):
                return {'error': 'Path is a directory, not a file'}
            
            # Decode and save file
            content = base64.b64decode(contents.content)
            
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, 'wb') as f:
                f.write(content)
            
            return {
                'success': True,
                'path': target_path,
                'size': len(content)
            }
            
        except GithubException as e:
            return {'error': str(e)}
    
    def get_rate_limit_status(self):
        """Get current rate limit status"""
        return self._check_rate_limit()
    
    def wait_for_rate_limit(self):
        """Wait until rate limit resets if exceeded"""
        rate_limit = self._check_rate_limit()
        
        if rate_limit.get('core', {}).get('remaining', 0) == 0:
            reset_time = rate_limit['core']['reset']
            wait_seconds = (reset_time - datetime.now()).total_seconds()
            
            if wait_seconds > 0:
                print(f"⏳ Rate limit exceeded. Waiting {int(wait_seconds)} seconds...")
                time.sleep(wait_seconds + 1)
                return True
        
        return False