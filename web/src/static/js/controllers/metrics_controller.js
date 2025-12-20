function display_metrics_by_commit_id(repository_id, branch_id, commit_id, include_complexity, include_identifiable_identities, include_code_duplication) {
    return fetch(DISPLAY_METRICS_BY_COMMIT_ID, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            repository_id: repository_id,
            branch_id: branch_id,
            commit_id: commit_id,
            include_complexity: include_complexity,
            include_identifiable_identities: include_identifiable_identities,
            include_code_duplication: include_code_duplication,
        })
    })
    .then(async response => {
        if (!response.ok) {
            const err = new Error(`HTTP error! Status: ${response.status}`);
            err.status = response.status;
            throw err;
        }
        return response.json();
    })
    .then(data => {
        // Check if we got a task_id (new async mode)
        if (data.task_id) {
            return new Promise((resolve, reject) => {
                // Show progress modal
                showProgressModal('Calculating Metrics');
                
                // Create task tracker
                const tracker = new TaskTracker(data.task_id);
                
                // Set up handlers
                tracker.onProgress = (taskData) => {
                    updateProgressModal(taskData);
                };
                
                tracker.onComplete = (result) => {
                    tracker.stop();
                    hideProgressModal();
                    resolve(result);
                };
                
                tracker.onError = (error) => {
                    tracker.stop();
                    hideProgressModal();
                    reject(new Error(error));
                };
                
                // Handle cancel button
                const cancelBtn = document.getElementById('cancel-task-btn');
                const handleCancel = async () => {
                    if (await tracker.cancel()) {
                        tracker.stop();
                        hideProgressModal();
                        reject(new Error('Cancelled by user'));
                    }
                };
                
                if (cancelBtn) {
                    cancelBtn.addEventListener('click', handleCancel, { once: true });
                }
                
                // Start tracking (try SSE first, fallback to polling)
                tracker.startSSE();
            });
        } else {
            // Old synchronous response - return directly
            return data;
        }
    });
}