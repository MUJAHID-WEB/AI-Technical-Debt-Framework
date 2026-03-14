// Real-time updates for tier processing
class RealTimeUpdater {
    constructor(jobId) {
        this.jobId = jobId;
        this.pollInterval = null;
        this.tiers = {
            1: { name: 'Data Collection', status: 'pending', data: null },
            2: { name: 'System Analysis', status: 'pending', data: null },
            3: { name: 'AI Smell Detection', status: 'pending', data: null },
            4: { name: 'Metrics Computation', status: 'pending', data: null },
            5: { name: 'Maintainability', status: 'pending', data: null },
            6: { name: 'Validation', status: 'pending', data: null }
        };
    }

    start() {
        this.pollInterval = setInterval(() => this.poll(), 2000);
    }

    poll() {
        $.get(`/job-status/${this.jobId}`, (data) => {
            this.updateProgress(data);
            
            if (data.status === 'complete') {
                this.stop();
                setTimeout(() => window.location.reload(), 1000);
            } else if (data.status === 'error') {
                this.stop();
                this.showError(data.error);
            }
        }).fail(() => {
            this.stop();
        });
    }

    updateProgress(data) {
        // Update progress bar
        $('#progressBar').css('width', data.progress + '%').text(data.progress + '%');
        $('#statusMessage').text(data.message);

        // Update tier status
        if (data.tier_status) {
            for (let tier = 1; tier <= 6; tier++) {
                const status = data.tier_status[tier] || 'pending';
                const card = $(`#tier${tier}Card`);
                const badge = $(`#tier${tier}Status`);

                // Update card appearance
                card.removeClass('border-secondary border-warning border-success');
                badge.removeClass('bg-secondary bg-warning bg-success');

                if (status === 'running') {
                    card.addClass('border-warning');
                    badge.addClass('bg-warning').text('Running');
                } else if (status === 'complete') {
                    card.addClass('border-success');
                    badge.addClass('bg-success').text('Complete');
                } else {
                    card.addClass('border-secondary');
                    badge.addClass('bg-secondary').text('Pending');
                }
            }
        }

        // Update tier details as they come in
        let details = [];
        if (data.tier_results) {
            if (data.tier_results.tier1) {
                const t1 = data.tier_results.tier1;
                details.push(`📊 TIER 1: Found ${t1.services?.length || 0} services, ${t1.models?.length || 0} models`);
            }
            if (data.tier_results.tier2) {
                const t2 = data.tier_results.tier2;
                details.push(`🔍 TIER 2: Detected ${t2.endpoint_count || 0} API endpoints`);
            }
            if (data.tier_results.tier3) {
                const t3 = data.tier_results.tier3;
                details.push(`👃 TIER 3: Direct calls: ${t3.direct_model_calls?.count || 0}`);
            }
            if (data.tier_results.tier4) {
                const t4 = data.tier_results.tier4;
                details.push(`📐 TIER 4: MES Score: ${t4.mes_score || 0}/10`);
            }
        }
        
        if (details.length > 0) {
            $('#operationDetails').text(details.join('\n'));
        }
    }

    stop() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    showError(error) {
        $('#operationDetails').text('Error: ' + error);
        $('#progressBar').removeClass('progress-bar-animated').addClass('bg-danger');
    }
}

// Initialize when document is ready
$(document).ready(function() {
    const jobId = $('#jobId').val();
    if (jobId) {
        const updater = new RealTimeUpdater(jobId);
        updater.start();
    }
});