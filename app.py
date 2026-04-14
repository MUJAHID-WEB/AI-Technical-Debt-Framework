import os
import json
import uuid
import shutil
import zipfile
import tarfile
import threading
import time
import traceback
from datetime import datetime
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, send_file
from flask.json.provider import DefaultJSONProvider
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
from utils.ai_analyzer import AIAnalyzer
from utils.ai_architect import AIArchitect

app = Flask(__name__)
app.secret_key = 'ai-debt-framework-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max upload

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

class CustomJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, set):
            return list(o)
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if hasattr(o, '__dict__'):
            return o.__dict__
        try:
            return super().default(o)
        except TypeError:
            return str(o)

app.json = CustomJSONProvider(app)

# Store analysis jobs with detailed progress (use dictionary with thread safety)
analysis_jobs = {}
job_lock = threading.Lock()

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
    with job_lock:
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
        
        with job_lock:
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
        
        with job_lock:
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
        
        with job_lock:
            analysis_jobs[job_id].update({
                'status': 'uploading',
                'progress': 5,
                'message': 'Uploading files...'
            })
        
        saved_files = []
        for file in files:
            if file and (file.filename.endswith('.zip') or file.filename.endswith('.tar.gz') or file.filename.endswith('.tgz')):
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_path, filename)
                file.save(file_path)
                saved_files.append(file_path)
                print(f"  Saved: {filename}")
        
        if saved_files:
            with job_lock:
                analysis_jobs[job_id].update({
                    'status': 'extracting',
                    'progress': 10,
                    'message': f'Extracting {len(saved_files)} archive(s)...'
                })
            
            thread = threading.Thread(
                target=process_local_upload,
                args=(job_id, upload_path, saved_files)
            )
            thread.daemon = True
            thread.start()
        else:
            with job_lock:
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
    with job_lock:
        if job_id not in analysis_jobs:
            return jsonify({'error': 'Job not found'}), 404
        
        job_data = analysis_jobs[job_id].copy()
    
    # Also check if results file exists (in case of completed job after restart)
    results_path = os.path.join(app.config['RESULTS_FOLDER'], f'{job_id}_results.json')
    if os.path.exists(results_path) and job_data.get('status') != 'complete':
        try:
            with open(results_path, 'r') as f:
                results = json.load(f)
            job_data['status'] = 'complete'
            job_data['progress'] = 100
            job_data['results'] = results
            job_data['results_url'] = f'/results/{job_id}'
        except:
            pass
    
    return jsonify(job_data)

@app.route('/api/collectors/github/search', methods=['POST'])
def github_search():
    """Search for GitHub repositories"""
    try:
        data = request.json
        query = data.get('query', '')
        if not query:
            return jsonify({'error': 'Query is required'}), 400
            
        collector = GitHubCollector()
        results = collector.search_repositories(query)
        return jsonify(results)
    except Exception as e:
        print(f"GitHub search error: {e}")
        return jsonify({'error': str(e)}), 500

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
    with job_lock:
        if job_id in analysis_jobs:
            return render_template('analysis.html', 
                                 job_id=job_id, 
                                 processing=True,
                                 job_info=analysis_jobs[job_id])
    
    return render_template('analysis.html', 
                         job_id=job_id, 
                         error='Job not found')

