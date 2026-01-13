"""
Supabase Database Manager for ScrapeX
Handles job storage, results, and user usage tracking
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupabaseManager:
    """
    Manages all database operations for ScrapeX
    Stores jobs, results, and tracks user usage
    """

    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not supabase_url or not supabase_key:
            logger.warning("Supabase credentials not found. Database features disabled.")
            self.client = None
        else:
            self.client = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized")

    def create_job(self, job_id: str, user_id: str, job_type: str, **kwargs) -> Dict:
        """
        Create a new scraping job
        
        Args:
            job_id: Unique job identifier
            user_id: User who created the job
            job_type: Type of job (scrape, bulk_scrape, directory_scrape)
            **kwargs: Additional job parameters
            
        Returns:
            Created job record
        """
        if not self.client:
            return {'status': 'error', 'message': 'Database not available'}
        
        try:
            job_data = {
                'id': job_id,
                'user_id': user_id,
                'type': job_type,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                **kwargs
            }
            
            result = self.client.table('scraping_jobs').insert(job_data).execute()
            logger.info(f"Created job {job_id} for user {user_id}")
            return result.data[0] if result.data else job_data
            
        except Exception as e:
            logger.error(f"Failed to create job: {e}")
            return {'status': 'error', 'message': str(e)}

    def update_job(self, job_id: str, updates: Dict) -> Dict:
        """
        Update job status and progress
        
        Args:
            job_id: Job identifier
            updates: Fields to update
            
        Returns:
            Updated job record
        """
        if not self.client:
            return {'status': 'error', 'message': 'Database not available'}
        
        try:
            result = self.client.table('scraping_jobs').update(updates).eq('id', job_id).execute()
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Failed to update job {job_id}: {e}")
            return {'status': 'error', 'message': str(e)}

    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        if not self.client:
            return None
        
        try:
            result = self.client.table('scraping_jobs').select('*').eq('id', job_id).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None

    def get_user_jobs(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get all jobs for a user"""
        if not self.client:
            return []
        
        try:
            result = self.client.table('scraping_jobs')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to get user jobs: {e}")
            return []

    def save_business(self, job_id: str, user_id: str, business_data: Dict) -> Dict:
        """
        Save scraped business data
        
        Args:
            job_id: Associated job ID
            user_id: User who owns this data
            business_data: Business information
            
        Returns:
            Saved business record
        """
        if not self.client:
            return {'status': 'error', 'message': 'Database not available'}
        
        try:
            record = {
                'job_id': job_id,
                'user_id': user_id,
                'business_name': business_data.get('business_name'),
                'business_type': business_data.get('business_type'),
                'website': business_data.get('url') or business_data.get('website'),
                'phone': business_data.get('phone', []),
                'email': business_data.get('email', []),
                'address': business_data.get('address'),
                'description': business_data.get('description'),
                'owner_names': business_data.get('owner_info', {}).get('names', []),
                'owner_emails': business_data.get('owner_info', {}).get('emails', []),
                'owner_linkedin': business_data.get('owner_info', {}).get('linkedin', []),
                'services': business_data.get('services', []),
                'social_media': business_data.get('social_media', {}),
                'source_directory': business_data.get('directory_listing', {}).get('website'),
                'raw_data': business_data
            }
            
            result = self.client.table('scraped_businesses').insert(record).execute()
            return result.data[0] if result.data else record
            
        except Exception as e:
            logger.error(f"Failed to save business: {e}")
            return {'status': 'error', 'message': str(e)}

    def get_job_businesses(self, job_id: str) -> List[Dict]:
        """Get all businesses for a job"""
        if not self.client:
            return []
        
        try:
            result = self.client.table('scraped_businesses')\
                .select('*')\
                .eq('job_id', job_id)\
                .execute()
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to get job businesses: {e}")
            return []

    def check_user_limits(self, user_id: str) -> Dict:
        """
        Check if user has exceeded usage limits
        
        Returns:
            Dict with can_proceed, active_jobs, and limit info
        """
        if not self.client:
            return {'can_proceed': True, 'message': 'Limits not enforced (database unavailable)'}
        
        try:
            # Get or create user usage record
            result = self.client.table('user_usage').select('*').eq('user_id', user_id).execute()
            
            if not result.data:
                # Create new usage record
                self.client.table('user_usage').insert({
                    'user_id': user_id,
                    'active_jobs': 0,
                    'total_jobs_today': 0,
                    'total_businesses_scraped_today': 0
                }).execute()
                return {'can_proceed': True, 'active_jobs': 0, 'message': 'New user'}
            
            usage = result.data[0]
            
            # Check limits
            if usage['active_jobs'] >= usage['max_concurrent_jobs']:
                return {
                    'can_proceed': False,
                    'active_jobs': usage['active_jobs'],
                    'message': f"Maximum concurrent jobs limit reached ({usage['max_concurrent_jobs']})"
                }
            
            if usage['total_jobs_today'] >= usage['max_jobs_per_day']:
                return {
                    'can_proceed': False,
                    'total_jobs_today': usage['total_jobs_today'],
                    'message': f"Daily job limit reached ({usage['max_jobs_per_day']})"
                }
            
            return {
                'can_proceed': True,
                'active_jobs': usage['active_jobs'],
                'total_jobs_today': usage['total_jobs_today'],
                'message': 'Within limits'
            }
            
        except Exception as e:
            logger.error(f"Failed to check user limits: {e}")
            return {'can_proceed': True, 'message': 'Limit check failed, allowing'}

    def increment_user_usage(self, user_id: str):
        """Increment user's active jobs and daily count"""
        if not self.client:
            return
        
        try:
            self.client.rpc('increment_user_usage', {'p_user_id': user_id}).execute()
        except Exception as e:
            logger.error(f"Failed to increment usage: {e}")

    def decrement_active_jobs(self, user_id: str):
        """Decrement user's active jobs count"""
        if not self.client:
            return
        
        try:
            result = self.client.table('user_usage').select('active_jobs').eq('user_id', user_id).execute()
            if result.data:
                current = result.data[0]['active_jobs']
                self.client.table('user_usage')\
                    .update({'active_jobs': max(0, current - 1)})\
                    .eq('user_id', user_id)\
                    .execute()
        except Exception as e:
            logger.error(f"Failed to decrement active jobs: {e}")


# Global instance
db_manager = SupabaseManager()
