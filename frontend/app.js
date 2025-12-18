const API_BASE = window.location.origin;

// Tab switching
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.dataset.tab;

        // Update active tab button
        document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
        button.classList.add('active');

        // Update active tab content
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        document.getElementById(tabName).classList.add('active');

        // Load data for specific tabs
        if (tabName === 'dashboard') {
            loadDashboard();
        } else if (tabName === 'upload') {
            loadSpecs();
        } else if (tabName === 'generate') {
            loadSpecsForGeneration();
        } else if (tabName === 'execute') {
            loadSuitesForExecution();
        } else if (tabName === 'results') {
            loadExecutionsForResults();
        }
    });
});

// Load dashboard
async function loadDashboard() {
    try {
        const response = await fetch(`${API_BASE}/api/reports/dashboard`);
        const data = await response.json();

        document.getElementById('total-specs').textContent = data.total_api_specs;
        document.getElementById('total-suites').textContent = data.total_test_suites;
        document.getElementById('total-executions').textContent = data.total_executions;
        document.getElementById('avg-coverage').textContent = `${data.average_coverage}%`;

        const tbody = document.getElementById('executions-tbody');
        tbody.innerHTML = '';

        data.recent_executions.forEach(exec => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${exec.id}</td>
                <td>${exec.test_suite_id}</td>
                <td><span class="status ${exec.status}">${exec.status}</span></td>
                <td>${exec.passed_tests}</td>
                <td>${exec.failed_tests}</td>
                <td>${exec.coverage.toFixed(2)}%</td>
                <td>${new Date(exec.started_at).toLocaleString()}</td>
                <td>
                    <button onclick="viewExecution(${exec.id})" class="btn btn-sm">View</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Upload API spec
document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('spec-name').value;
    const content = document.getElementById('spec-content').value;

    try {
        // Validate JSON
        JSON.parse(content);

        const response = await fetch(`${API_BASE}/api/generation/specs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, spec_content: content })
        });

        if (response.ok) {
            alert('API specification uploaded successfully!');
            document.getElementById('upload-form').reset();
            loadSpecs();
        } else {
            alert('Error uploading specification');
        }
    } catch (error) {
        alert('Invalid JSON format');
    }
});

// Load specs
async function loadSpecs() {
    try {
        const response = await fetch(`${API_BASE}/api/generation/specs`);
        const specs = await response.json();

        const container = document.getElementById('specs-list');
        container.innerHTML = '';

        specs.forEach(spec => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <h4>${spec.name}</h4>
                <p><strong>ID:</strong> ${spec.id}</p>
                <p><strong>Created:</strong> ${new Date(spec.created_at).toLocaleDateString()}</p>
                <p><strong>Updated:</strong> ${new Date(spec.updated_at).toLocaleDateString()}</p>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading specs:', error);
    }
}

// Load specs for generation dropdown
async function loadSpecsForGeneration() {
    try {
        const response = await fetch(`${API_BASE}/api/generation/specs`);
        const specs = await response.json();

        const select = document.getElementById('select-spec');
        select.innerHTML = '<option value="">-- Select a specification --</option>';

        specs.forEach(spec => {
            const option = document.createElement('option');
            option.value = spec.id;
            option.textContent = `${spec.name} (ID: ${spec.id})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading specs:', error);
    }
}

// Generate tests
document.getElementById('generate-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const apiSpecId = parseInt(document.getElementById('select-spec').value);
    const baseUrl = document.getElementById('base-url').value;
    const includeEdgeCases = document.getElementById('include-edge-cases').checked;

    const statusDiv = document.getElementById('generation-status');
    const resultDiv = document.getElementById('generated-suite');

    statusDiv.style.display = 'block';
    resultDiv.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/api/generation/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                api_spec_id: apiSpecId,
                base_url: baseUrl,
                include_edge_cases: includeEdgeCases
            })
        });

        if (response.ok) {
            const suite = await response.json();

            statusDiv.style.display = 'none';
            resultDiv.style.display = 'block';

            document.getElementById('suite-id').textContent = suite.id;
            document.getElementById('suite-name').textContent = suite.name;
            document.getElementById('suite-count').textContent = suite.generated_tests.length;
        } else {
            statusDiv.innerHTML = '<i class="fas fa-times"></i> Failed to generate tests';
        }
    } catch (error) {
        console.error('Error generating tests:', error);
        statusDiv.innerHTML = '<i class="fas fa-times"></i> Error generating tests';
    }
});

// Load suites for execution
async function loadSuitesForExecution() {
    try {
        const response = await fetch(`${API_BASE}/api/generation/suites`);
        const suites = await response.json();

        const select = document.getElementById('select-suite');
        select.innerHTML = '<option value="">-- Select a test suite --</option>';

        suites.forEach(suite => {
            const option = document.createElement('option');
            option.value = suite.id;
            option.textContent = `${suite.name} (${suite.generated_tests.length} tests)`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading suites:', error);
    }
}

// Execute tests
document.getElementById('execute-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const testSuiteId = parseInt(document.getElementById('select-suite').value);
    const baseUrl = document.getElementById('target-url').value;

    const statusDiv = document.getElementById('execution-status');
    const resultDiv = document.getElementById('execution-result');

    statusDiv.style.display = 'block';
    resultDiv.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/api/execution/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                test_suite_id: testSuiteId,
                base_url: baseUrl
            })
        });

        if (response.ok) {
            const execution = await response.json();

            // Poll for results
            pollExecutionStatus(execution.id, statusDiv, resultDiv);
        } else {
            statusDiv.innerHTML = '<i class="fas fa-times"></i> Failed to start execution';
        }
    } catch (error) {
        console.error('Error executing tests:', error);
        statusDiv.innerHTML = '<i class="fas fa-times"></i> Error executing tests';
    }
});

