import os
import subprocess
import re
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

class MaintainabilityAnalyzer:
    """
    TIER 5: Maintainability Analysis
    Analyzes code churn, change impact, and bug frequency
    """
    
    def __init__(self, project_path, tier1_data, tier2_data):
        self.project_path = project_path
        self.tier1 = tier1_data
        self.tier2 = tier2_data
        self.services = tier2_data.get('services', [])
        self.models = tier1_data.get('models', [])
        
        self.results = {
            'commit_count': 0,
            'contributors': [],
            'churn_by_service': {},
            'churn_by_file': {},
            'top_changed': [],
            'impact_metrics': {
                'avg_impact': 0,
                'max_impact': 0,
                'impact_by_model': {}
            },
            'bug_metrics': {
                'bug_rate': 0,
                'bug_count': 0,
                'bugs_by_model': {},
                'bug_prone_files': []
            },
            'maintainability_score': 0,
            'trends': {}
        }
    
    def analyze(self):
        """Run complete maintainability analysis"""
        print(f"\n🔧 TIER 5: Analyzing maintainability")
        
        # Analyze code churn
        self._analyze_code_churn()
        
        # Analyze change impact
        self._analyze_change_impact()
        
        # Analyze bug frequency
        self._analyze_bug_frequency()
        
        # Calculate maintainability score
        self._calculate_maintainability_score()
        
        # Analyze trends
        self._analyze_trends()
        
        return self.results
    
    def _analyze_code_churn(self):
        """Analyze code churn from git history"""
        git_path = os.path.join(self.project_path, '.git')
        
        if os.path.exists(git_path):
            try:
                # Get commit count
                result = subprocess.run(
                    ['git', 'rev-list', '--count', 'HEAD'],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.results['commit_count'] = int(result.stdout.strip())
                
                # Get contributors
                result = subprocess.run(
                    ['git', 'shortlog', '-sn', '--all'],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    contributors = []
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            parts = line.strip().split('\t')
                            if len(parts) == 2:
                                contributors.append({
                                    'commits': int(parts[0]),
                                    'name': parts[1]
                                })
                    self.results['contributors'] = contributors
                
                # Get file churn stats
                result = subprocess.run(
                    ['git', 'log', '--pretty=format:', '--name-only', '--since="6 months"'],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                file_changes = defaultdict(int)
                for line in result.stdout.split('\n'):
                    if line.strip():
                        file_changes[line.strip()] += 1
                
                # Sort by change count
                sorted_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)
                self.results['top_changed'] = sorted_files[:20]
                
                # Calculate churn by service
                for service in self.services:
                    service_path = service.get('path', '')
                    service_churn = 0
                    
                    for file, changes in file_changes.items():
                        if file.startswith(service_path):
                            service_churn += changes
                    
                    self.results['churn_by_service'][service['name']] = service_churn
                
                self.results['churn_by_file'] = dict(sorted(file_changes.items(), 
                                                           key=lambda x: x[1], 
                                                           reverse=True)[:50])
                
                print(f"  ✓ Commit count: {self.results['commit_count']}")
                print(f"  ✓ Contributors: {len(self.results['contributors'])}")
                print(f"  ✓ Top changed files: {len(self.results['top_changed'])}")
                
            except Exception as e:
                print(f"  ⚠ Git analysis failed: {e}")
                self._estimate_churn_from_files()
        else:
            print(f"  ⚠ No git repository found, estimating from file stats")
            self._estimate_churn_from_files()
    
    def _estimate_churn_from_files(self):
        """Estimate churn from file modification times"""
        file_changes = defaultdict(int)
        
        for file_info in self.tier1.get('file_inventory', []):
            # Use modified date as proxy for activity
            # More recent = more churn (simplified)
            file_changes[file_info['path']] = 1
        
        sorted_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)
        self.results['top_changed'] = sorted_files[:20]
        self.results['commit_count'] = len(file_changes)
    
    def _analyze_change_impact(self):
        """Analyze impact of changes on the system"""
        impact_by_model = {}
        
        for model in self.models:
            model_name = model.get('name', 'unknown')
            
            # Find files that depend on this model
            dependent_files = set()
            
            for file_info in self.tier1.get('file_inventory', []):
                if file_info['extension'] in ['.py', '.js', '.java']:
                    file_path = os.path.join(self.project_path, file_info['path'])
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if model_name in content:
                                dependent_files.add(file_info['path'])
                    except:
                        pass
            
            impact_by_model[model_name] = len(dependent_files)
        
        if impact_by_model:
            self.results['impact_metrics']['impact_by_model'] = impact_by_model
            self.results['impact_metrics']['avg_impact'] = sum(impact_by_model.values()) / len(impact_by_model)
            self.results['impact_metrics']['max_impact'] = max(impact_by_model.values())
        
        print(f"  ✓ Avg change impact: {self.results['impact_metrics']['avg_impact']:.1f} files")
        print(f"  ✓ Max change impact: {self.results['impact_metrics']['max_impact']} files")
    
    def _analyze_bug_frequency(self):
        """Analyze bug frequency and correlation with models"""
        bug_keywords = ['fix', 'bug', 'error', 'issue', 'hotfix', 'patch', 'resolve']
        
        git_path = os.path.join(self.project_path, '.git')
        
        if os.path.exists(git_path):
            try:
                # Get commits with bug fixes
                result = subprocess.run(
                    ['git', 'log', '--pretty=format:%H|%s', '--since="6 months"'],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                bug_commits = []
                total_commits = 0
                
                for line in result.stdout.split('\n'):
                    if '|' in line:
                        total_commits += 1
                        hash_part, msg = line.split('|', 1)
                        
                        if any(keyword in msg.lower() for keyword in bug_keywords):
                            bug_commits.append({
                                'hash': hash_part,
                                'message': msg
                            })
                
                self.results['bug_metrics']['bug_count'] = len(bug_commits)
                if total_commits > 0:
                    self.results['bug_metrics']['bug_rate'] = len(bug_commits) / total_commits
                
                # Find which files are most bug-prone
                bug_files = defaultdict(int)
                
                for bug in bug_commits[:20]:  # Limit to recent bugs
                    result = subprocess.run(
                        ['git', 'show', '--name-only', '--pretty=format:', bug['hash']],
                        cwd=self.project_path,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            bug_files[line.strip()] += 1
                
                self.results['bug_metrics']['bug_prone_files'] = sorted(
                    bug_files.items(), key=lambda x: x[1], reverse=True
                )[:20]
                
                # Correlate bugs with models
                bugs_by_model = defaultdict(int)
                for model in self.models:
                    model_name = model.get('name', '')
                    for bug in bug_commits:
                        # Check if bug commit touched model files
                        result = subprocess.run(
                            ['git', 'show', '--name-only', '--pretty=format:', bug['hash']],
                            cwd=self.project_path,
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        
                        for line in result.stdout.split('\n'):
                            if model_name in line:
                                bugs_by_model[model_name] += 1
                                break
                
                self.results['bug_metrics']['bugs_by_model'] = dict(bugs_by_model)
                
            except Exception as e:
                print(f"  ⚠ Bug analysis failed: {e}")
                self._estimate_bug_frequency()
        else:
            self._estimate_bug_frequency()
        
        print(f"  ✓ Bug rate: {self.results['bug_metrics'].get('bug_rate', 0):.1%}")
        print(f"  ✓ Bug count: {self.results['bug_metrics'].get('bug_count', 0)}")
    
    def _estimate_bug_frequency(self):
        """Estimate bug frequency from file names and comments"""
        bug_count = 0
        bug_files = defaultdict(int)
        
        for file_info in self.tier1.get('file_inventory', []):
            if 'bug' in file_info['name'].lower() or 'fix' in file_info['name'].lower():
                bug_count += 1
                bug_files[file_info['path']] += 1
            
            # Check file content for TODO/FIXME comments
            if file_info['extension'] in ['.py', '.js', '.java']:
                file_path = os.path.join(self.project_path, file_info['path'])
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if 'TODO' in content or 'FIXME' in content or 'BUG' in content:
                            bug_count += content.count('TODO') + content.count('FIXME')
                            bug_files[file_info['path']] += 1
                except:
                    pass
        
        self.results['bug_metrics']['bug_count'] = bug_count
        self.results['bug_metrics']['bug_rate'] = bug_count / len(self.tier1.get('file_inventory', [1]))
        self.results['bug_metrics']['bug_prone_files'] = sorted(
            bug_files.items(), key=lambda x: x[1], reverse=True
        )[:20]
    
    def _calculate_maintainability_score(self):
        """Calculate overall maintainability score (0-10)"""
        score = 10.0
        factors = []
        
        # Factor 1: Code churn (high churn reduces maintainability)
        if self.results['commit_count'] > 1000:
            score -= 2
            factors.append('Very high code churn')
        elif self.results['commit_count'] > 500:
            score -= 1
            factors.append('High code churn')
        
        # Factor 2: Bug rate
        bug_rate = self.results['bug_metrics'].get('bug_rate', 0)
        if bug_rate > 0.3:
            score -= 3
            factors.append('Very high bug rate')
        elif bug_rate > 0.2:
            score -= 2
            factors.append('High bug rate')
        elif bug_rate > 0.1:
            score -= 1
            factors.append('Moderate bug rate')
        
        # Factor 3: Change impact
        avg_impact = self.results['impact_metrics'].get('avg_impact', 0)
        if avg_impact > 10:
            score -= 2
            factors.append('Changes affect many files')
        elif avg_impact > 5:
            score -= 1
            factors.append('Moderate change impact')
        
        # Factor 4: File concentration (are changes focused?)
        if self.results['top_changed']:
            top_changed_count = sum(count for _, count in self.results['top_changed'][:5])
            total_changes = sum(count for _, count in self.results['top_changed'])
            
            if total_changes > 0:
                concentration = top_changed_count / total_changes
                if concentration > 0.5:
                    score -= 1
                    factors.append('Changes concentrated in few files')
        
        # Ensure score is within 0-10
        self.results['maintainability_score'] = max(0, min(10, round(score, 1)))
        self.results['maintainability_factors'] = factors
        
        print(f"  ✓ Maintainability score: {self.results['maintainability_score']}/10")
    
    def _analyze_trends(self):
        """Analyze trends in maintainability metrics"""
        trends = {
            'churn_trend': 'stable',
            'bug_trend': 'stable',
            'activity_trend': 'stable'
        }
        
        # This would require time-series analysis of git history
        # For now, provide placeholder
        self.results['trends'] = trends