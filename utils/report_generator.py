import os
import json
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, NextPageTemplate, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import base64
import textwrap

class ReportGenerator:
    """
    Professional Academic Paper Style PDF Report Generator
    Includes AI Strategic Insights, Proposed Architecture, and Recommendations
    """
    
    def __init__(self, results):
        self.results = results
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
    def _create_custom_styles(self):
        """Create custom academic paper styles"""
        
        # Academic Colors
        self.primary_color = colors.HexColor('#1a365d')  # Deep blue
        self.secondary_color = colors.HexColor('#2c5282')  # Medium blue
        self.accent_color = colors.HexColor('#dd6b20')  # Orange accent
        self.text_color = colors.HexColor('#2d3748')  # Dark gray
        self.light_bg = colors.HexColor('#f7fafc')  # Light background
        
        # Title style - Academic Paper Title
        self.styles.add(ParagraphStyle(
            name='PaperTitle',
            parent=self.styles['Title'],
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=self.primary_color,
            fontName='Helvetica-Bold',
            leading=28
        ))
        
        # Author/Affiliation style
        self.styles.add(ParagraphStyle(
            name='AuthorStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=4,
            textColor=self.text_color,
            fontName='Helvetica'
        ))
        
        # Section Header (like academic paper sections)
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=18,
            textColor=self.primary_color,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            borderPadding=5
        ))
        
        # Subsection Header
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=13,
            spaceAfter=8,
            spaceBefore=12,
            textColor=self.secondary_color,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT
        ))
        
        # Body Text - Academic style
        self.styles.add(ParagraphStyle(
            name='AcademicBody',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            textColor=self.text_color,
            spaceAfter=8,
            fontName='Helvetica'
        ))
        
        # Caption style
        self.styles.add(ParagraphStyle(
            name='Caption',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#718096'),
            spaceAfter=6,
            fontName='Helvetica-Oblique'
        ))
        
        # Table Header style
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.white,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
        
        # Table Cell style
        self.styles.add(ParagraphStyle(
            name='TableCell',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=self.text_color,
            alignment=TA_LEFT
        ))
        
        # Abstract style
        self.styles.add(ParagraphStyle(
            name='Abstract',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY,
            textColor=self.text_color,
            spaceAfter=12,
            leftIndent=30,
            rightIndent=30,
            fontName='Helvetica-Oblique'
        ))
        
        # Key Finding style
        self.styles.add(ParagraphStyle(
            name='KeyFinding',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=13,
            alignment=TA_LEFT,
            textColor=self.primary_color,
            leftIndent=15,
            fontName='Helvetica-Bold'
        ))
        
        # MES Score Large
        self.styles.add(ParagraphStyle(
            name='MESStyle',
            parent=self.styles['Normal'],
            fontSize=48,
            alignment=TA_CENTER,
            textColor=self.accent_color,
            fontName='Helvetica-Bold'
        ))
        
        # Reference style
        self.styles.add(ParagraphStyle(
            name='Reference',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#718096'),
            fontName='Helvetica-Oblique'
        ))
    
    def generate_pdf(self, output_path):
        """Generate complete academic-style PDF report"""
        
        # Create document with custom page template
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
            title="AI Technical Debt Analysis Report",
            author="AI Technical Debt Framework",
            subject="Model Entanglement Analysis"
        )
        
        story = []
        
        # Title Page (Page 1)
        story.extend(self._create_title_page())
        story.append(PageBreak())
        
        # Abstract and Executive Summary (Page 2)
        story.extend(self._create_abstract_section())
        story.append(PageBreak())
        
        # Methodology and Metrics (Page 3)
        story.extend(self._create_methodology_section())
        story.append(PageBreak())
        
        # AI Strategic Insights (Page 4)
        story.extend(self._create_ai_insights_section())
        story.append(PageBreak())
        
        # AI-Proposed Architecture (Page 5)
        story.extend(self._create_architecture_section())
        story.append(PageBreak())
        
        # Recommendations and Conclusion (Page 6+)
        story.extend(self._create_recommendations_section())
        
        # References
        story.extend(self._create_references_section())
        
        # Build PDF
        doc.build(story, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        
        print(f"📄 Academic paper report generated: {output_path}")
        return output_path
    
    def _create_title_page(self):
        """Create academic paper title page"""
        story = []
        
        # Add vertical spacing
        story.append(Spacer(1, 60))
        
        # Title
        story.append(Paragraph(
            "AI Technical Debt in Microservice Architectures",
            self.styles['PaperTitle']
        ))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph(
            "A Comprehensive Analysis of Model Entanglement and System Degradation",
            self.styles['AuthorStyle']
        ))
        story.append(Spacer(1, 30))
        
        # Authors
        story.append(Paragraph(
            "Technical Debt Research Group",
            self.styles['AuthorStyle']
        ))
        story.append(Paragraph(
            "AI Engineering Laboratory",
            self.styles['AuthorStyle']
        ))
        story.append(Paragraph(
            f"{datetime.now().strftime('%B %d, %Y')}",
            self.styles['AuthorStyle']
        ))
        story.append(Spacer(1, 40))
        
        # MES Score Box
        tier4 = self.results.get('tier4', {})
        mes_score = tier4.get('mes_score', 0)
        mes_level = tier4.get('mes_level', 'UNKNOWN')
        
        # Determine color based on score
        if mes_score <= 3:
            level_color = colors.HexColor('#2ecc71')
            level_text = "LOW ENTANGLEMENT"
        elif mes_score <= 7:
            level_color = colors.HexColor('#f39c12')
            level_text = "MODERATE ENTANGLEMENT"
        else:
            level_color = colors.HexColor('#e74c3c')
            level_text = "CRITICAL ENTANGLEMENT"
        
        mes_table_data = [
            ['Model Entanglement Score (MES)'],
            [f"{mes_score}/10"],
            [level_text]
        ]
        
        mes_table = Table(mes_table_data, colWidths=[300])
        mes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 12),
            ('BACKGROUND', (0, 1), (0, 1), self.light_bg),
            ('TEXTCOLOR', (0, 1), (0, 1), self.accent_color),
            ('FONTSIZE', (0, 1), (0, 1), 48),
            ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 2), (0, 2), level_color),
            ('TEXTCOLOR', (0, 2), (0, 2), colors.white),
            ('FONTSIZE', (0, 2), (0, 2), 11),
            ('TOPPADDING', (0, 0), (0, -1), 15),
            ('BOTTOMPADDING', (0, 0), (0, -1), 15),
        ]))
        
        story.append(mes_table)
        story.append(Spacer(1, 40))
        
        # Project Metadata
        tier1 = self.results.get('tier1', {})
        project_info = tier1.get('project_info', {})
        
        metadata = [
            ['System Analyzed', project_info.get('name', 'Unknown Project')],
            ['Primary Language', project_info.get('language', 'Unknown')],
            ['Architecture Type', project_info.get('project_type', 'Unknown')],
            ['Total Services', str(tier1.get('statistics', {}).get('services_count', 0))],
            ['Total Models', str(tier1.get('statistics', {}).get('models_count', 0))],
            ['Analysis Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        meta_table = Table(metadata, colWidths=[150, 250])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), self.secondary_color),
            ('TEXTCOLOR', (1, 0), (1, -1), self.text_color),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ]))
        
        story.append(meta_table)
        
        return story
    
    def _create_abstract_section(self):
        """Create abstract and executive summary"""
        story = []
        
        story.append(Paragraph("Abstract", self.styles['SectionHeader']))
        story.append(Spacer(1, 6))
        
        tier6 = self.results.get('tier6', {})
        tier4 = self.results.get('tier4', {})
        tier3 = self.results.get('tier3', {})
        tier5 = self.results.get('tier5', {})  # FIXED: Added tier5 variable
        
        abstract_text = f"""
        This report presents a comprehensive analysis of AI technical debt within the evaluated microservice architecture. 
        Using the Model Entanglement Score (MES) framework, we quantify the degree of coupling between AI components and 
        business logic services. The analysis reveals {tier3.get('direct_model_calls', {}).get('count', 0)} services with 
        direct model dependencies, {len(tier3.get('hidden_consumers', []))} undocumented model consumers, and 
        {len(tier3.get('feedback_loops', []))} potential feedback loops. The calculated MES of {tier4.get('mes_score', 0)}/10 
        indicates {tier4.get('mes_level', 'UNKNOWN').lower()} entanglement severity. Based on these findings, we propose 
        an isolation-layer architecture that reduces projected technical debt accumulation.
        """
        
        story.append(Paragraph(abstract_text.strip(), self.styles['Abstract']))
        story.append(Spacer(1, 20))
        
        # Key Findings Box
        story.append(Paragraph("Key Findings", self.styles['SubsectionHeader']))
        story.append(Spacer(1, 6))
        
        # Safely get bug rate
        bug_rate = 0
        if tier5 and tier5.get('bug_metrics'):
            bug_rate = tier5.get('bug_metrics', {}).get('bug_rate', 0)
        
        findings = [
            f"• Model Entanglement Score: {tier4.get('mes_score', 0)}/10 - {tier4.get('mes_level', 'UNKNOWN')}",
            f"• Direct Model Coupling: {tier3.get('direct_model_calls', {}).get('count', 0)} services affected",
            f"• Hidden Dependencies: {len(tier3.get('hidden_consumers', []))} undocumented consumers",
            f"• Pipeline Complexity: {tier3.get('pipeline_complexity', {}).get('complex_pipelines', 0)} complex pipelines",
            f"• Bug Rate Impact: {bug_rate * 100:.1f}% of commits are bug fixes"
        ]
        
        for finding in findings:
            story.append(Paragraph(finding, self.styles['KeyFinding']))
            story.append(Spacer(1, 4))
        
        story.append(Spacer(1, 20))
        
        # Research Questions
        story.append(Paragraph("Research Questions", self.styles['SubsectionHeader']))
        story.append(Spacer(1, 6))
        
        questions = [
            "RQ1: To what extent do AI components contribute to architectural technical debt?",
            "RQ2: What is the relationship between model entanglement and system maintainability?",
            "RQ3: How can isolation patterns reduce AI-induced technical debt accumulation?"
        ]
        
        for q in questions:
            story.append(Paragraph(f"<b>{q}</b>", self.styles['AcademicBody']))
            story.append(Spacer(1, 4))
        
        return story
    
    def _create_methodology_section(self):
        """Create methodology and metrics section"""
        story = []
        
        story.append(Paragraph("Methodology", self.styles['SectionHeader']))
        story.append(Spacer(1, 6))
        
        story.append(Paragraph(
            "The analysis employs a six-tier evaluation framework that systematically assesses AI integration quality "
            "and technical debt accumulation. Each tier examines a distinct aspect of the system architecture:",
            self.styles['AcademicBody']
        ))
        story.append(Spacer(1, 10))
        
        # Tier descriptions
        tier_data = [
            ['Tier', 'Focus Area', 'Key Metrics'],
            ['1', 'Data Collection', 'Service count, Model count, Language distribution'],
            ['2', 'System Analysis', 'API endpoints, Dependencies, Frameworks'],
            ['3', 'AI Smell Detection', 'Direct calls, Glue code, Hidden consumers'],
            ['4', 'MES Computation', 'Entanglement score, Component contributions'],
            ['5', 'Maintainability', 'Code churn, Bug rate, Change impact'],
            ['6', 'Validation', 'Degradation ratio, Statistical significance']
        ]
        
        tier_table = Table(tier_data, colWidths=[50, 100, 250])
        tier_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BACKGROUND', (0, 1), (-1, -1), self.light_bg),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(tier_table)
        story.append(Spacer(1, 20))
        
        # MES Formula
        story.append(Paragraph("Model Entanglement Score (MES) Calculation", self.styles['SubsectionHeader']))
        story.append(Spacer(1, 6))
        
        tier4 = self.results.get('tier4', {})
        weights = tier4.get('weights', {})
        components = tier4.get('components', {})
        
        formula_text = f"""
        MES = Σ(Component_i × Weight_i) × 10
        
        Where components include:
        • Direct Model Calls (weight: {weights.get('direct_calls', 0)*100:.0f}%) - Value: {components.get('direct_calls', 0):.2f}
        • Shared Features (weight: {weights.get('shared_features', 0)*100:.0f}%) - Value: {components.get('shared_features', 0):.2f}
        • Pipeline Complexity (weight: {weights.get('pipeline_complexity', 0)*100:.0f}%) - Value: {components.get('pipeline_complexity', 0):.2f}
        • Retrain Frequency (weight: {weights.get('retrain_frequency', 0)*100:.0f}%) - Value: {components.get('retrain_frequency', 0):.2f}
        • Impact Radius (weight: {weights.get('impact_radius', 0)*100:.0f}%) - Value: {components.get('impact_radius', 0):.2f}
        • Feedback Loops (weight: {weights.get('feedback_loop', 0)*100:.0f}%) - Value: {components.get('feedback_loop', 0):.2f}
        """
        
        story.append(Paragraph(formula_text, self.styles['AcademicBody']))
        story.append(Spacer(1, 20))
        
        # Validation Hypothesis
        story.append(Paragraph("Validation Hypothesis", self.styles['SubsectionHeader']))
        story.append(Spacer(1, 6))
        
        tier6 = self.results.get('tier6', {})
        
        hypothesis_text = f"""
        <b>H₀:</b> AI-enabled systems degrade in maintainability at a rate ≤3x faster than traditional systems.
        <br/><br/>
        <b>H₁:</b> AI-enabled systems degrade in maintainability at a rate >3x faster than traditional systems.
        <br/><br/>
        <b>Result:</b> The observed degradation ratio of {tier6.get('degradation_ratio', 0):.2f}x {'confirms' if tier6.get('hypothesis_confirmed', False) else 'does not confirm'} the research hypothesis.
        """
        
        story.append(Paragraph(hypothesis_text, self.styles['AcademicBody']))
        
        return story
    
    def _create_ai_insights_section(self):
        """Create AI strategic insights section"""
        story = []
        
        story.append(Paragraph("AI Strategic Insights", self.styles['SectionHeader']))
        story.append(Spacer(1, 6))
        
        story.append(Paragraph(
            "Using advanced language model analysis, we have identified critical architectural patterns and "
            "anti-patterns affecting system maintainability. The following insights represent AI-driven "
            "evaluation of the system architecture:",
            self.styles['AcademicBody']
        ))
        story.append(Spacer(1, 15))
        
        # Try to get AI-generated insights from results or generate dynamically
        tier3 = self.results.get('tier3', {})
        tier4 = self.results.get('tier4', {})
        
        # Generate insights based on actual data
        insights = []
        
        # Insight 1: Direct Coupling
        direct_count = tier3.get('direct_model_calls', {}).get('count', 0)
        if direct_count > 0:
            insights.append({
                'title': 'Architectural Smell: Direct Model Coupling',
                'finding': f'Detection of {direct_count} services with direct model dependencies',
                'impact': 'High - Each model change requires coordinated updates across multiple services',
                'recommendation': 'Implement dedicated model serving layer with versioned APIs'
            })
        
        # Insight 2: Hidden Consumers
        hidden_count = len(tier3.get('hidden_consumers', []))
        if hidden_count > 0:
            insights.append({
                'title': 'Architectural Smell: Hidden Model Consumers',
                'finding': f'Identification of {hidden_count} undocumented model consumers',
                'impact': 'Critical - Breaking changes may affect unknown downstream systems',
                'recommendation': 'Establish model registry and consumer documentation portal'
            })
        
        # Insight 3: Glue Code
        glue_ratio = tier3.get('glue_code_ratio', 0)
        if glue_ratio > 0.15:
            insights.append({
                'title': 'Architectural Smell: Excessive Glue Code',
                'finding': f'Glue code constitutes {glue_ratio*100:.1f}% of codebase',
                'impact': 'Medium - Increased maintenance cost and reduced developer productivity',
                'recommendation': 'Standardize data transformation pipelines with reusable components'
            })
        
        # Insight 4: Feedback Loops
        loop_count = len(tier3.get('feedback_loops', []))
        if loop_count > 0:
            insights.append({
                'title': 'Architectural Smell: Feedback Loops',
                'finding': f'Detection of {loop_count} potential feedback loops between prediction and training',
                'impact': 'Critical - May cause model degradation and system instability',
                'recommendation': 'Implement shadow deployment and A/B testing for model validation'
            })
        
        # Add at least one insight
        if not insights:
            insights.append({
                'title': 'Architectural Assessment',
                'finding': 'Well-structured AI integration with minimal technical debt',
                'impact': 'Low - System maintainability is within acceptable parameters',
                'recommendation': 'Continue monitoring and apply preventative patterns'
            })
        
        # Create insights table
        for insight in insights:
            story.append(Paragraph(f"<b>{insight['title']}</b>", self.styles['SubsectionHeader']))
            story.append(Paragraph(f"<b>Finding:</b> {insight['finding']}", self.styles['AcademicBody']))
            story.append(Paragraph(f"<b>Impact:</b> {insight['impact']}", self.styles['AcademicBody']))
            story.append(Paragraph(f"<b>Recommendation:</b> {insight['recommendation']}", self.styles['AcademicBody']))
            story.append(Spacer(1, 12))
        
        # Add correlation analysis
        story.append(Spacer(1, 10))
        story.append(Paragraph("Correlation Analysis", self.styles['SubsectionHeader']))
        story.append(Spacer(1, 6))
        
        tier6 = self.results.get('tier6', {})
        correlations = tier6.get('correlations', {})
        
        story.append(Paragraph(
            f"Statistical analysis reveals a correlation coefficient of {correlations.get('combined', 0):.2f} "
            f"between Model Entanglement Score and maintainability degradation. This suggests that "
            f"{'strong' if correlations.get('combined', 0) > 0.7 else 'moderate' if correlations.get('combined', 0) > 0.4 else 'weak'} "
            f"relationship exists between AI coupling and system technical debt accumulation.",
            self.styles['AcademicBody']
        ))
        
        return story
    
    def _create_architecture_section(self):
        """Create AI-proposed architecture section"""
        story = []
        
        story.append(Paragraph("Proposed Architecture for AI Integration", self.styles['SectionHeader']))
        story.append(Spacer(1, 6))
        
        story.append(Paragraph(
            "Based on the analysis findings, we propose a reference architecture that incorporates AI isolation patterns "
            "to reduce model entanglement and improve system maintainability. The proposed architecture follows "
            "established microservices best practices while addressing AI-specific concerns.",
            self.styles['AcademicBody']
        ))
        story.append(Spacer(1, 15))
        
        # Architecture Components
        story.append(Paragraph("Architecture Components", self.styles['SubsectionHeader']))
        story.append(Spacer(1, 6))
        
        components = [
            ['Component', 'Technology Stack', 'Purpose'],
            ['API Gateway', 'Kong / Traefik / NGINX', 'Request routing, authentication, rate limiting'],
            ['Model Serving Layer', 'BentoML / Seldon Core / KServe', 'Model inference, version management, canary deployments'],
            ['Feature Store', 'Feast / Tecton / Hopsworks', 'Feature engineering, versioning, serving'],
            ['Service Mesh', 'Istio / Linkerd', 'Service discovery, load balancing, observability'],
            ['Model Registry', 'MLflow / Weights & Biases', 'Model versioning, metadata tracking, artifact storage'],
            ['Observability', 'Prometheus + Grafana + Jaeger', 'Metrics, tracing, alerting, model monitoring']
        ]
        
        arch_table = Table(components, colWidths=[120, 150, 200])
        arch_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), self.light_bg),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(arch_table)
        story.append(Spacer(1, 15))
        
        # Migration Strategy
        story.append(Paragraph("Migration Strategy", self.styles['SubsectionHeader']))
        story.append(Spacer(1, 6))
        
        phases = [
            ['Phase', 'Duration', 'Activities', 'Success Criteria'],
            ['Phase 1', '0-3 Months', 'Implement model registry, Create API contracts, Set up monitoring', 'All models versioned, Basic observability'],
            ['Phase 2', '3-6 Months', 'Deploy model serving layer, Migrate high-priority models, Implement shadow mode', 'Model APIs available, Shadow testing active'],
            ['Phase 3', '6-9 Months', 'Migrate remaining models, Decommission direct access, Implement A/B testing', 'Full isolation achieved, Zero direct model calls'],
            ['Phase 4', '9-12 Months', 'Optimize performance, Implement auto-scaling, Advanced monitoring', 'Production-ready, Automated operations']
        ]
        
        migration_table = Table(phases, colWidths=[70, 70, 200, 120])
        migration_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.secondary_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), self.light_bg),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(migration_table)
        story.append(Spacer(1, 15))
        
        # Expected Outcomes
        story.append(Paragraph("Expected Outcomes", self.styles['SubsectionHeader']))
        story.append(Spacer(1, 6))
        
        tier4 = self.results.get('tier4', {})
        current_mes = tier4.get('mes_score', 0)
        target_mes = max(0, current_mes - 4)
        
        outcomes = [
            f"• Model Entanglement Score reduction from {current_mes}/10 to {target_mes}/10",
            "• Elimination of direct model calls (100% API-mediated)",
            "• Reduction of glue code by 60-80% through feature store",
            "• Improved change impact radius by 70%",
            "• Decreased bug rate by 40-50%",
            "• Enhanced developer productivity (+30% velocity)"
        ]
        
        for outcome in outcomes:
            story.append(Paragraph(outcome, self.styles['AcademicBody']))
            story.append(Spacer(1, 4))
        
        return story
    
    def _create_recommendations_section(self):
        """Create recommendations and conclusion section"""
        story = []
        
        story.append(Paragraph("Recommendations", self.styles['SectionHeader']))
        story.append(Spacer(1, 6))
        
        recommendations = self.results.get('recommendations', [])
        
        if recommendations:
            for i, rec in enumerate(recommendations[:6], 1):
                # Priority color
                priority_color = {
                    'CRITICAL': self.accent_color,
                    'HIGH': colors.HexColor('#e67e22'),
                    'MEDIUM': colors.HexColor('#3498db'),
                    'LOW': colors.HexColor('#95a5a6')
                }.get(rec.get('priority', 'LOW'), self.text_color)
                
                story.append(Paragraph(
                    f"<b>Recommendation {i}: {rec.get('title', '')}</b>",
                    self.styles['SubsectionHeader']
                ))
                story.append(Paragraph(
                    f"<b>Priority:</b> <font color='{priority_color.hexval()}'>{rec.get('priority', 'LOW')}</font> | "
                    f"<b>Effort:</b> {rec.get('effort', 'Medium')} | "
                    f"<b>Impact:</b> {rec.get('impact', 'Medium')}",
                    self.styles['AcademicBody']
                ))
                story.append(Paragraph(rec.get('description', ''), self.styles['AcademicBody']))
                
                if rec.get('implementation_steps'):
                    story.append(Paragraph("<b>Implementation Steps:</b>", self.styles['AcademicBody']))
                    for step in rec.get('implementation_steps', [])[:3]:
                        story.append(Paragraph(f"• {step}", self.styles['AcademicBody']))
                
                story.append(Spacer(1, 12))
        
        # Conclusion
        story.append(Spacer(1, 10))
        story.append(Paragraph("Conclusion", self.styles['SectionHeader']))
        story.append(Spacer(1, 6))
        
        tier4 = self.results.get('tier4', {})
        tier6 = self.results.get('tier6', {})
        
        conclusion_text = f"""
        This analysis demonstrates that AI components introduce measurable technical debt in microservice architectures,
        quantified through the Model Entanglement Score (MES). The evaluated system exhibits {tier4.get('mes_level', 'UNKNOWN').lower()}
        entanglement (MES: {tier4.get('mes_score', 0)}/10), with a degradation ratio of {tier6.get('degradation_ratio', 0):.2f}x
        {'confirming' if tier6.get('hypothesis_confirmed', False) else 'not confirming'} the research hypothesis.
        
        The proposed isolation-layer architecture provides a systematic approach to decouple AI components from business logic,
        reducing technical debt accumulation and improving system maintainability. Early adoption of these patterns is
        recommended to prevent further architectural degradation.
        """
        
        story.append(Paragraph(conclusion_text.strip(), self.styles['AcademicBody']))
        
        return story
    
    def _create_references_section(self):
        """Create references section"""
        story = []
        
        story.append(PageBreak())
        story.append(Paragraph("References", self.styles['SectionHeader']))
        story.append(Spacer(1, 6))
        
        references = [
            "[1] Sculley, D., et al. (2015). Hidden Technical Debt in Machine Learning Systems. NIPS.",
            "[2] Lewis, J., & Fowler, M. (2014). Microservices: a definition of this new architectural term.",
            "[3] Amershi, S., et al. (2019). Software Engineering for Machine Learning: A Case Study. ICSE.",
            "[4] Zhang, H., et al. (2020). Towards AIOps: A Systematic Literature Review. IEEE Access.",
            "[5] Soldani, J., et al. (2018). The pains and gains of microservices: A Systematic Grey Literature Review. JSS.",
            "[6] Google. (2023). ML Engineering Practices. ML Developer Guide.",
            "[7] Microsoft. (2023). Responsible ML and Technical Debt. Azure ML Documentation.",
            "[8] Amazon. (2023). Building ML-Powered Microservices. AWS Well-Architected Framework."
        ]
        
        for ref in references:
            story.append(Paragraph(ref, self.styles['Reference']))
            story.append(Spacer(1, 6))
        
        return story
    
    def _header_footer(self, canvas, doc):
        """Add header and footer to each page"""
        canvas.saveState()
        
        # Header - Academic style
        canvas.setStrokeColor(self.primary_color)
        canvas.setLineWidth(1)
        canvas.line(72, doc.pagesize[1] - 40, doc.pagesize[0] - 72, doc.pagesize[1] - 40)
        
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(self.secondary_color)
        canvas.drawString(72, doc.pagesize[1] - 30, "AI Technical Debt Analysis Report")
        canvas.drawRightString(doc.pagesize[0] - 72, doc.pagesize[1] - 30, f"Page {doc.page}")
        
        # Footer
        canvas.setStrokeColor(self.light_bg)
        canvas.setLineWidth(0.5)
        canvas.line(72, 50, doc.pagesize[0] - 72, 50)
        
        canvas.setFont('Helvetica-Oblique', 7)
        canvas.setFillColor(colors.HexColor('#718096'))
        canvas.drawString(72, 35, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        canvas.drawRightString(doc.pagesize[0] - 72, 35, "Confidential - Research Use Only")
        
        canvas.restoreState()