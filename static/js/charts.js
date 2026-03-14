// Chart utilities for AI Technical Debt Framework

// Global chart functions
window.AITechnicalDebtCharts = {
    
    // Create MES Gauge Chart
    createMESGauge: function(score, elementId) {
        if (!document.getElementById(elementId)) return;
        
        const data = [{
            type: "indicator",
            mode: "gauge+number+delta",
            value: score,
            title: { text: "Model Entanglement Score", font: { size: 24 } },
            delta: { reference: 5 },
            gauge: {
                axis: { range: [0, 10], tickwidth: 1, tickcolor: "darkblue" },
                bar: { color: this.getScoreColor(score) },
                bgcolor: "white",
                borderwidth: 2,
                bordercolor: "gray",
                steps: [
                    { range: [0, 3], color: "#28a745" },
                    { range: [3, 7], color: "#ffc107" },
                    { range: [7, 10], color: "#dc3545" }
                ],
                threshold: {
                    line: { color: "red", width: 4 },
                    thickness: 0.75,
                    value: 7
                }
            }
        }];
        
        const layout = {
            width: 400,
            height: 300,
            margin: { t: 25, r: 25, l: 25, b: 25 },
            paper_bgcolor: "white",
            font: { color: "darkblue", family: "Arial" }
        };
        
        Plotly.newPlot(elementId, data, layout);
    },
    
    // Create Entanglement Heatmap
    createEntanglementHeatmap: function(services, models, dependencies, elementId) {
        if (!document.getElementById(elementId) || !services || !models) return;
        
        const serviceNames = services.map(s => s.name || 'Unknown');
        const modelNames = models.map(m => m.name || 'Unknown');
        
        const matrix = [];
        for (let i = 0; i < serviceNames.length; i++) {
            const row = [];
            for (let j = 0; j < modelNames.length; j++) {
                let depends = false;
                if (dependencies) {
                    depends = dependencies.some(d => 
                        (d.source === serviceNames[i] && d.target === modelNames[j]) ||
                        (d.from === serviceNames[i] && d.to === modelNames[j])
                    );
                }
                row.push(depends ? 1 : 0);
            }
            matrix.push(row);
        }
        
        const data = [{
            z: matrix,
            x: modelNames,
            y: serviceNames,
            type: 'heatmap',
            colorscale: [
                [0, '#f7fbff'],
                [0.5, '#6baed6'],
                [1, '#08519c']
            ],
            showscale: true,
            hoverongaps: false
        }];
        
        const layout = {
            title: 'Service-Model Entanglement Heatmap',
            xaxis: { title: 'Models', tickangle: -45 },
            yaxis: { title: 'Services' },
            width: 600,
            height: 400,
            margin: { l: 100, r: 50, t: 50, b: 100 }
        };
        
        Plotly.newPlot(elementId, data, layout);
    },
    
    // Create Churn Timeline
    createChurnTimeline: function(commits, elementId) {
        if (!document.getElementById(elementId) || !commits) return;
        
        const dates = {};
        commits.forEach(commit => {
            const date = commit.date ? commit.date.split('T')[0] : 'Unknown';
            dates[date] = (dates[date] || 0) + 1;
        });
        
        const data = [{
            x: Object.keys(dates),
            y: Object.values(dates),
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#0d6efd', width: 2 },
            marker: { size: 8 }
        }];
        
        const layout = {
            title: 'Commit Activity Timeline',
            xaxis: { title: 'Date' },
            yaxis: { title: 'Number of Commits' },
            width: 600,
            height: 300,
            margin: { l: 50, r: 20, t: 50, b: 50 }
        };
        
        Plotly.newPlot(elementId, data, layout);
    },
    
    // Create Smell Radar Chart
    createSmellRadarChart: function(smells, elementId) {
        if (!document.getElementById(elementId) || !smells) return;
        
        const categories = [
            'Direct Model Calls',
            'Glue Code',
            'Hidden Consumers',
            'Pipeline Complexity',
            'Retrain Frequency',
            'Feedback Loops'
        ];
        
        const values = [
            Math.min((smells.direct_model_calls?.ratio || 0) * 10, 10),
            Math.min((smells.glue_code_ratio || 0) * 10, 10),
            Math.min((smells.hidden_consumers?.length || 0) * 2, 10),
            Math.min((smells.pipeline_complexity?.complex_pipelines || 0) * 2, 10),
            Math.min((smells.retrain_frequency || 0) / 2, 10),
            Math.min((smells.feedback_loops?.length || 0) * 2, 10)
        ];
        
        const data = [{
            type: 'scatterpolar',
            r: values,
            theta: categories,
            fill: 'toself',
            name: 'AI Smells',
            line: { color: '#dc3545', width: 2 }
        }];
        
        const layout = {
            polar: {
                radialaxis: {
                    visible: true,
                    range: [0, 10]
                }
            },
            title: 'AI Smell Radar',
            width: 500,
            height: 500,
            margin: { l: 80, r: 80, t: 80, b: 80 }
        };
        
        Plotly.newPlot(elementId, data, layout);
    },
    
    // Create Correlation Matrix
    createCorrelationMatrix: function(correlations, elementId) {
        if (!document.getElementById(elementId)) return;
        
        const metrics = ['MES', 'Churn', 'Bugs', 'Impact'];
        const matrix = [
            [1, correlations?.mes_churn || 0, correlations?.mes_bug || 0, correlations?.mes_impact || 0],
            [correlations?.mes_churn || 0, 1, 0.6, 0.5],
            [correlations?.mes_bug || 0, 0.6, 1, 0.7],
            [correlations?.mes_impact || 0, 0.5, 0.7, 1]
        ];
        
        const data = [{
            z: matrix,
            x: metrics,
            y: metrics,
            type: 'heatmap',
            colorscale: [
                [0, '#f7fbff'],
                [0.25, '#c6dbef'],
                [0.5, '#6baed6'],
                [0.75, '#2171b5'],
                [1, '#08306b']
            ],
            zmin: -1,
            zmax: 1,
            text: matrix.map(row => row.map(v => v.toFixed(2))),
            texttemplate: '%{text}',
            colorbar: { title: 'Correlation' }
        }];
        
        const layout = {
            title: 'Correlation Matrix',
            width: 500,
            height: 500,
            margin: { l: 80, r: 50, t: 50, b: 80 }
        };
        
        Plotly.newPlot(elementId, data, layout);
    },
    
    // Helper function to get color based on score
    getScoreColor: function(score) {
        if (score <= 3) return '#28a745';
        if (score <= 7) return '#ffc107';
        return '#dc3545';
    }
};

// Initialize charts when document is ready
$(document).ready(function() {
    console.log('Charts.js loaded successfully');
});