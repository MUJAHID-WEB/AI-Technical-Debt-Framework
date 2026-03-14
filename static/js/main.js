// Main JavaScript for AI Technical Debt Framework

// Use IIFE to avoid global scope pollution
(function() {
    'use strict';
    
    // Check if we're in a browser environment
    if (typeof window === 'undefined') return;
    
    // Store variables in a namespace instead of global
    const AITDebt = {
        currentJobId: null,
        analysisInterval: null,
        progressModal: null
    };
    
    // Initialize when document is ready
    $(document).ready(function() {
        console.log('Main.js loaded - jQuery version:', $.fn.jquery);
        
        // Load saved analyses from localStorage
        loadSavedAnalyses();
        
        // Initialize tooltips
        initializeTooltips();
        
        // Handle form submissions
        setupFormValidation();
        
        // Check for existing job in URL
        const urlParams = new URLSearchParams(window.location.search);
        const jobId = urlParams.get('job');
        if (jobId) {
            checkJobStatus(jobId);
        }
    });
    
    function initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    function setupFormValidation() {
        // Local upload validation
        const localForm = $('#localUploadForm');
        if (localForm.length) {
            localForm.on('submit', function(e) {
                const files = $('#projectFiles')[0]?.files;
                if (!files || files.length === 0) {
                    e.preventDefault();
                    showNotification('Please select at least one file', 'error');
                    return false;
                }
                
                // Check file size
                let totalSize = 0;
                for (let i = 0; i < files.length; i++) {
                    totalSize += files[i].size;
                }
                
                if (totalSize > 500 * 1024 * 1024) { // 500MB
                    e.preventDefault();
                    showNotification('Total file size exceeds 500MB limit', 'error');
                    return false;
                }
            });
        }
        
        // GitHub URL validation
        const githubForm = $('#githubForm');
        if (githubForm.length) {
            githubForm.on('submit', function(e) {
                const url = $('#githubUrl').val();
                if (!url || !url.match(/^https?:\/\/github\.com\/[\w-]+\/[\w-]+/)) {
                    e.preventDefault();
                    showNotification('Please enter a valid GitHub repository URL', 'error');
                    return false;
                }
            });
        }
        
        // MLOps endpoint validation
        const mlopsForm = $('#mlopsForm');
        if (mlopsForm.length) {
            mlopsForm.on('submit', function(e) {
                const endpoint = $('#mlopsEndpoint').val();
                if (!endpoint) {
                    e.preventDefault();
                    showNotification('Please enter an API endpoint', 'error');
                    return false;
                }
            });
        }
    }
    
    window.showNotification = function(message, type = 'info') {
        // Check if toast container exists
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <i class="fas fa-${type === 'error' ? 'exclamation-circle' : type === 'success' ? 'check-circle' : 'info-circle'} me-2 text-${type}"></i>
                    <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 5000 });
        toast.show();
        
        // Remove toast after it's hidden
        toastElement.addEventListener('hidden.bs.toast', function() {
            this.remove();
        });
    };
    
    function loadSavedAnalyses() {
        const analyses = JSON.parse(localStorage.getItem('recentAnalyses') || '[]');
        const list = $('#analysisList');
        
        if (!list.length) return;
        
        if (analyses.length === 0) {
            list.html('<p class="text-muted text-center">No recent analyses</p>');
            return;
        }
        
        list.empty();
        analyses.slice(0, 5).forEach(function(analysis) {
            const date = analysis.timestamp ? new Date(analysis.timestamp).toLocaleDateString() : 'Unknown';
            const item = $(`
                <a href="/results/${analysis.job_id}" class="list-group-item list-group-item-action">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${analysis.name || 'Analysis'}</h6>
                        <small>${date}</small>
                    </div>
                    <small>MES: ${analysis.mes || 'N/A'}</small>
                    ${analysis.status ? `<span class="badge bg-${getStatusColor(analysis.status)}">${analysis.status}</span>` : ''}
                </a>
            `);
            list.append(item);
        });
    }
    
    function getStatusColor(status) {
        switch(status?.toLowerCase()) {
            case 'complete': return 'success';
            case 'processing': return 'warning';
            case 'error': return 'danger';
            default: return 'secondary';
        }
    }
    
    window.saveAnalysis = function(jobId, data) {
        const analyses = JSON.parse(localStorage.getItem('recentAnalyses') || '[]');
        
        analyses.unshift({
            job_id: jobId,
            name: data.name || `Analysis ${new Date().toLocaleString()}`,
            timestamp: new Date().toISOString(),
            mes: data.tier4?.mes_score || 'Pending',
            status: data.status || 'processing'
        });
        
        // Keep only last 20 analyses
        if (analyses.length > 20) {
            analyses.pop();
        }
        
        localStorage.setItem('recentAnalyses', JSON.stringify(analyses));
        loadSavedAnalyses();
    };
    
    window.checkJobStatus = function(jobId) {
        $.get(`/job-status/${jobId}`, function(data) {
            if (data.status === 'complete') {
                window.location.href = data.results_url || `/results/${jobId}`;
            } else if (data.status === 'error') {
                showNotification(`Analysis failed: ${data.message}`, 'error');
            } else {
                // Still processing
                setTimeout(function() {
                    checkJobStatus(jobId);
                }, 2000);
            }
        }).fail(function() {
            showNotification('Job not found', 'error');
        });
    };
    
    // Export functions for use in other scripts
    window.AITechnicalDebt = {
        showNotification: showNotification,
        saveAnalysis: saveAnalysis,
        checkJobStatus: checkJobStatus,
        loadSavedAnalyses: loadSavedAnalyses
    };
    
})();

// Fallback for any code that might be using the old global variables
if (typeof currentJobId !== 'undefined') {
    console.warn('currentJobId global variable detected - this should be avoided');
}