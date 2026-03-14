import os
import re
import ast
import json
from collections import defaultdict
import networkx as nx

class UniversalSystemAnalyzer:
    """
    TIER 2: Universal System Analyzer
    Works for ANY project type and language
    """
    
    def __init__(self, project_path, tier1_data):
        self.project_path = project_path
        self.tier1 = tier1_data
        self.file_inventory = tier1_data.get('file_inventory', [])
        
        self.results = {
            'services': tier1_data.get('services', []),
            'api_endpoints': [],
            'dependencies': {},
            'dependency_graph': {'nodes': [], 'links': []},
            'frameworks': set(),
            'languages': tier1_data.get('languages', {}),
            'endpoint_count': 0,
            'dependency_count': 0,
            'analysis_details': {}
        }
        
        # Language-specific patterns
        self.api_patterns = {
            'Python': {
                'flask': [
                    r'@app\.route\([\'"]([^\'"]+)[\'"]',
                    r'@app\.(get|post|put|delete)\([\'"]([^\'"]+)[\'"]'
                ],
                'fastapi': [
                    r'@app\.(get|post|put|delete)\([\'"]([^\'"]+)[\'"]',
                    r'@router\.(get|post|put|delete)\([\'"]([^\'"]+)[\'"]'
                ],
                'django': [
                    r'path\([\'"]([^\'"]+)[\'"]',
                    r're_path\([\'"]([^\'"]+)[\'"]'
                ]
            },
            'JavaScript/Node.js': {
                'express': [
                    r'app\.(get|post|put|delete)\([\'"]([^\'"]+)[\'"]',
                    r'router\.(get|post|put|delete)\([\'"]([^\'"]+)[\'"]'
                ],
                'fastify': [
                    r'fastify\.(get|post|put|delete)\([\'"]([^\'"]+)[\'"]'
                ],
                'koa': [
                    r'router\.(get|post|put|delete)\([\'"]([^\'"]+)[\'"]'
                ]
            },
            'Java': {
                'spring': [
                    r'@RequestMapping\([\'"]([^\'"]+)[\'"]',
                    r'@GetMapping\([\'"]([^\'"]+)[\'"]',
                    r'@PostMapping\([\'"]([^\'"]+)[\'"]'
                ],
                'jax-rs': [
                    r'@Path\([\'"]([^\'"]+)[\'"]',
                    r'@GET\s*@Path\([\'"]([^\'"]+)[\'"]'
                ]
            },
            'Go': {
                'gin': [
                    r'r\.(GET|POST|PUT|DELETE)\([\'"]([^\'"]+)[\'"]',
                    r'router\.(GET|POST|PUT|DELETE)\([\'"]([^\'"]+)[\'"]'
                ],
                'echo': [
                    r'e\.(GET|POST|PUT|DELETE)\([\'"]([^\'"]+)[\'"]'
                ]
            },
            'Ruby': {
                'rails': [
                    r'get\s+[\'"]([^\'"]+)[\'"]',
                    r'post\s+[\'"]([^\'"]+)[\'"]',
                    r'resources\s+:[\w]+'
                ]
            },
            'PHP': {
                'laravel': [
                    r'Route::(get|post|put|delete)\([\'"]([^\'"]+)[\'"]',
                    r'Route::resource\([\'"]([^\'"]+)[\'"]'
                ]
            }
        }
        
        self.dependency_patterns = {
            'Python': r'(?:import|from)\s+([\w.]+)',
            'JavaScript': r'(?:require\([\'"]([^\'"]+)[\'"]\)|import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"])',
            'Java': r'import\s+([\w.]+);',
            'Go': r'import\s+\(?\s*[\'"]([^\'"]+)[\'"]',
            'Ruby': r'require\s+[\'"]([^\'"]+)[\'"]',
            'PHP': r'use\s+([\w\\\\]+);'
        }
    
    def analyze(self):
        """Run complete system analysis"""
        print(f"\n🔍 TIER 2: Analyzing system architecture")
        
        # Detect API endpoints
        self._detect_api_endpoints()
        
        # Detect dependencies
        self._detect_dependencies()
        
        # Build dependency graph
        self._build_dependency_graph()
        
        # Detect frameworks
        self._detect_frameworks()
        
        # Update counts
        self.results['endpoint_count'] = len(self.results['api_endpoints'])
        self.results['dependency_count'] = len(self.results['dependencies'])
        self.results['frameworks'] = list(self.results['frameworks'])
        
        return self.results
    
    def _detect_api_endpoints(self):
        """Detect API endpoints across all services"""
        
        for service in self.results['services']:
            service_path = os.path.join(self.project_path, service['path'])
            service_endpoints = []
            
            # Get language for this service
            language = service.get('language', 'Unknown')
            
            for root, dirs, files in os.walk(service_path):
                for file in files:
                    if file.endswith(('.py', '.js', '.java', '.go', '.rb', '.php')):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, service_path)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                
                                # Apply language-specific patterns
                                for lang, frameworks in self.api_patterns.items():
                                    if language == lang or lang in language:
                                        for framework, patterns in frameworks.items():
                                            for pattern in patterns:
                                                matches = re.finditer(pattern, content)
                                                for match in matches:
                                                    if match.groups():
                                                        if len(match.groups()) == 2:
                                                            method, path = match.groups()
                                                            endpoint = {
                                                                'path': path,
                                                                'method': method.upper() if method else 'GET',
                                                                'framework': framework,
                                                                'file': rel_path,
                                                                'service': service['name']
                                                            }
                                                        else:
                                                            endpoint = {
                                                                'path': match.group(1),
                                                                'method': 'GET',
                                                                'framework': framework,
                                                                'file': rel_path,
                                                                'service': service['name']
                                                            }
                                                        service_endpoints.append(endpoint)
                                                        self.results['api_endpoints'].append(endpoint)
                        except:
                            pass
            
            # Add endpoints to service info
            service['endpoints'] = service_endpoints
            service['endpoint_count'] = len(service_endpoints)
    
    def _detect_dependencies(self):
        """Detect dependencies between services"""
        
        # Map service paths
        service_paths = {s['name']: s['path'] for s in self.results['services']}
        
        for service in self.results['services']:
            service_path = os.path.join(self.project_path, service['path'])
            dependencies = set()
            
            for root, dirs, files in os.walk(service_path):
                for file in files:
                    if file.endswith(('.py', '.js', '.java', '.go', '.rb', '.php')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                
                                # Look for HTTP calls to other services
                                for other_name, other_path in service_paths.items():
                                    if other_name != service['name']:
                                        patterns = [
                                            f'http://{other_name}',
                                            f'https://{other_name}',
                                            f'{other_name}.com',
                                            f'{other_path}',
                                            f'/{other_name}/'
                                        ]
                                        for pattern in patterns:
                                            if pattern in content:
                                                dependencies.add(other_name)
                                                break
                        except:
                            pass
            
            service['dependencies'] = list(dependencies)
            self.results['dependencies'][service['name']] = list(dependencies)
    
    def _build_dependency_graph(self):
        """Build NetworkX dependency graph"""
        graph = nx.DiGraph()
        
        # Add nodes
        for service in self.results['services']:
            graph.add_node(
                service['name'],
                type='service',
                service_type=service.get('language', 'Unknown'),
                endpoints=service.get('endpoint_count', 0)
            )
        
        # Add edges
        for service in self.results['services']:
            for dep in service.get('dependencies', []):
                if graph.has_node(dep):
                    graph.add_edge(service['name'], dep, type='http_call')
        
        # Convert to node-link format for JSON serialization
        self.results['dependency_graph'] = nx.node_link_data(graph)
    
    def _detect_frameworks(self):
        """Detect frameworks used in the project"""
        frameworks = set()
        
        for file_info in self.file_inventory:
            if file_info['name'] in ['package.json', 'requirements.txt', 'pom.xml', 'go.mod']:
                file_path = os.path.join(self.project_path, file_info['path'])
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Check for common frameworks
                        framework_keywords = {
                            'django': ['django'],
                            'flask': ['flask'],
                            'fastapi': ['fastapi'],
                            'react': ['react', 'react-dom'],
                            'vue': ['vue'],
                            'angular': ['angular', '@angular/core'],
                            'spring': ['spring-boot', 'spring-core'],
                            'express': ['express'],
                            'tensorflow': ['tensorflow'],
                            'pytorch': ['torch'],
                            'sklearn': ['scikit-learn']
                        }
                        
                        for framework, keywords in framework_keywords.items():
                            for keyword in keywords:
                                if keyword in content:
                                    frameworks.add(framework)
                except:
                    pass
        
        self.results['frameworks'] = list(frameworks)