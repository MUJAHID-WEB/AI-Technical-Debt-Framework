$(document).ready(function() {
    // AI Analysis Click Handler
    $('#generateAIInsights').on('click', function() {
        const btn = $(this);
        const jobId = btn.data('job-id');
        
        btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i>Analysing Architecture...');
        
        $('#aiLoading').removeClass('d-none');
        $('#aiResult').addClass('d-none');
        
        $.get('/ai-analysis/' + jobId, function(data) {
            $('#aiLoading').addClass('d-none');
            
            if (data.error) {
                btn.prop('disabled', false).html('<i class="fas fa-exclamation-triangle me-2"></i>Analysis Failed').removeClass('btn-premium').addClass('btn-outline-danger');
                $('#aiReportText').html('<div class="text-danger">' + data.error + '</div>');
                $('#aiResult').removeClass('d-none');
            } else {
                btn.html('<i class="fas fa-check-circle me-2"></i>Analysis Complete').removeClass('btn-premium').addClass('btn-outline-success');
                
                // Set report content using JSON structure
                $('#aiReportText').html(renderJSONReport(data.report_json));
                
                // Set reasoning content (handle objects and strings)
                let reasoningHtml = '';
                if (data.reasoning) {
                    if (Array.isArray(data.reasoning)) {
                        reasoningHtml = data.reasoning.map(r => r.content || '').join('\n\n');
                    } else if (typeof data.reasoning === 'object') {
                        reasoningHtml = data.reasoning.content || JSON.stringify(data.reasoning, null, 2);
                    } else {
                        reasoningHtml = data.reasoning;
                    }
                } else {
                    reasoningHtml = 'Reasoning details not provided by the model.';
                }
                $('#aiReasoningText').text(reasoningHtml);
                
                $('#aiResult').removeClass('d-none');
                
                // Smooth scroll to results
                $('html, body').animate({
                    scrollTop: $("#aiInsightsRow").offset().top - 100
                }, 800);
            }
        }).fail(function(xhr) {
            $('#aiLoading').addClass('d-none');
            const errorMsg = xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : 'Network timeout or server error. Please retry.';
            
            btn.prop('disabled', false).html('<i class="fas fa-redo me-2"></i>Retry AI Analysis').addClass('btn-outline-warning');
            
            $('#aiReportText').html(`<div class="p-4 text-center">
                <i class="fas fa-clock-rotate-left fa-2x text-warning mb-3"></i>
                <div class="text-bright fw-bold mb-1">Analysis Interrupted</div>
                <div class="text-muted small">${errorMsg}</div>
            </div>`);
            $('#aiResult').removeClass('d-none');
        });
    });

    /**
     * Renders the structured JSON report into beautiful Glassmorphism components
     */
    function renderJSONReport(json) {
        if (!json || json.error) {
            return `<div class="p-4 text-center text-danger">Error parsing AI report: ${json ? json.error : 'Empty response'}</div>`;
        }

        let html = '<div class="ai-report-container">';

        // 1. Executive Summary
        if (json.executive_summary) {
            html += `<div class="glass-card mb-4 p-4">
                <div class="text-bright small opacity-75 mb-2 uppercase tracking-wider">Executive Summary</div>
                <div class="text-bright lead">${json.executive_summary}</div>
            </div>`;
        }

        // 2. Findings
        if (json.findings && Array.isArray(json.findings)) {
            json.findings.forEach(finding => {
                const p = (finding.priority || 'Low').toLowerCase();
                let pClass = 'priority-low';
                if (p.includes('critical') || p.includes('highest')) pClass = 'priority-critical';
                else if (p.includes('high')) pClass = 'priority-high';
                else if (p.includes('medium')) pClass = 'priority-medium';

                html += `<div class="glass-card mb-4 overflow-hidden">
                    <div class="ai-card-title px-4 py-3 d-flex justify-content-between align-items-center">
                        <span class="fw-bold text-bright">${finding.title}</span>
                        <span class="ai-badge ${pClass}">${finding.priority}</span>
                    </div>
                    <div class="p-4">
                        <div class="ai-field mb-3">
                            <span class="ai-field-label">Root Cause:</span>
                            <span class="ai-field-value">${finding.root_cause}</span>
                        </div>
                        <div class="ai-field mb-3">
                            <span class="ai-field-label">Architectural Impact:</span>
                            <span class="ai-field-value">${finding.impact}</span>
                        </div>
                        <div class="ai-field">
                            <span class="ai-field-label">Strategic recommendation:</span>
                            <span class="ai-field-value text-accent">${finding.recommendation}</span>
                        </div>
                    </div>
                </div>`;
            });
        }

        // 3. Strategic Execution Plan
        if (json.strategic_plan) {
            html += `<div class="glass-card p-4 secondary-glass">
                <h5 class="text-bright fw-bold mb-4 border-bottom border-glass pb-2">
                    <i class="fas fa-chess-knight me-2 text-accent"></i>Strategic Execution Plan
                </h5>
                <div class="row">`;

            if (json.strategic_plan.phase1) {
                html += `<div class="col-md-6 mb-4 mb-md-0">
                    <div class="ai-phase-title mb-3">${json.strategic_plan.phase1.title}</div>
                    <ul class="ai-list">
                        ${(json.strategic_plan.phase1.tasks || []).map(t => `<li>${t}</li>`).join('')}
                    </ul>
                </div>`;
            }

            if (json.strategic_plan.phase2) {
                html += `<div class="col-md-6">
                    <div class="ai-phase-title mb-3">${json.strategic_plan.phase2.title}</div>
                    <ul class="ai-list">
                        ${(json.strategic_plan.phase2.tasks || []).map(t => `<li>${t}</li>`).join('')}
                    </ul>
                </div>`;
            }

            html += `</div></div>`;
        }

        html += '</div>';
        return html;
    }
});
