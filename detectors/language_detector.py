import os
import re
from collections import defaultdict
from pathlib import Path

class LanguageDetector:
    """
    Universal Language Detector
    Detects programming languages and frameworks in any project
    """
    
    def __init__(self):
        # Language definitions with file extensions and indicators
        self.languages = {
            'Python': {
                'extensions': ['.py', '.py3', '.pyx', '.pxd', '.pyi', '.ipynb'],
                'indicators': ['requirements.txt', 'setup.py', 'Pipfile', 'pyproject.toml'],
                'frameworks': {
                    'flask': ['flask', 'Flask'],
                    'django': ['django', 'Django'],
                    'fastapi': ['fastapi', 'FastAPI'],
                    'tensorflow': ['tensorflow', 'tf.'],
                    'pytorch': ['torch', 'pytorch'],
                    'scikit-learn': ['sklearn', 'scikit-learn'],
                    'pandas': ['pandas', 'pd.'],
                    'numpy': ['numpy', 'np.'],
                }
            },
            'JavaScript': {
                'extensions': ['.js', '.jsx', '.mjs', '.cjs'],
                'indicators': ['package.json', 'package-lock.json', 'yarn.lock'],
                'frameworks': {
                    'react': ['react', 'React'],
                    'vue': ['vue', 'Vue'],
                    'angular': ['angular', '@angular'],
                    'express': ['express', 'Express'],
                    'node': ['node', 'Node'],
                    'next': ['next', 'Next.js'],
                    'jquery': ['jquery', '$(']
                }
            },
            'TypeScript': {
                'extensions': ['.ts', '.tsx'],
                'indicators': ['tsconfig.json', 'typescript'],
                'frameworks': {
                    'angular': ['@angular'],
                    'react': ['react', '@types/react'],
                    'nestjs': ['@nestjs'],
                    'next': ['next'],
                }
            },
            'Java': {
                'extensions': ['.java', '.class', '.jar'],
                'indicators': ['pom.xml', 'build.gradle', 'mvnw', 'gradlew'],
                'frameworks': {
                    'spring': ['spring', 'Spring', '@SpringBoot'],
                    'hibernate': ['hibernate', 'Hibernate'],
                    'junit': ['junit', 'JUnit'],
                    'maven': ['maven', 'Maven'],
                    'gradle': ['gradle', 'Gradle'],
                }
            },
            'Go': {
                'extensions': ['.go'],
                'indicators': ['go.mod', 'go.sum', 'Gopkg.toml'],
                'frameworks': {
                    'gin': ['gin', 'Gin'],
                    'echo': ['echo', 'Echo'],
                    'fiber': ['fiber', 'Fiber'],
                    'gorilla': ['gorilla'],
                }
            },
            'Ruby': {
                'extensions': ['.rb', '.erb', '.rake'],
                'indicators': ['Gemfile', 'Rakefile', '*.gemspec'],
                'frameworks': {
                    'rails': ['rails', 'Rails'],
                    'sinatra': ['sinatra', 'Sinatra'],
                    'rspec': ['rspec'],
                }
            },
            'PHP': {
                'extensions': ['.php', '.phtml', '.php3', '.php4', '.php5', '.php7'],
                'indicators': ['composer.json', 'composer.lock'],
                'frameworks': {
                    'laravel': ['laravel', 'Laravel'],
                    'symfony': ['symfony', 'Symfony'],
                    'wordpress': ['wp-', 'wordpress'],
                    'codeigniter': ['codeigniter'],
                }
            },
            'C#': {
                'extensions': ['.cs', '.cshtml', '.aspx', '.ascx'],
                'indicators': ['.sln', '.csproj', 'packages.config'],
                'frameworks': {
                    'aspnet': ['Microsoft.AspNetCore'],
                    'entity': ['EntityFramework'],
                    'xunit': ['xunit'],
                    'nunit': ['nunit'],
                }
            },
            'C++': {
                'extensions': ['.cpp', '.hpp', '.cc', '.hh', '.cxx', '.hxx', '.c', '.h'],
                'indicators': ['CMakeLists.txt', 'Makefile', '*.vcxproj'],
                'frameworks': {
                    'qt': ['Qt', 'QApplication'],
                    'boost': ['boost', 'Boost'],
                    'stl': ['std::'],
                }
            },
            'Rust': {
                'extensions': ['.rs'],
                'indicators': ['Cargo.toml', 'Cargo.lock'],
                'frameworks': {
                    'rocket': ['rocket'],
                    'actix': ['actix'],
                    'tokio': ['tokio'],
                }
            },
            'Swift': {
                'extensions': ['.swift'],
                'indicators': ['Package.swift', '*.xcodeproj'],
                'frameworks': {
                    'uikit': ['UIKit'],
                    'swiftui': ['SwiftUI'],
                    'combine': ['Combine'],
                }
            },
            'Kotlin': {
                'extensions': ['.kt', '.kts'],
                'indicators': ['build.gradle.kts'],
                'frameworks': {
                    'kotlinx': ['kotlinx'],
                    'ktor': ['ktor'],
                }
            },
            'R': {
                'extensions': ['.r', '.R', '.Rmd'],
                'indicators': ['DESCRIPTION', 'NAMESPACE'],
                'frameworks': {
                    'tidyverse': ['tidyverse'],
                    'shiny': ['shiny'],
                    'ggplot2': ['ggplot2'],
                }
            },
            'Scala': {
                'extensions': ['.scala', '.sc'],
                'indicators': ['build.sbt'],
                'frameworks': {
                    'akka': ['akka'],
                    'play': ['play'],
                    'spark': ['spark'],
                }
            },
            'HTML': {
                'extensions': ['.html', '.htm', '.xhtml'],
                'indicators': ['index.html'],
                'frameworks': {}
            },
            'CSS': {
                'extensions': ['.css', '.scss', '.sass', '.less', '.styl'],
                'indicators': [],
                'frameworks': {
                    'bootstrap': ['bootstrap'],
                    'tailwind': ['tailwind'],
                    'sass': ['sass'],
                }
            },
            'SQL': {
                'extensions': ['.sql', '.psql'],
                'indicators': [],
                'frameworks': {}
            },
            'Shell': {
                'extensions': ['.sh', '.bash', '.zsh', '.fish'],
                'indicators': [],
                'frameworks': {}
            },
            'Docker': {
                'extensions': [],
                'indicators': ['Dockerfile', 'docker-compose.yml'],
                'frameworks': {}
            },
            'YAML': {
                'extensions': ['.yml', '.yaml'],
                'indicators': [],
                'frameworks': {}
            },
            'JSON': {
                'extensions': ['.json'],
                'indicators': [],
                'frameworks': {}
            },
            'Markdown': {
                'extensions': ['.md', '.markdown'],
                'indicators': ['README.md'],
                'frameworks': {}
            }
        }
        
        # Framework-specific patterns for code analysis
        self.framework_patterns = {
            # Web frameworks
            'flask': [r'from flask import', r'import flask', r'Flask\('],
            'django': [r'django\.', r'from django', r'DJANGO_'],
            'fastapi': [r'from fastapi', r'import fastapi', r'FastAPI\('],
            'express': [r'require\([\'"]express[\'"]\)', r'import express'],
            'react': [r'import React', r'from \'react\'', r'React\.'],
            'vue': [r'import Vue', r'new Vue\('],
            'angular': [r'@angular', r'Component\({', r'NgModule\('],
            'spring': [r'@SpringBoot', r'@Controller', r'@RestController'],
            
            # ML frameworks
            'tensorflow': [r'import tensorflow', r'tf\.', r'keras\.'],
            'pytorch': [r'import torch', r'torch\.', r'nn\.Module'],
            'sklearn': [r'import sklearn', r'from sklearn', r'joblib\.'],
            'keras': [r'import keras', r'keras\.', r'tf\.keras'],
            
            # Testing frameworks
            'junit': [r'import org.junit', r'@Test'],
            'pytest': [r'import pytest', r'@pytest\.'],
            'rspec': [r'require \'rspec\'', r'RSpec\.'],
        }
    
    def detect_languages(self, file_list):
        """
        Detect programming languages used in the project
        Returns: dict with language stats
        """
        language_stats = defaultdict(lambda: {
            'count': 0,
            'files': [],
            'frameworks': set()
        })
        
        for file_path in file_list:
            ext = os.path.splitext(file_path)[1].lower()
            
            # Find matching language
            for lang_name, lang_info in self.languages.items():
                if ext in lang_info['extensions']:
                    language_stats[lang_name]['count'] += 1
                    language_stats[lang_name]['files'].append(file_path)
                    break
            
            # Check for language indicators in filename
            basename = os.path.basename(file_path)
            for lang_name, lang_info in self.languages.items():
                for indicator in lang_info['indicators']:
                    if indicator in basename or basename.endswith(indicator):
                        language_stats[lang_name]['count'] += 1
                        language_stats[lang_name]['files'].append(file_path)
                        break
        
        # Sort by file count
        result = dict(sorted(
            language_stats.items(), 
            key=lambda x: x[1]['count'], 
            reverse=True
        ))
        
        return result
    
    def detect_primary_language(self, file_list):
        """Detect the primary language of the project"""
        languages = self.detect_languages(file_list)
        
        if not languages:
            return 'Unknown'
        
        # Get the language with most files
        primary = next(iter(languages))
        
        # Calculate percentage
        total_files = len(file_list)
        percentage = (languages[primary]['count'] / total_files * 100) if total_files > 0 else 0
        
        return {
            'name': primary,
            'file_count': languages[primary]['count'],
            'percentage': round(percentage, 1),
            'all_languages': languages
        }
    
    def detect_frameworks_from_code(self, project_path, language):
        """
        Detect frameworks by analyzing code content
        """
        frameworks = set()
        
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith(('.py', '.js', '.java', '.rb', '.php', '.go')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            # Check framework patterns
                            for framework, patterns in self.framework_patterns.items():
                                for pattern in patterns:
                                    if re.search(pattern, content, re.IGNORECASE):
                                        frameworks.add(framework)
                                        break
                    except:
                        pass
        
        return list(frameworks)
    
    def get_language_details(self, language_name):
        """Get detailed information about a language"""
        return self.languages.get(language_name, {})
    
    def detect_project_type(self, languages, file_list):
        """
        Detect project type based on languages and files
        """
        scores = defaultdict(int)
        
        # Check for common project types
        patterns = {
            'Microservices': [
                'docker-compose.yml', 'service', 'microservice', 
                'api-gateway', 'eureka', 'consul'
            ],
            'Web Application': [
                'package.json', 'index.html', 'public/', 'src/',
                'templates/', 'static/'
            ],
            'Single Page App': [
                'index.html', 'App.js', 'App.tsx', 'components/',
                'routes/', 'store/'
            ],
            'Mobile App': [
                'AndroidManifest.xml', 'Info.plist', 'MainActivity',
                'AppDelegate', 'gradle'
            ],
            'Desktop App': [
                'main_window', 'MainWindow', 'main.cpp',
                'electron', 'Qt'
            ],
            'ML/AI Project': [
                'model.pkl', 'train.py', 'notebooks/', 'jupyter',
                'tensorflow', 'pytorch', 'keras', 'data/'
            ],
            'Data Pipeline': [
                'etl', 'pipeline', 'airflow', 'dags/',
                'spark', 'kafka', 'beam'
            ],
            'API Service': [
                'api/', 'routes/', 'controllers/',
                'swagger', 'openapi', 'postman'
            ],
            'Library/Package': [
                'setup.py', 'lib/', '__init__.py',
                'package.json', 'dist/'
            ],
            'Infrastructure': [
                'terraform', 'kubernetes', 'helm',
                'cloudformation', 'ansible'
            ]
        }
        
        for ptype, indicators in patterns.items():
            for indicator in indicators:
                for file_path in file_list:
                    if indicator in file_path:
                        scores[ptype] += 1
        
        # Consider language mix
        if 'Python' in languages and 'JavaScript' in languages:
            scores['Full Stack'] += 2
        
        if scores:
            project_type = max(scores, key=scores.get)
            confidence = scores[project_type] / max(scores.values()) if scores else 0
        else:
            project_type = 'Unknown'
            confidence = 0
        
        return {
            'type': project_type,
            'confidence': round(confidence * 100, 1),
            'scores': dict(scores)
        }
    
    def detect_build_system(self, file_list):
        """Detect build system used in project"""
        build_systems = {
            'Maven': ['pom.xml'],
            'Gradle': ['build.gradle', 'build.gradle.kts'],
            'npm': ['package.json', 'package-lock.json'],
            'yarn': ['yarn.lock'],
            'pip': ['requirements.txt', 'setup.py'],
            'poetry': ['poetry.lock', 'pyproject.toml'],
            'Cargo': ['Cargo.toml'],
            'Go Modules': ['go.mod'],
            'Bundler': ['Gemfile'],
            'Composer': ['composer.json'],
            'MSBuild': ['.csproj', '.sln'],
            'Make': ['Makefile', 'makefile'],
            'CMake': ['CMakeLists.txt'],
            'Bazel': ['WORKSPACE', 'BUILD']
        }
        
        detected = []
        for system, indicators in build_systems.items():
            for indicator in indicators:
                if any(indicator in f for f in file_list):
                    detected.append(system)
                    break
        
        return detected
    
    def generate_language_report(self, project_path):
        """Generate comprehensive language report"""
        file_list = []
        for root, dirs, files in os.walk(project_path):
            for file in files:
                file_list.append(os.path.relpath(os.path.join(root, file), project_path))
        
        languages = self.detect_languages(file_list)
        primary = self.detect_primary_language(file_list)
        project_type = self.detect_project_type(languages, file_list)
        build_systems = self.detect_build_system(file_list)
        
        return {
            'primary_language': primary,
            'all_languages': languages,
            'project_type': project_type,
            'build_systems': build_systems,
            'total_files': len(file_list)
        }