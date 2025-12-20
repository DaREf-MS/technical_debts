// Task tracking utilities for long-running operations

class TaskTracker {
    constructor(taskId) {
        this.taskId = taskId;
        this.eventSource = null;
        this.pollInterval = null;
        this.onProgress = null;
        this.onComplete = null;
        this.onError = null;
    }

    /**
     * Start tracking task progress using Server-Sent Events
     */
    startSSE() {
        if (!this.taskId) {
            console.error('No task ID provided');
            return;
        }

        this.eventSource = new EventSource(`/api/task/${this.taskId}/stream`);
        
        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleUpdate(data);
            } catch (e) {
                console.error('Error parsing SSE data:', e);
            }
        };

        this.eventSource.onerror = (error) => {
            console.error('SSE error:', error);
            this.stopSSE();
            
            // Fall back to polling
            this.startPolling();
        };
    }

    /**
     * Start polling for task status (fallback method)
     */
    startPolling(interval = 1000) {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }

        this.pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/task/${this.taskId}`);
                if (response.ok) {
                    const data = await response.json();
                    this.handleUpdate(data);
                } else {
                    console.error('Failed to fetch task status');
                }
            } catch (error) {
                console.error('Error polling task status:', error);
            }
        }, interval);
    }

    /**
     * Handle task update
     */
    handleUpdate(data) {
        if (data.status === 'completed') {
            if (this.onComplete) {
                this.onComplete(data.result);
            }
            this.stop();
        } else if (data.status === 'failed') {
            if (this.onError) {
                this.onError(data.error);
            }
            this.stop();
        } else if (data.status === 'running' || data.status === 'pending') {
            if (this.onProgress) {
                this.onProgress(data);
            }
        }
    }

    /**
     * Stop tracking
     */
    stop() {
        this.stopSSE();
        this.stopPolling();
    }

    stopSSE() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    /**
     * Cancel the task
     */
    async cancel() {
        try {
            const response = await fetch(`/api/task/${this.taskId}/cancel`, {
                method: 'POST'
            });
            if (response.ok) {
                this.stop();
                return true;
            }
        } catch (error) {
            console.error('Error cancelling task:', error);
        }
        return false;
    }
}

/**
 * Show a progress modal for a task
 */
function showProgressModal(title = 'Processing...') {
    // Remove existing modal if any
    const existingModal = document.getElementById('progress-modal');
    if (existingModal) {
        existingModal.remove();
    }

    const modalHTML = `
        <div class="modal fade" id="progress-modal" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <div class="progress" style="height: 25px;">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                     id="progress-bar" 
                                     role="progressbar" 
                                     style="width: 0%"
                                     aria-valuenow="0" 
                                     aria-valuemin="0" 
                                     aria-valuemax="100">0%</div>
                            </div>
                        </div>
                        <div id="progress-status" class="text-muted small">
                            <strong id="progress-step">Initializing...</strong>
                            <div id="progress-message" class="mt-1"></div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" id="cancel-task-btn">Cancel</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);
    const modal = new bootstrap.Modal(document.getElementById('progress-modal'));
    modal.show();

    return modal;
}

/**
 * Update progress modal
 */
function updateProgressModal(data) {
    const progressBar = document.getElementById('progress-bar');
    const progressStep = document.getElementById('progress-step');
    const progressMessage = document.getElementById('progress-message');

    if (progressBar) {
        progressBar.style.width = `${data.progress}%`;
        progressBar.setAttribute('aria-valuenow', data.progress);
        progressBar.textContent = `${data.progress}%`;
    }

    if (progressStep && data.current_step) {
        progressStep.textContent = data.current_step;
    }

    if (progressMessage && data.message) {
        progressMessage.textContent = data.message;
    }
}

/**
 * Hide progress modal
 */
function hideProgressModal() {
    const modalElement = document.getElementById('progress-modal');
    if (modalElement) {
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            modal.hide();
        }
        
        // Remove backdrop manually if it exists
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.remove();
        }
        
        // Remove modal-open class from body
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('overflow');
        document.body.style.removeProperty('padding-right');
        
        // Remove modal after hiding
        setTimeout(() => {
            modalElement.remove();
        }, 300);
    }
}
