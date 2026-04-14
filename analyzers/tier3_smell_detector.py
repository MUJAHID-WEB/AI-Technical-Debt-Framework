import os
import re
import ast
from collections import defaultdict
from pathlib import Path

class AISmellDetector:
    """
    TIER 3: AI Smell Detection Layer
    Detects architectural smells in AI-enabled systems
    Universal - works for any project type and language
    """
    
    def __init__(self, project_path, tier1_data, tier2_data):
        self.project_path = project_path
        self.tier1 = tier1_data
        self.tier2 = tier2_data
        self.file_inventory = tier1_data.get('file_inventory', [])
        self.services = tier2_data.get('services', [])
        
        self.results = {
            'direct_model_calls': {'count': 0, 'services': [], 'details': []},
            'glue_code_ratio': 0,
            'glue_code_details': {},
            'hidden_consumers': [],
            'pipeline_complexity': {
                'pipelines': [],
                'complex_pipelines': 0,
                'details': []
            },
            'retrain_frequency': 0,
            'retrain_details': [],
            'feedback_loop_strength': 0,
            'feedback_loops': [],
            'shared_features': [],
            'impact_radius': {},
            'smell_summary': {}
        }
        
        # Patterns for detecting model operations across languages
        self.model_patterns = {
            'loading': [
                r'joblib\.load\(', r'pickle\.load\(', r'torch\.load\(',
                r'load_model\(', r'keras\.models\.load_model\(',
                r'tf\.keras\.models\.load_model\(', r'onnx\.load\(',
                r'model\.load_weights\(', r'from_pretrained\(',
                r'pmml\.load\(', r'mlflow\.pyfunc\.load_model\(',
                r'bentoml\.load\(', r'load\(', r'readRDS\(',
                r'keras::load_model_hdf5\(', r'joblib::load\(',
                r'pickle::load\(', r'torch::load\('
            ],
            'prediction': [
                r'\.predict\(', r'\.predict_proba\(', r'\.transform\(',
                r'\.score\(', r'\.forward\(', r'\.infer\(', r'\.generate\(',
                r'\.run\(', r'\.evaluate\(', r'\.classify\(', r'\.detect\('
            ],
            'training': [
                r'\.fit\(', r'\.train\(', r'\.learn\(', r'\.compile\(',
                r'\.backward\(', r'\.step\(', r'\.optimize\('
            ]
        }
        
        # Data transformation indicators (glue code)
        self.glue_patterns = {
            'conversions': [
                r'\.to_json\(', r'\.to_csv\(', r'\.to_dict\(', r'\.to_numpy\(',
                r'\.to_tensor\(', r'\.to_list\(', r'\.to_frame\(',
                r'json\.loads\(', r'json\.dumps\(', r'ast\.literal_eval\(',
                r'pd\.DataFrame\(', r'np\.array\(', r'torch\.tensor\(',
                r'tf\.convert_to_tensor\(', r'pd\.read_csv\(', r'pd\.read_json\('
            ],
            'reshaping': [
                r'\.reshape\(', r'\.transpose\(', r'\.flatten\(',
                r'\.squeeze\(', r'\.unsqueeze\(', r'\.permute\(',
                r'\.view\(', r'\.resize\(', r'\.expand\('
            ],
            'normalization': [
                r'\.normalize\(', r'\.standardize\(', r'\.scale\(',
                r'MinMaxScaler\(', r'StandardScaler\(', r'RobustScaler\(',
                r'normalize\(', r'preprocessing\.'
            ]
        }
        
        # Pipeline complexity indicators
        self.pipeline_indicators = [
            'pipeline', 'etl', 'extract', 'transform', 'load',
            'preprocess', 'postprocess', 'feature_engineering',
            'data_processing', 'batch_process', 'stream_process'
        ]
        
        # Retraining indicators
        self.retrain_indicators = [
            'train', 'retrain', 'fit', 'learn', 'update_model',
            'scheduler', 'cron', 'every_day', 'every_week',
            'periodic', 'automated_training'
        ]
    
    def detect_all(self):
        """Run all smell detectors"""
        print(f"\n👃 TIER 3: Detecting AI architectural smells")
        
        # Detect direct model calls
        self._detect_direct_model_calls()
        
        # Measure glue code
        self._measure_glue_code()
        
        # Find hidden consumers
        self._find_hidden_consumers()
        
        # Assess pipeline complexity
        self._assess_pipeline_complexity()
        
        # Measure retraining frequency
        self._measure_retrain_frequency()
        
        # Detect feedback loops
        self._detect_feedback_loops()
        
        # Detect shared features
        self._detect_shared_features()
        
        # Calculate impact radius
        self._calculate_impact_radius()
        
        # Generate summary
        self._generate_summary()
        
        return self.results
    
    def _detect_direct_model_calls(self):
        """Detect services that directly call ML models"""
        direct_calls = []
        
        for service in self.services:
            service_path = os.path.join(self.project_path, service.get('path', ''))
            if not os.path.exists(service_path):
                continue
            
            has_direct_call = False
            call_details = []
            
            for root, dirs, files in os.walk(service_path):
                for file in files:
                    if file.endswith(('.py', '.js', '.java', '.r', '.ipynb')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                lines = content.split('\n')
                                
                                # Check for model loading
                                for pattern in self.model_patterns['loading']:
                                    matches = re.finditer(pattern, content)
                                    for match in matches:
                                        line_num = self._get_line_number(content, match.start())
                                        context = lines[line_num-1] if line_num <= len(lines) else ''
                                        
                                        has_direct_call = True
                                        call_details.append({
                                            'file': os.path.relpath(file_path, service_path),
                                            'line': line_num,
                                            'pattern': 'loading',
                                            'code': context.strip()
                                        })
                                
                                # Check for direct predictions
                                if 'sklearn' in content or 'tensorflow' in content or 'torch' in content:
                                    for pattern in self.model_patterns['prediction']:
                                        matches = re.finditer(pattern, content)
                                        for match in matches:
                                            line_num = self._get_line_number(content, match.start())
                                            context = lines[line_num-1] if line_num <= len(lines) else ''
                                            
                                            has_direct_call = True
                                            call_details.append({
                                                'file': os.path.relpath(file_path, service_path),
                                                'line': line_num,
                                                'pattern': 'prediction',
                                                'code': context.strip()
                                            })
                        except Exception as e:
                            # Skip files that can't be read
                            pass
            
            if has_direct_call:
                direct_calls.append({
                    'service': service['name'],
                    'count': len(call_details),
                    'details': call_details[:5]  # Limit to 5 examples
                })
        
        self.results['direct_model_calls'] = {
            'count': len(direct_calls),
            'services': [d['service'] for d in direct_calls],
            'ratio': len(direct_calls) / len(self.services) if self.services else 0,
            'details': direct_calls
        }
        
        print(f"  ✓ Direct model calls: {len(direct_calls)} services")
    
    def _measure_glue_code(self):
        """Measure the amount of glue code (data transformation)"""
        total_lines = 0
        glue_lines = 0
        glue_by_service = {}
        
        for service in self.services:
            service_path = os.path.join(self.project_path, service.get('path', ''))
            if not os.path.exists(service_path):
                continue
            
            service_glue = 0
            service_total = 0
            
            for root, dirs, files in os.walk(service_path):
                for file in files:
                    if file.endswith(('.py', '.js', '.java', '.r')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                                service_total += len(lines)
                                total_lines += len(lines)
                                
                                # Count lines with glue code patterns
                                for line in lines:
                                    line_lower = line.lower()
                                    
                                    # Check all glue patterns
                                    for category, patterns in self.glue_patterns.items():
                                        for pattern in patterns:
                                            if pattern.lower() in line_lower:
                                                glue_lines += 1
                                                service_glue += 1
                                                break
                        except:
                            pass
            
            if service_total > 0:
                glue_by_service[service['name']] = {
                    'glue_lines': service_glue,
                    'total_lines': service_total,
                    'ratio': service_glue / service_total
                }
        
        self.results['glue_code_ratio'] = glue_lines / total_lines if total_lines > 0 else 0
        self.results['glue_code_details'] = glue_by_service
        
        print(f"  ✓ Glue code ratio: {self.results['glue_code_ratio']:.1%}")
    
    def _find_hidden_consumers(self):
        """Find undocumented consumers of models"""
        hidden_consumers = []
        
        # Get declared consumers from documentation
        declared = self._get_declared_consumers()
        
        # Get actual consumers from code
        actual = self._get_actual_consumers()
        
        # Find differences
        for model, consumers in actual.items():
            declared_for_model = declared.get(model, [])
            for consumer in consumers:
                if consumer not in declared_for_model:
                    hidden_consumers.append({
                        'model': model,
                        'consumer': consumer,
                        'type': 'undocumented',
                        'file': consumers[consumer].get('file', 'unknown'),
                        'line': consumers[consumer].get('line', 0)
                    })
        
        self.results['hidden_consumers'] = hidden_consumers
        
        print(f"  ✓ Hidden consumers: {len(hidden_consumers)}")
    
    def _get_declared_consumers(self):
        """Parse documentation for declared model consumers"""
        declared = defaultdict(list)
        
        # Look for README files
        for service in self.services:
            service_path = os.path.join(self.project_path, service.get('path', ''))
            readme_paths = [
                os.path.join(service_path, 'README.md'),
                os.path.join(service_path, 'README.txt'),
                os.path.join(service_path, 'docs', 'README.md')
            ]
            
            for readme_path in readme_paths:
                if os.path.exists(readme_path):
                    try:
                        with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                            
                            # Look for model references
                            for model in self.tier1.get('models', []):
                                model_name = model.get('name', '').replace('.pkl', '').replace('.h5', '').lower()
                                if model_name and model_name in content:
                                    declared[model['name']].append(service['name'])
                    except:
                        pass
        
        return declared
    
    def _get_actual_consumers(self):
        """Find actual consumers from code analysis"""
        actual = defaultdict(dict)
        
        for service in self.services:
            service_path = os.path.join(self.project_path, service.get('path', ''))
            
            for root, dirs, files in os.walk(service_path):
                for file in files:
                    if file.endswith(('.py', '.js', '.java')):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                lines = content.split('\n')
                                
                                for model in self.tier1.get('models', []):
                                    model_name = model.get('name', '')
                                    if model_name and model_name in content:
                                        # Find where it's used
                                        for i, line in enumerate(lines):
                                            if model_name in line:
                                                actual[model_name][service['name']] = {
                                                    'file': os.path.relpath(file_path, service_path),
                                                    'line': i + 1,
                                                    'code': line.strip()
                                                }
                        except:
                            pass
        
        return actual
    
    def _assess_pipeline_complexity(self):
        """Assess complexity of data pipelines"""
        complex_pipelines = []
        
        for pipeline in self.tier1.get('pipelines', []):
            stages = pipeline.get('stages', 1)
            path = pipeline.get('path', '')
            
            # Implementation aligned with Sub-step 3D (Page 4)
            branching_factor = self._calculate_branching_factor(path)
            complexity_score = stages * branching_factor
            
            pipeline_info = {
                'name': pipeline.get('name', 'unknown'),
                'path': path,
                'stages': stages,
                'branching_factor': branching_factor,
                'complexity': complexity_score,
                'is_complex': stages > 5 or branching_factor > 2
            }
            
            if pipeline_info['is_complex']:
                complex_pipelines.append(pipeline_info)
        
        self.results['pipeline_complexity'] = {
            'pipelines': [p.get('name') for p in self.tier1.get('pipelines', [])],
            'complex_pipelines': len(complex_pipelines),
            'details': complex_pipelines
        }
        
        print(f"  ✓ Complex pipelines: {len(complex_pipelines)}")
    
    def _calculate_branching_factor(self, pipeline_path):
        """
        Calculate branching factor (average branching per stage)
        Aligned with Equation 5 / Sub-step 3D
        """
        branch_count = 0
        file_count = 0
        full_path = os.path.join(self.project_path, pipeline_path)
        
        if not os.path.exists(full_path):
            return 1.0
        
        for root, dirs, files in os.walk(full_path):
            for file in files:
                if file.endswith('.py'):
                    file_count += 1
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            # Count branching points
                            branch_count += content.count('if ')
                            branch_count += content.count('elif ')
                            branch_count += content.count('case ')
                    except:
                        pass
        
        # Branching factor = (Total branches / Total relevant files) + 1
        # This is a heuristic to approximate the paper's branching metric
        return round((branch_count / max(1, file_count)) + 1, 2)
    
    def _measure_retrain_frequency(self):
        """Measure how often models are retrained"""
        retrain_events = []
        
        # Look for training scripts and scheduling
        for file_info in self.file_inventory:
            if 'train' in file_info['name'].lower() or 'retrain' in file_info['name'].lower():
                file_path = os.path.join(self.project_path, file_info['path'])
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Check for scheduling
                        has_schedule = any(pattern in content.lower() for pattern in [
                            'schedule', 'cron', 'every_day', 'every_week', 
                            'timedelta', 'sleep', 'periodic'
                        ])
                        
                        # Check for triggers
                        has_trigger = any(pattern in content.lower() for pattern in [
                            'trigger', 'webhook', 'event', 'listener',
                            'on_', 'when_', 'if condition'
                        ])
                        
                        if has_schedule or has_trigger:
                            retrain_events.append({
                                'file': file_info['path'],
                                'has_schedule': has_schedule,
                                'has_trigger': has_trigger,
                                'reason': 'scheduled' if has_schedule else 'triggered' if has_trigger else 'manual'
                            })
                except:
                    pass
        
        # Check git history for model file changes (would need git log analysis)
        # For now, estimate based on file modifications
        model_changes = 0
        for model in self.tier1.get('models', []):
            if 'modified' in model:
                # Rough estimate: count model files modified in last 30 days
                pass
        
        self.results['retrain_frequency'] = len(retrain_events)
        self.results['retrain_details'] = retrain_events
        
        print(f"  ✓ Retrain events: {len(retrain_events)}")
    
    def _detect_feedback_loops(self):
        """Detect potential feedback loops where model outputs influence training"""
        feedback_loops = []
        
        for service in self.services:
            service_path = os.path.join(self.project_path, service.get('path', ''))
            
            for root, dirs, files in os.walk(service_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                
                                # Check for patterns that indicate feedback
                                # 1. Model prediction followed by data storage
                                has_prediction = any(re.search(p, content) for p in self.model_patterns['prediction'])
                                has_storage = any(p in content.lower() for p in ['insert', 'update', 'save', 'store'])
                                
                                # 2. Training script reading from production DB
                                is_training = 'train' in file or 'fit' in content
                                has_db_read = any(p in content.lower() for p in ['select', 'query', 'read'])
                                
                                if (has_prediction and has_storage) or (is_training and has_db_read):
                                    feedback_loops.append({
                                        'service': service['name'],
                                        'file': os.path.relpath(file_path, service_path),
                                        'type': 'prediction_to_storage' if has_prediction else 'training_from_prod',
                                        'evidence': {
                                            'has_prediction': has_prediction,
                                            'has_storage': has_storage,
                                            'is_training': is_training,
                                            'has_db_read': has_db_read
                                        }
                                    })
                        except:
                            pass
        
        self.results['feedback_loops'] = feedback_loops
        self.results['feedback_loop_strength'] = len(feedback_loops) / len(self.services) if self.services else 0
        
        print(f"  ✓ Feedback loops: {len(feedback_loops)}")
    
    def _detect_shared_features(self):
        """Detect feature pipelines shared across services"""
        shared_features = []
        
        # Find Python modules that are imported by multiple services
        import_counts = defaultdict(list)
        
        for service in self.services:
            service_path = os.path.join(self.project_path, service.get('path', ''))
            
            for root, dirs, files in os.walk(service_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                
                                # Find imports
                                imports = re.findall(r'^(?:from|import)\s+([\w.]+)', content, re.MULTILINE)
                                for imp in imports:
                                    import_counts[imp].append(service['name'])
                        except:
                            pass
        
        # Find modules imported by multiple services
        for module, services in import_counts.items():
            if len(set(services)) > 1:
                shared_features.append({
                    'module': module,
                    'services': list(set(services)),
                    'count': len(set(services))
                })
        
        self.results['shared_features'] = sorted(shared_features, key=lambda x: x['count'], reverse=True)
        
        print(f"  ✓ Shared features: {len(shared_features)}")
    
    def _calculate_impact_radius(self):
        """Calculate how many services are affected when a model changes"""
        impact_by_model = {}
        
        for model in self.tier1.get('models', []):
            model_name = model.get('name', 'unknown')
            consumers = set()
            
            # Find all services that use this model
            for service in self.services:
                service_path = os.path.join(self.project_path, service.get('path', ''))
                
                for root, dirs, files in os.walk(service_path):
                    for file in files:
                        if file.endswith(('.py', '.js', '.java')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    if model_name in content:
                                        consumers.add(service['name'])
                            except:
                                pass
            
            impact_by_model[model_name] = len(consumers)
        
        self.results['impact_radius'] = impact_by_model
        
        avg_impact = sum(impact_by_model.values()) / len(impact_by_model) if impact_by_model else 0
        print(f"  ✓ Avg impact radius: {avg_impact:.1f} services")
    
    def _generate_summary(self):
        """Generate summary of all smells"""
        summary = {
            'total_smells': 0,
            'critical_smells': 0,
            'warning_smells': 0,
            'info_smells': 0,
            'top_issues': []
        }
        
        # Count direct model calls as critical if > 30%
        if self.results['direct_model_calls']['ratio'] > 0.3:
            summary['critical_smells'] += 1
            summary['top_issues'].append({
                'type': 'direct_model_calls',
                'severity': 'critical',
                'message': f"{self.results['direct_model_calls']['count']} services directly call ML models"
            })
        elif self.results['direct_model_calls']['count'] > 0:
            summary['warning_smells'] += 1
        
        # Glue code > 20% is problematic
        if self.results['glue_code_ratio'] > 0.2:
            if self.results['glue_code_ratio'] > 0.3:
                summary['critical_smells'] += 1
                summary['top_issues'].append({
                    'type': 'glue_code',
                    'severity': 'critical',
                    'message': f"Glue code is {self.results['glue_code_ratio']:.1%} of codebase"
                })
            else:
                summary['warning_smells'] += 1
        
        # Hidden consumers are always problematic
        if len(self.results['hidden_consumers']) > 0:
            if len(self.results['hidden_consumers']) > 3:
                summary['critical_smells'] += 1
                summary['top_issues'].append({
                    'type': 'hidden_consumers',
                    'severity': 'critical',
                    'message': f"{len(self.results['hidden_consumers'])} hidden model consumers"
                })
            else:
                summary['warning_smells'] += 1
        
        # Complex pipelines
        if self.results['pipeline_complexity']['complex_pipelines'] > 0:
            summary['warning_smells'] += self.results['pipeline_complexity']['complex_pipelines']
        
        # Retrain frequency
        if self.results['retrain_frequency'] > 4:
            summary['warning_smells'] += 1
            summary['top_issues'].append({
                'type': 'retrain_frequency',
                'severity': 'warning',
                'message': f"Models retrained {self.results['retrain_frequency']}x/month"
            })
        
        # Feedback loops
        if len(self.results['feedback_loops']) > 0:
            summary['warning_smells'] += 1
            summary['top_issues'].append({
                'type': 'feedback_loops',
                'severity': 'warning',
                'message': f"{len(self.results['feedback_loops'])} potential feedback loops"
            })
        
        summary['total_smells'] = summary['critical_smells'] + summary['warning_smells'] + summary['info_smells']
        
        self.results['smell_summary'] = summary
        
        print(f"  ✓ Smells detected: {summary['total_smells']} total")
        print(f"    - Critical: {summary['critical_smells']}")
        print(f"    - Warning: {summary['warning_smells']}")
    
    def _get_line_number(self, content, position):
        """Get line number from character position"""
        return content.count('\n', 0, position) + 1