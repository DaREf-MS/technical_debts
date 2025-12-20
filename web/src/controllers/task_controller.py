"""
Controller for task management and Server-Sent Events (SSE) for progress tracking.
"""
from flask import Response, jsonify, stream_with_context
import json

from src.app import app
from src.services.task_manager import task_manager, DateTimeEncoder


@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get the current status of a task."""
    
    task = task_manager.get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task.to_dict())


@app.route('/api/task/<task_id>/stream', methods=['GET'])
def stream_task_progress(task_id):
    """Server-Sent Events endpoint for streaming task progress updates."""
    task = task_manager.get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    def generate():
        """Generator function for SSE."""
        # Send initial task state
        yield f"data: {json.dumps(task.to_dict(), cls=DateTimeEncoder)}\n\n"
        
        # Stream updates
        for update in task_manager.get_task_updates(task_id, timeout=30.0):
            if update["type"] == "heartbeat":
                # Send heartbeat to keep connection alive
                yield f": heartbeat\n\n"
            elif update["type"] == "update":
                # Send actual update
                yield f"data: {json.dumps(update['data'], cls=DateTimeEncoder)}\n\n"
        
        # Ensure we send a final update
        final_task = task_manager.get_task(task_id)
        if final_task:
            yield f"data: {json.dumps(final_task.to_dict(), cls=DateTimeEncoder)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',  # Disable nginx buffering
            'Connection': 'keep-alive'
        }
    )


@app.route('/api/task/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """Cancel a running task (mark as cancelled, actual cancellation depends on implementation)."""
    task = task_manager.get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    if task.status in ["completed", "failed"]:
        return jsonify({"error": "Task already finished"}), 400
    
    task_manager.fail_task(task_id, "Cancelled by user")
    return jsonify({"message": "Task cancelled"})
