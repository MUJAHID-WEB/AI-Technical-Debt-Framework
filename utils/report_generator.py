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
        # Enterprise Colors (Professional Slate & Cyan Palette)
        self.primary_blue = colors.HexColor('#0062ff')
        self.secondary_blue = colors.HexColor('#00f3ff')
        self.slate_900 = colors.HexColor('#0f172a')
        self.slate_700 = colors.HexColor('#334155')
        self.slate_500 = colors.HexColor('#64748b')
        self.slate_100 = colors.HexColor('#f1f5f9')
        self.border_color = colors.HexColor('#e2e8f0')

        # Title style
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=28,
                alignment=TA_CENTER,
                spaceAfter=30,
                textColor=self.slate_900,
                fontName='Helvetica-Bold'
            ))
        
        # Heading style
        if 'CustomHeading' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomHeading',
                parent=self.styles['Heading2'],
                fontSize=18,
                spaceAfter=14,
                textColor=self.primary_blue,
                fontName='Helvetica-Bold'
            ))
        
        # Subheading style
        if 'CustomSubheading' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomSubheading',
                parent=self.styles['Heading3'],
                fontSize=12,
                spaceAfter=8,
                textColor=self.slate_700,
                fontName='Helvetica-Bold',
                textTransform='uppercase'
            ))
        
        # Body style
        if 'CustomBody' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomBody',
                parent=self.styles['Normal'],
                fontSize=10,
                spaceAfter=10,
                leading=16,
                textColor=self.slate_700
            ))
        
        # Table styles
        self.main_table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.slate_900),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [self.slate_100, colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, self.border_color),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ])
    
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
        story.append(Spacer(1, 100))
        
        # Logo/Icon Placeholder (styled box)
        logo_data = [['   AI TECHNICAL DEBT FRAMEWORK   ']]
        logo_table = Table(logo_data, colWidths=[400])
        logo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.primary_blue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('ROUNDEDCORNERS', [10, 10, 10, 10])
        ]))
        story.append(logo_table)
        story.append(Spacer(1, 50))
        
        # Title
        story.append(Paragraph("System Architectural Audit Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 10))
        
        # Subtitle
        story.append(Paragraph("Comprehensive Analysis of Model Entanglement and Technical Debt", self.styles['CustomSubheading']))
        story.append(Spacer(1, 60))
        
        # MES Score Visual
        mes_score = self.results.get('tier4', {}).get('mes_score', 'N/A')
        mes_level = self.results.get('tier4', {}).get('mes_level', 'UNKNOWN')
        
        # Color based on score
        if isinstance(mes_score, (int, float)):
            if mes_score <= 3: color = colors.HexColor('#10b981') # Emerald
            elif mes_score <= 7: color = colors.HexColor('#f59e0b') # Amber
            else: color = colors.HexColor('#ef4444') # Red
        else: color = self.primary_blue
        
        score_box_data = [
            [Paragraph("MODEL ENTANGLEMENT SCORE", ParagraphStyle('ScoreLabel', fontSize=10, textColor=self.slate_500, alignment=TA_CENTER))],
            [Paragraph(f"{mes_score}/10", ParagraphStyle('ScoreVal', fontSize=56, textColor=color, fontName='Helvetica-Bold', alignment=TA_CENTER))],
            [Paragraph(f"Classification: {mes_level}", ParagraphStyle('ScoreLevel', fontSize=14, textColor=self.slate_700, fontName='Helvetica-Bold', alignment=TA_CENTER))]
        ]
        score_table = Table(score_box_data, colWidths=[300])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.slate_100),
            ('BOX', (0, 0), (-1, -1), 1, self.border_color),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('REGPADDING', (0, 0), (-1, -1), 20),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 80))
        
        # Meta Info
        tier1 = self.results.get('tier1', {})
        project_info = tier1.get('project_info', {})
        timestamp = self.results.get('timestamp', datetime.now().isoformat())
        try: date_str = datetime.fromisoformat(timestamp).strftime('%B %d, %Y')
        except: date_str = datetime.now().strftime('%B %d, %Y')

        meta_data = [
            ['PROJECT IDENTIFIER', project_info.get('name', 'Unknown').upper()],
            ['TECHNOLOGY STACK', project_info.get('language', 'Unknown').upper()],
            ['AUDIT TIMESTAMP', date_str.upper()],
            ['REPORT SERIAL', self.results.get('job_id', 'N/A').upper()[:12]]
        ]
        
        meta_table = Table(meta_data, colWidths=[150, 250])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), self.slate_500),
            ('TEXTCOLOR', (1, 0), (1, -1), self.slate_900),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, self.border_color),
        ]))
        story.append(meta_table)
        
        return story
    
    def _create_executive_summary(self):
        """Create executive summary"""
        story = []
        
        story.append(Paragraph("I. EXECUTIVE SUMMARY", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph(
            "This document provides a technical audit of the architectural integrity and model entanglement within the analyzed repository. "
            "The following findings represent a high-level overview of the system's current hygiene and technical debt status.",
            self.styles['CustomBody']
        ))
        story.append(Spacer(1, 10))
        
        # Key Findings
        story.append(Paragraph("CRITICAL ARCHITECTURAL FINDINGS:", self.styles['CustomSubheading']))
        story.append(Spacer(1, 6))
        
        findings = []
        mes_score = self.results.get('tier4', {}).get('mes_score', 0)
        if mes_score <= 3: findings.append("<b>OPTIMAL:</b> Model entanglement is within safe operational parameters.")
        elif mes_score <= 7: findings.append("<b>CAUTION:</b> Moderate model entanglement detected - architectural degradation in progress.")
        else: findings.append("<b>CRITICAL:</b> High model entanglement - system maintainability is severely compromised.")
        
        tier3 = self.results.get('tier3', {})
        direct_count = tier3.get('direct_model_calls', {}).get('count', 0)
        if direct_count > 0: findings.append(f"<b>COUPLING:</b> {direct_count} services exhibit direct model dependency (Anti-pattern).")
        
        glue = tier3.get('glue_code_ratio', 0)
        if glue > 0.2: findings.append(f"<b>COMPLEXITY:</b> Glue code represents {glue:.1%} of analyzed logic assets.")
        
        for finding in findings:
            story.append(Paragraph(f"• {finding}", self.styles['CustomBody']))
        
        story.append(Spacer(1, 20))
        
        # Top Recommendations
        story.append(Paragraph("PRIMARY MITIGATION STRATEGIES:", self.styles['CustomSubheading']))
        story.append(Spacer(1, 6))
        
        recommendations = self.results.get('recommendations', [])[:3]
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"<b>{i}. {rec.get('title', '').upper()}</b>", self.styles['CustomBody']))
            story.append(Paragraph(f"<i>Classification: {rec.get('priority', 'LOW')} Priority</i>", 
                                 ParagraphStyle('ItalBody', parent=self.styles['CustomBody'], fontSize=8)))
        
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
            ['METRIC', 'SPECIFICATION'],
            ['SERVICES DETECTED', str(stats.get('services_count', 0))],
            ['MODELS IDENTIFIED', str(stats.get('models_count', 0))],
            ['PIPELINES MAPPED', str(stats.get('pipelines_count', 0))],
            ['TOTAL FILE COUNT', str(stats.get('total_files', 0))],
            ['TOTAL FOOTPRINT', stats.get('total_size_mb', 0) > 0 and f"{stats['total_size_mb']} MB" or '0 MB']
        ]
        
        table = Table(data, colWidths=[200, 200])
        table.setStyle(self.main_table_style)
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Languages
        languages = tier1.get('languages', {})
        if languages:
            story.append(Paragraph("LANGUAGE DISTRIBUTION OVERVIEW", self.styles['CustomSubheading']))
            story.append(Spacer(1, 8))
            
            lang_data = [['LANGUAGE ASSET', 'FILE QUANTITY']]
            for lang, count in list(languages.items())[:12]:
                lang_data.append([lang.upper(), str(count)])
            
            lang_table = Table(lang_data, colWidths=[200, 200])
            lang_table.setStyle(self.main_table_style)
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
            service_data = [['IDENTIFIED SERVICE', 'PRIMARY STACK', 'ENDPOINT CAPACITY']]
            for service in services[:15]:
                service_data.append([
                    service.get('name', 'Unknown').upper(),
                    service.get('language', 'Unknown').upper(),
                    str(service.get('endpoint_count', 0))
                ])
            
            service_table = Table(service_data, colWidths=[180, 120, 100])
            service_table.setStyle(self.main_table_style)
            story.append(service_table)
            story.append(Spacer(1, 20))
        
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
        smell_data = [['SMELL CLASSIFICATION', 'DETECTED VALUE', 'CRITICALITY']]
        
        direct_count = tier3.get('direct_model_calls', {}).get('count', 0)
        glue_ratio = tier3.get('glue_code_ratio', 0)
        
        smell_data.append(['DIRECT MODEL COUPLING', f"{direct_count} SERVICES", 'CRITICAL' if direct_count > 0 else 'EXEMPT'])
        smell_data.append(['GLUE CODE PROLIFERATION', f"{glue_ratio:.1%}", 'HIGH' if glue_ratio > 0.2 else 'NOMINAL'])
        smell_data.append(['HIDDEN MODEL CONSUMERS', str(len(tier3.get('hidden_consumers', []))), 'HIGH' if len(tier3.get('hidden_consumers', [])) > 0 else 'EXEMPT'])
        
        smell_table = Table(smell_data, colWidths=[180, 120, 100])
        smell_table.setStyle(self.main_table_style)
        
        # Apply conditional coloring to severity column
        for i, row in enumerate(smell_data[1:], 1):
            severity = row[2]
            if severity in ['CRITICAL', 'HIGH']:
                smell_table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#ef4444'))]))
            elif severity == 'NOMINAL':
                smell_table.setStyle(TableStyle([('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#10b981'))]))

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
        story.append(Paragraph("SPECIFIC COMPONENT BREAKDOWN", self.styles['CustomSubheading']))
        story.append(Spacer(1, 8))
        
        comp_data = [['COMPONENT CATEGORY', 'SATURATION', 'WEIGHTING', 'IMPACT']]
        weights = tier4.get('weights', {})
        contributions = tier4.get('contributions', {})
        
        for comp, value in components.items():
            weight = weights.get(comp, 0)
            contribution = contributions.get(comp, 0) * 10
            
            comp_data.append([
                comp.replace('_', ' ').upper(),
                f"{value:.1%}",
                f"{weight:.1%}",
                f"{contribution:.2f}"
            ])
        
        comp_table = Table(comp_data, colWidths=[140, 80, 80, 80])
        comp_table.setStyle(self.main_table_style)
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
            ['OPERATIONAL METRIC', 'QUANTITATIVE VALUE'],
            ['HISTORICAL COMMIT VOLUME', str(tier5.get('commit_count', 0))],
            ['CONTRIBUTOR DENSITY', str(len(tier5.get('contributors', [])))],
            ['ANOMALY/BUG FREQUENCY', f"{tier5.get('bug_metrics', {}).get('bug_rate', 0):.1%}"],
            ['TOTAL DEFECT COUNT', str(tier5.get('bug_metrics', {}).get('bug_count', 0))],
            ['AVERAGE CHANGE RADIUS', f"{tier5.get('impact_metrics', {}).get('avg_impact', 0):.1f} FILES"]
        ]
        
        metrics_table = Table(data, colWidths=[200, 200])
        metrics_table.setStyle(self.main_table_style)
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
            ['CORRELATION INDEX', 'STATISTICAL COEFFICIENT'],
            ['MES SCORE VS CODE CHURN', str(correlations.get('mes_churn', 0))],
            ['MES SCORE VS DEFECT DENSITY', str(correlations.get('mes_bug', 0))],
            ['MES SCORE VS ARCHITECTURAL IMPACT', str(correlations.get('mes_impact', 0))],
            ['AGGREGATED DEBT CORRELATION', str(correlations.get('combined', 0))]
        ]
        
        corr_table = Table(corr_data, colWidths=[220, 180])
        corr_table.setStyle(self.main_table_style)
        story.append(corr_table)
        
        return story
    
    def _create_recommendations_section(self):
        """Create recommendations section"""
        story = []
        
        story.append(Paragraph("Recommendations", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        recommendations = self.results.get('recommendations', [])
        
        for i, rec in enumerate(recommendations, 1):
            priority = rec.get('priority', 'LOW')
            p_color = {'CRITICAL': colors.HexColor('#ef4444'), 
                      'HIGH': colors.HexColor('#f59e0b'), 
                      'MEDIUM': colors.HexColor('#3b82f6'), 
                      'LOW': self.slate_500}.get(priority, self.slate_500)
            
            story.append(Paragraph(f"{i}. {rec.get('title', '').upper()}", 
                                 ParagraphStyle(f'RecTitle{i}', parent=self.styles['CustomSubheading'], textColor=p_color)))
            
            story.append(Paragraph(rec.get('description', ''), self.styles['CustomBody']))
            
            # Recommendation Details Table
            rec_meta = [[
                f"PRIORITY: {priority}",
                f"EFFORT: {rec.get('effort', 'N/A').upper()}",
                f"EST. IMPACT: {rec.get('impact', 'N/A').upper()}"
            ]]
            meta_tab = Table(rec_meta, colWidths=[130, 130, 130])
            meta_tab.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.slate_500),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ]))
            story.append(meta_tab)
            story.append(Spacer(1, 15))
        
        return story
    
    def _header_footer(self, canvas, doc):
        """Add header and footer to each page"""
        canvas.saveState()
        
        # Header - Professional Bar
        canvas.setStrokeColor(self.primary_blue)
        canvas.setLineWidth(2)
        canvas.line(72, doc.pagesize[1] - 50, doc.pagesize[0] - 72, doc.pagesize[1] - 50)
        
        canvas.setFont('Helvetica-Bold', 8)
        canvas.setFillColor(self.slate_500)
        canvas.drawString(72, doc.pagesize[1] - 45, "AI TECHNICAL DEBT ANALYTICS | CONFIDENTIAL")
        
        # Footer
        canvas.setStrokeColor(self.border_color)
        canvas.setLineWidth(0.5)
        canvas.line(72, 50, doc.pagesize[0] - 72, 50)
        
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(self.slate_500)
        canvas.drawString(72, 35, f"Audit Execution: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        canvas.drawRightString(doc.pagesize[0] - 72, 35, f"PAGE {doc.page} OF SECURED REPORT")
        
        canvas.restoreState()