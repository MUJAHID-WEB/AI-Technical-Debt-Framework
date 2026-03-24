import os
import fnmatch
import hashlib
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

class UniversalDataCollector:
    """
    TIER 1: Universal Data Collection Layer
    Works for ANY project type: microservices, React, Python, ML models, etc.
    """
    
    def __init__(self, project_path):
        self.project_path = project_path
        self.project_name = os.path.basename(project_path)
        
        self.data = {
            'project_info': {
                'name': self.project_name,
                'path': project_path,
                'scan_time': datetime.now().isoformat(),
                'language': None,
                'project_type': None,
                'file_count': 0,
                'total_size': 0
            },
            'services': [],
            'models': [],
            'pipelines': [],
            'config_files': [],
            'docker_files': [],
            'git_info': {},
            'file_inventory': [],
            'languages': defaultdict(int),
            'frameworks': set(),
            'dependencies': {},
            'statistics': {}
        }
        
        # Patterns for universal detection
        self.language_patterns = {
            'Python': ['.py', 'requirements.txt', 'setup.py', 'Pipfile'],
            'JavaScript': ['.js', '.jsx', 'package.json', 'yarn.lock'],
            'TypeScript': ['.ts', '.tsx', 'tsconfig.json'],
            'Java': ['.java', 'pom.xml', 'build.gradle', '.jar'],
            'Go': ['.go', 'go.mod', 'go.sum'],
            'Ruby': ['.rb', 'Gemfile', 'Rakefile'],
            'PHP': ['.php', 'composer.json'],
            'C#': ['.cs', '.csproj', '.sln'],
            'C++': ['.cpp', '.hpp', 'CMakeLists.txt'],
            'Rust': ['.rs', 'Cargo.toml'],
            'Swift': ['.swift', 'Podfile'],
            'Kotlin': ['.kt', 'build.gradle.kts'],
            'Dart': ['.dart', 'pubspec.yaml'],
            'R': ['.r', '.R', 'DESCRIPTION'],
            'Scala': ['.scala', 'build.sbt'],
            'HTML': ['.html', '.htm'],
            'CSS': ['.css', '.scss', '.sass', '.less']
        }
        
        self.project_type_patterns = {
            'Microservices': ['docker-compose.yml', 'service', 'microservice', 'api-gateway'],
            'Web Application': ['package.json', 'index.html', 'public/', 'src/'],
            'React App': ['react', 'jsx', 'components/', 'App.js', 'index.js'],
            'Python Application': ['app.py', 'main.py', 'flask', 'django', 'fastapi'],
            'ML Project': ['model.pkl', 'train.py', 'notebooks/', 'jupyter', 'tensorflow'],
            'Data Pipeline': ['etl', 'pipeline', 'airflow', 'dags/'],
            'Library/Package': ['setup.py', 'lib/', '__init__.py'],
            'Mobile App': ['AndroidManifest.xml', 'Info.plist', 'MainActivity.kt'],
            'Desktop App': ['main_window', 'gui', 'electron']
        }
        
        self.model_patterns = {
            'extensions': [
                '.pkl', '.pickle', '.joblib', '.sav',          # Python serialized
                '.pt', '.pth', '.ckpt',                         # PyTorch
                '.h5', '.hdf5', '.keras',                       # Keras/HDF5
                '.onnx',                                         # ONNX
                '.pb', '.pbtxt', '.tflite', '.meta',            # TensorFlow
                '.mlmodel', '.mlpackage',                        # CoreML
                '.caffemodel', '.caffemodel',                    # Caffe
                '.mar', '.torchscript',                          # PyTorch Serve
                '.pmml', '.xml',                                 # PMML/XML models
                '.bin', '.model', '.data-00000-of-00001',       # Generic
                '.weights', '.index',                            # Generic
                '.rds', '.rda',                                  # R models
                '.joblib', '.m',                                 # MATLAB/Octave
                '.tflite', '.lite'                               # TFLite
            ],
            'loading_patterns': [
                r'joblib\.load\(', r'pickle\.load\(', r'torch\.load\(',
                r'load_model\(', r'keras\.models\.load_model\(',
                r'tf\.keras\.models\.load_model\(', r'onnx\.load\(',
                r'model\.load_weights\(', r'from_pretrained\(',
                r'pmml\.load\(', r'pmml\.read\(', r'readRDS\(',
                r'keras::load_model_hdf5\(', r'load_weights\(',
                r'mlflow\.pyfunc\.load_model\(', r'bentoml\.load\('
            ]
        }
        
        self.ignore_patterns = [
            '*.pyc', '__pycache__', '*.git*', '*.idea', '*.vscode',
            'node_modules', 'venv', 'env', '.env', '*.log', '*.tmp',
            '*.cache', '*.egg-info', 'build', 'dist', '*.so', '*.dll',
            '*.dylib', '*.exe', '*.bin', '*.jpg', '*.jpeg', '*.png',
            '*.gif', '*.mp4', '*.mp3', '*.wav', '*.zip', '*.tar', '*.gz',
            'coverage', '.nyc_output', '__tests__', 'test', 'tests',
            'node_modules', 'bower_components', 'vendor'
        ]
        
    def collect_all(self):
        """Collect all data from the project"""
        print(f"\n📊 TIER 1: Collecting data from {self.project_path}")
        
        # Walk through directory and collect files
        self._walk_directory()
        
        # Detect project language and type
        self._detect_language()
        self._detect_project_type()
        
        # Detect services, models, pipelines
        self._detect_services()
        self._detect_models()
        self._detect_pipelines()
        
        # Collect git history if available
        self._collect_git_info()
        
        # Update statistics
        self._update_statistics()
        
        # Convert non-serializable types to standard Python types
        self.data['frameworks'] = list(self.data['frameworks'])
        self.data['languages'] = dict(self.data['languages'])
        
        return self.data
    
    def _walk_directory(self):
        """Walk through directory and collect file information"""
        file_count = 0
        
        for root, dirs, files in os.walk(self.project_path):
            # Filter ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]
            
            for file in files:
                if self._should_ignore(file):
                    continue
                
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.project_path)
                
                # Get file info
                stat = os.stat(file_path)
                ext = os.path.splitext(file)[1].lower()
                
                file_info = {
                    'path': rel_path,
                    'name': file,
                    'extension': ext,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'directory': os.path.dirname(rel_path)
                }
                
                self.data['file_inventory'].append(file_info)
                
                # Track language based on extension
                if ext:
                    for lang, patterns in self.language_patterns.items():
                        if ext in patterns or file in patterns:
                            self.data['languages'][lang] += 1
                            break
                
                file_count += 1
        
        self.data['project_info']['file_count'] = file_count
    
    def _detect_language(self):
        """Detect primary programming language"""
        if not self.data['languages']:
            self.data['project_info']['language'] = 'Unknown'
            return
        
        # Get most common language
        primary_lang = max(self.data['languages'], key=self.data['languages'].get)
        self.data['project_info']['language'] = primary_lang
        
        # Add all detected languages
        self.data['project_info']['all_languages'] = dict(self.data['languages'])
    
    def _detect_project_type(self):
        """Detect project type based on files and structure"""
        scores = defaultdict(int)
        file_list = [f['path'] for f in self.data['file_inventory']]
        
        for ptype, patterns in self.project_type_patterns.items():
            for pattern in patterns:
                for file in file_list:
                    if pattern in file or fnmatch.fnmatch(file, pattern):
                        scores[ptype] += 1
                if os.path.exists(os.path.join(self.project_path, pattern)):
                    scores[ptype] += 2
        
        if scores:
            self.data['project_info']['project_type'] = max(scores, key=scores.get)
            self.data['project_info']['type_scores'] = dict(scores)
        else:
            self.data['project_info']['project_type'] = 'Unknown'
    
    def _detect_services(self):
        """Detect services/microservices"""
        service_indicators = [
            'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
            'requirements.txt', 'package.json', 'setup.py', 'pom.xml',
            'build.gradle', 'Cargo.toml', 'go.mod', 'main.py', 'app.py',
            'index.js', 'server.js', 'application.py', 'wsgi.py',
            'manage.py', 'index.html', 'service.yaml', 'deployment.yaml'
        ]
        
        service_dirs = set()
        
        for root, dirs, files in os.walk(self.project_path):
            # Check for service indicators
            has_indicator = any(ind in files for ind in service_indicators)
            
            if has_indicator:
                rel_path = os.path.relpath(root, self.project_path)
                if rel_path == '.':
                    service_name = self.project_name
                else:
                    service_name = os.path.basename(root)
                
                # Don't add if it's a subdirectory of a service
                parent_is_service = False
                parent = os.path.dirname(root)
                while parent and parent != self.project_path and parent != '/':
                    if any(os.path.exists(os.path.join(parent, ind)) for ind in service_indicators):
                        parent_is_service = True
                        break
                    parent = os.path.dirname(parent)
                
                if not parent_is_service:
                    service_info = {
                        'name': service_name,
                        'path': rel_path,
                        'indicators': [ind for ind in service_indicators if ind in files],
                        'file_count': len([f for f in files if not self._should_ignore(f)]),
                        'has_docker': 'Dockerfile' in files,
                        'has_requirements': 'requirements.txt' in files or 'package.json' in files,
                        'language': self._detect_service_language(root)
                    }
                    
                    self.data['services'].append(service_info)
        
        self.data['services'].sort(key=lambda x: x['name'])
    
    def _detect_service_language(self, service_path):
        """Detect language of a service"""
        files = os.listdir(service_path)
        
        if 'requirements.txt' in files or 'setup.py' in files:
            return 'Python'
        if 'package.json' in files:
            return 'JavaScript/Node.js'
        if 'pom.xml' in files:
            return 'Java (Maven)'
        if 'build.gradle' in files:
            return 'Java (Gradle)'
        if 'go.mod' in files:
            return 'Go'
        if 'Cargo.toml' in files:
            return 'Rust'
        if 'Gemfile' in files:
            return 'Ruby'
        if 'composer.json' in files:
            return 'PHP'
        
        return 'Unknown'
    
    def _detect_models(self):
        """Detect ML models (files and in-code references)"""
        models_found = set()
        
        # Find model files by extension
        for file_info in self.data['file_inventory']:
            if file_info['extension'] in self.model_patterns['extensions']:
                model_info = {
                    'name': file_info['name'],
                    'path': file_info['path'],
                    'type': self._get_model_type(file_info['extension']),
                    'size': file_info['size'],
                    'modified': file_info['modified'],
                    'detected_by': 'file_extension'
                }
                
                # Avoid duplicates
                model_key = f"{file_info['path']}:{file_info['size']}"
                if model_key not in models_found:
                    models_found.add(model_key)
                    self.data['models'].append(model_info)
        
        # Find model references in code
        code_files = [f for f in self.data['file_inventory'] 
                     if f['extension'] in ['.py', '.js', '.java', '.r', '.ipynb']]
        
        for file_info in code_files:
            file_path = os.path.join(self.project_path, file_info['path'])
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    for pattern in self.model_patterns['loading_patterns']:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            # Try to extract model name/path
                            line_start = max(0, match.start() - 50)
                            line_end = min(len(content), match.end() + 50)
                            context = content[line_start:line_end]
                            
                            model_ref = self._extract_model_reference(context)
                            
                            if model_ref:
                                model_info = {
                                    'name': model_ref,
                                    'path': file_info['path'],
                                    'type': 'Inferred',
                                    'detected_by': 'code_reference',
                                    'context': context[:100] + '...'
                                }
                                
                                model_key = f"{file_info['path']}:{model_ref}"
                                if model_key not in models_found:
                                    models_found.add(model_key)
                                    self.data['models'].append(model_info)
            except:
                pass
    
    def _get_model_type(self, extension):
        """Get model type from extension"""
        types = {
            '.pkl': 'Pickle',
            '.pickle': 'Pickle',
            '.joblib': 'Joblib',
            '.sav': 'Pickle/Joblib',
            '.pt': 'PyTorch',
            '.pth': 'PyTorch',
            '.ckpt': 'Checkpoint',
            '.h5': 'Keras/HDF5',
            '.hdf5': 'HDF5',
            '.keras': 'Keras',
            '.onnx': 'ONNX',
            '.pb': 'TensorFlow',
            '.tflite': 'TensorFlow Lite',
            '.mlmodel': 'CoreML',
            '.caffemodel': 'Caffe',
            '.mar': 'PyTorch MAR',
            '.pmml': 'PMML',
            '.bin': 'Binary Model',
            '.model': 'Generic Model',
            '.rds': 'R Model',
            '.rda': 'R Data'
        }
        return types.get(extension, 'Unknown')
    
    def _extract_model_reference(self, text):
        """Extract model name/reference from text"""
        # Look for quoted strings that look like model files
        matches = re.findall(r'[\'"]([^\'"]*\.(?:pkl|pt|h5|onnx|pb|joblib|sav))[\'"]', text)
        if matches:
            return matches[0]
        
        # Look for variable names with 'model' in them
        matches = re.findall(r'(\w*model\w*)\s*=', text)
        if matches:
            return matches[0]
        
        return None
    
    def _detect_pipelines(self):
        """Detect data/ML pipelines"""
        pipeline_patterns = [
            '*pipeline*', '*etl*', '*extract*', '*transform*', '*load*',
            '*feature*', '*preprocess*', '*postprocess*', '*train*', '*evaluate*',
            '*inference*', '*prediction*', '*model_serving*', 'dags/',
            '*airflow*', '*beam*', '*spark*', '*flink*', '*kafka*'
        ]
        
        pipeline_dirs = set()
        
        for root, dirs, files in os.walk(self.project_path):
            for pattern in pipeline_patterns:
                if fnmatch.fnmatch(os.path.basename(root).lower(), pattern):
                    pipeline_dirs.add(root)
                for file in files:
                    if fnmatch.fnmatch(file.lower(), pattern):
                        pipeline_dirs.add(root)
        
        for pipeline_dir in pipeline_dirs:
            rel_path = os.path.relpath(pipeline_dir, self.project_path)
            
            # Get all files in pipeline
            pipeline_files = []
            for root, dirs, files in os.walk(pipeline_dir):
                for file in files:
                    if file.endswith(('.py', '.sql', '.ipynb', '.sh', '.java', '.scala')):
                        file_path = os.path.relpath(os.path.join(root, file), self.project_path)
                        pipeline_files.append(file_path)
            
            if pipeline_files:
                self.data['pipelines'].append({
                    'name': os.path.basename(pipeline_dir),
                    'path': rel_path,
                    'stages': len(pipeline_files),
                    'files': pipeline_files[:10]  # Limit to 10 files
                })
    
    def _collect_git_info(self):
        """Collect git repository information"""
        git_path = os.path.join(self.project_path, '.git')
        if os.path.exists(git_path):
            try:
                import subprocess
                
                # Get remote URL
                result = subprocess.run(
                    ['git', 'remote', 'get-url', 'origin'],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.data['git_info']['remote'] = result.stdout.strip()
                
                # Get last commit
                result = subprocess.run(
                    ['git', 'log', '-1', '--pretty=format:%h|%an|%ad|%s', '--date=iso'],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout:
                    parts = result.stdout.split('|', 3)
                    if len(parts) == 4:
                        self.data['git_info']['last_commit'] = {
                            'hash': parts[0],
                            'author': parts[1],
                            'date': parts[2],
                            'message': parts[3]
                        }
                
                # Get commit count
                result = subprocess.run(
                    ['git', 'rev-list', '--count', 'HEAD'],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.data['git_info']['commit_count'] = int(result.stdout.strip())
                    
            except Exception as e:
                print(f"  Warning: Git info collection failed: {e}")
    
    def _update_statistics(self):
        """Update statistics about the scan"""
        total_files = len(self.data['file_inventory'])
        total_size = sum(f['size'] for f in self.data['file_inventory'])
        
        # Group by extension
        extensions = defaultdict(int)
        for file in self.data['file_inventory']:
            ext = file['extension'] or 'no_extension'
            extensions[ext] += 1
        
        def format_bytes(size):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024:
                    return f"{size:.2f} {unit}"
                size /= 1024
            return f"{size:.2f} PB"

        self.data['statistics'] = {
            'total_files': total_files,
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'total_size_hr': format_bytes(total_size),
            'file_types': dict(extensions),
            'services_count': len(self.data['services']),
            'models_count': len(self.data['models']),
            'pipelines_count': len(self.data['pipelines'])
        }
        
        self.data['project_info']['total_size'] = total_size
    
    def _should_ignore(self, name):
        """Check if file/directory should be ignored"""
        return any(fnmatch.fnmatch(name, pattern) for pattern in self.ignore_patterns)
    
    def summary(self):
        """Generate summary of collected data"""
        info = self.data['project_info']
        stats = self.data['statistics']
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    TIER 1: DATA COLLECTION                   ║
╠════════════════════════════════════════════════════════════════╣
║ Project: {info['name'][:50]:<50} ║
║ Language: {info['language'][:20]:<20}                         ║
║ Type: {info['project_type'][:20]:<20}                         ║
╠════════════════════════════════════════════════════════════════╣
║ Total Files:    {stats.get('total_files', 0):>8}                               ║
║ Total Size:     {stats.get('total_size_mb', 0):>8} MB                           ║
╠════════════════════════════════════════════════════════════════╣
║ Services Found:     {stats.get('services_count', 0):>8}                        ║
║ Models Found:       {stats.get('models_count', 0):>8}                        ║
║ Pipelines Found:    {stats.get('pipelines_count', 0):>8}                        ║
╚════════════════════════════════════════════════════════════════╝
"""