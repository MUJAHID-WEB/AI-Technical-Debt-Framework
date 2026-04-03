import os
import json
import requests
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

class AIAnalyzer:
    """
    Enhanced OpenRouter-powered AI Analyst for the 6-Tier Technical Debt Framework.
    Provides intelligent analysis across all tiers with reasoning capabilities.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "stepfun/step-3.5-flash:free"
        
    def analyze_structure(self, tier1_data):
        """
        Analyze project structure with semantic understanding
        """
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return self._generate_structure_analysis(tier1_data)
            
        services = tier1_data.get('services', [])
        models = tier1_data.get('models', [])
        languages = tier1_data.get('languages', {})
        
        prompt = f"""Analyze this project structure and provide semantic insights:

Project Stats:
- Services: {len(services)}
- Models: {len(models)}
- Languages: {list(languages.keys())}

Service names: {[s.get('name') for s in services[:10]]}
Model names: {[m.get('name') for m in models[:10]]}

Provide analysis of:
1. Project organization patterns
2. Potential architectural style (monolith, microservices, hybrid)
3. AI integration maturity level
4. Suggested improvements for structure

Return JSON with: {{
    "patterns": ["pattern1", "pattern2"],
    "architectural_style": "style",
    "ai_maturity": "level",
    "structure_improvements": ["improvement1"]
}}"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(self.url, headers=headers, data=json.dumps(payload), timeout=60)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            return json.loads(content)
            
        except Exception as e:
            print(f"Structure analysis error: {e}")
            return self._generate_structure_analysis(tier1_data)
    
    def analyze_architecture(self, tier2_data):
        """
        Analyze architecture patterns and anti-patterns
        """
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return self._generate_architecture_analysis(tier2_data)
            
        services = tier2_data.get('services', [])
        dependencies = tier2_data.get('dependencies', {})
        endpoints = tier2_data.get('api_endpoints', [])
        
        prompt = f"""Analyze this system architecture:

Services: {len(services)}
Service details: {json.dumps([{'name': s.get('name'), 'endpoints': s.get('endpoint_count', 0)} for s in services[:10]], indent=2)}
Dependencies: {json.dumps(dependencies, indent=2)[:500]}
API Endpoints: {len(endpoints)}

Identify:
1. Architectural patterns (e.g., layered, event-driven, microservices)
2. Anti-patterns (e.g., chatty services, tight coupling)
3. Communication style (sync/async)
4. Potential bottlenecks

Return JSON: {{
    "patterns": ["pattern1", "pattern2"],
    "anti_patterns": ["anti_pattern1"],
    "communication_style": "sync|async|hybrid",
    "bottlenecks": ["bottleneck1"]
}}"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(self.url, headers=headers, data=json.dumps(payload), timeout=60)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            return json.loads(content)
            
        except Exception as e:
            print(f"Architecture analysis error: {e}")
            return self._generate_architecture_analysis(tier2_data)
    
    def analyze_smells(self, tier3_data, tier2_data):
        """
        Analyze AI smells with severity assessment
        """
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return self._generate_smell_analysis(tier3_data)
            
        direct_calls = tier3_data.get('direct_model_calls', {})
        hidden_consumers = tier3_data.get('hidden_consumers', [])
        feedback_loops = tier3_data.get('feedback_loops', [])
        glue_ratio = tier3_data.get('glue_code_ratio', 0)
        
        prompt = f"""Assess these AI architectural smells:

Direct Model Calls: {direct_calls.get('count', 0)} services (ratio: {direct_calls.get('ratio', 0):.1%})
Hidden Consumers: {len(hidden_consumers)}
Feedback Loops: {len(feedback_loops)}
Glue Code Ratio: {glue_ratio:.1%}

Provide:
1. Severity assessment for each smell (Critical/High/Medium/Low)
2. Impact prediction on maintainability
3. Priority ranking for fixes

