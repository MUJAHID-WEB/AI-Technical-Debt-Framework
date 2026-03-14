import os
import requests
import json
import yaml
import time
from datetime import datetime
from pathlib import Path
import base64

class MLOpsCollector:
    """
    MLOps Platform Collector
    Collects data from Kubeflow, MLflow, BentoML, and Seldon Core
    """
    
    def __init__(self):
        self.platforms = {
            'kubeflow': {
                'name': 'Kubeflow',
                'collector': self._collect_kubeflow,
                'pipelines_endpoint': '/apis/v1beta1/pipelines',
                'runs_endpoint': '/apis/v1beta1/runs',
                'experiments_endpoint': '/apis/v1beta1/experiments'
            },
            'mlflow': {
                'name': 'MLflow',
                'collector': self._collect_mlflow,
                'experiments_endpoint': '/api/2.0/mlflow/experiments/list',
                'runs_endpoint': '/api/2.0/mlflow/runs/search',
                'models_endpoint': '/api/2.0/mlflow/registered-models/list'
            },
            'bentoml': {
                'name': 'BentoML',
                'collector': self._collect_bentoml,
                'bentos_endpoint': '/api/v1/bentos',
                'models_endpoint': '/api/v1/models',
                'runners_endpoint': '/api/v1/runners'
            },
            'seldon': {
                'name': 'Seldon Core',
                'collector': self._collect_seldon,
                'deployments_endpoint': '/apis/machinelearning.seldon.io/v1/seldondeployments',
                'models_endpoint': '/api/v1/models'
            }
        }
        
        self.session = requests.Session()
        self.results = {}
    
    def collect_from_platform(self, platform, endpoint, target_path, token=None):
        """
        Collect data from specified MLOps platform
        
        Args:
            platform: Platform name (kubeflow, mlflow, bentoml, seldon)
            endpoint: API endpoint URL
            target_path: Local path to save collected data
            token: Optional authentication token
            
        Returns:
            Dictionary with collection results
        """
        if platform not in self.platforms:
            return {
                'success': False,
                'error': f"Unsupported platform: {platform}. Supported: {list(self.platforms.keys())}"
            }
        
        print(f"\n📡 Collecting from {self.platforms[platform]['name']}")
        print(f"   Endpoint: {endpoint}")
        
        # Setup authentication
        if token:
            self.session.headers.update({'Authorization': f'Bearer {token}'})
        
        # Create target directory
        os.makedirs(target_path, exist_ok=True)
        
        # Run platform-specific collector
        collector = self.platforms[platform]['collector']
        result = collector(endpoint, target_path)
        
        if result['success']:
            # Save collection info
            info = {
                'platform': platform,
                'endpoint': endpoint,
                'collection_time': datetime.now().isoformat(),
                'items_collected': result.get('items_collected', {}),
                'target_path': target_path
            }
            
            info_path = os.path.join(target_path, 'collection_info.json')
            with open(info_path, 'w') as f:
                json.dump(info, f, indent=2)
            
            result['info_file'] = info_path
        
        return result
    
    def _collect_kubeflow(self, endpoint, target_path):
        """Collect from Kubeflow"""
        result = {
            'success': True,
            'items_collected': {},
            'errors': []
        }
        
        base_url = endpoint.rstrip('/')
        
        # Collect pipelines
        try:
            pipelines_url = f"{base_url}{self.platforms['kubeflow']['pipelines_endpoint']}"
            response = self.session.get(pipelines_url, timeout=30)
            
            if response.status_code == 200:
                pipelines = response.json()
                
                pipelines_dir = os.path.join(target_path, 'pipelines')
                os.makedirs(pipelines_dir, exist_ok=True)
                
                pipeline_count = 0
                for pipeline in pipelines.get('pipelines', []):
                    pipeline_id = pipeline['id']
                    
                    # Get pipeline details
                    detail_url = f"{pipelines_url}/{pipeline_id}"
                    detail_response = self.session.get(detail_url, timeout=30)
                    
                    if detail_response.status_code == 200:
                        pipeline_detail = detail_response.json()
                        
                        # Save pipeline
                        pipeline_file = os.path.join(pipelines_dir, f"pipeline_{pipeline_id}.yaml")
                        with open(pipeline_file, 'w') as f:
                            yaml.dump(pipeline_detail, f, default_flow_style=False)
                        
                        pipeline_count += 1
                        
                        # Get pipeline runs
                        runs_url = f"{base_url}{self.platforms['kubeflow']['runs_endpoint']}?pipeline_id={pipeline_id}"
                        runs_response = self.session.get(runs_url, timeout=30)
                        
                        if runs_response.status_code == 200:
                            runs = runs_response.json()
                            runs_file = os.path.join(pipelines_dir, f"pipeline_{pipeline_id}_runs.json")
                            with open(runs_file, 'w') as f:
                                json.dump(runs, f, indent=2)
                
                result['items_collected']['pipelines'] = pipeline_count
                print(f"   ✓ Collected {pipeline_count} pipelines")
            else:
                error_msg = f"Failed to get pipelines: {response.status_code}"
                result['errors'].append(error_msg)
                print(f"   ⚠ {error_msg}")
                
        except Exception as e:
            result['errors'].append(f"Pipeline collection error: {str(e)}")
            print(f"   ⚠ Error collecting pipelines: {e}")
        
        # Collect experiments
        try:
            experiments_url = f"{base_url}{self.platforms['kubeflow']['experiments_endpoint']}"
            response = self.session.get(experiments_url, timeout=30)
            
            if response.status_code == 200:
                experiments = response.json()
                
                experiments_dir = os.path.join(target_path, 'experiments')
                os.makedirs(experiments_dir, exist_ok=True)
                
                experiment_count = 0
                for experiment in experiments.get('experiments', []):
                    experiment_id = experiment['id']
                    
                    exp_file = os.path.join(experiments_dir, f"experiment_{experiment_id}.json")
                    with open(exp_file, 'w') as f:
                        json.dump(experiment, f, indent=2)
                    
                    experiment_count += 1
                
                result['items_collected']['experiments'] = experiment_count
                print(f"   ✓ Collected {experiment_count} experiments")
            else:
                print(f"   ⚠ No experiments found")
                
        except Exception as e:
            print(f"   ⚠ Experiment collection skipped: {e}")
        
        return result
    
    def _collect_mlflow(self, endpoint, target_path):
        """Collect from MLflow"""
        result = {
            'success': True,
            'items_collected': {},
            'errors': []
        }
        
        base_url = endpoint.rstrip('/')
        
        # Collect experiments
        try:
            experiments_url = f"{base_url}{self.platforms['mlflow']['experiments_endpoint']}"
            response = self.session.get(experiments_url, timeout=30)
            
            if response.status_code == 200:
                experiments_data = response.json()
                
                experiments_dir = os.path.join(target_path, 'experiments')
                os.makedirs(experiments_dir, exist_ok=True)
                
                experiment_count = 0
                runs_count = 0
                
                for experiment in experiments_data.get('experiments', []):
                    exp_id = experiment['experiment_id']
                    
                    # Save experiment
                    exp_file = os.path.join(experiments_dir, f"experiment_{exp_id}.json")
                    with open(exp_file, 'w') as f:
                        json.dump(experiment, f, indent=2)
                    
                    experiment_count += 1
                    
                    # Get runs for this experiment
                    runs_url = f"{base_url}{self.platforms['mlflow']['runs_endpoint']}"
                    runs_response = self.session.post(
                        runs_url,
                        json={'experiment_ids': [exp_id], 'max_results': 100},
                        timeout=30
                    )
                    
                    if runs_response.status_code == 200:
                        runs = runs_response.json()
                        
                        runs_file = os.path.join(experiments_dir, f"experiment_{exp_id}_runs.json")
                        with open(runs_file, 'w') as f:
                            json.dump(runs, f, indent=2)
                        
                        runs_count += len(runs.get('runs', []))
                
                result['items_collected']['experiments'] = experiment_count
                result['items_collected']['runs'] = runs_count
                print(f"   ✓ Collected {experiment_count} experiments with {runs_count} runs")
            else:
                print(f"   ⚠ No experiments found")
                
        except Exception as e:
            result['errors'].append(f"Experiment collection error: {str(e)}")
            print(f"   ⚠ Error collecting experiments: {e}")
        
        # Collect models
        try:
            models_url = f"{base_url}{self.platforms['mlflow']['models_endpoint']}"
            response = self.session.get(models_url, timeout=30)
            
            if response.status_code == 200:
                models = response.json()
                
                models_dir = os.path.join(target_path, 'models')
                os.makedirs(models_dir, exist_ok=True)
                
                models_count = len(models.get('registered_models', []))
                models_file = os.path.join(models_dir, 'registered_models.json')
                with open(models_file, 'w') as f:
                    json.dump(models, f, indent=2)
                
                result['items_collected']['models'] = models_count
                print(f"   ✓ Collected {models_count} registered models")
            else:
                print(f"   ⚠ No models found")
                
        except Exception as e:
            print(f"   ⚠ Model collection skipped: {e}")
        
        return result
    
    def _collect_bentoml(self, endpoint, target_path):
        """Collect from BentoML"""
        result = {
            'success': True,
            'items_collected': {},
            'errors': []
        }
        
        base_url = endpoint.rstrip('/')
        
        # Collect bentos
        try:
            bentos_url = f"{base_url}{self.platforms['bentoml']['bentos_endpoint']}"
            response = self.session.get(bentos_url, timeout=30)
            
            if response.status_code == 200:
                bentos = response.json()
                
                bentos_dir = os.path.join(target_path, 'bentos')
                os.makedirs(bentos_dir, exist_ok=True)
                
                bento_count = 0
                for bento in bentos.get('bentos', []):
                    bento_name = bento['name']
                    bento_version = bento['version']
                    
                    # Save bento info
                    bento_file = os.path.join(bentos_dir, f"bento_{bento_name}_{bento_version}.json")
                    with open(bento_file, 'w') as f:
                        json.dump(bento, f, indent=2)
                    
                    # Get bento details
                    detail_url = f"{base_url}/api/v1/bentos/{bento_name}/versions/{bento_version}"
                    detail_response = self.session.get(detail_url, timeout=30)
                    
                    if detail_response.status_code == 200:
                        detail = detail_response.json()
                        detail_file = os.path.join(bentos_dir, f"bento_{bento_name}_{bento_version}_detail.json")
                        with open(detail_file, 'w') as f:
                            json.dump(detail, f, indent=2)
                    
                    bento_count += 1
                
                result['items_collected']['bentos'] = bento_count
                print(f"   ✓ Collected {bento_count} bentos")
            else:
                print(f"   ⚠ No bentos found")
                
        except Exception as e:
            result['errors'].append(f"Bento collection error: {str(e)}")
            print(f"   ⚠ Error collecting bentos: {e}")
        
        # Collect models
        try:
            models_url = f"{base_url}{self.platforms['bentoml']['models_endpoint']}"
            response = self.session.get(models_url, timeout=30)
            
            if response.status_code == 200:
                models = response.json()
                
                models_dir = os.path.join(target_path, 'models')
                os.makedirs(models_dir, exist_ok=True)
                
                model_count = 0
                for model in models.get('models', []):
                    model_name = model['name']
                    model_version = model['version']
                    
                    model_file = os.path.join(models_dir, f"model_{model_name}_{model_version}.json")
                    with open(model_file, 'w') as f:
                        json.dump(model, f, indent=2)
                    
                    model_count += 1
                
                result['items_collected']['models'] = model_count
                print(f"   ✓ Collected {model_count} models")
            else:
                print(f"   ⚠ No models found")
                
        except Exception as e:
            print(f"   ⚠ Model collection skipped: {e}")
        
        return result
    
    def _collect_seldon(self, endpoint, target_path):
        """Collect from Seldon Core"""
        result = {
            'success': True,
            'items_collected': {},
            'errors': []
        }
        
        base_url = endpoint.rstrip('/')
        
        # Collect deployments
        try:
            deployments_url = f"{base_url}{self.platforms['seldon']['deployments_endpoint']}"
            response = self.session.get(deployments_url, timeout=30)
            
            if response.status_code == 200:
                deployments = response.json()
                
                deployments_dir = os.path.join(target_path, 'deployments')
                os.makedirs(deployments_dir, exist_ok=True)
                
                deployment_count = 0
                for deployment in deployments.get('items', []):
                    name = deployment['metadata']['name']
                    namespace = deployment['metadata']['namespace']
                    
                    # Save deployment
                    deployment_file = os.path.join(deployments_dir, f"deployment_{namespace}_{name}.yaml")
                    with open(deployment_file, 'w') as f:
                        yaml.dump(deployment, f, default_flow_style=False)
                    
                    deployment_count += 1
                    
                    # Get model details if available
                    if 'spec' in deployment and 'predictors' in deployment['spec']:
                        for predictor in deployment['spec']['predictors']:
                            if 'graph' in predictor:
                                model_name = predictor['graph'].get('name')
                                if model_name:
                                    model_info = {
                                        'deployment': name,
                                        'namespace': namespace,
                                        'model': model_name,
                                        'predictor': predictor['name']
                                    }
                                    
                                    models_file = os.path.join(deployments_dir, 'models.json')
                                    if os.path.exists(models_file):
                                        with open(models_file, 'r') as f:
                                            models = json.load(f)
                                    else:
                                        models = []
                                    
                                    models.append(model_info)
                                    with open(models_file, 'w') as f:
                                        json.dump(models, f, indent=2)
                
                result['items_collected']['deployments'] = deployment_count
                print(f"   ✓ Collected {deployment_count} deployments")
            else:
                print(f"   ⚠ No deployments found")
                
        except Exception as e:
            result['errors'].append(f"Deployment collection error: {str(e)}")
            print(f"   ⚠ Error collecting deployments: {e}")
        
        return result
    
    def test_connection(self, platform, endpoint, token=None):
        """Test connection to MLOps platform"""
        if token:
            self.session.headers.update({'Authorization': f'Bearer {token}'})
        
        try:
            if platform == 'kubeflow':
                url = f"{endpoint.rstrip('/')}{self.platforms['kubeflow']['pipelines_endpoint']}"
            elif platform == 'mlflow':
                url = f"{endpoint.rstrip('/')}{self.platforms['mlflow']['experiments_endpoint']}"
            elif platform == 'bentoml':
                url = f"{endpoint.rstrip('/')}{self.platforms['bentoml']['bentos_endpoint']}"
            elif platform == 'seldon':
                url = f"{endpoint.rstrip('/')}{self.platforms['seldon']['deployments_endpoint']}"
            else:
                return {'success': False, 'error': 'Invalid platform'}
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return {'success': True, 'message': 'Connection successful'}
            else:
                return {
                    'success': False, 
                    'error': f"HTTP {response.status_code}: {response.reason}"
                }
                
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Connection failed - check endpoint URL'}
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Connection timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_platform_info(self, platform):
        """Get information about a platform"""
        return self.platforms.get(platform, {})
    
    def list_supported_platforms(self):
        """List all supported platforms"""
        return list(self.platforms.keys())