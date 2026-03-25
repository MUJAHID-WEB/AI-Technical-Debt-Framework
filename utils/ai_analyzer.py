import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class AIAnalyzer:
    """
    OpenRouter-powered AI Analyst for the 6-Tier Technical Debt Framework.
    Uses stepfun/step-3.5-flash:free with reasoning enabled.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "stepfun/step-3.5-flash:free"
        
    def analyze_results(self, results):
        """
        Performs a deep-reasoning analysis of the 6-tier framework results.
        """
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return {
                "error": "OpenRouter API Key not configured. Please update the .env file.",
                "reasoning": "N/A"
            }
            
        # Format the 6-tier results into a structured prompt
        tier1 = results.get('tier1', {})
        tier2 = results.get('tier2', {})
        tier3 = results.get('tier3', {})
        tier4 = results.get('tier4', {})
        tier5 = results.get('tier5', {})
        tier6 = results.get('tier6', {})
        
        # Extract detailed findings for better AI reasoning
        direct_calls_detail = ""
        if tier3.get('direct_model_calls', {}).get('details'):
            direct_calls_detail = "\n        Direct Model Call Examples:"
            for service_call in tier3['direct_model_calls']['details'][:3]:
                for detail in service_call.get('details', [])[:2]:
                    direct_calls_detail += f"\n        - {service_call['service']}: {detail['file']}:{detail['line']} -> `{detail['code']}`"

        hidden_consumers_detail = ""
        if tier3.get('hidden_consumers'):
            hidden_consumers_detail = "\n        Hidden Model Consumers:"
            for sc in tier3['hidden_consumers'][:5]:
                hidden_consumers_detail += f"\n        - Model `{sc['model']}` used in `{sc['consumer']}` ({sc['file']}:{sc['line']})"

        glue_code_detail = ""
        if tier3.get('glue_code_details'):
            # Get top 3 services by glue ratio
            sorted_glue = sorted(tier3['glue_code_details'].items(), key=lambda x: x[1].get('ratio', 0), reverse=True)
            glue_code_detail = "\n        High Glue Code Services:"
            for name, data in sorted_glue[:3]:
                glue_code_detail += f"\n        - {name}: {data.get('ratio', 0):.1%} glue code ({data.get('glue_lines', 0)} lines)"

        prompt = f"""Analyze the architectural health of this system and return a strictly structured JSON report.
        Use the specific file names, code snippets, and metrics provided to explain the root cause and provide actionable recommendations.
        
        JSON SCHEMA:
        {{
            "findings": [
                {{
                    "title": "Finding Title (Tier X)",
                    "priority": "Critical|High|Medium|Low",
                    "root_cause": "Detailed explanation mentioning specific files/code if possible",
                    "impact": "System impact",
                    "recommendation": "Specific mitigation steps (e.g., 'Refactor X to use Y')"
                }}
            ],
            "strategic_plan": {{
                "phase1": {{ "title": "Phase 1 (0-3 Months)", "tasks": ["task1", "task2"] }},
                "phase2": {{ "title": "Phase 2 (3-6 Months)", "tasks": ["task1", "task2"] }}
            }},
            "executive_summary": "High-level overview"
        }}

        System Data:
        TIER 1 (DATA COLLECTION):
        - Services: {tier1.get('statistics', {}).get('services_count', 0)}
        - Models: {tier1.get('statistics', {}).get('models_count', 0)}
        - Languages: {', '.join(tier1.get('languages', {}).keys())}

        TIER 2 (SYSTEM ANALYSIS):
        - Endpoints: {tier2.get('endpoint_count', 0)}
        - Dependencies: {tier2.get('dependency_count', 0)}

        TIER 3 (AI SMELL DETECTION):
        - Coupling: {tier3.get('direct_model_calls', {}).get('count', 0)} services{direct_calls_detail}{hidden_consumers_detail}{glue_code_detail}
        - Complex Pipelines: {tier3.get('pipeline_complexity', {}).get('complex_pipelines', 0)}
        - Feedback Loops: {len(tier3.get('feedback_loops', []))} detected

        TIER 4 (MES SCORE):
        - SCORE: {tier4.get('mes_score', 0)}/10 ({tier4.get('mes_level', 'UNKNOWN')})

        TIER 5 (MAINTAINABILITY):
        - Bug Rate: {tier5.get('bug_metrics', {}).get('bug_rate', 0):.1%}
        - Avg Change Radius: {tier5.get('impact_metrics', {}).get('avg_impact', 0):.2f} files

        TIER 6 (VALIDATION):
        - Degradation: {tier6.get('degradation_ratio', 0):.2f}x
        """

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            # Initial Analysis with Reasoning
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "reasoning": {"enabled": True},
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(self.url, headers=headers, data=json.dumps(payload), timeout=120)
            response.raise_for_status()
            
            resp_json = response.json()
            choice = resp_json['choices'][0]['message']
            
            # Final JSON refinement
            messages = [
                {"role": "user", "content": prompt},
                {
                    "role": "assistant",
                    "content": choice.get('content'),
                    "reasoning_details": choice.get('reasoning_details')
                },
                {"role": "user", "content": "Return the finalized JSON report based on your initial findings. Ensure it is perfectly valid JSON according to the schema."}
            ]
            
            payload2 = {
                "model": self.model,
                "messages": messages,
                "reasoning": {"enabled": True},
                "response_format": {"type": "json_object"}
            }
            
            response2 = requests.post(self.url, headers=headers, data=json.dumps(payload2), timeout=120)
            response2.raise_for_status()
            
            final_resp = response2.json()
            final_choice = final_resp['choices'][0]['message']
            
            # Try to parse content as JSON
            try:
                report_data = json.loads(final_choice.get('content', '{}'))
            except:
                report_data = {"error": "JSON Parse Error", "raw_content": final_choice.get('content')}
            
            return {
                "report_json": report_data,
                "reasoning": final_choice.get('reasoning_details') or choice.get('reasoning_details')
            }
            
        except Exception as e:
            return {
                "error": f"AI Analysis failed: {str(e)}",
                "reasoning": "Connection error"
            }
