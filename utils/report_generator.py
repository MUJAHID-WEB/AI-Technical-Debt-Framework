import os
import json
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import matplotlib.pyplot as plt
import io
import base64

class ReportGenerator:
    """
    Professional PDF Report Generator
    """
    
    def __init__(self, results):
        self.results = results
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom styles for the report"""
        # Title style
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                alignment=TA_CENTER,
                spaceAfter=30,
                textColor=colors.HexColor('#0d6efd')
            ))
        
        # Heading style
        if 'CustomHeading' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomHeading',
                parent=self.styles['Heading2'],
                fontSize=18,
                spaceAfter=12,
                textColor=colors.HexColor('#0d6efd')
            ))
        
        # Subheading style
        if 'CustomSubheading' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomSubheading',
                parent=self.styles['Heading3'],
                fontSize=14,
                spaceAfter=6,
                textColor=colors.HexColor('#495057')
            ))
        
        # Body style
        if 'CustomBody' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomBody',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                leading=14
            ))
        
        # Footer style
        if 'CustomFooter' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomFooter',
                parent=self.styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.gray
            ))
    
    def generate_pdf(self, output_path):
        """Generate complete PDF report"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Title Page
        story.extend(self._create_title_page())
        story.append(PageBreak())
        
        # Executive Summary
        story.extend(self._create_executive_summary())
        story.append(PageBreak())
        
        # Tier 1: Data Collection
        story.extend(self._create_tier1_section())
        story.append(PageBreak())
        
        # Tier 2: System Analysis
        story.extend(self._create_tier2_section())
        story.append(PageBreak())
        
        # Tier 3: AI Smells
        story.extend(self._create_tier3_section())
        story.append(PageBreak())
        
        # Tier 4: MES Score
        story.extend(self._create_tier4_section())
        story.append(PageBreak())
        
        # Tier 5: Maintainability
        story.extend(self._create_tier5_section())
        story.append(PageBreak())
        
        # Tier 6: Validation
        story.extend(self._create_tier6_section())
        story.append(PageBreak())
        
        # Recommendations
        story.extend(self._create_recommendations_section())
        
        # Build PDF
        doc.build(story, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        
        print(f"📄 PDF report generated: {output_path}")
        return output_path
    
    def _create_title_page(self):
        """Create title page"""
        story = []
        
        # Title
        story.append(Paragraph("AI Technical Debt Management Framework", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Subtitle
        story.append(Paragraph("Comprehensive Architectural Analysis Report", self.styles['CustomHeading']))
        story.append(Spacer(1, 40))
        
        # MES Score
        mes_score = self.results.get('tier4', {}).get('mes_score', 'N/A')
        mes_level = self.results.get('tier4', {}).get('mes_level', 'UNKNOWN')
        
        # Color based on score
        if isinstance(mes_score, (int, float)):
            if mes_score <= 3:
                color = colors.green
            elif mes_score <= 7:
                color = colors.orange
            else:
                color = colors.red
        else:
            color = colors.blue
        
        score_style = ParagraphStyle(
            'ScoreStyle',
            parent=self.styles['CustomHeading'],
            fontSize=48,
            textColor=color,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph(f"{mes_score}/10", score_style))
        story.append(Paragraph(f"Level: {mes_level}", self.styles['CustomHeading']))
        story.append(Spacer(1, 40))
        
        # Project Info
        tier1 = self.results.get('tier1', {})
        project_info = tier1.get('project_info', {})
        
        info_data = [
            ['Project:', project_info.get('name', 'Unknown')],
            ['Language:', project_info.get('language', 'Unknown')],
            ['Type:', project_info.get('project_type', 'Unknown')],
            ['Files:', str(tier1.get('statistics', {}).get('total_files', 0))],
            ['Services:', str(tier1.get('statistics', {}).get('services_count', 0))],
            ['Models:', str(tier1.get('statistics', {}).get('models_count', 0))]
        ]
        
        info_table = Table(info_data, colWidths=[100, 300])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 30))
        
        # Date
        timestamp = self.results.get('timestamp', datetime.now().isoformat())
        try:
            date_str = datetime.fromisoformat(timestamp).strftime('%B %d, %Y')
        except:
            date_str = datetime.now().strftime('%B %d, %Y')
        
        story.append(Paragraph(f"Generated: {date_str}", self.styles['CustomBody']))
        
        return story
    
    def _create_executive_summary(self):
        """Create executive summary"""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        # Key Findings
        story.append(Paragraph("Key Findings:", self.styles['CustomSubheading']))
        
        findings = []
        
        # MES interpretation
        mes_score = self.results.get('tier4', {}).get('mes_score', 0)
        if mes_score <= 3:
            findings.append("• ✅ Low model entanglement - architecture is well-isolated")
        elif mes_score <= 7:
            findings.append("• ⚠ Medium model entanglement - some architectural debt detected")
        else:
            findings.append("• ❌ CRITICAL: High model entanglement - immediate action required")
        
        # Smells detected
        tier3 = self.results.get('tier3', {})
        direct_calls = tier3.get('direct_model_calls', {}).get('count', 0)
        if direct_calls > 0:
            findings.append(f"• 🔴 {direct_calls} services directly call ML models")
        
        hidden = len(tier3.get('hidden_consumers', []))
        if hidden > 0:
            findings.append(f"• 🕵️ {hidden} hidden model consumers detected")
        
        glue = tier3.get('glue_code_ratio', 0)
        if glue > 0.2:
            findings.append(f"• 🔧 Glue code represents {glue:.1%} of codebase")
        
        # Hypothesis
        tier6 = self.results.get('tier6', {})
        if tier6.get('hypothesis_confirmed', False):
            findings.append("• 📊 Hypothesis CONFIRMED: Isolated systems degrade 3x slower")
        else:
            findings.append("• 📊 Hypothesis partially confirmed")
        
        for finding in findings:
            story.append(Paragraph(finding, self.styles['CustomBody']))
        
        story.append(Spacer(1, 20))
        
        # Top Recommendations
        story.append(Paragraph("Top Recommendations:", self.styles['CustomSubheading']))
        
        recommendations = self.results.get('recommendations', [])[:3]
        for i, rec in enumerate(recommendations, 1):
            priority_color = {
                'CRITICAL': colors.red,
                'HIGH': colors.orange,
                'MEDIUM': colors.blue,
                'LOW': colors.gray
            }.get(rec.get('priority', 'LOW'), colors.black)
            
            rec_text = f"{i}. [{rec.get('priority', 'LOW')}] {rec.get('title', 'No title')}"
            story.append(Paragraph(rec_text, self.styles['CustomBody']))
            story.append(Paragraph(f"   {rec.get('description', '')}", self.styles['CustomBody']))
        
        return story
    
    def _create_tier1_section(self):
        """Create Tier 1 section"""
        story = []
        
        story.append(Paragraph("TIER 1: Data Collection", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        tier1 = self.results.get('tier1', {})
        stats = tier1.get('statistics', {})
        
        # Overview table
        data = [
            ['Metric', 'Value'],
            ['Services Found', str(stats.get('services_count', 0))],
            ['Models Found', str(stats.get('models_count', 0))],
            ['Pipelines Found', str(stats.get('pipelines_count', 0))],
            ['Total Files', str(stats.get('total_files', 0))],
            ['Total Size', stats.get('total_size_mb', 0) > 0 and f"{stats['total_size_mb']} MB" or '0 MB']
        ]
        
        table = Table(data, colWidths=[200, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 12))
        
        # Languages
        languages = tier1.get('languages', {})
        if languages:
            story.append(Paragraph("Languages Detected:", self.styles['CustomSubheading']))
            
            lang_data = [['Language', 'Files']]
            for lang, count in list(languages.items())[:10]:
                lang_data.append([lang, str(count)])
            
            lang_table = Table(lang_data, colWidths=[200, 100])
            lang_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(lang_table)
        
        return story
    
    def _create_tier2_section(self):
        """Create Tier 2 section"""
        story = []
        
        story.append(Paragraph("TIER 2: System Analysis", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        tier2 = self.results.get('tier2', {})
        services = tier2.get('services', [])
        
        story.append(Paragraph(f"Services Detected: {len(services)}", self.styles['CustomSubheading']))
        
        if services:
            service_data = [['Service Name', 'Language', 'Endpoints']]
            for service in services[:10]:
                service_data.append([
                    service.get('name', 'Unknown'),
                    service.get('language', 'Unknown'),
                    str(service.get('endpoint_count', 0))
                ])
            
            service_table = Table(service_data, colWidths=[150, 100, 80])
            service_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(service_table)
            story.append(Spacer(1, 12))
        
        # Frameworks
        frameworks = tier2.get('frameworks', [])
        if frameworks:
            story.append(Paragraph("Frameworks Detected:", self.styles['CustomSubheading']))
            story.append(Paragraph(", ".join(frameworks[:10]), self.styles['CustomBody']))
        
        return story
    
    def _create_tier3_section(self):
        """Create Tier 3 section"""
        story = []
        
        story.append(Paragraph("TIER 3: AI Smell Detection", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        tier3 = self.results.get('tier3', {})
        
        # Smells summary
        smell_data = [
            ['Smell Type', 'Value', 'Severity'],
            ['Direct Model Calls', f"{tier3.get('direct_model_calls', {}).get('count', 0)} services", 
             'HIGH' if tier3.get('direct_model_calls', {}).get('ratio', 0) > 0.3 else 'LOW'],
            ['Glue Code Ratio', f"{tier3.get('glue_code_ratio', 0):.1%}", 
             'HIGH' if tier3.get('glue_code_ratio', 0) > 0.2 else 'LOW'],
            ['Hidden Consumers', str(len(tier3.get('hidden_consumers', []))), 
             'HIGH' if len(tier3.get('hidden_consumers', [])) > 0 else 'LOW'],
            ['Complex Pipelines', str(tier3.get('pipeline_complexity', {}).get('complex_pipelines', 0)), 
             'MEDIUM' if tier3.get('pipeline_complexity', {}).get('complex_pipelines', 0) > 0 else 'LOW'],
            ['Retrain Frequency', f"{tier3.get('retrain_frequency', 0)}/month", 
             'MEDIUM' if tier3.get('retrain_frequency', 0) > 4 else 'LOW']
        ]
        
        smell_table = Table(smell_data, colWidths=[150, 100, 80])
        smell_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ffc107')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(smell_table)
        
        return story
    
    def _create_tier4_section(self):
        """Create Tier 4 section"""
        story = []
        
        story.append(Paragraph("TIER 4: Model Entanglement Score", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        tier4 = self.results.get('tier4', {})
        components = tier4.get('components', {})
        
        # MES Score
        mes_score = tier4.get('mes_score', 0)
        mes_level = tier4.get('mes_level', 'UNKNOWN')
        
        # Color based on score
        if mes_score <= 3:
            color = colors.green
        elif mes_score <= 7:
            color = colors.orange
        else:
            color = colors.red
        
        score_style = ParagraphStyle(
            'ScoreStyle',
            parent=self.styles['CustomHeading'],
            fontSize=36,
            textColor=color,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph(f"{mes_score}/10", score_style))
        story.append(Paragraph(f"Level: {mes_level}", self.styles['CustomSubheading']))
        story.append(Paragraph(tier4.get('interpretation', ''), self.styles['CustomBody']))
        story.append(Spacer(1, 12))
        
        # Components
        story.append(Paragraph("Component Breakdown:", self.styles['CustomSubheading']))
        
        comp_data = [['Component', 'Value', 'Weight', 'Contribution']]
        weights = tier4.get('weights', {})
        contributions = tier4.get('contributions', {})
        
        for comp, value in components.items():
            weight = weights.get(comp, 0)
            contribution = contributions.get(comp, 0) * 10
            
            comp_data.append([
                comp.replace('_', ' ').title(),
                f"{value:.1%}",
                f"{weight:.1%}",
                f"{contribution:.2f}"
            ])
        
        comp_table = Table(comp_data, colWidths=[150, 80, 80, 80])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(comp_table)
        
        return story
    
    def _create_tier5_section(self):
        """Create Tier 5 section"""
        story = []
        
        story.append(Paragraph("TIER 5: Maintainability Analysis", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        tier5 = self.results.get('tier5', {})
        
        # Maintainability Score
        maint_score = tier5.get('maintainability_score', 0)
        
        story.append(Paragraph(f"Maintainability Score: {maint_score}/10", self.styles['CustomSubheading']))
        story.append(Spacer(1, 6))
        
        # Key metrics
        data = [
            ['Metric', 'Value'],
            ['Total Commits', str(tier5.get('commit_count', 0))],
            ['Contributors', str(len(tier5.get('contributors', [])))],
            ['Bug Rate', f"{tier5.get('bug_metrics', {}).get('bug_rate', 0):.1%}"],
            ['Bug Count', str(tier5.get('bug_metrics', {}).get('bug_count', 0))],
            ['Avg Change Impact', f"{tier5.get('impact_metrics', {}).get('avg_impact', 0):.1f} files"]
        ]
        
        metrics_table = Table(data, colWidths=[150, 150])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c757d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(metrics_table)
        
        return story
    
    def _create_tier6_section(self):
        """Create Tier 6 section"""
        story = []
        
        story.append(Paragraph("TIER 6: Validation & Results", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        tier6 = self.results.get('tier6', {})
        
        # Hypothesis
        hypothesis_confirmed = tier6.get('hypothesis_confirmed', False)
        
        hypo_style = ParagraphStyle(
            'HypoStyle',
            parent=self.styles['CustomSubheading'],
            textColor=colors.green if hypothesis_confirmed else colors.orange
        )
        
        story.append(Paragraph(
            f"Hypothesis: {'CONFIRMED' if hypothesis_confirmed else 'NOT CONFIRMED'}",
            hypo_style
        ))
        story.append(Spacer(1, 6))
        
        # Degradation ratio
        story.append(Paragraph(
            f"Degradation Ratio: {tier6.get('degradation_ratio', 0):.2f}x",
            self.styles['CustomBody']
        ))
        story.append(Paragraph(
            f"Isolated Systems MES: {tier6.get('avg_isolated_mes', 0):.1f}",
            self.styles['CustomBody']
        ))
        story.append(Paragraph(
            f"Non-Isolated Systems MES: {tier6.get('avg_non_isolated_mes', 0):.1f}",
            self.styles['CustomBody']
        ))
        story.append(Spacer(1, 12))
        
        # Correlations
        correlations = tier6.get('correlations', {})
        
        corr_data = [
            ['Correlation', 'Value'],
            ['MES vs Churn', str(correlations.get('mes_churn', 0))],
            ['MES vs Bugs', str(correlations.get('mes_bug', 0))],
            ['MES vs Impact', str(correlations.get('mes_impact', 0))],
            ['Combined', str(correlations.get('combined', 0))]
        ]
        
        corr_table = Table(corr_data, colWidths=[150, 100])
        corr_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(corr_table)
        
        return story
    
    def _create_recommendations_section(self):
        """Create recommendations section"""
        story = []
        
        story.append(Paragraph("Recommendations", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        recommendations = self.results.get('recommendations', [])
        
        for i, rec in enumerate(recommendations, 1):
            # Color based on priority
            priority = rec.get('priority', 'LOW')
            if priority == 'CRITICAL':
                color = colors.red
            elif priority == 'HIGH':
                color = colors.orange
            elif priority == 'MEDIUM':
                color = colors.blue
            else:
                color = colors.gray
            
            rec_style = ParagraphStyle(
                f'Rec{i}Style',
                parent=self.styles['CustomSubheading'],
                textColor=color
            )
            
            story.append(Paragraph(f"{i}. [{priority}] {rec.get('title', '')}", rec_style))
            story.append(Paragraph(rec.get('description', ''), self.styles['CustomBody']))
            story.append(Paragraph(
                f"Effort: {rec.get('effort', 'Unknown')} | Impact: {rec.get('impact', 'Unknown')}",
                self.styles['CustomBody']
            ))
            story.append(Spacer(1, 6))
        
        return story
    
    def _header_footer(self, canvas, doc):
        """Add header and footer to each page"""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica', 8)
        canvas.drawString(72, doc.height + 72 + 20, "AI Technical Debt Management Framework")
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.drawString(72, 72 - 20, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        canvas.drawRightString(doc.width + 72, 72 - 20, f"Page {doc.page}")
        
        canvas.restoreState()