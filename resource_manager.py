"""
Resource Manager for ScrapeX
Handles rate limiting, job timeouts, and memory management
"""

import time
import psutil
import os
import logging
import signal
from typing import Dict, Optional
from functools import wraps
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResourceManager:
    """
    Manages system resources and prevents overload
    
    Features:
    - Rate limiting per user
    - Concurrent job limits
    - Memory monitoring
    - Job timeouts
    - Automatic cleanup
    """

    # Configuration
    MAX_CONCURRENT_JOBS_PER_USER = 5
    MAX_BATCH_SIZE = 50
    JOB_TIMEOUT_SECONDS = 1800  # 30 minutes
    MEMORY_LIMIT_MB = 400  # Alert if job uses more than 400MB
    CLEANUP_INTERVAL_SECONDS = 300  # 5 minutes

    def __init__(self):
        """Initialize resource manager"""
        self.active_jobs = {}  # job_id -> {user_id, start_time, memory_start}
        self.user_job_counts = {}  # user_id -> count
        self.last_cleanup = time.time()

    def check_can_start_job(self, user_id: str) -> Dict:
        """
        Check if user can start a new job
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with can_start and message
        """
        # Clean up old jobs first
        self._cleanup_old_jobs()
        
        # Check user's concurrent job limit
        user_jobs = self.user_job_counts.get(user_id, 0)
        
        if user_jobs >= self.MAX_CONCURRENT_JOBS_PER_USER:
            return {
                'can_start': False,
                'message': f'Maximum concurrent jobs limit reached ({self.MAX_CONCURRENT_JOBS_PER_USER}). Please wait for existing jobs to complete.',
                'active_jobs': user_jobs
            }
        
        # Check system memory
        memory = psutil.virtual_memory()
        if memory.percent > 85:
            return {
                'can_start': False,
                'message': 'System is currently under heavy load. Please try again in a few minutes.',
                'memory_usage': f'{memory.percent}%'
            }
        
        return {
            'can_start': True,
            'message': 'OK',
            'active_jobs': user_jobs
        }

    def register_job(self, job_id: str, user_id: str):
        """
        Register a new job
        
        Args:
            job_id: Job identifier
            user_id: User identifier
        """
        process = psutil.Process(os.getpid())
        
        self.active_jobs[job_id] = {
            'user_id': user_id,
            'start_time': time.time(),
            'memory_start': process.memory_info().rss / 1024 / 1024  # MB
        }
        
        self.user_job_counts[user_id] = self.user_job_counts.get(user_id, 0) + 1
        
        logger.info(f"Registered job {job_id} for user {user_id}. User now has {self.user_job_counts[user_id]} active jobs.")

    def unregister_job(self, job_id: str):
        """
        Unregister a completed job
        
        Args:
            job_id: Job identifier
        """
        if job_id in self.active_jobs:
            job_info = self.active_jobs[job_id]
            user_id = job_info['user_id']
            
            # Calculate stats
            duration = time.time() - job_info['start_time']
            process = psutil.Process(os.getpid())
            memory_end = process.memory_info().rss / 1024 / 1024
            memory_used = memory_end - job_info['memory_start']
            
            logger.info(f"Job {job_id} completed. Duration: {duration:.1f}s, Memory used: {memory_used:.1f}MB")
            
            # Update counts
            del self.active_jobs[job_id]
            if user_id in self.user_job_counts:
                self.user_job_counts[user_id] = max(0, self.user_job_counts[user_id] - 1)
                if self.user_job_counts[user_id] == 0:
                    del self.user_job_counts[user_id]
            
            return {
                'duration_seconds': duration,
                'memory_used_mb': memory_used
            }
        
        return {}

    def get_job_stats(self, job_id: str) -> Optional[Dict]:
        """Get current stats for a job"""
        if job_id not in self.active_jobs:
            return None
        
        job_info = self.active_jobs[job_id]
        process = psutil.Process(os.getpid())
        memory_current = process.memory_info().rss / 1024 / 1024
        
        return {
            'user_id': job_info['user_id'],
            'duration_seconds': time.time() - job_info['start_time'],
            'memory_used_mb': memory_current - job_info['memory_start']
        }

    def check_job_timeout(self, job_id: str) -> bool:
        """
        Check if job has exceeded timeout
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if job has timed out
        """
        if job_id not in self.active_jobs:
            return False
        
        job_info = self.active_jobs[job_id]
        duration = time.time() - job_info['start_time']
        
        if duration > self.JOB_TIMEOUT_SECONDS:
            logger.warning(f"Job {job_id} exceeded timeout ({duration:.1f}s > {self.JOB_TIMEOUT_SECONDS}s)")
            return True
        
        return False

    def validate_batch_size(self, batch_size: int) -> int:
        """
        Validate and cap batch size
        
        Args:
            batch_size: Requested batch size
            
        Returns:
            Validated batch size (capped at MAX_BATCH_SIZE)
        """
        if batch_size > self.MAX_BATCH_SIZE:
            logger.warning(f"Batch size {batch_size} exceeds limit. Capping at {self.MAX_BATCH_SIZE}")
            return self.MAX_BATCH_SIZE
        return batch_size

    def _cleanup_old_jobs(self):
        """Remove jobs that have been active too long"""
        current_time = time.time()
        
        # Only cleanup every CLEANUP_INTERVAL_SECONDS
        if current_time - self.last_cleanup < self.CLEANUP_INTERVAL_SECONDS:
            return
        
        self.last_cleanup = current_time
        
        jobs_to_remove = []
        for job_id, job_info in self.active_jobs.items():
            duration = current_time - job_info['start_time']
            if duration > self.JOB_TIMEOUT_SECONDS:
                logger.warning(f"Cleaning up timed out job {job_id}")
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            self.unregister_job(job_id)

    def get_system_stats(self) -> Dict:
        """Get current system resource usage"""
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        
        return {
            'memory_percent': memory.percent,
            'memory_available_mb': memory.available / 1024 / 1024,
            'cpu_percent': cpu,
            'active_jobs': len(self.active_jobs),
            'active_users': len(self.user_job_counts)
        }


def with_timeout(timeout_seconds: int):
    """
    Decorator to add timeout to functions
    
    Args:
        timeout_seconds: Timeout in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function {func.__name__} exceeded timeout of {timeout_seconds}s")
            
            # Set timeout alarm
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
            
            try:
                result = func(*args, **kwargs)
            finally:
                # Disable alarm
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
            
            return result
        return wrapper
    return decorator


# Global instance
resource_manager = ResourceManager()
