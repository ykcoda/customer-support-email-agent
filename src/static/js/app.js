// Global state
let emails = [];
let selectedEmailId = null;

// DOM elements
const emailForm = document.getElementById('email-form');
const formMessage = document.getElementById('form-message');
const emailList = document.getElementById('email-list');
const detailSection = document.getElementById('detail-section');
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
    updateStats();
    // Auto-refresh every 3 seconds
    setInterval(() => {
        loadEmails();
        updateStats();
    }, 3000);
});

// ============================================
// Form Handling
// ============================================

function handleSubjectChange(e) {
    if (e.target.value === 'Custom message') {
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
    const subject = subjectSelect.value === 'Custom message'
        ? customSubjectInput.value
        : subjectSelect.value;
    const body = bodyTextarea.value;

    if (!subject || !body) {
        showMessage('Please fill in all fields', 'danger');
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
        setTimeout(() => {
            loadEmails();
            updateStats();
        }, 500);
    } catch (error) {
        showMessage(`✗ Error: ${error.message}`, 'danger');
    }
}

function showMessage(msg, type = 'info') {
    formMessage.textContent = msg;
    formMessage.className = `alert alert-${type} alert-dismissible fade show`;
    formMessage.style.display = 'block';

    if (type !== 'danger') {
        setTimeout(() => {
            formMessage.classList.remove('show');
            setTimeout(() => {
                formMessage.style.display = 'none';
            }, 150);
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
        updateStats();
    } catch (error) {
        console.error('Error loading emails:', error);
        emailList.innerHTML = `<div class="empty-state"><i class="bi bi-exclamation-triangle"></i><p>Error loading emails: ${error.message}</p></div>`;
    }
}

function renderEmailList() {
    if (emails.length === 0) {
        emailList.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-inbox"></i>
                <p>No emails yet. Send one to get started!</p>
            </div>
        `;
        document.getElementById('inbox-count').textContent = '0';
        return;
    }

    document.getElementById('inbox-count').textContent = emails.length;

    emailList.innerHTML = emails
        .sort((a, b) => new Date(b.received_at || b.created_at) - new Date(a.received_at || a.created_at))
        .map(email => {
            const statusClass = getStatusBadgeClass(email.status);
            const statusIcon = getStatusIcon(email.status);
            const priorityBadge = email.priority ? `<span class="badge priority-badge ${getPriorityClass(email.priority)}">P${email.priority}</span>` : '';
            const timeAgo = getTimeAgo(new Date(email.received_at || email.created_at));

            return `
                <div class="list-group-item email-item ${email.status === 'processing' ? 'unread' : ''}" onclick="selectEmail('${email.id || email.email_id}')">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div class="flex-grow-1">
                            <h6 class="mb-1 fw-600">${email.subject}</h6>
                            <small class="text-muted">${email.sender}</small>
                        </div>
                        ${priorityBadge}
                    </div>
                    <p class="mb-2 small text-muted">${email.body.substring(0, 80)}...</p>
                    <div class="d-flex gap-2 flex-wrap">
                        <span class="badge status-badge ${statusClass}">
                            ${statusIcon} ${formatStatus(email.status)}
                        </span>
                        ${email.category ? `<span class="badge bg-info">${email.category}</span>` : ''}
                        <small class="text-muted ms-auto">${timeAgo}</small>
                    </div>
                </div>
            `;
        })
        .join('');
}

function getStatusIcon(status) {
    const icons = {
        'processing': '<i class="bi bi-hourglass-split"></i>',
        'completed': '<i class="bi bi-check-circle"></i>',
        'awaiting_review': '<i class="bi bi-exclamation-circle"></i>',
        'error': '<i class="bi bi-x-circle"></i>',
        'pending': '<i class="bi bi-clock"></i>',
    };
    return icons[status] || '';
}

function getStatusBadgeClass(status) {
    const classes = {
        'processing': 'processing',
        'completed': 'completed',
        'awaiting_review': 'awaiting_review',
        'error': 'error',
        'pending': 'pending',
    };
    return classes[status] || 'pending';
}

function formatStatus(status) {
    const formats = {
        'processing': 'Processing',
        'completed': 'Completed',
        'awaiting_review': 'Review',
        'error': 'Error',
        'pending': 'Pending',
    };
    return formats[status] || status;
}

function getPriorityClass(priority) {
    if (priority >= 4) return 'high';
    if (priority >= 3) return 'medium';
    return 'low';
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
    const emailId = email.id || email.email_id;

    // Header
    document.getElementById('detail-subject').textContent = email.subject;
    document.getElementById('detail-from').textContent = email.sender;
    document.getElementById('detail-time').textContent = new Date(email.received_at || email.created_at).toLocaleString();

    // Status
    const statusElement = document.getElementById('detail-status');
    statusElement.className = `badge status-badge ${getStatusBadgeClass(email.status)}`;
    statusElement.innerHTML = `${getStatusIcon(email.status)} ${formatStatus(email.status)}`;

    // Priority & Category
    const priorityElement = document.getElementById('detail-priority');
    if (email.priority) {
        priorityElement.className = `badge priority-badge ${getPriorityClass(email.priority)}`;
        priorityElement.textContent = `${email.priority}/5`;
    } else {
        priorityElement.className = 'badge bg-secondary';
        priorityElement.textContent = '-';
    }

    const categoryElement = document.getElementById('detail-category');
    categoryElement.textContent = email.category || '-';

    // Body
    document.getElementById('detail-body').textContent = email.body;

    // Classification
    document.getElementById('detail-intent').textContent = email.intent || '-';
    document.getElementById('detail-category-text').textContent = email.category || '-';

    // KB Results
    const kbSection = document.getElementById('kb-results');
    if (email.kb_results && email.kb_results.length > 0) {
        kbSection.innerHTML = email.kb_results
            .map((result, idx) => `
                <div class="kb-result" style="animation: slideIn 0.3s ease ${idx * 0.1}s both;">
                    <div class="kb-result-header">
                        <span class="kb-result-id">${result.id}</span>
                        <span class="kb-result-score">
                            <i class="bi bi-lightning-charge"></i> ${(result._similarity_score || 0).toFixed(3)}
                        </span>
                    </div>
                    <span class="kb-result-category">${result.category}</span>
                    <div class="kb-result-content">${result.content.substring(0, 200)}...</div>
                </div>
            `)
            .join('');
    } else {
        kbSection.innerHTML = '<p class="text-muted small">No KB results available</p>';
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
            <div class="row g-2">
                <div class="col-md-6">
                    <div class="small text-muted mb-1">Scheduled Date</div>
                    <div class="fw-600">${new Date(email.follow_up_date).toLocaleString()}</div>
                </div>
                <div class="col-md-6">
                    <div class="small text-muted mb-1">Type</div>
                    <div class="fw-600">Follow-up</div>
                </div>
            </div>
        `;
        followupSection.style.display = 'block';
    } else {
        followupSection.style.display = 'none';
    }

    // Human Review
    const reviewSection = document.getElementById('review-section');
    if (email.status === 'awaiting_review') {
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

        showMessage('✓ Email approved and sent!', 'success');
        closeDetail();
        setTimeout(() => {
            loadEmails();
            updateStats();
        }, 1000);
    } catch (error) {
        showMessage(`✗ Error: ${error.message}`, 'danger');
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

        showMessage('✓ Email rejected', 'warning');
        closeDetail();
        setTimeout(() => {
            loadEmails();
            updateStats();
        }, 1000);
    } catch (error) {
        showMessage(`✗ Error: ${error.message}`, 'danger');
    }
}

// ============================================
// Statistics
// ============================================

function updateStats() {
    if (!emails || emails.length === 0) {
        updateStatElements(0, 0, 0, 0);
        return;
    }

    const completed = emails.filter(e => e.status === 'completed').length;
    const review = emails.filter(e => e.status === 'awaiting_review').length;
    const processing = emails.filter(e => e.status === 'processing').length;
    const total = emails.length;

    // Sidebar stats
    document.getElementById('stat-inbox').textContent = total;
    document.getElementById('stat-review').textContent = review;
    document.getElementById('stat-completed').textContent = completed;

    // Modal stats
    updateStatElements(total, completed, review, processing);
}

function updateStatElements(total, completed, review, processing) {
    document.getElementById('modal-total-emails').textContent = total;
    document.getElementById('modal-completed-emails').textContent = completed;
    document.getElementById('modal-review-emails').textContent = review;
    document.getElementById('modal-processing-emails').textContent = processing;
}

// ============================================
// Animations
// ============================================

const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);
