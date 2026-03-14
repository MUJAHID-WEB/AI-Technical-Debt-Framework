import os
import json
import uuid
import shutil
import zipfile
import threading
import time
import traceback
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, session, Response
from werkzeug.utils import secure_filename

# Import enhanced modules
from collectors.github_collector import GitHubCollector
from collectors.local_scanner import LocalScanner
from collectors.mlops_collector import MLOpsCollector
from analyzers.tier1_collector import UniversalDataCollector
from analyzers.tier2_analyzer import UniversalSystemAnalyzer
from analyzers.tier3_smell_detector import AISmellDetector
from analyzers.tier4_metrics import ModelEntanglementEngine
from analyzers.tier5_maintainability import MaintainabilityAnalyzer
from analyzers.tier6_validator import ValidationEngine
from utils.report_generator import ReportGenerator
from detectors.language_detector import LanguageDetector

app = Flask(__name__)
app.secret_key = 'ai-debt-framework-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Store analysis jobs with detailed progress
analysis_jobs = {}

@app.route('/')
def index():
    """Home page with upload options"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_project():
    """Handle project uploads with real-time tracking"""
    job_id = str(uuid.uuid4())
    source_type = request.form.get('source_type', 'local')
    
    print(f"📦 New upload: {source_type} - Job ID: {job_id}")
    
    # Initialize job with detailed progress tracking
    analysis_jobs[job_id] = {
        'job_id': job_id,
        'status': 'initializing',
        'progress': 0,
        'current_tier': 0,
        'tier_results': {},
        'message': 'Initializing...',
        'start_time': datetime.now().isoformat(),
        'source_type': source_type,
        'error': None
    }
    
    if source_type == 'github':
        repo_url = request.form.get('github_url')
        branch = request.form.get('branch', 'main')
        
        analysis_jobs[job_id].update({
            'status': 'cloning',
            'progress': 5,
            'message': f'Cloning repository: {repo_url}'
        })
        
        thread = threading.Thread(
            target=process_github_repo,
            args=(job_id, repo_url, branch)
        )
        thread.daemon = True
        thread.start()
        
    elif source_type == 'mlops':
        platform = request.form.get('mlops_platform')
        endpoint = request.form.get('endpoint')
        
        analysis_jobs[job_id].update({
            'status': 'collecting',
            'progress': 5,
            'message': f'Collecting from {platform}...'
        })
        
        thread = threading.Thread(
            target=process_mlops_project,
            args=(job_id, platform, endpoint)
        )
        thread.daemon = True
        thread.start()
        
    else:  # local upload
        if 'project_files' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        files = request.files.getlist('project_files')
        if not files or files[0].filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], job_id)
        os.makedirs(upload_path, exist_ok=True)
        
        analysis_jobs[job_id].update({
            'status': 'uploading',
            'progress': 10,
            'message': 'Uploading files...'
        })
        
        saved_files = []
        for file in files:
            if file and (file.filename.endswith('.zip') or file.filename.endswith('.tar.gz')):
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_path, filename)
                file.save(file_path)
                saved_files.append(file_path)
                print(f"  Saved: {filename}")
        
        if saved_files:
            analysis_jobs[job_id].update({
                'status': 'extracting',
                'progress': 15,
                'message': f'Extracting {len(saved_files)} archive(s)...'
            })
            
            thread = threading.Thread(
                target=process_local_upload,
                args=(job_id, upload_path, saved_files)
            )
            thread.daemon = True
            thread.start()
        else:
            analysis_jobs[job_id].update({
                'status': 'error',
                'message': 'No valid archive files found'
            })
            return jsonify({'error': 'No valid archive files'}), 400
    
    return jsonify({
        'job_id': job_id,
        'status': 'processing',
        'message': 'Upload started'
    })

@app.route('/job-status/<job_id>')
def job_status(job_id):
    """Get real-time job status"""
    if job_id in analysis_jobs:
        return jsonify(analysis_jobs[job_id])
    
    # Check if results exist
    results_path = os.path.join(app.config['RESULTS_FOLDER'], f'{job_id}_results.json')
    if os.path.exists(results_path):
        try:
            with open(results_path, 'r') as f:
                results = json.load(f)
            return jsonify({
                'status': 'complete',
                'progress': 100,
                'results': results,
                'results_url': f'/results/{job_id}'
            })
        except:
            pass
    
    return jsonify({'status': 'not_found'}), 404

@app.route('/results/<job_id>')
def show_results(job_id):
    """Show analysis results"""
    results_path = os.path.join(app.config['RESULTS_FOLDER'], f'{job_id}_results.json')
    
    if os.path.exists(results_path):
        try:
            with open(results_path, 'r') as f:
                results = json.load(f)
            return render_template('analysis.html', 
                                 job_id=job_id, 
                                 results=results)
        except Exception as e:
            return render_template('analysis.html', 
                                 job_id=job_id, 
                                 error=str(e))
    
    # Show progress page if still processing
    if job_id in analysis_jobs:
        return render_template('analysis.html', 
                             job_id=job_id, 
                             processing=True,
                             job_info=analysis_jobs[job_id])
    
    return render_template('analysis.html', 
                         job_id=job_id, 
                         error='Job not found')

@app.route('/download-report/<job_id>')
def download_report(job_id):
    """Download PDF report"""
    report_path = os.path.join(app.config['RESULTS_FOLDER'], f'{job_id}_report.pdf')
    
    if os.path.exists(report_path):
        return send_file(
            report_path,
            as_attachment=True,
            download_name=f'ai_debt_report_{job_id[:8]}.pdf',
            mimetype='application/pdf'
        )
    
    # Generate report if it doesn't exist
    results_path = os.path.join(app.config['RESULTS_FOLDER'], f'{job_id}_results.json')
    if os.path.exists(results_path):
        try:
            with open(results_path, 'r') as f:
                results = json.load(f)
            
            generator = ReportGenerator(results)
            generator.generate_pdf(report_path)
            
            return send_file(
                report_path,
                as_attachment=True,
                download_name=f'ai_debt_report_{job_id[:8]}.pdf',
                mimetype='application/pdf'
            )
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Report not found'}), 404

def process_local_upload(job_id, upload_path, archive_files):
    """Process uploaded archive files"""
    try:
        # Extract all archives
        extracted_path = os.path.join(upload_path, 'extracted')
        os.makedirs(extracted_path, exist_ok=True)
        
        analysis_jobs[job_id].update({
            'status': 'extracting',
            'progress': 20,
            'message': 'Extracting archives...'
        })
        
        for archive in archive_files:
            if archive.endswith('.zip'):
                with zipfile.ZipFile(archive, 'r') as zip_ref:
                    zip_ref.extractall(extracted_path)
            elif archive.endswith('.tar.gz'):
                import tarfile
                with tarfile.open(archive, 'r:gz') as tar_ref:
                    tar_ref.extractall(extracted_path)
        
        # Find the actual project root (might be in a subfolder)
        project_root = find_project_root(extracted_path)
        
        # Run full analysis
        run_complete_analysis(job_id, project_root)
        
    except Exception as e:
        print(f"Error processing upload: {e}")
        traceback.print_exc()
        analysis_jobs[job_id].update({
            'status': 'error',
            'error': str(e),
            'message': f'Error: {str(e)}'
        })

def process_github_repo(job_id, repo_url, branch):
    """Process GitHub repository"""
    try:
        analysis_jobs[job_id].update({
            'status': 'cloning',
            'progress': 10,
            'message': f'Cloning {repo_url}...'
        })
        
        clone_path = os.path.join(app.config['UPLOAD_FOLDER'], job_id, 'repo')
        os.makedirs(clone_path, exist_ok=True)
        
        collector = GitHubCollector()
        result = collector.clone_repository(repo_url, clone_path, branch)
        
        if result.get('success'):
            analysis_jobs[job_id].update({
                'status': 'analyzing',
                'progress': 20,
                'message': 'Repository cloned, starting analysis...'
            })
            
            run_complete_analysis(job_id, clone_path)
        else:
            analysis_jobs[job_id].update({
                'status': 'error',
                'error': result.get('error'),
                'message': f'Clone failed: {result.get("error")}'
            })
            
    except Exception as e:
        print(f"GitHub processing error: {e}")
        traceback.print_exc()
        analysis_jobs[job_id].update({
            'status': 'error',
            'error': str(e),
            'message': f'Error: {str(e)}'
        })

def process_mlops_project(job_id, platform, endpoint):
    """Process MLOps platform project"""
    try:
        analysis_jobs[job_id].update({
            'status': 'collecting',
            'progress': 10,
            'message': f'Collecting from {platform}...'
        })
        
        collector = MLOpsCollector()
        project_path = os.path.join(app.config['UPLOAD_FOLDER'], job_id, 'mlops')
        os.makedirs(project_path, exist_ok=True)
        
        result = collector.collect_from_platform(platform, endpoint, project_path)
        
        if result.get('success'):
            analysis_jobs[job_id].update({
                'status': 'analyzing',
                'progress': 20,
                'message': 'Data collected, starting analysis...'
            })
            
            run_complete_analysis(job_id, project_path)
        else:
            analysis_jobs[job_id].update({
                'status': 'error',
                'error': result.get('error'),
                'message': f'Collection failed: {result.get("error")}'
            })
            
    except Exception as e:
        print(f"MLOps processing error: {e}")
        traceback.print_exc()
        analysis_jobs[job_id].update({
            'status': 'error',
            'error': str(e),
            'message': f'Error: {str(e)}'
        })

def find_project_root(extracted_path):
    """Find the actual project root (handles nested folders)"""
    items = os.listdir(extracted_path)
    
    # If there's only one directory and it's not a known structure, go into it
    if len(items) == 1:
        single_item = os.path.join(extracted_path, items[0])
        if os.path.isdir(single_item) and not items[0].startswith('.'):
            # Check if this directory contains project files
            sub_items = os.listdir(single_item)
            if any(f in sub_items for f in ['src', 'lib', 'package.json', 'requirements.txt', 'pom.xml']):
                return single_item
    
    return extracted_path

def run_complete_analysis(job_id, project_path):
    """Run all 6 tiers of analysis with real-time updates"""
    print(f"\n{'='*60}")
    print(f"Starting analysis for job {job_id}")
    print(f"Project path: {project_path}")
    print(f"{'='*60}\n")
    
    tier_results = {}
    
    try:
        # ===== TIER 1: DATA COLLECTION =====
        analysis_jobs[job_id].update({
            'current_tier': 1,
            'progress': 20,
            'message': 'TIER 1: Collecting project data...',
            'tier_status': {1: 'running'}
        })
        
        print("\n📊 TIER 1: Data Collection")
        print("-" * 40)
        
        collector = UniversalDataCollector(project_path)
        tier1_result = collector.collect_all()
        tier_results['tier1'] = tier1_result
        
        # Display TIER 1 results
        print(f"  ✓ Language: {tier1_result.get('language', 'Unknown')}")
        print(f"  ✓ Project Type: {tier1_result.get('project_type', 'Unknown')}")
        print(f"  ✓ Files Found: {tier1_result.get('file_count', 0)}")
        print(f"  ✓ Services: {len(tier1_result.get('services', []))}")
        print(f"  ✓ Models: {len(tier1_result.get('models', []))}")
        print(f"  ✓ Pipelines: {len(tier1_result.get('pipelines', []))}")
        
        analysis_jobs[job_id].update({
            'tier_status': {1: 'complete'},
            'tier_results': {'tier1': tier1_result}
        })
        
        # ===== TIER 2: SYSTEM ANALYSIS =====
        analysis_jobs[job_id].update({
            'current_tier': 2,
            'progress': 35,
            'message': 'TIER 2: Analyzing system architecture...',
            'tier_status': {1: 'complete', 2: 'running'}
        })
        
        print("\n🔍 TIER 2: System Analysis")
        print("-" * 40)
        
        analyzer = UniversalSystemAnalyzer(project_path, tier1_result)
        tier2_result = analyzer.analyze()
        tier_results['tier2'] = tier2_result
        
        print(f"  ✓ Services Detected: {len(tier2_result.get('services', []))}")
        for svc in tier2_result.get('services', [])[:3]:
            print(f"    - {svc.get('name')}: {svc.get('type', 'Unknown')}")
        print(f"  ✓ API Endpoints: {tier2_result.get('endpoint_count', 0)}")
        print(f"  ✓ Dependencies: {tier2_result.get('dependency_count', 0)}")
        
        analysis_jobs[job_id].update({
            'tier_status': {1: 'complete', 2: 'complete'},
            'tier_results': {**analysis_jobs[job_id].get('tier_results', {}), 'tier2': tier2_result}
        })
        
        # ===== TIER 3: AI SMELL DETECTION =====
        analysis_jobs[job_id].update({
            'current_tier': 3,
            'progress': 50,
            'message': 'TIER 3: Detecting AI architectural smells...',
            'tier_status': {1: 'complete', 2: 'complete', 3: 'running'}
        })
        
        print("\n👃 TIER 3: AI Smell Detection")
        print("-" * 40)
        
        smell_detector = AISmellDetector(project_path, tier1_result, tier2_result)
        tier3_result = smell_detector.detect_all()
        tier_results['tier3'] = tier3_result
        
        print(f"  ✓ Direct Model Calls: {tier3_result.get('direct_model_calls', {}).get('count', 0)}")
        print(f"  ✓ Glue Code Ratio: {tier3_result.get('glue_code_ratio', 0):.1%}")
        print(f"  ✓ Hidden Consumers: {len(tier3_result.get('hidden_consumers', []))}")
        print(f"  ✓ Complex Pipelines: {tier3_result.get('complex_pipelines', 0)}")
        
        analysis_jobs[job_id].update({
            'tier_status': {1: 'complete', 2: 'complete', 3: 'complete'},
            'tier_results': {**analysis_jobs[job_id].get('tier_results', {}), 'tier3': tier3_result}
        })
        
        # ===== TIER 4: METRICS COMPUTATION =====
        analysis_jobs[job_id].update({
            'current_tier': 4,
            'progress': 65,
            'message': 'TIER 4: Computing Model Entanglement Score...',
            'tier_status': {1: 'complete', 2: 'complete', 3: 'complete', 4: 'running'}
        })
        
        print("\n📐 TIER 4: Model Entanglement Score")
        print("-" * 40)
        
        metrics_engine = ModelEntanglementEngine(tier1_result, tier2_result, tier3_result)
        tier4_result = metrics_engine.calculate()
        tier_results['tier4'] = tier4_result
        
        print(f"  ✓ MES Score: {tier4_result.get('mes_score', 0)}/10")
        print(f"  ✓ Level: {tier4_result.get('mes_level', 'Unknown')}")
        print("\n  Components:")
        for comp, val in tier4_result.get('components', {}).items():
            print(f"    - {comp}: {val:.2f}")
        
        analysis_jobs[job_id].update({
            'tier_status': {1: 'complete', 2: 'complete', 3: 'complete', 4: 'complete'},
            'tier_results': {**analysis_jobs[job_id].get('tier_results', {}), 'tier4': tier4_result}
        })
        
        # ===== TIER 5: MAINTAINABILITY =====
        analysis_jobs[job_id].update({
            'current_tier': 5,
            'progress': 80,
            'message': 'TIER 5: Analyzing maintainability...',
            'tier_status': {1: 'complete', 2: 'complete', 3: 'complete', 4: 'complete', 5: 'running'}
        })
        
        print("\n🔧 TIER 5: Maintainability Analysis")
        print("-" * 40)
        
        maintainability = MaintainabilityAnalyzer(project_path, tier1_result, tier2_result)
        tier5_result = maintainability.analyze()
        tier_results['tier5'] = tier5_result
        
        print(f"  ✓ Total Commits: {tier5_result.get('commit_count', 0)}")
        print(f"  ✓ Bug Rate: {tier5_result.get('bug_rate', 0):.1%}")
        print(f"  ✓ Change Impact: {tier5_result.get('avg_impact', 0):.1f} files/change")
        
        analysis_jobs[job_id].update({
            'tier_status': {1: 'complete', 2: 'complete', 3: 'complete', 4: 'complete', 5: 'complete'},
            'tier_results': {**analysis_jobs[job_id].get('tier_results', {}), 'tier5': tier5_result}
        })
        
        # ===== TIER 6: VALIDATION =====
        analysis_jobs[job_id].update({
            'current_tier': 6,
            'progress': 90,
            'message': 'TIER 6: Validating hypotheses...',
            'tier_status': {1: 'complete', 2: 'complete', 3: 'complete', 4: 'complete', 5: 'complete', 6: 'running'}
        })
        
        print("\n✅ TIER 6: Validation")
        print("-" * 40)
        
        validator = ValidationEngine(tier_results)
        tier6_result = validator.validate()
        tier_results['tier6'] = tier6_result
        
        print(f"  ✓ Hypothesis: {tier6_result.get('hypothesis_confirmed', False)}")
        print(f"  ✓ Degradation Ratio: {tier6_result.get('degradation_ratio', 0):.2f}")
        print(f"  ✓ Correlation: {tier6_result.get('correlation', 0):.2f}")
        
        # ===== GENERATE RECOMMENDATIONS =====
        print("\n💡 Generating Recommendations")
        print("-" * 40)
        
        recommendations = generate_recommendations(tier_results)
        tier_results['recommendations'] = recommendations
        
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. [{rec.get('priority')}] {rec.get('title')}")
        
        # Save results
        results_path = os.path.join(app.config['RESULTS_FOLDER'], f'{job_id}_results.json')
        with open(results_path, 'w') as f:
            json.dump(tier_results, f, indent=2, default=str)
        
        # Generate PDF report
        analysis_jobs[job_id].update({
            'progress': 95,
            'message': 'Generating final report...'
        })
        
        report_path = os.path.join(app.config['RESULTS_FOLDER'], f'{job_id}_report.pdf')
        generator = ReportGenerator(tier_results)
        generator.generate_pdf(report_path)
        
        # Mark as complete
        analysis_jobs[job_id].update({
            'status': 'complete',
            'progress': 100,
            'message': 'Analysis complete!',
            'tier_status': {i: 'complete' for i in range(1, 7)},
            'results': tier_results,
            'results_url': f'/results/{job_id}',
            'report_url': f'/download-report/{job_id}',
            'mes_score': tier4_result.get('mes_score', 0)
        })
        
        print(f"\n{'='*60}")
        print(f"✅ Analysis complete for job {job_id}")
        print(f"   Results saved to: {results_path}")
        print(f"   Report saved to: {report_path}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Error in analysis: {e}")
        traceback.print_exc()
        analysis_jobs[job_id].update({
            'status': 'error',
            'error': str(e),
            'message': f'Error: {str(e)}'
        })

def generate_recommendations(tier_results):
    """Generate actionable recommendations"""
    recommendations = []
    
    tier3 = tier_results.get('tier3', {})
    tier4 = tier_results.get('tier4', {})
    
    # Direct model calls
    direct_calls = tier3.get('direct_model_calls', {})
    if direct_calls.get('count', 0) > 0:
        recommendations.append({
            'priority': 'HIGH' if direct_calls.get('count', 0) > 2 else 'MEDIUM',
            'title': 'Direct Model Calls Detected',
            'description': f"{direct_calls.get('count', 0)} services directly load or call ML models. Implement an AI service isolation layer.",
            'effort': 'Medium',
            'impact': 'High',
            'category': 'Architecture'
        })
    
    # Glue code
    glue_ratio = tier3.get('glue_code_ratio', 0)
    if glue_ratio > 0.2:
        recommendations.append({
            'priority': 'HIGH' if glue_ratio > 0.3 else 'MEDIUM',
            'title': 'Excessive Glue Code',
            'description': f"Glue code represents {glue_ratio:.1%} of codebase. Standardize data transformation interfaces.",
            'effort': 'Medium',
            'impact': 'Medium',
            'category': 'Code Quality'
        })
    
    # Hidden consumers
    hidden = tier3.get('hidden_consumers', [])
    if hidden:
        recommendations.append({
            'priority': 'HIGH',
            'title': f'{len(hidden)} Hidden Model Consumers',
            'description': 'Undocumented services are consuming model outputs. Document all consumers or implement API contracts.',
            'effort': 'Low',
            'impact': 'High',
            'category': 'Documentation'
        })
    
    # MES-based
    mes = tier4.get('mes_score', 0)
    if mes > 7:
        recommendations.append({
            'priority': 'CRITICAL',
            'title': 'Critical Model Entanglement',
            'description': f'MES score of {mes}/10 indicates severe architectural debt. Consider architectural refactoring with proper isolation layers.',
            'effort': 'High',
            'impact': 'Critical',
            'category': 'Architecture'
        })
    elif mes > 4:
        recommendations.append({
            'priority': 'MEDIUM',
            'title': 'Moderate Model Entanglement',
            'description': f'MES score of {mes}/10 indicates technical debt. Review and improve model isolation.',
            'effort': 'Medium',
            'impact': 'Medium',
            'category': 'Architecture'
        })
    
    # Always add at least one recommendation
    if not recommendations:
        recommendations.append({
            'priority': 'LOW',
            'title': 'Well-Architected System',
            'description': 'No critical issues detected. Continue monitoring and maintaining current practices.',
            'effort': 'Low',
            'impact': 'Low',
            'category': 'General'
        })
    
    return recommendations

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 AI Technical Debt Management Framework")
    print("="*60)
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"📁 Results folder: {app.config['RESULTS_FOLDER']}")
    print(f"🌐 Access the application at: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)