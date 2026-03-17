// Global state
let emails = [];
let selectedEmailId = null;

// DOM elements
const emailForm = document.getElementById('email-form');
const formMessage = document.getElementById('form-message');
const emailList = document.getElementById('email-list');
const detailSection = document.getElementById('detail-section');
const emailDetail = document.getElementById('email-detail');
const refreshBtn = document.getElementById('refresh-btn');
const closeDetailBtn = document.getElementById('close-detail-btn');
const subjectSelect = document.getElementById('subject');
const customSubjectGroup = document.getElementById('custom-subject-group');
const customSubjectInput = document.getElementById('custom-subject');
const bodyTextarea = document.getElementById('body');
const approveBtn = document.getElementById('approve-btn');
const rejectBtn = document.getElementById('reject-btn');

// API Base URL
const API_BASE = '/api';

// Event listeners
emailForm.addEventListener('submit', handleEmailSubmit);
refreshBtn.addEventListener('click', loadEmails);
closeDetailBtn.addEventListener('click', closeDetail);
subjectSelect.addEventListener('change', handleSubjectChange);
approveBtn.addEventListener('click', handleApprove);
rejectBtn.addEventListener('click', handleReject);

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadEmails();
    // Auto-refresh every 5 seconds
    setInterval(loadEmails, 5000);
});

// ============================================
// Form Handling
// ============================================

function handleSubjectChange(e) {
    if (e.target.value === 'Custom question') {
        customSubjectGroup.style.display = 'block';
        customSubjectInput.required = true;
    } else {
        customSubjectGroup.style.display = 'none';
        customSubjectInput.required = false;
    }
}

