import os
import re
import json
from collections import defaultdict

class FrameworkDetector:
    """
    Universal Framework Detector
    Detects frameworks, libraries, and dependencies in any project
    """
    
    def __init__(self):
        self.frameworks = {
            # Web Frameworks
            'Flask': {
                'patterns': [r'from flask import', r'import flask', r'Flask\('],
                'files': ['flask'],
                'dependencies': ['flask'],
                'category': 'Web Framework'
            },
            'Django': {
                'patterns': [r'django\.', r'from django', r'DJANGO_'],
                'files': ['manage.py', 'settings.py', 'urls.py'],
                'dependencies': ['django'],
                'category': 'Web Framework'
            },
            'FastAPI': {
                'patterns': [r'from fastapi', r'import fastapi', r'FastAPI\('],
                'files': [],
                'dependencies': ['fastapi'],
                'category': 'Web Framework'
            },
            'Express': {
                'patterns': [r'require\([\'"]express[\'"]\)', r'import express'],
                'files': ['app.js', 'server.js', 'index.js'],
                'dependencies': ['express'],
                'category': 'Web Framework'
            },
            'React': {
                'patterns': [r'import React', r'from \'react\'', r'React\.'],
                'files': ['App.js', 'App.tsx', 'index.js'],
                'dependencies': ['react', 'react-dom'],
                'category': 'Frontend Framework'
            },
            'Vue': {
                'patterns': [r'import Vue', r'new Vue\(', r'Vue\.component'],
                'files': ['vue.config.js', 'main.js'],
                'dependencies': ['vue'],
                'category': 'Frontend Framework'
            },
            'Angular': {
                'patterns': [r'@angular', r'Component\({', r'NgModule\('],
                'files': ['angular.json', 'app.module.ts'],
                'dependencies': ['@angular/core'],
                'category': 'Frontend Framework'
            },
            'Spring': {
                'patterns': [r'@SpringBoot', r'@Controller', r'@RestController'],
                'files': ['application.properties', 'pom.xml'],
                'dependencies': ['spring-boot', 'spring-core'],
                'category': 'Web Framework'
            },
            
            # ML/AI Frameworks
            'TensorFlow': {
                'patterns': [r'import tensorflow', r'tf\.', r'tensorflow\.'],
                'files': ['model.h5', 'saved_model.pb'],
                'dependencies': ['tensorflow', 'tf'],
                'category': 'ML Framework'
            },
            'PyTorch': {
                'patterns': [r'import torch', r'torch\.', r'nn\.Module'],
                'files': ['.pt', '.pth'],
                'dependencies': ['torch', 'pytorch'],
                'category': 'ML Framework'
            },
            'Scikit-learn': {
                'patterns': [r'import sklearn', r'from sklearn', r'sklearn\.'],
                'files': ['.pkl', '.joblib'],
                'dependencies': ['scikit-learn', 'sklearn'],
                'category': 'ML Framework'
            },
            'Keras': {
                'patterns': [r'import keras', r'keras\.', r'tf\.keras'],
                'files': ['.h5', '.keras'],
                'dependencies': ['keras'],
                'category': 'ML Framework'
            },
            'JAX': {
                'patterns': [r'import jax', r'jax\.', r'jaxlib'],
                'files': [],
                'dependencies': ['jax'],
                'category': 'ML Framework'
            },
            'ONNX': {
                'patterns': [r'import onnx', r'onnx\.', r'onnxruntime'],
                'files': ['.onnx'],
                'dependencies': ['onnx', 'onnxruntime'],
                'category': 'ML Framework'
            },
            'XGBoost': {
                'patterns': [r'import xgboost', r'xgb\.', r'XGB'],
                'files': [],
                'dependencies': ['xgboost'],
                'category': 'ML Framework'
            },
            'LightGBM': {
                'patterns': [r'import lightgbm', r'lgb\.', r'LightGBM'],
                'files': [],
                'dependencies': ['lightgbm'],
                'category': 'ML Framework'
            },
            
            # Data Processing
            'Pandas': {
                'patterns': [r'import pandas', r'pd\.', r'DataFrame'],
                'files': [],
                'dependencies': ['pandas'],
                'category': 'Data Processing'
            },
            'NumPy': {
                'patterns': [r'import numpy', r'np\.', r'numpy\.'],
                'files': [],
                'dependencies': ['numpy'],
                'category': 'Data Processing'
            },
            'Spark': {
                'patterns': [r'import pyspark', r'spark\.', r'SparkSession'],
                'files': [],
                'dependencies': ['pyspark'],
                'category': 'Data Processing'
            },
            
            # Testing
            'JUnit': {
                'patterns': [r'import org.junit', r'@Test'],
                'files': [],
                'dependencies': ['junit'],
                'category': 'Testing'
            },
            'pytest': {
                'patterns': [r'import pytest', r'@pytest\.', r'pytest\.'],
                'files': ['test_*.py', '*_test.py'],
                'dependencies': ['pytest'],
                'category': 'Testing'
            },
            'Mocha': {
                'patterns': [r'describe\(', r'it\(', r'beforeEach\('],
                'files': ['test/'],
                'dependencies': ['mocha', 'chai'],
                'category': 'Testing'
            },
            'Jest': {
                'patterns': [r'test\(', r'expect\(', r'jest\.'],
                'files': ['jest.config.js'],
                'dependencies': ['jest'],
                'category': 'Testing'
            },
            
            # Build Tools
            'Webpack': {
                'patterns': [],
                'files': ['webpack.config.js'],
                'dependencies': ['webpack'],
                'category': 'Build Tool'
            },
            'Babel': {
                'patterns': [],
                'files': ['.babelrc', 'babel.config.js'],
                'dependencies': ['@babel/core'],
                'category': 'Build Tool'
            },
            'Maven': {
                'patterns': [],
                'files': ['pom.xml'],
                'dependencies': [],
                'category': 'Build Tool'
            },
            'Gradle': {
                'patterns': [],
                'files': ['build.gradle', 'settings.gradle'],
                'dependencies': [],
                'category': 'Build Tool'
            },
            
            # Databases/ORMs
            'SQLAlchemy': {
                'patterns': [r'import sqlalchemy', r'sa\.', r'declarative_base'],
                'files': [],
                'dependencies': ['sqlalchemy'],
                'category': 'ORM'
            },
            'Mongoose': {
                'patterns': [r'require\([\'"]mongoose[\'"]\)', r'import mongoose'],
                'files': [],
                'dependencies': ['mongoose'],
                'category': 'ORM'
            },
            'Hibernate': {
                'patterns': [r'import org.hibernate', r'@Entity', r'@Table'],
                'files': ['hibernate.cfg.xml'],
                'dependencies': ['hibernate'],
                'category': 'ORM'
            },
            
            # MLOps
            'MLflow': {
                'patterns': [r'import mlflow', r'mlflow\.', r'MlflowClient'],
                'files': ['mlruns/'],
                'dependencies': ['mlflow'],
                'category': 'MLOps'
            },
            'Kubeflow': {
                'patterns': [r'import kubeflow', r'kfp\.'],
                'files': ['pipeline.yaml'],
                'dependencies': ['kubeflow'],
                'category': 'MLOps'
            },
            'BentoML': {
                'patterns': [r'import bentoml', r'bentoml\.'],
                'files': ['bentofile.yaml'],
                'dependencies': ['bentoml'],
                'category': 'MLOps'
            }
        }
    
    def detect_from_files(self, project_path):
        """
        Detect frameworks by scanning project files
        """
        detected = defaultdict(lambda: {
            'name': '',
            'category': '',
            'confidence': 0,
            'evidence': []
        })
        
        for root, dirs, files in os.walk(project_path):
            # Check for framework-specific files
            for file in files:
                file_path = os.path.relpath(os.path.join(root, file), project_path)
                
                for fw_name, fw_info in self.frameworks.items():
                    for pattern in fw_info['files']:
                        if pattern in file_path or file_path.endswith(pattern):
                            detected[fw_name]['name'] = fw_name
                            detected[fw_name]['category'] = fw_info['category']
                            detected[fw_name]['confidence'] += 1
                            detected[fw_name]['evidence'].append({
                                'type': 'file',
                                'value': file_path
                            })
            
            # Check code files for framework patterns
            for file in files:
                if file.endswith(('.py', '.js', '.java', '.rb', '.php', '.go', '.ts')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            for fw_name, fw_info in self.frameworks.items():
                                for pattern in fw_info['patterns']:
                                    if re.search(pattern, content, re.IGNORECASE):
                                        detected[fw_name]['name'] = fw_name
                                        detected[fw_name]['category'] = fw_info['category']
                                        detected[fw_name]['confidence'] += 2
                                        detected[fw_name]['evidence'].append({
                                            'type': 'code',
                                            'file': os.path.relpath(file_path, project_path),
                                            'pattern': pattern
                                        })
                                        break
                    except:
                        pass
        
        # Calculate confidence scores
        for fw_name in detected:
            detected[fw_name]['confidence'] = min(10, detected[fw_name]['confidence'])
        
        return dict(detected)
    
    def detect_from_dependencies(self, project_path):
        """
        Detect frameworks by analyzing dependency files
        """
        dependencies = defaultdict(list)
        
        # Check package.json (Node.js)
        package_json_path = os.path.join(project_path, 'package.json')
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r') as f:
                    data = json.load(f)
                    all_deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    
                    for fw_name, fw_info in self.frameworks.items():
                        for dep in fw_info['dependencies']:
                            if dep in all_deps:
                                dependencies[fw_name].append({
                                    'file': 'package.json',
                                    'dependency': dep,
                                    'version': all_deps[dep]
                                })
            except:
                pass
        
        # Check requirements.txt (Python)
        req_path = os.path.join(project_path, 'requirements.txt')
        if os.path.exists(req_path):
            try:
                with open(req_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            dep = line.split('==')[0].split('>=')[0].split('<=')[0]
                            
                            for fw_name, fw_info in self.frameworks.items():
                                for fw_dep in fw_info['dependencies']:
                                    if fw_dep in dep:
                                        dependencies[fw_name].append({
                                            'file': 'requirements.txt',
                                            'dependency': dep
                                        })
            except:
                pass
        
        # Check pom.xml (Java/Maven)
        pom_path = os.path.join(project_path, 'pom.xml')
        if os.path.exists(pom_path):
            try:
                with open(pom_path, 'r') as f:
                    content = f.read()
                    for fw_name, fw_info in self.frameworks.items():
                        for dep in fw_info['dependencies']:
                            if dep in content:
                                dependencies[fw_name].append({
                                    'file': 'pom.xml',
                                    'dependency': dep
                                })
            except:
                pass
        
        return dict(dependencies)
    
    def detect_all(self, project_path):
        """
        Comprehensive framework detection
        """
        # Detect from files
        file_detected = self.detect_from_files(project_path)
        
        # Detect from dependencies
        dep_detected = self.detect_from_dependencies(project_path)
        
        # Merge results
        all_frameworks = {}
        
        for fw_name in set(list(file_detected.keys()) + list(dep_detected.keys())):
            fw_info = self.frameworks.get(fw_name, {})
            
            all_frameworks[fw_name] = {
                'name': fw_name,
                'category': fw_info.get('category', 'Unknown'),
                'file_evidence': file_detected.get(fw_name, {}).get('evidence', []),
                'dependency_evidence': dep_detected.get(fw_name, []),
                'confidence': 0
            }
            
            # Calculate combined confidence
            file_confidence = len(all_frameworks[fw_name]['file_evidence']) * 2
            dep_confidence = len(all_frameworks[fw_name]['dependency_evidence']) * 3
            all_frameworks[fw_name]['confidence'] = min(10, file_confidence + dep_confidence)
        
        # Sort by confidence
        all_frameworks = dict(sorted(
            all_frameworks.items(),
            key=lambda x: x[1]['confidence'],
            reverse=True
        ))
        
        return all_frameworks
    
    def get_frameworks_by_category(self, frameworks):
        """Group frameworks by category"""
        by_category = defaultdict(list)
        
        for fw_name, fw_info in frameworks.items():
            category = fw_info.get('category', 'Other')
            by_category[category].append({
                'name': fw_name,
                'confidence': fw_info['confidence']
            })
        
        return dict(by_category)
    
    def generate_framework_report(self, project_path):
        """Generate comprehensive framework report"""
        frameworks = self.detect_all(project_path)
        by_category = self.get_frameworks_by_category(frameworks)
        
        return {
            'frameworks': frameworks,
            'by_category': by_category,
            'total_frameworks': len(frameworks),
            'primary_frameworks': [fw for fw, info in frameworks.items() 
                                  if info['confidence'] >= 5][:5]
        }