"""
Task manager for handling long-running operations with progress tracking.
"""
import uuid
import threading
from typing import Dict, Callable, Any
from datetime import datetime
import time
import queue
import json


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class Task:
    def __init__(self, task_id: str, task_type: str):
        self.task_id = task_id
        self.task_type = task_type
        self.status = "pending"  # pending, running, completed, failed
        self.progress = 0  # 0-100
        self.current_step = ""
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.message = ""

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "message": self.message
        }


class TaskManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TaskManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.tasks: Dict[str, Task] = {}
        self.task_queues: Dict[str, queue.Queue] = {}  # For SSE updates
        self._initialized = True

    def create_task(self, task_type: str) -> str:
        """Create a new task and return its ID."""
        task_id = str(uuid.uuid4())
        task = Task(task_id, task_type)
        self.tasks[task_id] = task
        self.task_queues[task_id] = queue.Queue()
        return task_id

    def get_task(self, task_id: str) -> Task:
        """Get task by ID."""
        task = self.tasks.get(task_id)
        return task

    def update_task(self, task_id: str, **kwargs):
        """Update task properties."""
        task = self.tasks.get(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            # Push update to SSE queue
            if task_id in self.task_queues:
                try:
                    self.task_queues[task_id].put_nowait(task.to_dict())
                except queue.Full:
                    pass  # Skip if queue is full

    def start_task(self, task_id: str):
        """Mark task as started."""
        self.update_task(
            task_id,
            status="running",
            started_at=datetime.now()
        )

    def complete_task(self, task_id: str, result: Any = None):
        """Mark task as completed with result."""
        # Store the actual result so it can be retrieved by the frontend
        self.update_task(
            task_id,
            status="completed",
            completed_at=datetime.now(),
            progress=100,
            result=result
        )

    def fail_task(self, task_id: str, error: str):
        """Mark task as failed with error."""
        self.update_task(
            task_id,
            status="failed",
            completed_at=datetime.now(),
            error=error
        )

    def update_progress(self, task_id: str, progress: int, current_step: str = "", message: str = ""):
        """Update task progress."""
        self.update_task(
            task_id,
            progress=min(100, max(0, progress)),
            current_step=current_step,
            message=message
        )

    def run_task_in_background(self, task_id: str, func: Callable, app=None, *args, **kwargs):
        """Run a task function in a background thread with Flask app context."""
        def wrapper():
            try:
                self.start_task(task_id)
                
                # Push Flask app context if provided
                if app:
                    with app.app_context():
                        result = func(task_id, *args, **kwargs)
                else:
                    result = func(task_id, *args, **kwargs)
                    
                self.complete_task(task_id, result)
            except Exception as e:
                print(f"Task {task_id} failed: {str(e)}")
                import traceback
                traceback.print_exc()
                self.fail_task(task_id, str(e))

        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()

    def get_task_updates(self, task_id: str, timeout: float = 30.0):
        """Generator for SSE updates. Yields task updates as they occur."""
        task_queue = self.task_queues.get(task_id)
        if not task_queue:
            return

        start_time = time.time()
        while True:
            try:
                # Check for timeout
                if time.time() - start_time > timeout:
                    # Send heartbeat
                    yield {"type": "heartbeat"}
                    start_time = time.time()
                
                # Get update from queue with timeout
                update = task_queue.get(timeout=1.0)
                yield {"type": "update", "data": update}
                
                # If task is completed or failed, stop
                if update.get("status") in ["completed", "failed"]:
                    break
                    
            except queue.Empty:
                # Send heartbeat to keep connection alive
                yield {"type": "heartbeat"}
                
                # Check if task is done
                task = self.get_task(task_id)
                if task and task.status in ["completed", "failed"]:
                    yield {"type": "update", "data": task.to_dict()}
                    break

    def cleanup_old_tasks(self, max_age_seconds: int = 3600):
        """Remove old completed/failed tasks."""
        current_time = datetime.now()
        to_remove = []
        
        for task_id, task in self.tasks.items():
            if task.status in ["completed", "failed"] and task.completed_at:
                age = (current_time - task.completed_at).total_seconds()
                if age > max_age_seconds:
                    to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.tasks[task_id]
            if task_id in self.task_queues:
                del self.task_queues[task_id]


# Global singleton instance
task_manager = TaskManager()
