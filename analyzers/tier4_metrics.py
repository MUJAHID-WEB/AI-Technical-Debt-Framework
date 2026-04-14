import numpy as np
from collections import defaultdict

class ModelEntanglementEngine:
    """
    TIER 4: Model Entanglement Score (MES) Computation
    Calculates the degree of entanglement between AI models and system components
    """
    
    def __init__(self, tier1_data, tier2_data, tier3_data):
        self.tier1 = tier1_data
        self.tier2 = tier2_data
        self.tier3 = tier3_data
        
        # MES component weights (from research)
        self.weights = {
            'direct_calls': 0.25,
            'shared_features': 0.20,
            'pipeline_complexity': 0.15,
            'retrain_frequency': 0.20,
            'impact_radius': 0.10,
            'feedback_loop': 0.10
        }
        
        self.results = {
            'mes_score': 0,
            'mes_level': 'UNKNOWN',
            'components': {},
            'weights': self.weights,
            'interpretation': '',
            'contributions': {},
            'risk_factors': []
        }
    
    def calculate(self):
        """Calculate Model Entanglement Score (0-10)"""
        print(f"\n📐 TIER 4: Computing Model Entanglement Score")
        
        # Calculate each component
        D = self._calculate_direct_calls_factor()
        S = self._calculate_shared_features_factor()
        P = self._calculate_pipeline_complexity_factor()
        R = self._calculate_retrain_frequency_factor()
        I = self._calculate_impact_radius_factor()
        F = self._calculate_feedback_loop_factor()
        
        self.results['components'] = {
            'direct_calls': D,
            'shared_features': S,
            'pipeline_complexity': P,
            'retrain_frequency': R,
            'impact_radius': I,
            'feedback_loop': F
        }
        
        # Calculate weighted contributions
        contributions = {}
        for key, value in self.results['components'].items():
            contributions[key] = value * self.weights[key]
        
        self.results['contributions'] = contributions
        
        # Calculate MES (0-10 scale)
        mes = sum(contributions.values()) * 10
        self.results['mes_score'] = round(mes, 2)
        
        # Determine level
        self.results['mes_level'] = self._get_mes_level(mes)
        self.results['interpretation'] = self._get_interpretation(mes)
        
        # Identify risk factors
        self._identify_risk_factors()
        
        print(f"  ✓ MES Score: {self.results['mes_score']}/10")
        print(f"  ✓ Level: {self.results['mes_level']}")
        print(f"  ✓ Interpretation: {self.results['interpretation']}")
        
        return self.results
    
    def _calculate_direct_calls_factor(self):
        """Calculate factor for direct model calls (0-1)"""
        direct_calls = self.tier3.get('direct_model_calls', {})
        ratio = direct_calls.get('ratio', 0)
        
        # Normalize: 0% = 0, 30%+ = 1
        factor = min(ratio / 0.3, 1.0)
        
        print(f"    Direct calls factor: {factor:.2f} (ratio: {ratio:.1%})")
        return factor
    
    def _calculate_shared_features_factor(self):
        """Calculate factor for shared feature pipelines (0-1)"""
        shared_features = self.tier3.get('shared_features', [])
        
        # Count modules shared by multiple services
        shared_count = len(shared_features)
        
        # Normalize based on number of services
        num_services = len(self.tier2.get('services', []))
        if num_services > 0:
            factor = min(shared_count / (num_services * 0.5), 1.0)
        else:
            factor = 0
        
        print(f"    Shared features factor: {factor:.2f} ({shared_count} shared modules)")
        return factor
    
    def _calculate_pipeline_complexity_factor(self):
        """Calculate factor for pipeline complexity (0-1)"""
        pipeline_complexity = self.tier3.get('pipeline_complexity', {})
        complex_count = pipeline_complexity.get('complex_pipelines', 0)
        total_pipelines = len(pipeline_complexity.get('pipelines', []))
        
        if total_pipelines > 0:
            factor = min(complex_count / total_pipelines, 1.0)
        else:
            factor = 0
        
        print(f"    Pipeline complexity factor: {factor:.2f} ({complex_count}/{total_pipelines} complex)")
        return factor
    
    def _calculate_retrain_frequency_factor(self):
        """Calculate factor for retraining frequency (0-1)"""
        retrain_freq = self.tier3.get('retrain_frequency', 0)
        
        # Normalize: 0 = 0, 4+ per month = 1
        factor = min(retrain_freq / 4, 1.0)
        
        print(f"    Retrain frequency factor: {factor:.2f} ({retrain_freq} events/month)")
        return factor
    
    def _calculate_impact_radius_factor(self):
        """Calculate factor for impact radius (0-1)"""
        impact_radius = self.tier3.get('impact_radius', {})
        
        if impact_radius:
            avg_impact = sum(impact_radius.values()) / len(impact_radius)
            num_services = len(self.tier2.get('services', []))
            
            if num_services > 0:
                factor = min(avg_impact / num_services, 1.0)
            else:
                factor = 0
        else:
            factor = 0
        
        print(f"    Impact radius factor: {factor:.2f}")
        return factor
    
    def _calculate_feedback_loop_factor(self):
        """Calculate factor for feedback loops (0-1)"""
        feedback_loops = self.tier3.get('feedback_loops', [])
        num_services = len(self.tier2.get('services', []))
        
        if num_services > 0:
            factor = min(len(feedback_loops) / (num_services * 0.3), 1.0)
        else:
            factor = 0
        
        print(f"    Feedback loop factor: {factor:.2f} ({len(feedback_loops)} loops)")
        return factor
    
    def _get_mes_level(self, mes):
        """
        Get qualitative level from MES score.
        Strictly aligned with Equation 10 (Page 5)
        """
        if mes <= 3:
            return 'LOW'
        elif mes <= 7:
            return 'MODERATE'
        else:
            return 'CRITICAL'
    
    def _get_interpretation(self, mes):
        """
        Get interpretation text for MES score.
        Strictly aligned with paper terminology.
        """
        if mes <= 3:
            return "LOW ENTANGLEMENT: Well-isolated architecture with minimal technical debt."
        elif mes <= 7:
            return "MODERATE ENTANGLEMENT: Significant architectural debt. Phased isolation recommended."
        else:
            return "CRITICAL ENTANGLEMENT: Severe model-service coupling. Immediate remediation required."
    
    def _identify_risk_factors(self):
        """Identify specific risk factors contributing to MES"""
        risk_factors = []
        
        # Check each component
        for component, value in self.results['components'].items():
            if value > 0.7:
                risk_factors.append({
                    'component': component,
                    'severity': 'HIGH',
                    'value': value,
                    'description': self._get_risk_description(component, value)
                })
            elif value > 0.4:
                risk_factors.append({
                    'component': component,
                    'severity': 'MEDIUM',
                    'value': value,
                    'description': self._get_risk_description(component, value)
                })
        
        self.results['risk_factors'] = sorted(risk_factors, key=lambda x: x['value'], reverse=True)
    
    def _get_risk_description(self, component, value):
        """Get description for risk factor"""
        descriptions = {
            'direct_calls': f"Direct model calls: {value:.0%} of threshold",
            'shared_features': f"Shared features: {value:.0%} of services affected",
            'pipeline_complexity': f"Complex pipelines: {value:.0%} are overly complex",
            'retrain_frequency': f"Frequent retraining: {value:.0%} of threshold",
            'impact_radius': f"Wide impact: changes affect {value:.0%} of services",
            'feedback_loop': f"Feedback loops: {value:.0%} of services involved"
        }
        return descriptions.get(component, f"{component}: {value:.0%}")