Return JSON: {{
    "critical_issues": [{{"type": "smell_type", "severity": "level", "impact": "description"}}],
    "impact_predictions": ["prediction1"],
    "priority_order": ["issue1", "issue2"]
}}"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(self.url, headers=headers, data=json.dumps(payload), timeout=60)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            return json.loads(content)
            
        except Exception as e:
            print(f"Smell analysis error: {e}")
            return self._generate_smell_analysis(tier3_data)
    
    def forecast_debt(self, tier4_data, tier5_data):
        """
        Forecast technical debt accumulation
        """
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return self._generate_debt_forecast(tier4_data)
            
        mes_score = tier4_data.get('mes_score', 0)
        mes_level = tier4_data.get('mes_level', 'UNKNOWN')
        
        prompt = f"""Forecast technical debt accumulation based on current MES:

Current MES Score: {mes_score}/10
Current Level: {mes_level}

Predict:
1. Expected MES increase over 6/12/24 months
2. Impact on development velocity
3. Recommended intervention timeline

Return JSON: {{
    "predicted_increase": 0.0,
    "six_month_forecast": 0.0,
    "twelve_month_forecast": 0.0,
    "velocity_impact": "description",
    "intervention_timeline": "ASAP|Within 3 months|Within 6 months|Within 12 months"
}}"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(self.url, headers=headers, data=json.dumps(payload), timeout=60)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            return json.loads(content)
            
        except Exception as e:
            print(f"Debt forecast error: {e}")
            return self._generate_debt_forecast(tier4_data)
    
    def assess_risks(self, tier5_data, tier4_data):
        """
        Assess system risks and provide mitigation strategies
        """
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return self._generate_risk_assessment(tier5_data, tier4_data)
            
        bug_rate = tier5_data.get('bug_metrics', {}).get('bug_rate', 0)
        commit_count = tier5_data.get('commit_count', 0)
        mes_score = tier4_data.get('mes_score', 0)
        
        prompt = f"""Assess system risks:

Bug Rate: {bug_rate:.1%}
Commit Count: {commit_count}
MES Score: {mes_score}/10

Provide:
1. Overall risk level (Low/Medium/High/Critical)
2. Specific risk factors
3. Mitigation strategies for each risk