// Poll execution status
async function pollExecutionStatus(executionId, statusDiv, resultDiv) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/api/execution/executions/${executionId}`);
            const execution = await response.json();

            if (execution.status === 'completed') {
                clearInterval(interval);

                statusDiv.style.display = 'none';
                resultDiv.style.display = 'block';

                document.getElementById('result-passed').textContent = execution.passed_tests;
                document.getElementById('result-failed').textContent = execution.failed_tests;
                document.getElementById('result-coverage').textContent = `${execution.coverage_percentage.toFixed(2)}%`;
                document.getElementById('result-time').textContent = `${execution.execution_time.toFixed(2)}s`;
            }
        } catch (error) {
            console.error('Error polling execution:', error);
            clearInterval(interval);
        }
    }, 2000);
}

// Load executions for results
async function loadExecutionsForResults() {
    try {
        const response = await fetch(`${API_BASE}/api/execution/executions`);
        const executions = await response.json();

        const select = document.getElementById('select-execution');
        select.innerHTML = '<option value="">-- Select an execution --</option>';

        executions.forEach(exec => {
            if (exec.status === 'completed') {
                const option = document.createElement('option');
                option.value = exec.id;
                option.textContent = `Execution #${exec.id} - ${exec.passed_tests}/${exec.total_tests} passed`;
                select.appendChild(option);
            }
        });
    } catch (error) {
        console.error('Error loading executions:', error);
    }
}

// View results
document.getElementById('view-results-btn').addEventListener('click', async () => {
    const executionId = document.getElementById('select-execution').value;

    if (!executionId) {
        alert('Please select an execution');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/execution/executions/${executionId}`);
        const execution = await response.json();

        const container = document.getElementById('test-results-list');
        container.innerHTML = '';

        execution.results.forEach(result => {
            const item = document.createElement('div');
            item.className = `test-result-item ${result.status}`;

            let errorsHtml = '';
            if (result.errors && result.errors.length > 0) {
                errorsHtml = `
                    <div class="errors">
                        <strong>Errors:</strong>
                        <ul>
                            ${result.errors.map(e => `<li>${e}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }

            item.innerHTML = `
                <h4>${result.name}</h4>
                <span class="status ${result.status}">${result.status.toUpperCase()}</span>
                <div class="details">
                    <p><strong>Expected Status:</strong> ${result.expected_status}</p>
                    <p><strong>Actual Status:</strong> ${result.actual_status}</p>
                    <p><strong>Execution Time:</strong> ${result.execution_time.toFixed(3)}s</p>
                    <p><strong>Assertions Passed:</strong> ${result.assertions_passed.length}</p>
                    <p><strong>Assertions Failed:</strong> ${result.assertions_failed.length}</p>
                </div>
                ${errorsHtml}
            `;
            container.appendChild(item);
        });

        document.getElementById('test-results-container').style.display = 'block';
    } catch (error) {
        console.error('Error loading results:', error);
        alert('Error loading test results');
    }
});
// Get AI analysis
// Get AI analysis
document.getElementById('get-ai-analysis-btn').addEventListener('click', async () => {
    const executionId = document.getElementById('select-execution').value;

    if (!executionId) {
        alert('Please select an execution');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/reports/analysis/${executionId}`);
        const data = await response.json();

        console.log("DEBUG: Full analysis data:", data);
        console.log("DEBUG: Critical issues:", data.analysis.critical_issues);
        console.log("DEBUG: Type of critical issues:", typeof data.analysis.critical_issues);
        console.log("DEBUG: Is array?", Array.isArray(data.analysis.critical_issues));
        const analysis = data.analysis;

        document.getElementById('quality-score').textContent = analysis.overall_quality_score || 'N/A';

        // Helper function to render lists safely
        function renderList(elementId, items) {
            const element = document.getElementById(elementId);
            if (items && Array.isArray(items) && items.length > 0 && items[0] !== '') {
                element.innerHTML = items.map(item => `<li>${item}</li>`).join('');
            } else {
                element.innerHTML = '<li class="empty-item">None</li>';
            }
        }

        renderList('critical-issues', analysis.critical_issues);
        renderList('recommendations', analysis.recommendations);
        renderList('well-covered', analysis.well_covered_areas);
        renderList('coverage-gaps', analysis.coverage_gaps);

        // Summary
        const analysisSummary = document.getElementById('analysis-summary');
        analysisSummary.textContent = analysis.summary || 'No analysis summary available.';

        document.getElementById('ai-analysis-container').style.display = 'block';
    } catch (error) {
        console.error('Error getting AI analysis:', error);
        alert('Error getting AI analysis');
    }
});
// View execution from dashboard
function viewExecution(executionId) {
    document.querySelector('[data-tab="results"]').click();
    document.getElementById('select-execution').value = executionId;
    document.getElementById('view-results-btn').click();
}

// Load dashboard on page load
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});
