import os
import fnmatch
import hashlib
import json
import zipfile
import tarfile
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import subprocess
import re

class LocalScanner:
    """
    Local Repository Scanner
    Scans local directories and archives for project analysis
    """
    
    def __init__(self, base_path=None):
        self.base_path = base_path or os.getcwd()
        self.scanned_data = {
            'project_info': {
                'name': '',
                'path': '',
                'scan_time': datetime.now().isoformat(),
                'size': 0,
                'file_count': 0
            },
            'services': [],
            'models': [],
            'pipelines': [],
            'config_files': [],
            'docker_files': [],
            'git_info': {},
            'dependencies': {},
            'file_inventory': [],
            'statistics': {}
        }
        
        # Patterns for detection
        self.service_indicators = [
            'Dockerfile',
            'docker-compose.yml',
            'docker-compose.yaml',
            'requirements.txt',
            'package.json',
            'setup.py',
            'pom.xml',
            'build.gradle',
            'Cargo.toml',
            'go.mod',
            'main.py',
            'app.py',
            'application.py',
            'wsgi.py',
            'manage.py',
            'index.js',
            'server.js',
            'app.js',
            'main.go',
            'main.java'
        ]
        
        self.model_extensions = [
            '.pkl', '.pickle', '.joblib', '.sav',
            '.pt', '.pth', '.ckpt', '.bin',
            '.h5', '.hdf5', '.keras',
            '.onnx',
            '.pb', '.pbtxt', '.tflite',
            '.mlmodel', '.caffemodel',
            '.mar', '.torchscript',
            '.pmml', '.xml',
            '.rds', '.rda',
            '.model', '.weights'
        ]
        
        self.pipeline_patterns = [
            '*pipeline*', '*etl*', '*extract*', '*transform*', '*load*',
            '*feature*', '*preprocess*', '*postprocess*', '*train*', '*evaluate*',
            '*inference*', '*prediction*', '*model_serving*', '*dags*',
            '*airflow*', '*spark*', '*flink*', '*beam*', '*kafka*'
        ]
        
        self.ignore_patterns = [
            '*.pyc', '__pycache__', '*.git*', '*.idea', '*.vscode',
            'node_modules', 'venv', 'env', '.env', '*.log', '*.tmp',
            '*.cache', '*.egg-info', 'build', 'dist', '*.so', '*.dll',
            '*.dylib', '*.exe', '*.bin', '*.jpg', '*.jpeg', '*.png',
            '*.gif', '*.mp4', '*.mp3', '*.wav', '*.zip', '*.tar', '*.gz',
            'coverage', '.nyc_output', '__tests__', 'test', 'tests',
            'node_modules', 'bower_components', 'vendor', '.gradle',
            '.mvn', 'target', '.idea', '.vscode', '.DS_Store'
        ]
    
    def scan_directory(self, path, recursive=True):
        """
        Scan a directory for project files
        
        Args:
            path: Path to scan
            recursive: Whether to scan subdirectories recursively
            
        Returns:
            Dictionary containing scanned data
        """
        print(f"\n📁 Scanning directory: {path}")
        
        self.base_path = path
        self.scanned_data = {
            'project_info': {
                'path': os.path.abspath(path),
                'name': os.path.basename(path),
                'scan_time': datetime.now().isoformat(),
                'size': self._get_directory_size(path)
            },
            'services': [],
            'models': [],
            'pipelines': [],
            'config_files': [],
            'docker_files': [],
            'git_info': {},
            'dependencies': {},
            'file_inventory': [],
            'statistics': {}
        }
        
        file_count = 0
        dir_count = 0
        
        # Walk through directory
        for root, dirs, files in os.walk(path):
            # Filter ignored directories
            original_dirs = dirs.copy()
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]
            dir_count += len(original_dirs) - len(dirs)
            
            # Filter ignored files
            files = [f for f in files if not self._should_ignore(f)]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, path)
                
                # Collect file info
                file_info = self._get_file_info(file_path, rel_path)
                self.scanned_data['file_inventory'].append(file_info)
                
                # Categorize files
                self._categorize_file(file_info, file_path)
                
                file_count += 1
        
        # Detect services
        self._detect_services(path)
        
        # Detect models in code
        self._detect_models_in_code(path)
        
        # Detect pipelines
        self._detect_pipelines(path)
        
        # Parse dependency files
        self._parse_dependency_files(path)
        
        # Collect git history if available
        self._collect_git_info(path)
        
        # Detect project type and languages
        self._detect_project_type()
        self._detect_languages()
        
        # Update statistics
        self._update_statistics()
        
        print(f"✅ Scan complete:")
        print(f"   - {file_count} files processed")
        print(f"   - {len(self.scanned_data['services'])} services found")
        print(f"   - {len(self.scanned_data['models'])} models found")
        print(f"   - {len(self.scanned_data['pipelines'])} pipelines found")
        
        return self.scanned_data
    
    def scan_zip(self, zip_path, extract_to=None):
        """
        Scan a ZIP file containing a project
        
        Args:
            zip_path: Path to ZIP file
            extract_to: Directory to extract to (if None, uses temp dir)
            
        Returns:
            Dictionary containing scanned data
        """
        print(f"📦 Scanning ZIP file: {zip_path}")
        
        if extract_to is None:
            extract_to = tempfile.mkdtemp(prefix='aidebt_scan_')
            self._temp_dir = extract_to
        else:
            os.makedirs(extract_to, exist_ok=True)
        
        try:
            # Extract based on file type
            if zip_path.endswith('.zip'):
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
                    print(f"   Extracted {len(zip_ref.namelist())} files")
            
            elif zip_path.endswith(('.tar.gz', '.tgz')):
                with tarfile.open(zip_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(extract_to)
                    print(f"   Extracted {len(tar_ref.getmembers())} files")
            
            elif zip_path.endswith('.tar.bz2'):
                with tarfile.open(zip_path, 'r:bz2') as tar_ref:
                    tar_ref.extractall(extract_to)
            
            elif zip_path.endswith('.tar'):
                with tarfile.open(zip_path, 'r:') as tar_ref:
                    tar_ref.extractall(extract_to)
            
            else:
                raise ValueError(f"Unsupported archive format: {zip_path}")
            
            # Find the actual project root (might be in a subfolder)
            project_root = self._find_project_root(extract_to)
            
            # Scan the extracted directory
            results = self.scan_directory(project_root)
            
            # Add ZIP info
            results['project_info']['source'] = 'zip'
            results['project_info']['zip_file'] = os.path.basename(zip_path)
            results['project_info']['zip_size'] = os.path.getsize(zip_path)
            results['project_info']['extract_path'] = extract_to
            
            return results
            
        except Exception as e:
            print(f"❌ Error scanning ZIP: {e}")
            # Clean up if we created temp dir
            if extract_to and hasattr(self, '_temp_dir'):
                shutil.rmtree(extract_to, ignore_errors=True)
            raise
    
    def _find_project_root(self, extract_path):
        """Find the actual project root (handles nested folders)"""
        items = os.listdir(extract_path)
        
        # If there's only one directory and it's not a known structure, go into it
        if len(items) == 1:
            single_item = os.path.join(extract_path, items[0])
            if os.path.isdir(single_item) and not items[0].startswith('.'):
                # Check if this directory contains project files
                sub_items = os.listdir(single_item)
                if any(f in sub_items for f in ['src', 'lib', 'package.json', 
                                                'requirements.txt', 'pom.xml', 
                                                'Dockerfile']):
                    return single_item
        
        return extract_path
    
    def _get_file_info(self, file_path, rel_path):
        """Get detailed information about a file"""
        stat = os.stat(file_path)
        
        # Get file hash for change detection
        file_hash = self._calculate_hash(file_path)
        
        return {
            'path': rel_path,
            'full_path': file_path,
            'name': os.path.basename(file_path),
            'extension': os.path.splitext(file_path)[1].lower(),
            'size': stat.st_size,
            'size_hr': self._format_size(stat.st_size),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
            'hash': file_hash,
            'lines': self._count_lines(file_path) if file_path.endswith(('.py', '.js', '.java', '.go', '.rb', '.php', '.r')) else None
        }
    
    def _calculate_hash(self, file_path, algorithm='md5'):
        """Calculate file hash"""
        hash_func = hashlib.new(algorithm)
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except:
            return None
    
    def _format_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def _count_lines(self, file_path):
        """Count lines in a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def _categorize_file(self, file_info, file_path):
        """Categorize file based on its type and content"""
        name = file_info['name']
        ext = file_info['extension']
        
        # Model files
        if ext in self.model_extensions:
            self.scanned_data['models'].append({
                'name': name,
                'path': file_info['path'],
                'type': self._get_model_type(ext),
                'size': file_info['size'],
                'size_hr': file_info['size_hr'],
                'modified': file_info['modified'],
                'hash': file_info['hash']
            })
        
        # Docker files
        if name in ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml']:
            self.scanned_data['docker_files'].append(file_info)
            
            # Parse docker-compose for service info
            if 'docker-compose' in name:
                self._parse_docker_compose(file_path)
        
        # Config files
        if ext in ['.yml', '.yaml', '.json', '.toml', '.ini', '.cfg', '.conf', '.properties']:
            self.scanned_data['config_files'].append(file_info)
    
    def _get_model_type(self, extension):
        """Get model type from file extension"""
        types = {
            '.pkl': 'Pickle',
            '.pickle': 'Pickle',
            '.joblib': 'Joblib',
            '.sav': 'Pickle/Joblib',
            '.pt': 'PyTorch',
            '.pth': 'PyTorch',
            '.ckpt': 'Checkpoint',
            '.bin': 'Binary Model',
            '.h5': 'Keras/HDF5',
            '.hdf5': 'HDF5',
            '.keras': 'Keras',
            '.onnx': 'ONNX',
            '.pb': 'TensorFlow',
            '.pbtxt': 'TensorFlow Text',
            '.tflite': 'TensorFlow Lite',
            '.mlmodel': 'CoreML',
            '.caffemodel': 'Caffe',
            '.mar': 'PyTorch MAR',
            '.torchscript': 'TorchScript',
            '.pmml': 'PMML',
            '.xml': 'XML Model',
            '.rds': 'R Model',
            '.rda': 'R Data',
            '.model': 'Generic Model',
            '.weights': 'Model Weights'
        }
        return types.get(extension, 'Unknown')
    
    def _detect_services(self, base_path):
        """Detect microservices in the codebase"""
        service_dirs = set()
        
        for root, dirs, files in os.walk(base_path):
            # Check for service indicators
            has_indicator = any(indicator in files for indicator in self.service_indicators)
            
            if has_indicator:
                rel_path = os.path.relpath(root, base_path)
                if rel_path == '.':
                    service_name = os.path.basename(base_path)
                else:
                    service_name = os.path.basename(root)
                
                # Don't add if it's just a subdirectory of a service
                parent_is_service = False
                parent = os.path.dirname(root)
                while parent and parent != base_path and parent != '/':
                    if any(os.path.exists(os.path.join(parent, ind)) for ind in self.service_indicators):
                        parent_is_service = True
                        break
                    parent = os.path.dirname(parent)
                
                if not parent_is_service:
                    service_info = {
                        'name': service_name,
                        'path': rel_path,
                        'full_path': root,
                        'indicators': [ind for ind in self.service_indicators if ind in files],
                        'file_count': len([f for f in files if not self._should_ignore(f)]),
                        'has_docker': 'Dockerfile' in files,
                        'has_requirements': 'requirements.txt' in files,
                        'has_package_json': 'package.json' in files,
                        'has_pom': 'pom.xml' in files,
                        'language': self._detect_service_language(root)
                    }
                    
                    self.scanned_data['services'].append(service_info)
        
        self.scanned_data['services'].sort(key=lambda x: x['name'])
    
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
        if 'main.py' in files or 'app.py' in files:
            return 'Python'
        if 'index.js' in files or 'server.js' in files:
            return 'JavaScript'
        if 'main.go' in files:
            return 'Go'
        if 'main.java' in files:
            return 'Java'
        
        # Check file extensions
        py_files = [f for f in files if f.endswith('.py')]
        if py_files:
            return 'Python'
        
        js_files = [f for f in files if f.endswith('.js')]
        if js_files:
            return 'JavaScript'
        
        java_files = [f for f in files if f.endswith('.java')]
        if java_files:
            return 'Java'
        
        return 'Unknown'
    
    def _detect_models_in_code(self, base_path):
        """Detect model loading and usage in code files"""
        model_patterns = [
            r'joblib\.load\([\'"]([^\'"]+\.(?:pkl|joblib))[\'"]',
            r'pickle\.load\([\'"]([^\'"]+\.(?:pkl|pickle))[\'"]',
            r'torch\.load\([\'"]([^\'"]+\.(?:pt|pth))[\'"]',
            r'keras\.models\.load_model\([\'"]([^\'"]+\.(?:h5|keras))[\'"]',
            r'tf\.keras\.models\.load_model\([\'"]([^\'"]+\.(?:h5|keras))[\'"]',
            r'onnx\.load\([\'"]([^\'"]+\.onnx)[\'"]',
            r'model = [\w]+\(pretrained=[Tt]rue\)',
            r'from_pretrained\([\'"]([^\'"]+)[\'"]',
            r'load_weights\([\'"]([^\'"]+)[\'"]',
            r'readRDS\([\'"]([^\'"]+\.rds)[\'"]'
        ]
        
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith(('.py', '.ipynb', '.r', '.R', '.js')):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, base_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            for pattern in model_patterns:
                                matches = re.finditer(pattern, content)
                                for match in matches:
                                    model_ref = match.group(1) if match.groups() else match.group(0)
                                    
                                    # Check if this model is already in our list
                                    model_found = False
                                    for model in self.scanned_data['models']:
                                        if model['name'] in model_ref or model_ref in model['path']:
                                            model_found = True
                                            # Add consumer
                                            if 'consumers' not in model:
                                                model['consumers'] = []
                                            model['consumers'].append({
                                                'file': rel_path,
                                                'line': self._get_line_number(content, match.start()),
                                                'context': self._get_context(content, match.start())
                                            })
                                            break
                                    
                                    if not model_found:
                                        # New model detected in code
                                        self.scanned_data['models'].append({
                                            'name': os.path.basename(model_ref) if '/' in model_ref else model_ref,
                                            'path': model_ref,
                                            'type': 'Inferred',
                                            'size': 0,
                                            'size_hr': 'Unknown',
                                            'modified': None,
                                            'consumers': [{
                                                'file': rel_path,
                                                'line': self._get_line_number(content, match.start()),
                                                'context': self._get_context(content, match.start())
                                            }],
                                            'inferred': True
                                        })
                    except Exception as e:
                        pass
    
    def _get_line_number(self, content, position):
        """Get line number from character position"""
        return content.count('\n', 0, position) + 1
    
    def _get_context(self, content, position, window=50):
        """Get context around a position"""
        start = max(0, position - window)
        end = min(len(content), position + window)
        return content[start:end].replace('\n', ' ').strip()
    
    def _detect_pipelines(self, base_path):
        """Detect data pipelines in the codebase"""
        pipeline_dirs = set()
        
        for root, dirs, files in os.walk(base_path):
            for pattern in self.pipeline_patterns:
                if fnmatch.fnmatch(os.path.basename(root).lower(), pattern):
                    pipeline_dirs.add(root)
                for file in files:
                    if fnmatch.fnmatch(file.lower(), pattern):
                        pipeline_dirs.add(root)
        
        for pipeline_dir in pipeline_dirs:
            rel_path = os.path.relpath(pipeline_dir, base_path)
            
            # Get all files in pipeline
            pipeline_files = []
            for root, dirs, files in os.walk(pipeline_dir):
                for file in files:
                    if file.endswith(('.py', '.sql', '.ipynb', '.sh', '.java', '.scala', '.r')):
                        pipeline_files.append({
                            'name': file,
                            'path': os.path.relpath(os.path.join(root, file), base_path),
                            'size': os.path.getsize(os.path.join(root, file))
                        })
            
            # Calculate complexity
            complexity = self._calculate_pipeline_complexity(pipeline_dir)
            
            self.scanned_data['pipelines'].append({
                'name': os.path.basename(pipeline_dir),
                'path': rel_path,
                'stages': len(pipeline_files),
                'files': pipeline_files[:20],  # Limit to 20 files
                'complexity': complexity
            })
    
    def _calculate_pipeline_complexity(self, pipeline_dir):
        """Calculate complexity score for a pipeline"""
        complexity = 1.0
        
        for root, dirs, files in os.walk(pipeline_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            # Count conditional branches
                            if_count = content.count('if ')
                            elif_count = content.count('elif ')
                            else_count = content.count('else:')
                            
                            complexity += (if_count + elif_count + else_count) * 0.1
                            
                            # Count loops
                            for_count = content.count('for ')
                            while_count = content.count('while ')
                            complexity += (for_count + while_count) * 0.1
                            
                            # Count function calls
                            complexity += content.count('def ') * 0.2
                            
                            # Check for branching in data flow
                            if 'branch' in content or 'case' in content:
                                complexity += 0.5
                    except:
                        pass
        
        return round(complexity, 2)
    
    def _parse_docker_compose(self, file_path):
        """Parse docker-compose file for service information"""
        try:
            import yaml
            with open(file_path, 'r') as f:
                compose = yaml.safe_load(f)
            
            if compose and 'services' in compose:
                for service_name, config in compose['services'].items():
                    # Find corresponding service in our list
                    for service in self.scanned_data['services']:
                        if service['name'] == service_name or service_name in service['path']:
                            service['docker_compose'] = {
                                'image': config.get('image'),
                                'build': config.get('build'),
                                'ports': config.get('ports', []),
                                'environment': list(config.get('environment', {}).keys()) if isinstance(config.get('environment'), dict) else config.get('environment', []),
                                'volumes': config.get('volumes', []),
                                'depends_on': config.get('depends_on', [])
                            }
                            
                            # Check for model mounts
                            for volume in config.get('volumes', []):
                                if 'model' in volume.lower() or 'ml' in volume.lower():
                                    if 'model_mounts' not in service:
                                        service['model_mounts'] = []
                                    service['model_mounts'].append(volume)
        except Exception as e:
            print(f"   Warning: Could not parse docker-compose: {e}")
    
    def _parse_dependency_files(self, base_path):
        """Parse various dependency files"""
        # Find all requirements.txt
        for root, dirs, files in os.walk(base_path):
            if 'requirements.txt' in files:
                rel_path = os.path.relpath(root, base_path)
                req_path = os.path.join(root, 'requirements.txt')
                try:
                    with open(req_path, 'r') as f:
                        deps = []
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                deps.append(line)
                        self.scanned_data['dependencies'][rel_path] = {
                            'type': 'pip',
                            'file': req_path,
                            'dependencies': deps
                        }
                except:
                    pass
            
            if 'package.json' in files:
                rel_path = os.path.relpath(root, base_path)
                pkg_path = os.path.join(root, 'package.json')
                try:
                    with open(pkg_path, 'r') as f:
                        pkg = json.load(f)
                        self.scanned_data['dependencies'][rel_path] = {
                            'type': 'npm',
                            'file': pkg_path,
                            'dependencies': pkg.get('dependencies', {}),
                            'devDependencies': pkg.get('devDependencies', {})
                        }
                except:
                    pass
            
            if 'pom.xml' in files:
                rel_path = os.path.relpath(root, base_path)
                self.scanned_data['dependencies'][rel_path] = {
                    'type': 'maven',
                    'file': os.path.join(root, 'pom.xml')
                }
    
    def _collect_git_info(self, base_path):
        """Collect git repository information"""
        git_path = os.path.join(base_path, '.git')
        if os.path.exists(git_path):
            try:
                # Get basic repo info
                result = subprocess.run(
                    ['git', 'remote', 'get-url', 'origin'],
                    cwd=base_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.scanned_data['git_info']['remote'] = result.stdout.strip()
                
                # Get current branch
                result = subprocess.run(
                    ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                    cwd=base_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.scanned_data['git_info']['branch'] = result.stdout.strip()
                
                # Get last commit
                result = subprocess.run(
                    ['git', 'log', '-1', '--pretty=format:%h|%an|%ad|%s', '--date=iso'],
                    cwd=base_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0 and result.stdout:
                    parts = result.stdout.split('|', 3)
                    if len(parts) == 4:
                        self.scanned_data['git_info']['last_commit'] = {
                            'hash': parts[0],
                            'author': parts[1],
                            'date': parts[2],
                            'message': parts[3]
                        }
                
                # Get commit count
                result = subprocess.run(
                    ['git', 'rev-list', '--count', 'HEAD'],
                    cwd=base_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.scanned_data['git_info']['commit_count'] = int(result.stdout.strip())
                
                # Get contributors
                result = subprocess.run(
                    ['git', 'shortlog', '-sn', '--all'],
                    cwd=base_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                contributors = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.strip().split('\t')
                        if len(parts) == 2:
                            contributors.append({
                                'commits': int(parts[0]),
                                'name': parts[1]
                            })
                
                self.scanned_data['contributors'] = contributors
                
            except Exception as e:
                print(f"   Warning: Git info collection failed: {e}")
    
    def _detect_project_type(self):
        """Detect project type based on files"""
        files = [f['name'] for f in self.scanned_data['file_inventory']]
        paths = [f['path'] for f in self.scanned_data['file_inventory']]
        
        project_types = []
        
        # Check for microservices
        if len(self.scanned_data['services']) > 1:
            project_types.append('Microservices')
        
        # Check for web application
        if any('package.json' in f for f in files) and any(f.endswith('.html') for f in files):
            project_types.append('Web Application')
        
        # Check for ML project
        if self.scanned_data['models'] or any('train.py' in f for f in files):
            project_types.append('Machine Learning')
        
        # Check for data pipeline
        if self.scanned_data['pipelines'] or any('pipeline' in f for f in paths):
            project_types.append('Data Pipeline')
        
        # Check for API service
        if any(f in ['app.py', 'main.py', 'server.js', 'api.py'] for f in files):
            project_types.append('API Service')
        
        # Check for library
        if 'setup.py' in files or '__init__.py' in files:
            project_types.append('Library/Package')
        
        self.scanned_data['project_info']['project_types'] = project_types
    
    def _detect_languages(self):
        """Detect programming languages used"""
        languages = defaultdict(int)
        
        for file_info in self.scanned_data['file_inventory']:
            ext = file_info['extension']
            
            # Map extension to language
            if ext in ['.py', '.py3']:
                languages['Python'] += 1
            elif ext in ['.js', '.jsx']:
                languages['JavaScript'] += 1
            elif ext in ['.ts', '.tsx']:
                languages['TypeScript'] += 1
            elif ext in ['.java']:
                languages['Java'] += 1
            elif ext in ['.go']:
                languages['Go'] += 1
            elif ext in ['.rb']:
                languages['Ruby'] += 1
            elif ext in ['.php']:
                languages['PHP'] += 1
            elif ext in ['.cs']:
                languages['C#'] += 1
            elif ext in ['.cpp', '.c', '.h']:
                languages['C/C++'] += 1
            elif ext in ['.rs']:
                languages['Rust'] += 1
            elif ext in ['.swift']:
                languages['Swift'] += 1
            elif ext in ['.kt']:
                languages['Kotlin'] += 1
            elif ext in ['.r', '.R']:
                languages['R'] += 1
            elif ext in ['.scala']:
                languages['Scala'] += 1
            elif ext in ['.sql']:
                languages['SQL'] += 1
            elif ext in ['.html', '.htm']:
                languages['HTML'] += 1
            elif ext in ['.css', '.scss', '.sass']:
                languages['CSS'] += 1
            elif ext in ['.sh', '.bash']:
                languages['Shell'] += 1
            elif ext in ['.yml', '.yaml']:
                languages['YAML'] += 1
            elif ext in ['.json']:
                languages['JSON'] += 1
            elif ext in ['.md']:
                languages['Markdown'] += 1
        
        self.scanned_data['languages'] = dict(languages)
        
        # Determine primary language
        if languages:
            primary = max(languages, key=languages.get)
            self.scanned_data['project_info']['primary_language'] = primary
    
    def _update_statistics(self):
        """Update statistics about the scan"""
        total_files = len(self.scanned_data['file_inventory'])
        total_size = sum(f['size'] for f in self.scanned_data['file_inventory'])
        
        # Group by extension
        extensions = defaultdict(int)
        for file in self.scanned_data['file_inventory']:
            ext = file['extension'] or 'no_extension'
            extensions[ext] += 1
        
        self.scanned_data['statistics'] = {
            'total_files': total_files,
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'total_size_hr': self._format_size(total_size),
            'file_types': dict(sorted(extensions.items(), key=lambda x: x[1], reverse=True)),
            'services_count': len(self.scanned_data['services']),
            'models_count': len(self.scanned_data['models']),
            'pipelines_count': len(self.scanned_data['pipelines']),
            'config_files_count': len(self.scanned_data['config_files']),
            'docker_files_count': len(self.scanned_data['docker_files'])
        }
    
    def _should_ignore(self, name):
        """Check if a file/directory should be ignored"""
        return any(fnmatch.fnmatch(name, pattern) for pattern in self.ignore_patterns)
    
    def _get_directory_size(self, path):
        """Get total size of directory in bytes"""
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir() and not self._should_ignore(entry.name):
                    total += self._get_directory_size(entry.path)
        except:
            pass
        return total
    
    def export_results(self, output_path, format='json'):
        """
        Export scan results to file
        
        Args:
            output_path: Path to output file
            format: Output format (json, yaml)
        """
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(self.scanned_data, f, indent=2, default=str)
            print(f"✅ Results exported to {output_path}")
            
        elif format == 'yaml':
            try:
                import yaml
                with open(output_path, 'w') as f:
                    yaml.dump(self.scanned_data, f, default_flow_style=False)
                print(f"✅ Results exported to {output_path}")
            except ImportError:
                print("❌ PyYAML not installed. Install with: pip install pyyaml")
        else:
            print(f"❌ Unsupported format: {format}")
    
    def cleanup(self):
        """Clean up temporary files"""
        if hasattr(self, '_temp_dir') and os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir, ignore_errors=True)
            print(f"🧹 Cleaned up temporary directory: {self._temp_dir}")
    
    def summary(self):
        """Generate a human-readable summary of the scan"""
        info = self.scanned_data['project_info']
        stats = self.scanned_data['statistics']
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                 LOCAL SCAN SUMMARY                            ║
╠════════════════════════════════════════════════════════════════╣
║ Project: {info['name'][:50]:<50} ║
║ Path: {info['path'][:50]:<50} ║
║ Languages: {self.scanned_data.get('project_info', {}).get('primary_language', 'Unknown'):<20} ║
║ Types: {', '.join(self.scanned_data.get('project_info', {}).get('project_types', ['Unknown']))[:40]:<40} ║
╠════════════════════════════════════════════════════════════════╣
║ Total Files:    {stats.get('total_files', 0):>8}                               ║
║ Total Size:     {stats.get('total_size_hr', '0 B'):>8}                           ║
╠════════════════════════════════════════════════════════════════╣
║ Services Found:     {stats.get('services_count', 0):>8}                        ║
║ Models Found:       {stats.get('models_count', 0):>8}                        ║
║ Pipelines Found:    {stats.get('pipelines_count', 0):>8}                        ║
║ Config Files:       {stats.get('config_files_count', 0):>8}                        ║
║ Docker Files:       {stats.get('docker_files_count', 0):>8}                        ║
╚════════════════════════════════════════════════════════════════╝
"""