Return JSON: {{
    "overall_risk": "level",
    "risk_factors": [
        {{"factor": "description", "severity": "level", "mitigation": "strategy"}}
    ],
    "criticality_score": 0.0
}}"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(self.url, headers=headers, data=json.dumps(payload), timeout=60)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            return json.loads(content)
            
        except Exception as e:
            print(f"Risk assessment error: {e}")
            return self._generate_risk_assessment(tier5_data, tier4_data)
    
    def analyze_results(self, results):
        """
        Comprehensive analysis of all tier results with strategic recommendations
        """
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return {
                "error": "OpenRouter API Key not configured. Please update the .env file.",
                "reasoning": "N/A"
            }
            
        tier1 = results.get('tier1', {})
        tier2 = results.get('tier2', {})
        tier3 = results.get('tier3', {})
        tier4 = results.get('tier4', {})
        tier5 = results.get('tier5', {})
        tier6 = results.get('tier6', {})
        
        prompt = f"""As an AI architecture expert, analyze this system and provide strategic recommendations.

SYSTEM METRICS:
- Services: {tier1.get('statistics', {}).get('services_count', 0)}
- Models: {tier1.get('statistics', {}).get('models_count', 0)}
- MES Score: {tier4.get('mes_score', 0)}/10 ({tier4.get('mes_level', 'UNKNOWN')})
- Direct Model Calls: {tier3.get('direct_model_calls', {}).get('count', 0)}
- Glue Code: {tier3.get('glue_code_ratio', 0):.1%}
- Hidden Consumers: {len(tier3.get('hidden_consumers', []))}
- Bug Rate: {tier5.get('bug_metrics', {}).get('bug_rate', 0):.1%}
- Degradation Ratio: {tier6.get('degradation_ratio', 0):.2f}x

Provide a comprehensive analysis with:

1. EXECUTIVE SUMMARY: High-level overview of system health
2. KEY FINDINGS: 3-5 critical findings with priorities (Critical/High/Medium/Low)
3. For each finding include: root cause, impact, and specific recommendation
4. STRATEGIC PLAN: Phased approach (0-3 months, 3-6 months, 6-12 months)

Return JSON with structure:
{{
    "executive_summary": "summary text",
    "findings": [
        {{
            "title": "Finding title",
            "priority": "Critical|High|Medium|Low",
            "root_cause": "Detailed explanation",
            "impact": "System impact description",
            "recommendation": "Actionable recommendation"
        }}
    ],
    "strategic_plan": {{
        "phase1": {{"title": "Phase 1 (0-3 Months)", "tasks": ["task1", "task2"]}},
        "phase2": {{"title": "Phase 2 (3-6 Months)", "tasks": ["task1", "task2"]}},
        "phase3": {{"title": "Phase 3 (6-12 Months)", "tasks": ["task1", "task2"]}}
    }}
}}"""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
                "temperature": 0.3
            }
            
            response = requests.post(self.url, headers=headers, data=json.dumps(payload), timeout=90)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            try:
                report_data = json.loads(content)
                return {
                    "report_json": report_data,
                    "reasoning": result['choices'][0]['message'].get('reasoning_details', {})
                }
            except json.JSONDecodeError:
                return {
                    "error": "JSON Parse Error",
                    "raw_content": content[:500]
                }
                
        except Exception as e:
            return {
                "error": f"AI Analysis failed: {str(e)}",
                "reasoning": "Connection error"
            }
    
    # Template methods for fallback when AI is unavailable
    
    def _generate_structure_analysis(self, tier1_data):
        """Generate structure analysis template"""
        services = tier1_data.get('services', [])
        models = tier1_data.get('models', [])
        
        patterns = []
        if len(services) > 1:
            patterns.append("Microservices architecture detected")
        if models:
            patterns.append("AI components integrated")
        
        return {
            "patterns": patterns,
            "architectural_style": "Microservices" if len(services) > 1 else "Monolith",
            "ai_maturity": "Emerging" if models else "None",
            "structure_improvements": [
                "Consider adding API gateway",
                "Implement service discovery",
                "Add distributed tracing"
            ]
        }
    
    def _generate_architecture_analysis(self, tier2_data):
        """Generate architecture analysis template"""
        services = tier2_data.get('services', [])
        endpoints = tier2_data.get('api_endpoints', [])
        
        return {
            "patterns": ["Service-based architecture" if len(services) > 1 else "Monolithic"],
            "anti_patterns": [],
            "communication_style": "hybrid",
            "bottlenecks": ["Potential single point of failure" if len(services) == 1 else "None detected"]
        }
    
    def _generate_smell_analysis(self, tier3_data):
        """Generate smell analysis template"""
        direct_calls = tier3_data.get('direct_model_calls', {})
        critical_issues = []
        
        if direct_calls.get('count', 0) > 0:
            critical_issues.append({
                "type": "direct_model_coupling",
                "severity": "High",
                "impact": "Increased maintenance cost and reduced flexibility"
            })
        
        return {
            "critical_issues": critical_issues,
            "impact_predictions": ["Model changes will require widespread service updates" if critical_issues else "Low impact expected"],
            "priority_order": ["direct_model_coupling"] if critical_issues else []
        }
    
    def _generate_debt_forecast(self, tier4_data):
        """Generate debt forecast template"""
        mes_score = tier4_data.get('mes_score', 0)
        
        # Simple forecasting based on MES
        if mes_score > 7:
            predicted_increase = 2.5
            intervention = "ASAP"
        elif mes_score > 4:
            predicted_increase = 1.5
            intervention = "Within 3 months"
        else:
            predicted_increase = 0.5
            intervention = "Within 6 months"
        
        return {
            "predicted_increase": predicted_increase,
            "six_month_forecast": min(10, mes_score + predicted_increase),
            "twelve_month_forecast": min(10, mes_score + predicted_increase * 2),
            "velocity_impact": "Development velocity will decrease by 15-20% if not addressed",
            "intervention_timeline": intervention
        }
    
    def _generate_risk_assessment(self, tier5_data, tier4_data):
        """Generate risk assessment template"""
        bug_rate = tier5_data.get('bug_metrics', {}).get('bug_rate', 0)
        mes_score = tier4_data.get('mes_score', 0)
        
        if bug_rate > 0.3 or mes_score > 7:
            overall_risk = "High"
            criticality_score = 0.8
        elif bug_rate > 0.15 or mes_score > 4:
            overall_risk = "Medium"
            criticality_score = 0.5
        else:
            overall_risk = "Low"
            criticality_score = 0.2
        
        return {
            "overall_risk": overall_risk,
            "risk_factors": [
                {
                    "factor": f"High bug rate ({bug_rate:.1%})" if bug_rate > 0.2 else "Low bug rate",
                    "severity": "High" if bug_rate > 0.2 else "Low",
                    "mitigation": "Implement comprehensive testing strategy"
                },
                {
                    "factor": f"Model entanglement (MES: {mes_score})",
                    "severity": "Critical" if mes_score > 7 else "Medium" if mes_score > 4 else "Low",
                    "mitigation": "Introduce model serving layer"
                }
            ],
            "criticality_score": criticality_score
        }