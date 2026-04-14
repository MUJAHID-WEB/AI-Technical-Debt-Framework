import os
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv()

class AIArchitect:
    """
    AI-Powered Architecture Designer
    Proposes improved architectures for AI-enabled systems
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.model = os.getenv("OPENROUTER_MODEL", "google/gemma-4-26b-a4b-it:free")
        print(f"🏗️ AIArchitect initialized with model: {self.model}")
        
    def propose_architecture(self, results):
        """
        Generate improved architecture proposal based on analysis results
        """
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return self._generate_template_architecture(results)
            
        # Extract key information for architecture proposal
        tier1 = results.get('tier1', {})
        tier2 = results.get('tier2', {})
        tier3 = results.get('tier3', {})
        tier4 = results.get('tier4', {})
        
        services = tier2.get('services', [])
        models = tier1.get('models', [])
        mes_score = tier4.get('mes_score', 0)
        
        # Build comprehensive prompt
        prompt = f"""As a senior software architect specializing in AI-enabled microservices, propose an improved architecture for the following system.

CURRENT SYSTEM ANALYSIS:
- Services: {len(services)} services detected
- Models: {len(models)} ML models
- MES Score: {mes_score}/10 (Model Entanglement Score)
- Direct Model Calls: {tier3.get('direct_model_calls', {}).get('count', 0)} services directly calling models
- Glue Code Ratio: {tier3.get('glue_code_ratio', 0):.1%}
- Feedback Loops: {len(tier3.get('feedback_loops', []))} detected

SERVICES:
{json.dumps([{'name': s.get('name'), 'language': s.get('language'), 'endpoints': s.get('endpoint_count', 0)} for s in services[:10]], indent=2)}

MODELS:
{json.dumps([{'name': m.get('name'), 'type': m.get('type', 'Unknown')} for m in models[:10]], indent=2)}

Please provide a detailed improved architecture that:
1. Introduces proper AI isolation layers (model serving, feature store, etc.)
2. Reduces model entanglement and technical debt
3. Improves maintainability and scalability
4. Follows microservices best practices
5. Includes specific component recommendations

