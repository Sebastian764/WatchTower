
const uploadArea = document.getElementById('uploadArea');
const videoFile = document.getElementById('videoFile');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const videoPreview = document.getElementById('videoPreview');
const uploadForm = document.getElementById('uploadForm');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const analyzeBtn = document.getElementById('analyzeBtn');

// File selection handlers
videoFile.addEventListener('change', handleFileSelect);
uploadArea.addEventListener('click', () => videoFile.click());

// Drag and drop handlers
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        videoFile.files = files;
        handleFileSelect();
    }
});

function handleFileSelect() {
    const file = videoFile.files[0];
    if (file) {
        // Check if it's a video file
        if (!file.type.startsWith('video/')) {
            showError('Please select a valid video file.');
            return;
        }
        
        // Check file size (100MB limit)
        if (file.size > 100 * 1024 * 1024) {
            showError('File size must be less than 100MB.');
            return;
        }
        
        fileName.textContent = `📁 ${file.name} (${formatFileSize(file.size)})`;
        fileInfo.style.display = 'block';
        
        // Show video preview
        const url = URL.createObjectURL(file);
        videoPreview.src = url;
        videoPreview.style.display = 'block';
        
        // Clear previous results
        results.innerHTML = '';
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Form submission
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const file = videoFile.files[0];
    if (!file) {
        showError('Please select a video file');
        return;
    }

    const formData = new FormData();
    formData.append('video', file);

    loading.style.display = 'block';
    analyzeBtn.disabled = true;
    results.innerHTML = '';

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Analysis failed');
        }

        displayResults(data);
    } catch (error) {
        showError(`Analysis failed: ${error.message}`);
    } finally {
        loading.style.display = 'none';
        analyzeBtn.disabled = false;
    }
});

function displayResults(data) {
    if (data.incidents.length === 0) {
        results.innerHTML = `
            <div class="results">
                <div class="success no-incidents">
                    <div class="no-incidents-icon">✅</div>
                    <h3>No Security Incidents Detected</h3>
                    <p>The AI analysis found no concerning activities in the video footage.</p>
                </div>
            </div>
        `;
        return;
    }

    let html = `
        <div class="results">
            <h3>🚨 Analysis Results: ${data.incidents.length} Incident${data.incidents.length > 1 ? 's' : ''} Detected</h3>
    `;
    
    data.incidents.forEach((incident, index) => {
        const isCritical = incident.recommendedAction === 'Notify Authorities' || 
                          incident.recommendedAction === 'Notify Paramedics';
        const cssClass = isCritical ? 'incident critical' : 'incident';
        
        html += `
            <div class="${cssClass}">
                <div class="incident-header">
                    <div class="incident-type">${getIncidentIcon(incident.incidentType)} ${incident.incidentType}</div>
                    <div class="incident-time">⏰ ${incident.timestamp}</div>
                </div>
                <div class="incident-description">${incident.description}</div>
                <div class="recommended-action">
                    <strong>Recommended Action:</strong> ${getActionIcon(incident.recommendedAction)} ${incident.recommendedAction}
                </div>
                ${isCritical ? '<div class="critical-alert">⚠️ CRITICAL INCIDENT - IMMEDIATE ATTENTION REQUIRED</div>' : ''}
            </div>
        `;
    });
    
    html += '</div>';
    results.innerHTML = html;
}

function getIncidentIcon(type) {
    const icons = {
        'Robbery': '🔫',
        'Medical Emergency': '🚑',
        'Altercation/Fight': '👊',
        'Vandalism': '🔨',
        'Other': '⚠️',
        'None': '✅'
    };
    return icons[type] || '⚠️';
}

function getActionIcon(action) {
    const icons = {
        'Notify Authorities': '🚔',
        'Notify Paramedics': '🚑',
        'Continue Monitoring': '👁️',
        'None': '✅'
    };
    return icons[action] || '📋';
}

function showError(message) {
    results.innerHTML = `
        <div class="results">
            <div class="error">
                <strong>❌ Error:</strong> ${message}
            </div>
        </div>
    `;
}