@app.route('/ai-analysis/<job_id>')
def ai_analysis(job_id):
    """Generate AI-powered architectural insights"""
    results_path = os.path.join(app.config['RESULTS_FOLDER'], f'{job_id}_results.json')
    if not os.path.exists(results_path):
        return jsonify({"error": "Results not found"}), 404
        
    try:
        with open(results_path, 'r') as f:
            results = json.load(f)
            
        analyzer = AIAnalyzer()
        ai_result = analyzer.analyze_results(results)
        return jsonify(ai_result)
    except Exception as e:
        print(f"❌ AI Analysis Route Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "type": "route_exception"}), 500

@app.route('/ai-architecture/<job_id>')
def ai_architecture(job_id):
    """Generate AI-proposed improved architecture"""
    results_path = os.path.join(app.config['RESULTS_FOLDER'], f'{job_id}_results.json')
    if not os.path.exists(results_path):
        return jsonify({"error": "Results not found"}), 404
        
    try:
        with open(results_path, 'r') as f:
            results = json.load(f)
            
        architect = AIArchitect()
        arch_result = architect.propose_architecture(results)
        return jsonify(arch_result)
    except Exception as e:
        print(f"❌ AI Architecture Route Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "type": "route_exception"}), 500

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
    
    return jsonify({'error': 'Report not found'}), 500

def process_local_upload(job_id, upload_path, archive_files):
    """Process uploaded archive files"""
    try:
        # Extract all archives
        extracted_path = os.path.join(upload_path, 'extracted')
        os.makedirs(extracted_path, exist_ok=True)
        
        with job_lock:
            analysis_jobs[job_id].update({
                'status': 'extracting',
                'progress': 12,
                'message': 'Extracting archives...'
            })
        
        for archive in archive_files:
            if archive.endswith('.zip'):
                with zipfile.ZipFile(archive, 'r') as zip_ref:
                    zip_ref.extractall(extracted_path)
            elif archive.endswith(('.tar.gz', '.tgz')):
                with tarfile.open(archive, 'r:gz') as tar_ref:
                    tar_ref.extractall(extracted_path)
        
        # Find the actual project root (might be in a subfolder)
        project_root = find_project_root(extracted_path)
        
        # Run full analysis
        run_complete_analysis(job_id, project_root)
        
    except Exception as e:
        print(f"Error processing upload: {e}")
        traceback.print_exc()
        with job_lock:
            analysis_jobs[job_id].update({
                'status': 'error',
                'error': str(e),
                'message': f'Error: {str(e)}'
            })

def process_github_repo(job_id, repo_url, branch):
    """Process GitHub repository"""
    try:
        with job_lock:
            analysis_jobs[job_id].update({
                'status': 'cloning',
                'progress': 5,
                'message': f'Cloning {repo_url}...'
            })
        
        clone_path = os.path.join(app.config['UPLOAD_FOLDER'], job_id, 'repo')
        os.makedirs(clone_path, exist_ok=True)
        
        collector = GitHubCollector()
        result = collector.clone_repository(repo_url, clone_path, branch)
        
        if result.get('success'):
            with job_lock:
                analysis_jobs[job_id].update({
                    'status': 'analyzing',
                    'progress': 15,
                    'message': 'Repository cloned successfully, starting analysis...'
                })
            
            run_complete_analysis(job_id, clone_path)
        else:
            error_msg = result.get('error', 'Unknown clone error')
            with job_lock:
                analysis_jobs[job_id].update({
                    'status': 'error',
                    'error': error_msg,
                    'message': f'Clone failed: {error_msg}'
                })
            print(f"❌ Job {job_id} failed: {error_msg}")
            
    except Exception as e:
        print(f"GitHub processing error: {e}")
        traceback.print_exc()
        with job_lock:
            analysis_jobs[job_id].update({
                'status': 'error',
                'error': str(e),
                'message': f'Error: {str(e)}'
            })

def process_mlops_project(job_id, platform, endpoint):
    """Process MLOps platform project"""
    try:
        with job_lock:
            analysis_jobs[job_id].update({
                'status': 'collecting',
                'progress': 5,
                'message': f'Collecting from {platform}...'
            })
        
        collector = MLOpsCollector()
        project_path = os.path.join(app.config['UPLOAD_FOLDER'], job_id, 'mlops')
        os.makedirs(project_path, exist_ok=True)
        
        result = collector.collect_from_platform(platform, endpoint, project_path)
        
        if result.get('success'):
            with job_lock:
                analysis_jobs[job_id].update({
                    'status': 'analyzing',
                    'progress': 15,
                    'message': 'Data collected, starting analysis...'
                })
            
            run_complete_analysis(job_id, project_path)
        else:
            with job_lock:
                analysis_jobs[job_id].update({
                    'status': 'error',
                    'error': result.get('error'),
                    'message': f'Collection failed: {result.get("error")}'
                })
            
    except Exception as e:
        print(f"MLOps processing error: {e}")
        traceback.print_exc()
        with job_lock:
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

def update_job_progress(job_id, tier, progress, message, tier_results=None):
    """Thread-safe job progress update"""
    with job_lock:
        if job_id in analysis_jobs:
            analysis_jobs[job_id].update({
                'current_tier': tier,
                'progress': progress,
                'message': message,
                'tier_status': {**analysis_jobs[job_id].get('tier_status', {}), tier: 'running'}
            })
            if tier_results:
                current_results = analysis_jobs[job_id].get('tier_results', {})
                current_results.update(tier_results)
                analysis_jobs[job_id]['tier_results'] = current_results

def complete_tier(job_id, tier, tier_data):
    """Mark a tier as complete and save its data"""
    with job_lock:
        if job_id in analysis_jobs:
            tier_status = analysis_jobs[job_id].get('tier_status', {})
            tier_status[tier] = 'complete'
            analysis_jobs[job_id]['tier_status'] = tier_status
            
            tier_results = analysis_jobs[job_id].get('tier_results', {})
            tier_results[f'tier{tier}'] = tier_data
            analysis_jobs[job_id]['tier_results'] = tier_results

def run_complete_analysis(job_id, project_path):
    """Run all 6 tiers of analysis with real-time updates and AI integration"""
    print(f"\n{'='*60}")
    print(f"Starting analysis for job {job_id}")
    print(f"Project path: {project_path}")
    print(f"{'='*60}\n")
    
    tier_results = {}
    
    try:
        # ===== TIER 1: DATA COLLECTION =====
        update_job_progress(job_id, 1, 10, 'TIER 1: AI-Enhanced Data Collection...')
        
        print("\n📊 TIER 1: Data Collection (AI-Enhanced)")
        print("-" * 40)
        
        collector = UniversalDataCollector(project_path)
        tier1_result = collector.collect_all()
        
        # AI Enhancement: Add semantic analysis of project structure
        ai_analyzer = AIAnalyzer()
        semantic_analysis = ai_analyzer.analyze_structure(tier1_result)
        tier1_result['ai_enhancements'] = semantic_analysis
        tier_results['tier1'] = tier1_result
        
        print(f"  ✓ Language: {tier1_result.get('project_info', {}).get('language', 'Unknown')}")
        print(f"  ✓ Project Type: {tier1_result.get('project_info', {}).get('project_type', 'Unknown')}")
        print(f"  ✓ Files Found: {tier1_result.get('project_info', {}).get('file_count', 0)}")
        print(f"  ✓ Services: {len(tier1_result.get('services', []))}")
        print(f"  ✓ Models: {len(tier1_result.get('models', []))}")
        
        complete_tier(job_id, 1, tier1_result)
        update_job_progress(job_id, 2, 25, 'TIER 2: AI-Powered System Architecture Analysis...')
        
        # ===== TIER 2: SYSTEM ANALYSIS =====
        print("\n🔍 TIER 2: System Analysis (AI-Powered)")
        print("-" * 40)
        
        analyzer = UniversalSystemAnalyzer(project_path, tier1_result)
        tier2_result = analyzer.analyze()
        
        # AI Enhancement: Detect architectural patterns and anti-patterns
        architecture_analysis = ai_analyzer.analyze_architecture(tier2_result)
        tier2_result['ai_enhancements'] = architecture_analysis
        tier_results['tier2'] = tier2_result
        
        print(f"  ✓ Services Detected: {len(tier2_result.get('services', []))}")
        print(f"  ✓ API Endpoints: {tier2_result.get('endpoint_count', 0)}")
        print(f"  ✓ Dependencies: {tier2_result.get('dependency_count', 0)}")
        print(f"  ✓ AI-Detected Patterns: {len(architecture_analysis.get('patterns', []))}")
        
        complete_tier(job_id, 2, tier2_result)
        update_job_progress(job_id, 3, 45, 'TIER 3: AI-Driven Smell Detection...')
        
        # ===== TIER 3: AI SMELL DETECTION =====
        print("\n👃 TIER 3: AI Smell Detection")
        print("-" * 40)
        
        smell_detector = AISmellDetector(project_path, tier1_result, tier2_result)
        tier3_result = smell_detector.detect_all()
        
        # AI Enhancement: Generate severity assessments and impact predictions
        smell_analysis = ai_analyzer.analyze_smells(tier3_result, tier2_result)
        tier3_result['ai_enhancements'] = smell_analysis
        tier_results['tier3'] = tier3_result
        
        print(f"  ✓ Direct Model Calls: {tier3_result.get('direct_model_calls', {}).get('count', 0)}")
        print(f"  ✓ Glue Code Ratio: {tier3_result.get('glue_code_ratio', 0):.1%}")
        print(f"  ✓ Hidden Consumers: {len(tier3_result.get('hidden_consumers', []))}")
        print(f"  ✓ Critical Smells (AI): {len(smell_analysis.get('critical_issues', []))}")
        
        complete_tier(job_id, 3, tier3_result)
        update_job_progress(job_id, 4, 60, 'TIER 4: Computing Model Entanglement Score...')
        
        # ===== TIER 4: METRICS COMPUTATION =====
        print("\n📐 TIER 4: Model Entanglement Score")
        print("-" * 40)
        
        metrics_engine = ModelEntanglementEngine(tier1_result, tier2_result, tier3_result)
        tier4_result = metrics_engine.calculate()
        
        # AI Enhancement: Predictive debt accumulation forecasting
        debt_forecast = ai_analyzer.forecast_debt(tier4_result, {})
        tier4_result['ai_enhancements'] = debt_forecast
        tier_results['tier4'] = tier4_result
        
        print(f"  ✓ MES Score: {tier4_result.get('mes_score', 0)}/10")
        print(f"  ✓ Level: {tier4_result.get('mes_level', 'Unknown')}")
        print(f"  ✓ 6-Month Forecast (AI): {debt_forecast.get('predicted_increase', 0):.1f}% increase")
        
        complete_tier(job_id, 4, tier4_result)
        update_job_progress(job_id, 5, 75, 'TIER 5: AI-Powered Maintainability Analysis...')
        
        # ===== TIER 5: MAINTAINABILITY =====
        print("\n🔧 TIER 5: Maintainability Analysis (AI-Powered)")
        print("-" * 40)
        
        maintainability = MaintainabilityAnalyzer(project_path, tier1_result, tier2_result)
        tier5_result = maintainability.analyze()
        
        # AI Enhancement: Risk assessment and mitigation strategies
        risk_assessment = ai_analyzer.assess_risks(tier5_result, tier4_result)
        tier5_result['ai_enhancements'] = risk_assessment
        tier_results['tier5'] = tier5_result
        
        print(f"  ✓ Total Commits: {tier5_result.get('commit_count', 0)}")
        print(f"  ✓ Bug Rate: {tier5_result.get('bug_metrics', {}).get('bug_rate', 0):.1%}")
        print(f"  ✓ Change Impact: {tier5_result.get('impact_metrics', {}).get('avg_impact', 0):.1f} files")
        print(f"  ✓ Risk Level (AI): {risk_assessment.get('overall_risk', 'Unknown')}")
        
        complete_tier(job_id, 5, tier5_result)
        update_job_progress(job_id, 6, 85, 'TIER 6: AI Validation and Architecture Proposal...')
        
        # ===== TIER 6: VALIDATION & AI ARCHITECTURE =====
        print("\n✅ TIER 6: Validation and AI Architecture")
        print("-" * 40)
        
        validator = ValidationEngine(tier_results)
        tier6_result = validator.validate()
        
        # AI Enhancement: Generate improved architecture proposal
        ai_architect = AIArchitect()
        proposed_architecture = ai_architect.propose_architecture(tier_results)
        tier6_result['proposed_architecture'] = proposed_architecture
        tier_results['tier6'] = tier6_result
        
        print(f"  ✓ Hypothesis: {tier6_result.get('hypothesis_confirmed', False)}")
        print(f"  ✓ Degradation Ratio: {tier6_result.get('degradation_ratio', 0):.2f}")
        print(f"  ✓ AI Architecture Proposed: Yes")
        
        # ===== GENERATE COMPREHENSIVE AI ANALYSIS & RECOMMENDATIONS =====
        print("\n💡 Generating AI-Powered Strategic Analysis")
        print("-" * 40)
        
        # This replaces the old static generate_ai_recommendations with a full AI analysis
        ai_analysis = ai_analyzer.analyze_results(tier_results)
        tier_results['ai_analysis'] = ai_analysis
        
        # Map findings back to the recommendations list for UI compatibility
        recommendations = ai_analysis.get('recommendations', [])
        tier_results['recommendations'] = recommendations
        
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"  {i}. [{rec.get('priority')}] {rec.get('title')}")
        
        # Save results
        results_path = os.path.join(app.config['RESULTS_FOLDER'], f'{job_id}_results.json')
        with open(results_path, 'w') as f:
            json.dump(tier_results, f, indent=2, default=str)
        
        # Generate comprehensive PDF report
        update_job_progress(job_id, 6, 95, 'Generating comprehensive report...')
        
        report_path = os.path.join(app.config['RESULTS_FOLDER'], f'{job_id}_report.pdf')
        generator = ReportGenerator(tier_results)
        generator.generate_pdf(report_path)
        
        # Mark as complete
        with job_lock:
            if job_id in analysis_jobs:
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
        with job_lock:
            if job_id in analysis_jobs:
                analysis_jobs[job_id].update({
                    'status': 'error',
                    'error': str(e),
                    'message': f'Error: {str(e)}'
                })

def generate_ai_recommendations(tier_results, ai_analyzer):
    """
    OBSOLETE: Retained for compatibility. 
    Analysis is now handled by ai_analyzer.analyze_results()
    """
    return []
    
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 AI-Enhanced Technical Debt Detection Framework")
    print("="*60)
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"📁 Results folder: {app.config['RESULTS_FOLDER']}")
    print(f"🌐 Access the application at: http://localhost:5000")
    print("="*60 + "\n")
    
    # Run without debug mode to avoid reloader issues
    # Use debug=False for production, debug=True for development with use_reloader=False
    app.run(debug=False, host='0.0.0.0', port=5000)