Return a JSON object with this structure:
{{
    "improved_architecture": {{
        "name": "Architecture Name",
        "description": "High-level description",
        "components": [
            {{
                "name": "Component Name",
                "type": "service|gateway|model_server|feature_store|orchestrator|monitoring",
                "purpose": "What this component does",
                "technologies": ["tech1", "tech2"],
                "responsibilities": ["resp1", "resp2"]
            }}
        ],
        "data_flow": [
            {{
                "from": "component_a",
                "to": "component_b",
                "description": "What data flows",
                "protocol": "gRPC|REST|message_queue"
            }}
        ],
        "improvements": [
            "Improvement 1",
            "Improvement 2"
        ],
        "migration_steps": [
            "Step 1: ...",
            "Step 2: ..."
        ],
        "estimated_effort": "Low|Medium|High|Very High",
        "expected_mes_reduction": 0.0
    }}
}}"""

        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.4
                }
                
                print(f"📡 AI Architecture Request: {self.model} (Attempt {attempt + 1})")
                response = requests.post(self.url, headers=headers, data=json.dumps(payload), timeout=90)
                print(f"📥 Response status: {response.status_code}")
                
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        print(f"⚠️ Rate limited (429). Retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    else:
                        return {
                            "error": "OpenRouter rate limit exceeded. Please wait a few minutes and try again.",
                            "type": "rate_limit_error"
                        }
                        
                response.raise_for_status()
                
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                try:
                    architecture_data = json.loads(content)
                    return {
                        "architecture_json": architecture_data,
                        "explanation": architecture_data.get('explanation', "AI-proposed architectural improvements.")
                    }
                except json.JSONDecodeError:
                    return {
                        "error": "Failed to parse AI response as JSON",
                        "raw_response": content
                    }
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Request failed: {str(e)}. Retrying...")
                    time.sleep(2)
                    continue
                print(f"❌ AI Architect Error: {str(e)}")
                return {
                    "error": f"AI Architecture failed after {max_retries} attempts: {str(e)}",
                    "reasoning": f"Exception occurred: {type(e).__name__}"
                }
        
        return {"error": "AI Architecture proposal failed after multiple attempts"}
    
    def _generate_template_architecture(self, results):
        """Generate template architecture when AI is unavailable"""
        tier1 = results.get('tier1', {})
        tier2 = results.get('tier2', {})
        tier3 = results.get('tier3', {})
        tier4 = results.get('tier4', {})
        
        services = tier2.get('services', [])
        models = tier1.get('models', [])
        mes_score = tier4.get('mes_score', 0)
        
        # Determine architecture based on MES score
        if mes_score > 7:
            architecture_type = "Full Isolation Architecture"
            description = "Complete separation of AI components with dedicated model serving layer"
        elif mes_score > 4:
            architecture_type = "Gradual Decoupling Architecture"
            description = "Phased approach to isolate AI components while maintaining existing functionality"
        else:
            architecture_type = "Well-Integrated Architecture"
            description = "Optimized existing architecture with minor improvements"
        
        components = [
            {
                "name": "API Gateway",
                "type": "gateway",
                "purpose": "Route requests and handle authentication",
                "technologies": ["Kong", "NGINX", "Traefik"],
                "responsibilities": ["Request routing", "Rate limiting", "Authentication"]
            }
        ]
        
        # Add service components
        for i, service in enumerate(services[:5]):
            components.append({
                "name": service.get('name', f'Service-{i+1}'),
                "type": "service",
                "purpose": f"Business logic for {service.get('name', 'service')}",
                "technologies": [service.get('language', 'Unknown')],
                "responsibilities": ["Business logic", "Data processing"]
            })
        
        # Add model serving if needed
        if models:
            components.append({
                "name": "Model Serving Layer",
                "type": "model_server",
                "purpose": "Serve ML models via APIs",
                "technologies": ["BentoML", "Seldon Core", "KServe"],
                "responsibilities": ["Model inference", "Version management", "Load balancing"]
            })
        
        # Add feature store if glue code is high
        if tier3.get('glue_code_ratio', 0) > 0.2:
            components.append({
                "name": "Feature Store",
                "type": "feature_store",
                "purpose": "Centralized feature management",
                "technologies": ["Feast", "Tecton", "Hopsworks"],
                "responsibilities": ["Feature engineering", "Feature serving", "Feature versioning"]
            })
        
        # Add monitoring
        components.append({
            "name": "Observability Stack",
            "type": "monitoring",
            "purpose": "Monitor system health and model performance",
            "technologies": ["Prometheus", "Grafana", "Jaeger"],
            "responsibilities": ["Metrics collection", "Tracing", "Alerting"]
        })
        
        # Build data flow
        data_flow = [
            {
                "from": "API Gateway",
                "to": "Service Layer",
                "description": "API requests",
                "protocol": "REST/gRPC"
            }
        ]
        
        if models:
            data_flow.append({
                "from": "Service Layer",
                "to": "Model Serving Layer",
                "description": "Inference requests",
                "protocol": "gRPC"
            })
        
        # Generate improvements
        improvements = [
            "Decouple AI models from business logic",
            "Implement model versioning and canary deployments",
            "Add comprehensive monitoring and observability",
            "Standardize data transformation pipelines"
        ]
        
        if tier3.get('direct_model_calls', {}).get('count', 0) > 0:
            improvements.insert(0, "Introduce model serving layer to eliminate direct model calls")
        
        if tier3.get('glue_code_ratio', 0) > 0.2:
            improvements.insert(1, "Implement shared feature engineering library")
        
        # Migration steps
        migration_steps = [
            "Audit all model dependencies and usage patterns",
            "Design model serving API contracts",
            "Implement model serving layer with shadow mode",
            "Gradually migrate services to use model APIs",
            "Decommission direct model access",
            "Set up monitoring and alerting"
        ]
        
        # Calculate expected MES reduction
        expected_reduction = min(5, mes_score * 0.6) if mes_score > 0 else 3
        
        return {
            "improved_architecture": {
                "name": architecture_type,
                "description": description,
                "components": components,
                "data_flow": data_flow,
                "improvements": improvements,
                "migration_steps": migration_steps,
                "estimated_effort": "High" if mes_score > 7 else "Medium" if mes_score > 4 else "Low",
                "expected_mes_reduction": round(expected_reduction, 1)
            }
        }
    
    def generate_architecture_diagram(self, architecture):
        """
        Generate Mermaid diagram code for architecture visualization
        """
        if not architecture or 'improved_architecture' not in architecture:
            return self._get_default_diagram()
        
        arch = architecture['improved_architecture']
        components = arch.get('components', [])
        data_flow = arch.get('data_flow', [])
        
        # Build Mermaid diagram
        diagram = "graph TB\n"
        
        # Add components
        for comp in components:
            comp_name = comp.get('name', 'Unknown').replace(' ', '_')
            comp_type = comp.get('type', 'service')
            
            # Style based on type
            if comp_type == 'gateway':
                diagram += f"    {comp_name}[{comp.get('name')}]:::gateway\n"
            elif comp_type == 'model_server':
                diagram += f"    {comp_name}(({comp.get('name')})):::model\n"
            elif comp_type == 'feature_store':
                diagram += f"    {comp_name}[{comp.get('name')}]:::feature\n"
            elif comp_type == 'monitoring':
                diagram += f"    {comp_name}[{comp.get('name')}]:::monitor\n"
            else:
                diagram += f"    {comp_name}[{comp.get('name')}]:::service\n"
        
        # Add flows
        for flow in data_flow:
            from_comp = flow.get('from', '').replace(' ', '_')
            to_comp = flow.get('to', '').replace(' ', '_')
            protocol = flow.get('protocol', 'REST')
            diagram += f"    {from_comp} -->|{protocol}| {to_comp}\n"
        
        # Add styles
        diagram += """
    classDef gateway fill:#2563eb,stroke:#1e40af,color:white
    classDef service fill:#7c3aed,stroke:#5b21b6,color:white
    classDef model fill:#dc2626,stroke:#b91c1c,color:white
    classDef feature fill:#ea580c,stroke:#c2410c,color:white
    classDef monitor fill:#059669,stroke:#047857,color:white
"""
        
        return diagram
    
    def _get_default_diagram(self):
        """Get default architecture diagram"""
        return """
graph TB
    Gateway[API Gateway]:::gateway
    Service1[Business Service]:::service
    Service2[Business Service]:::service
    ModelServer((Model Serving)):::model
    FeatureStore[Feature Store]:::feature
    Monitor[Monitoring]:::monitor
    
    Gateway -->|REST| Service1
    Gateway -->|REST| Service2
    Service1 -->|gRPC| ModelServer
    Service2 -->|gRPC| ModelServer
    Service1 -->|REST| FeatureStore
    Service2 -->|REST| FeatureStore
    ModelServer -.->|Metrics| Monitor
    FeatureStore -.->|Metrics| Monitor
    
    classDef gateway fill:#2563eb,stroke:#1e40af,color:white
    classDef service fill:#7c3aed,stroke:#5b21b6,color:white
    classDef model fill:#dc2626,stroke:#b91c1c,color:white
    classDef feature fill:#ea580c,stroke:#c2410c,color:white
    classDef monitor fill:#059669,stroke:#047857,color:white
"""