async function handleEmailSubmit(e) {
    e.preventDefault();

    const sender = document.getElementById('sender').value;
    const subject = subjectSelect.value === 'Custom question'
        ? customSubjectInput.value
        : subjectSelect.value;
    const body = bodyTextarea.value;

    if (!subject || !body) {
        showMessage('Please fill in all fields', 'error');
        return;
    }

    try {
        showMessage('Sending email...', 'info');
        const response = await fetch(`${API_BASE}/emails/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sender, subject, body }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to send email');
        }

        const result = await response.json();
        showMessage(`✓ Email submitted! ID: ${result.email_id}`, 'success');

        // Reset form
        emailForm.reset();
        subjectSelect.value = '';
        customSubjectGroup.style.display = 'none';

        // Reload emails
        setTimeout(loadEmails, 500);
    } catch (error) {
        showMessage(`✗ Error: ${error.message}`, 'error');
    }
}

function showMessage(msg, type = 'info') {
    formMessage.textContent = msg;
    formMessage.className = `form-message ${type}`;
    formMessage.style.display = 'block';

    if (type !== 'error') {
        setTimeout(() => {
            formMessage.style.display = 'none';
        }, 4000);
    }
}

// ============================================
// Email List
// ============================================

async function loadEmails() {
    try {
        const response = await fetch(`${API_BASE}/emails/`);
        if (!response.ok) throw new Error('Failed to load emails');

        emails = await response.json();
        renderEmailList();
    } catch (error) {
        console.error('Error loading emails:', error);
        emailList.innerHTML = `<div class="loading">Error loading emails: ${error.message}</div>`;
    }
}

function renderEmailList() {
    if (emails.length === 0) {
        emailList.innerHTML = '<div class="loading">No emails yet. Send one to get started!</div>';
        return;
    }

    emailList.innerHTML = emails
        .sort((a, b) => new Date(b.received_at) - new Date(a.received_at))
        .map(email => {
            const statusBadgeClass = getStatusBadgeClass(email.status);
            const priorityBadge = email.priority ? `<span class="email-item-badge" style="background-color: ${getPriorityColor(email.priority)}; color: white;">P${email.priority}</span>` : '';
            const timeAgo = getTimeAgo(new Date(email.received_at));

            return `
                <div class="email-item ${email.status === 'processing' ? 'unread' : ''}" onclick="selectEmail('${email.id}')">
                    <div class="email-item-header">
                        <div>
                            <div class="email-item-from">${email.sender}</div>
                            <div class="email-item-time">${timeAgo}</div>
                        </div>
                        ${priorityBadge}
                    </div>
                    <div class="email-item-subject">${email.subject}</div>
                    <div class="email-item-preview">${email.body.substring(0, 80)}</div>
                    <div class="email-item-meta">
                        <span class="status-badge ${statusBadgeClass}">${email.status}</span>
                        ${email.category ? `<span class="email-item-badge" style="background-color: #3b82f6; color: white;">${email.category}</span>` : ''}
                    </div>
                </div>
            `;
        })
        .join('');
}

function getStatusBadgeClass(status) {
    const classes = {
        'processing': 'processing',
        'completed': 'completed',
        'awaiting_review': 'awaiting_review',
        'error': 'error',
    };
    return classes[status] || 'processing';
}

function getPriorityColor(priority) {
    if (priority >= 4) return '#ef4444'; // Red
    if (priority >= 3) return '#f59e0b'; // Amber
    return '#10b981'; // Green
}

function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
}

// ============================================
// Email Detail View
// ============================================

async function selectEmail(emailId) {
    selectedEmailId = emailId;
    try {
        const response = await fetch(`${API_BASE}/emails/${emailId}`);
        if (!response.ok) throw new Error('Failed to load email details');

        const email = await response.json();
        renderEmailDetail(email);
        detailSection.style.display = 'block';
        detailSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (error) {
        console.error('Error loading email detail:', error);
        alert('Failed to load email details: ' + error.message);
    }
}

function closeDetail() {
    detailSection.style.display = 'none';
    selectedEmailId = null;
}

function renderEmailDetail(email) {
    // Header
    document.getElementById('detail-subject').textContent = email.subject;
    document.getElementById('detail-from').textContent = email.sender;
    document.getElementById('detail-received').textContent = new Date(email.received_at).toLocaleString();

    // Status
    const statusElement = document.getElementById('detail-status');
    statusElement.className = `status-badge ${getStatusBadgeClass(email.status)}`;
    statusElement.textContent = email.status;

    // Body
    document.getElementById('detail-body').textContent = email.body;

    // Classification
    document.getElementById('detail-intent').textContent = email.intent || '-';
    document.getElementById('detail-category').textContent = email.category || '-';
    const priorityElement = document.getElementById('detail-priority');
    if (email.priority) {
        priorityElement.className = `priority-badge ${email.priority >= 4 ? 'high' : email.priority >= 3 ? 'medium' : 'low'}`;
        priorityElement.textContent = `${email.priority}/5`;
    } else {
        priorityElement.textContent = '-';
    }

    // KB Results
    const kbSection = document.getElementById('kb-results');
    if (email.kb_results && email.kb_results.length > 0) {
        kbSection.innerHTML = email.kb_results
            .map(result => `
                <div class="kb-result">
                    <div class="kb-result-header">
                        <span class="kb-result-id">${result.id}</span>
                        <span class="kb-result-score">Score: ${(result._similarity_score || 0).toFixed(3)}</span>
                    </div>
                    <span class="kb-result-category">${result.category}</span>
                    <div class="kb-result-content">${result.content.substring(0, 200)}...</div>
                </div>
            `)
            .join('');
    } else {
        kbSection.innerHTML = '<p class="loading-text">No KB results available</p>';
    }

    // Draft Response
    if (email.draft_response) {
        document.getElementById('detail-draft').textContent = email.draft_response;
    } else {
        document.getElementById('detail-draft').textContent = 'No draft available';
    }

    // Final Response
    const finalResponseSection = document.getElementById('final-response-section');
    if (email.final_response) {
        document.getElementById('detail-final').textContent = email.final_response;
        finalResponseSection.style.display = 'block';
    } else {
        finalResponseSection.style.display = 'none';
    }

    // Follow-up
    const followupSection = document.getElementById('followup-section');
    if (email.follow_up_date) {
        document.getElementById('detail-followup').innerHTML = `
            <div class="detail-row">
                <span class="label">Scheduled for:</span>
                <span>${new Date(email.follow_up_date).toLocaleString()}</span>
            </div>
            <div class="detail-row">
                <span class="label">Status:</span>
                <span>Follow-up scheduled</span>
            </div>
        `;
        followupSection.style.display = 'block';
    } else {
        followupSection.style.display = 'none';
    }

    // Human Review
    const reviewSection = document.getElementById('review-section');
    if (email.status === 'awaiting_review') {
        document.getElementById('review-info').innerHTML = `
            <p>This email requires human review due to high priority or sensitive content.</p>
            <div class="detail-row">
                <span class="label">Reason:</span>
                <span>${email.priority >= 4 ? 'High priority (≥4)' : 'Sensitive category'}</span>
            </div>
        `;
        reviewSection.style.display = 'block';
    } else {
        reviewSection.style.display = 'none';
    }
}

// ============================================
// Review Actions
// ============================================

async function handleApprove() {
    if (!selectedEmailId) return;

    try {
        const response = await fetch(`${API_BASE}/review/${selectedEmailId}/approve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to approve');
        }

        alert('✓ Email approved and sent!');
        closeDetail();
        loadEmails();
    } catch (error) {
        alert('✗ Error: ' + error.message);
    }
}

async function handleReject() {
    if (!selectedEmailId) return;

    const reason = prompt('Reason for rejection:');
    if (reason === null) return;

    try {
        const response = await fetch(`${API_BASE}/review/${selectedEmailId}/reject`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reason }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to reject');
        }

        alert('✓ Email rejected');
        closeDetail();
        loadEmails();
    } catch (error) {
        alert('✗ Error: ' + error.message);
    }
}
