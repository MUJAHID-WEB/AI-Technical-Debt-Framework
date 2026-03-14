import os
import re
import hashlib
from collections import defaultdict
from pathlib import Path

class ModelDetector:
    """
    Universal ML Model Detector
    Detects ML models in any project (files and code references)
    """
    
    def __init__(self):
        # Model file extensions by framework
        self.model_extensions = {
            'Pickle': ['.pkl', '.pickle', '.sav'],
            'Joblib': ['.joblib'],
            'PyTorch': ['.pt', '.pth', '.ckpt', '.bin', '.pt.tar', '.pth.tar'],
            'TensorFlow': ['.pb', '.pbtxt', '.meta', '.index', '.data-00000-of-00001'],
            'Keras': ['.h5', '.hdf5', '.keras'],
            'ONNX': ['.onnx'],
            'TFLite': ['.tflite', '.lite'],
            'CoreML': ['.mlmodel', '.mlpackage'],
            'Caffe': ['.caffemodel', '.prototxt'],
            'Scikit-learn': ['.pkl', '.joblib'],
            'XGBoost': ['.model', '.ubj'],
            'LightGBM': ['.txt'],
            'R': ['.rds', '.rda'],
            'SageMaker': ['.tar.gz'],
            'MLflow': ['.mlflow'],
            'BentoML': ['.bento'],
            'PMML': ['.pmml', '.xml']
        }
        
        # Model loading patterns by language
        self.loading_patterns = {
            'python': {
                'pickle': [r'pickle\.load\(', r'pickle\.loads\('],
                'joblib': [r'joblib\.load\(', r'joblib\.dump\('],
                'torch': [r'torch\.load\(', r'torch\.save\(', r'load_state_dict\('],
                'keras': [r'keras\.models\.load_model\(', r'load_model\(', r'tf\.keras\.models\.load_model\('],
                'tensorflow': [r'tf\.saved_model\.load\(', r'saved_model\.load\(', r'tf\.train\.load_checkpoint\('],
                'onnx': [r'onnx\.load\(', r'onnxruntime\.InferenceSession\('],
                'sklearn': [r'joblib\.load\(', r'pickle\.load\(', r'load\(\''],
                'mlflow': [r'mlflow\.pyfunc\.load_model\(', r'mlflow\.sklearn\.load_model\('],
                'bentoml': [r'bentoml\.load\(', r'bentoml\.get\(', r'bentoml\.models\.get\('],
                'transformers': [r'from_pretrained\(', r'AutoModel\.from_pretrained\(']
            },
            'r': {
                'readRDS': [r'readRDS\(', r'load\(', r'read\.rds\('],
                'keras': [r'load_model_hdf5\(', r'keras::load_model_hdf5\('],
                'caret': [r'read\.rds\(', r'load\(\)']
            },
            'javascript': {
                'tensorflow': [r'tf\.loadLayersModel\(', r'tf\.loadGraphModel\('],
                'onnx': [r'onnx\.load\(', r'onnx\.InferenceSession\(']
            },
            'java': {
                'dl4j': [r'ModelSerializer\.restoreMultiLayerNetwork\(', r'ModelSerializer\.restoreComputationGraph\('],
                'h2o': [r'h2o\.loadModel\(', r'Model\.load\('],
                'mllib': [r'MLModel\.load\(', r'PipelineModel\.load\(']
            }
        }
        
        # Prediction/inference patterns
        self.prediction_patterns = {
            'python': [
                r'\.predict\(', r'\.predict_proba\(', r'\.transform\(',
                r'\.score\(', r'\.forward\(', r'\.infer\(', r'\.generate\(',
                r'\.run\(', r'\.evaluate\(', r'\.classify\(', r'\.detect\('
            ],
            'r': [
                r'predict\(', r'fitted\(', r'fitted.values\('
            ],
            'javascript': [
                r'\.predict\(', r'\.execute\(', r'\.run\('
            ],
            'java': [
                r'\.predict\(', r'\.score\(', r'\.classify\('
            ]
        }
        
        # Training patterns
        self.training_patterns = {
            'python': [
                r'\.fit\(', r'\.train\(', r'\.learn\(', r'\.compile\(',
                r'\.backward\(', r'\.step\(', r'\.optimize\(', r'\.update\('
            ],
            'r': [
                r'train\(', r'fit\(', r'caret::train\('
            ]
        }
    
    def detect_model_files(self, project_path):
        """
        Detect model files by extension
        """
        models = []
        
        for root, dirs, files in os.walk(project_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_path)
                ext = os.path.splitext(file)[1].lower()
                
                # Check against all extensions
                for fw_name, extensions in self.model_extensions.items():
                    if ext in extensions:
                        file_stat = os.stat(file_path)
                        
                        model_info = {
                            'name': file,
                            'path': rel_path,
                            'full_path': file_path,
                            'extension': ext,
                            'framework': fw_name,
                            'size': file_stat.st_size,
                            'size_kb': round(file_stat.st_size / 1024, 2),
                            'size_mb': round(file_stat.st_size / (1024 * 1024), 2),
                            'modified': os.path.getmtime(file_path),
                            'detected_by': 'file_extension'
                        }
                        
                        # Try to get model info from filename
                        model_info.update(self._parse_model_filename(file))
                        
                        models.append(model_info)
                        break
        
        return models
    
    def _parse_model_filename(self, filename):
        """Parse model information from filename"""
        info = {
            'version': None,
            'architecture': None,
            'dataset': None
        }
        
        # Look for version patterns (v1, v2, 2023, etc.)
        version_match = re.search(r'[vV]?(\d+[\._]?\d*)', filename)
        if version_match:
            info['version'] = version_match.group(0)
        
        # Look for architecture patterns
        arch_patterns = ['resnet', 'vgg', 'bert', 'gpt', 'lstm', 'cnn', 'rnn',
                        'transformer', 'efficientnet', 'yolo', 'ssd']
        for arch in arch_patterns:
            if arch in filename.lower():
                info['architecture'] = arch
                break
        
        return info
    
    def detect_model_references(self, project_path):
        """
        Detect model references in code files
        """
        references = defaultdict(list)
        
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith(('.py', '.r', '.R', '.js', '.java', '.ipynb')):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, project_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')
                            
                            # Determine language
                            if file.endswith('.py'):
                                lang = 'python'
                            elif file.endswith(('.r', '.R')):
                                lang = 'r'
                            elif file.endswith('.js'):
                                lang = 'javascript'
                            elif file.endswith('.java'):
                                lang = 'java'
                            else:
                                lang = 'unknown'
                            
                            # Check loading patterns
                            if lang in self.loading_patterns:
                                for fw_name, patterns in self.loading_patterns[lang].items():
                                    for pattern in patterns:
                                        matches = re.finditer(pattern, content)
                                        for match in matches:
                                            line_num = content.count('\n', 0, match.start()) + 1
                                            context = lines[line_num-1] if line_num <= len(lines) else ''
                                            
                                            # Try to extract model path/name
                                            model_ref = self._extract_model_reference(context)
                                            
                                            references['loading'].append({
                                                'file': rel_path,
                                                'line': line_num,
                                                'framework': fw_name,
                                                'pattern': pattern,
                                                'context': context.strip(),
                                                'model_reference': model_ref,
                                                'language': lang
                                            })
                            
                            # Check prediction patterns
                            if lang in self.prediction_patterns:
                                for pattern in self.prediction_patterns[lang]:
                                    matches = re.finditer(pattern, content)
                                    for match in matches:
                                        line_num = content.count('\n', 0, match.start()) + 1
                                        references['prediction'].append({
                                            'file': rel_path,
                                            'line': line_num,
                                            'pattern': pattern,
                                            'language': lang
                                        })
                            
                            # Check training patterns
                            if lang in self.training_patterns:
                                for pattern in self.training_patterns[lang]:
                                    matches = re.finditer(pattern, content)
                                    for match in matches:
                                        line_num = content.count('\n', 0, match.start()) + 1
                                        references['training'].append({
                                            'file': rel_path,
                                            'line': line_num,
                                            'pattern': pattern,
                                            'language': lang
                                        })
                    except:
                        pass
        
        return dict(references)
    
    def _extract_model_reference(self, text):
        """Extract model name/path from code line"""
        # Look for quoted strings that might be model paths
        quote_matches = re.findall(r'[\'"]([^\'"]*\.(?:pkl|pt|h5|onnx|pb|joblib|sav|model))[\'"]', text)
        if quote_matches:
            return quote_matches[0]
        
        # Look for variable names with 'model'
        var_matches = re.findall(r'(\w*model\w*)\s*=', text)
        if var_matches:
            return var_matches[0]
        
        # Look for from_pretrained calls
        pretrained_matches = re.findall(r'from_pretrained\([\'"]([^\'"]+)[\'"]', text)
        if pretrained_matches:
            return pretrained_matches[0]
        
        return None
    
    def detect_model_metadata(self, project_path):
        """
        Detect model metadata files (configs, checkpoints, etc.)
        """
        metadata = []
        
        patterns = [
            'config.json', 'config.yaml', 'config.yml',
            'params.json', 'hyperparameters.json',
            'checkpoint', 'model.ckpt', 'checkpoint-*',
            'training_args.json', 'model_config.json'
        ]
        
        for root, dirs, files in os.walk(project_path):
            for file in files:
                for pattern in patterns:
                    if re.match(pattern.replace('*', '.*'), file):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, project_path)
                        
                        metadata.append({
                            'name': file,
                            'path': rel_path,
                            'type': 'config' if 'config' in file else 'checkpoint' if 'checkpoint' in file else 'other',
                            'size': os.path.getsize(file_path)
                        })
                        break
        
        return metadata
    
    def detect_all(self, project_path):
        """
        Comprehensive model detection
        """
        print(f"\n🤖 Detecting ML models in {project_path}")
        
        # Detect model files
        model_files = self.detect_model_files(project_path)
        
        # Detect model references in code
        model_references = self.detect_model_references(project_path)
        
        # Detect model metadata
        model_metadata = self.detect_model_metadata(project_path)
        
        # Calculate statistics
        stats = {
            'total_models': len(model_files),
            'total_references': sum(len(v) for v in model_references.values()),
            'loading_references': len(model_references.get('loading', [])),
            'prediction_references': len(model_references.get('prediction', [])),
            'training_references': len(model_references.get('training', [])),
            'metadata_files': len(model_metadata),
            'total_size_mb': sum(m.get('size_mb', 0) for m in model_files),
            'frameworks': defaultdict(int)
        }
        
        # Count frameworks
        for model in model_files:
            stats['frameworks'][model['framework']] += 1
        
        return {
            'model_files': model_files,
            'model_references': model_references,
            'model_metadata': model_metadata,
            'statistics': stats
        }
    
    def generate_model_report(self, project_path):
        """
        Generate comprehensive model report
        """
        detection = self.detect_all(project_path)
        
        # Identify potential issues
        issues = []
        
        # Check for large models
        for model in detection['model_files']:
            if model.get('size_mb', 0) > 100:
                issues.append({
                    'type': 'large_model',
                    'severity': 'warning',
                    'model': model['name'],
                    'size_mb': model['size_mb'],
                    'message': f"Model {model['name']} is {model['size_mb']}MB, consider optimization"
                })
        
        # Check for model references without files
        model_files_set = {m['name'] for m in detection['model_files']}
        for ref in detection['model_references'].get('loading', []):
            if ref.get('model_reference') and ref['model_reference'] not in model_files_set:
                issues.append({
                    'type': 'missing_model',
                    'severity': 'critical',
                    'file': ref['file'],
                    'reference': ref['model_reference'],
                    'message': f"Model {ref['model_reference']} referenced but not found"
                })
        
        return {
            'detection': detection,
            'issues': issues,
            'summary': {
                'total_models': detection['statistics']['total_models'],
                'total_references': detection['statistics']['total_references'],
                'total_size_mb': detection['statistics']['total_size_mb'],
                'frameworks': dict(detection['statistics']['frameworks'])
            }
        }