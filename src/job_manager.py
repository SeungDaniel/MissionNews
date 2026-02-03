import threading
import queue
import time
import uuid
from datetime import datetime
import logging

class JobManager:
    def __init__(self):
        self.job_queue = queue.Queue()
        self.jobs = {} # job_id -> job_info
        self._shutdown_event = threading.Event()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        print("JobManager background thread started.")

    def add_job(self, job_type, title, task_func, **kwargs):
        """
        Add a job to the queue.
        :param job_type: 'testimony' or 'mission_news'
        :param title: Display title for the job
        :param task_func: Function to execute. Must accept (status_callback, log_callback) as kwargs or args.
        :param kwargs: Arguments to pass to task_func
        """
        job_id = str(uuid.uuid4())
        job_info = {
            'id': job_id,
            'type': job_type,
            'title': title,
            'task_func': task_func,
            'kwargs': kwargs,
            'submitted_at': datetime.now(),
            'status': 'queued', # queued, processing, completed, failed
            'progress': 0,
            'logs': [],
            'result': None,
            'error': None
        }
        self.jobs[job_id] = job_info
        self.job_queue.put(job_id)
        return job_id

    def _worker(self):
        while not self._shutdown_event.is_set():
            try:
                # Get job_id
                job_id = self.job_queue.get(timeout=1)
            except queue.Empty:
                continue

            job_info = self.jobs[job_id]
            job_info['status'] = 'processing'
            job_info['started_at'] = datetime.now()
            
            # Define callbacks to capture state
            def update_progress(current, total):
                if total > 0:
                    job_info['progress'] = int((current / total) * 100)
                else:
                    job_info['progress'] = 0
            
            def log_msg(msg):
                timestamp = datetime.now().strftime("%H:%M:%S")
                job_info['logs'].append(f"[{timestamp}] {msg}")

            def status_update(msg):
                 log_msg(f"STATUS: {msg}")

            try:
                # Execute the function
                # The task_func should accept specific callbacks if they are designed to support them
                # Adapting to our existing JobProcessor which expects (jobs, progress_callback)
                # But here we are processing ONE job at a time usually, or we wrap it.
                
                # We'll assume task_func is a wrapper that takes these callbacks.
                result = job_info['task_func'](
                    progress_callback=update_progress,
                    log_callback=log_msg,
                    status_callback=status_update,
                    **job_info['kwargs']
                )
                
                job_info['status'] = 'completed'
                job_info['result'] = result
                job_info['completed_at'] = datetime.now()
                job_info['progress'] = 100
                
            except Exception as e:
                job_info['status'] = 'failed'
                job_info['error'] = str(e)
                log_msg(f"CRITICAL ERROR: {e}")
            finally:
                self.job_queue.task_done()

    def get_all_jobs(self):
        return list(self.jobs.values())

    def get_job(self, job_id):
        return self.jobs.get(job_id)

    def clear_completed(self):
        """Remove completed or failed jobs to clean up memory"""
        keys_to_remove = [k for k, v in self.jobs.items() if v['status'] in ['completed', 'failed']]
        for k in keys_to_remove:
            del self.jobs[k]

# Singleton Pattern for Streamlit
# We will instantiate this in app.py using st.cache_resource

import streamlit as st

@st.cache_resource
def get_job_manager():
    return JobManager()
