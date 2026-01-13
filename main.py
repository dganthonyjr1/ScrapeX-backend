"""
ScrapeX Backend API
FastAPI application for healthcare facility scraping, analysis, and autonomous calling
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import json
import logging
import os
import requests

from universal_scraper import UniversalBusinessScraper
from directory_scraper import DirectoryScraper
from integrated_scraper import IntegratedScrapingPipeline
from batch_processor import BatchProcessor
from supabase_manager import db_manager
from resource_manager import resource_manager
from ai_analysis_engine import HealthcareAIAnalyzer
from autonomous_caller import AutonomousCallManager
from human_ai_caller import HumanAICaller
from multilingual_caller import MultilingualAICaller
from retell_webhook_handler import webhook_handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ScrapeX Universal Business API",
    description="API for scraping, analyzing, and calling ANY business type",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
# Version: 2.0 - Automated Calling with Universal Scraper
scraper = UniversalBusinessScraper()
directory_scraper = DirectoryScraper()
integrated_pipeline = IntegratedScrapingPipeline(max_workers=5)
batch_processor = BatchProcessor(batch_size=50, max_workers=5)
analyzer = HealthcareAIAnalyzer()
call_manager = AutonomousCallManager()
human_caller = HumanAICaller()
multilingual_caller = MultilingualAICaller()

# Request/Response models
class ScrapeRequest(BaseModel):
    """Request to scrape any business"""
    url: str
    business_name: Optional[str] = None
    business_type: Optional[str] = None

class BulkScrapeRequest(BaseModel):
    """Request to scrape multiple businesses"""
    urls: List[str]
    business_type: Optional[str] = None

class DirectoryScrapeRequest(BaseModel):
    """Request to scrape a business directory"""
    directory_url: str
    max_businesses: Optional[int] = None
    max_pages: int = 10
    use_batch_processing: bool = True
    batch_size: int = 50

class AnalysisRequest(BaseModel):
    """Request to analyze scraped business data"""
    business_data: Dict

class CallRequest(BaseModel):
    """Request to trigger an autonomous call"""
    facility_name: str
    phone_number: str
    analysis_data: Dict

class JobResponse(BaseModel):
    """Response for a job"""
    job_id: str
    status: str
    created_at: str
    data: Optional[Dict] = None


# In-memory job storage (in production, use database)
jobs_db = {}
job_counter = 0


def generate_job_id() -> str:
    """Generate unique job ID"""
    global job_counter
    job_counter += 1
    return f"job_{job_counter:06d}"


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "ScrapeX Universal Business API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "scrape": "/api/v1/scrape",
            "scrape_directory": "/api/v1/scrape-directory",
            "bulk_scrape": "/api/v1/bulk-scrape",
            "analyze": "/api/v1/analyze",
            "call": "/api/v1/call",
            "jobs": "/api/v1/jobs",
            "calls": "/api/v1/calls",
            "health": "/health",
            "note": "For large directories (100+ businesses), set use_batch_processing=true"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "scraper": "ready",
            "analyzer": "ready",
            "call_manager": "ready"
        }
    }


@app.post("/api/v1/scrape")
async def scrape_business(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Scrape a single business website (any type)
    
    Args:
        request: ScrapeRequest with URL and optional business type
        
    Returns:
        Job ID for tracking
    """
    try:
        job_id = generate_job_id()
        
        # Create job record
        jobs_db[job_id] = {
            'id': job_id,
            'type': 'scrape',
            'status': 'processing',
            'created_at': datetime.now().isoformat(),
            'url': request.url,
            'business_name': request.business_name,
            'business_type': request.business_type,
            'result': None,
            'error': None
        }
        
        # Process in background
        background_tasks.add_task(
            _process_scrape_job,
            job_id,
            request.url,
            request.business_type
        )
        
        return {
            'job_id': job_id,
            'status': 'processing',
            'message': 'Scraping job started'
        }
        
    except Exception as e:
        logger.error(f"Failed to start scrape job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/bulk-scrape")
async def bulk_scrape(request: BulkScrapeRequest, background_tasks: BackgroundTasks):
    """
    Scrape multiple businesses (any type)
    
    Args:
        request: BulkScrapeRequest with list of URLs
        
    Returns:
        Job ID for tracking
    """
    try:
        job_id = generate_job_id()
        
        # Create job record
        jobs_db[job_id] = {
            'id': job_id,
            'type': 'bulk_scrape',
            'status': 'processing',
            'created_at': datetime.now().isoformat(),
            'urls': request.urls,
            'total_urls': len(request.urls),
            'processed': 0,
            'results': [],
            'error': None
        }
        
        # Process in background
        background_tasks.add_task(
            _process_bulk_scrape_job,
            job_id,
            request.urls,
            request.business_type
        )
        
        return {
            'job_id': job_id,
            'status': 'processing',
            'message': f'Bulk scraping job started for {len(request.urls)} URLs'
        }
        
    except Exception as e:
        logger.error(f"Failed to start bulk scrape job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/scrape-directory")
async def scrape_directory(request: DirectoryScrapeRequest, background_tasks: BackgroundTasks):
    """
    Scrape a business directory (Chamber of Commerce, tourism sites, etc.)
    
    SAFETY FEATURES:
    - Rate limiting: Max 5 concurrent jobs per user
    - Batch size capped at 50 businesses
    - Job timeout: 30 minutes
    - Results stored in database
    
    Args:
        request: DirectoryScrapeRequest with directory URL
        
    Returns:
        Job ID for tracking
    """
    try:
        # TODO: Get user_id from auth token
        user_id = "demo_user"  # Replace with actual auth
        
        # Check rate limits
        limit_check = resource_manager.check_can_start_job(user_id)
        if not limit_check['can_start']:
            raise HTTPException(status_code=429, detail=limit_check['message'])
        
        # Validate and cap batch size
        batch_size = resource_manager.validate_batch_size(request.batch_size)
        
        # Generate job ID
        job_id = generate_job_id()
        
        # Register job with resource manager
        resource_manager.register_job(job_id, user_id)
        
        # Create job in database
        db_manager.create_job(
            job_id=job_id,
            user_id=user_id,
            job_type='directory_scrape',
            directory_url=request.directory_url,
            max_businesses=request.max_businesses,
            max_pages=request.max_pages,
            batch_size=batch_size
        )
        
        # Also store in memory for backward compatibility
        jobs_db[job_id] = {
            'id': job_id,
            'type': 'directory_scrape',
            'status': 'processing',
            'created_at': datetime.now().isoformat(),
            'directory_url': request.directory_url,
            'max_businesses': request.max_businesses,
            'max_pages': request.max_pages,
            'batch_size': batch_size,
            'result': None,
            'error': None
        }
        
        # Process in background
        background_tasks.add_task(
            _process_directory_scrape_job_safe,
            job_id,
            user_id,
            request.directory_url,
            request.max_businesses,
            request.max_pages,
            batch_size,
            request.use_batch_processing
        )
        
        return {
            'job_id': job_id,
            'status': 'processing',
            'message': f'Directory scraping job started for {request.directory_url}',
            'batch_size': batch_size,
            'estimated_time_minutes': (request.max_businesses or 50) / 5 if request.max_businesses else 10
        }
        
    except Exception as e:
        logger.error(f"Failed to start directory scrape job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analyze")
async def analyze_business(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """
    Analyze scraped business data for opportunities
    
    Args:
        request: AnalysisRequest with facility data
        
    Returns:
        Job ID for tracking
    """
    try:
        job_id = generate_job_id()
        
        # Create job record
        jobs_db[job_id] = {
            'id': job_id,
            'type': 'analysis',
            'status': 'processing',
            'created_at': datetime.now().isoformat(),
            'business_name': request.business_data.get('business_name'),
            'result': None,
            'error': None
        }
        
        # Process in background
        background_tasks.add_task(
            _process_analysis_job,
            job_id,
            request.business_data
        )
        
        return {
            'job_id': job_id,
            'status': 'processing',
            'message': 'Analysis job started'
        }
        
    except Exception as e:
        logger.error(f"Failed to start analysis job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/call")
async def trigger_call(request: CallRequest, background_tasks: BackgroundTasks):
    """
    Trigger an autonomous call to a healthcare facility
    
    Args:
        request: CallRequest with facility and phone info
        
    Returns:
        Call initiation response
    """
    try:
        # Generate call script
        script = analyzer.generate_call_script({
            'facility_name': request.facility_name,
            'analysis': request.analysis_data
        })
        
        # Trigger call
        result = call_manager.trigger_call(
            facility_name=request.facility_name,
            phone_number=request.phone_number,
            analysis=request.analysis_data,
            call_script=script
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to trigger call: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str):
    """
    Get job status and results
    
    Args:
        job_id: Job ID to retrieve
        
    Returns:
        Job status and results
    """
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs_db[job_id]


@app.get("/api/v1/jobs")
async def list_jobs(limit: int = 50):
    """
    List all jobs
    
    Args:
        limit: Maximum number of jobs to return
        
    Returns:
        List of jobs
    """
    jobs = list(jobs_db.values())
    return {
        'total': len(jobs),
        'jobs': jobs[-limit:]
    }


@app.get("/api/v1/calls")
async def get_calls(facility_name: Optional[str] = None):
    """
    Get call history
    
    Args:
        facility_name: Optional filter by facility name
        
    Returns:
        Call history
    """
    calls = call_manager.get_call_history(facility_name)
    stats = call_manager.get_call_statistics()
    
    return {
        'total_calls': len(calls),
        'statistics': stats,
        'calls': calls
    }


@app.get("/api/v1/calls/statistics")
async def get_call_statistics():
    """
    Get call statistics
    
    Returns:
        Call statistics and metrics
    """
    stats = call_manager.get_call_statistics()
    return stats


# Retell AI call function
async def _initiate_retell_call(business_name: str, phone_number: str) -> Dict:
    """Initiate a call via Retell AI"""
    retell_api_key = os.getenv('RETELL_API_KEY')
    agent_id = os.getenv('RETELL_AGENT_ID', 'agent_05e8f725879b2997086400e39f')
    from_number = os.getenv('RETELL_FROM_NUMBER', '+16099084403')
    
    headers = {
        'Authorization': f'Bearer {retell_api_key}',
        'Content-Type': 'application/json'
    }
    
    call_config = {
        'agent_id': agent_id,
        'from_number': from_number,
        'to_number': phone_number,
        'metadata': {
            'business_name': business_name,
            'source': 'automated_scrape',
            'timestamp': datetime.now().isoformat()
        }
    }
    
    response = requests.post(
        'https://api.retellai.com/v2/create-phone-call',
        headers=headers,
        json=call_config
    )
    
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Retell API error: {response.status_code} - {response.text}")


# Background task functions
async def _process_scrape_job(job_id: str, url: str, business_type: Optional[str] = None):
    """Process scrape job in background with automated calling"""
    try:
        # Scrape the business
        result = scraper.scrape_business(url, business_type)
        jobs_db[job_id]['status'] = 'completed'
        jobs_db[job_id]['result'] = result
        logger.info(f"Scrape job {job_id} completed")
        
        # Automatically initiate call if phone numbers found
        # Try both possible formats
        phone_numbers = result.get('contact_info', {}).get('phone_numbers', []) or result.get('phone', [])
        if phone_numbers:
            first_phone = phone_numbers[0]
            business_name = result.get('business_name', 'Unknown Business')
            
            logger.info(f"Initiating automated call to {first_phone} for {business_name}")
            
            # Initiate call via Retell AI
            try:
                call_result = await _initiate_retell_call(business_name, first_phone)
                jobs_db[job_id]['call_initiated'] = True
                jobs_db[job_id]['call_id'] = call_result.get('call_id')
                jobs_db[job_id]['call_phone'] = first_phone
                logger.info(f"Call initiated successfully: {call_result.get('call_id')}")
            except Exception as call_error:
                logger.error(f"Failed to initiate call: {str(call_error)}")
                jobs_db[job_id]['call_initiated'] = False
                jobs_db[job_id]['call_error'] = str(call_error)
        else:
            logger.warning(f"No phone numbers found for {url}, skipping automated call")
            jobs_db[job_id]['call_initiated'] = False
            jobs_db[job_id]['call_error'] = 'No phone numbers found'
            
    except Exception as e:
        jobs_db[job_id]['status'] = 'failed'
        jobs_db[job_id]['error'] = str(e)
        logger.error(f"Scrape job {job_id} failed: {str(e)}")


async def _process_bulk_scrape_job(job_id: str, urls: List[str], business_type: Optional[str] = None):
    """Process bulk scrape job in background"""
    try:
        results = scraper.scrape_multiple_businesses(urls)
        jobs_db[job_id]['status'] = 'completed'
        jobs_db[job_id]['results'] = results
        jobs_db[job_id]['processed'] = len(results)
        logger.info(f"Bulk scrape job {job_id} completed")
    except Exception as e:
        jobs_db[job_id]['status'] = 'failed'
        jobs_db[job_id]['error'] = str(e)
        logger.error(f"Bulk scrape job {job_id} failed: {str(e)}")


async def _process_directory_scrape_job(job_id: str, directory_url: str, 
                                        max_businesses: Optional[int] = None,
                                        max_pages: int = 10):
    """Process directory scrape job in background (legacy)"""
    try:
        result = integrated_pipeline.scrape_directory_and_businesses(
            directory_url,
            max_businesses=max_businesses,
            max_pages=max_pages
        )
        jobs_db[job_id]['status'] = 'completed'
        jobs_db[job_id]['result'] = result
        logger.info(f"Directory scrape job {job_id} completed - found {result.get('businesses_scraped', 0)} businesses")
    except Exception as e:
        jobs_db[job_id]['status'] = 'failed'
        jobs_db[job_id]['error'] = str(e)
        logger.error(f"Directory scrape job {job_id} failed: {str(e)}")


async def _process_directory_scrape_job_safe(job_id: str, user_id: str, directory_url: str,
                                            max_businesses: Optional[int] = None,
                                            max_pages: int = 10,
                                            batch_size: int = 50,
                                            use_batch_processing: bool = True):
    """Process directory scrape job with safety measures"""
    import time
    start_time = time.time()
    
    try:
        # Update job status
        db_manager.update_job(job_id, {'status': 'processing', 'started_at': datetime.now().isoformat()})
        jobs_db[job_id]['status'] = 'processing'
        
        # Check for timeout periodically
        if resource_manager.check_job_timeout(job_id):
            raise TimeoutError("Job exceeded 30 minute timeout")
        
        # Use batch processing for safety
        if use_batch_processing:
            logger.info(f"Using batch processing (batch_size={batch_size})")
            result = batch_processor.process_directory_in_batches(
                directory_url=directory_url,
                output_file=f"/tmp/job_{job_id}_results.json",
                max_businesses=max_businesses,
                max_pages=max_pages
            )
        else:
            logger.info("Using integrated pipeline")
            result = integrated_pipeline.scrape_directory_and_businesses(
                directory_url,
                max_businesses=max_businesses,
                max_pages=max_pages
            )
        
        # Save businesses to database
        if result.get('status') == 'success' or result.get('status') == 'completed':
            businesses = result.get('businesses', [])
            for business in businesses:
                db_manager.save_business(job_id, user_id, business)
        
        # Calculate stats
        duration = time.time() - start_time
        job_stats = resource_manager.get_job_stats(job_id)
        
        # Update job as completed
        db_manager.update_job(job_id, {
            'status': 'completed',
            'completed_at': datetime.now().isoformat(),
            'result': result,
            'processed_count': result.get('total_processed', 0),
            'successful_count': result.get('successful', 0),
            'failed_count': result.get('failed', 0),
            'duration_seconds': duration,
            'memory_used_mb': job_stats.get('memory_used_mb') if job_stats else None
        })
        
        jobs_db[job_id]['status'] = 'completed'
        jobs_db[job_id]['result'] = result
        
        logger.info(f"Directory scrape job {job_id} completed - {result.get('successful', 0)} businesses scraped in {duration:.1f}s")
        
    except TimeoutError as e:
        logger.error(f"Job {job_id} timed out: {str(e)}")
        db_manager.update_job(job_id, {'status': 'failed', 'error_message': str(e)})
        jobs_db[job_id]['status'] = 'failed'
        jobs_db[job_id]['error'] = str(e)
        
    except Exception as e:
        logger.error(f"Directory scrape job {job_id} failed: {str(e)}")
        db_manager.update_job(job_id, {'status': 'failed', 'error_message': str(e)})
        jobs_db[job_id]['status'] = 'failed'
        jobs_db[job_id]['error'] = str(e)
        
    finally:
        # Always unregister job to free up resources
        resource_manager.unregister_job(job_id)


async def _process_analysis_job(job_id: str, business_data: Dict):
    """Process analysis job in background"""
    try:
        result = analyzer.analyze_facility(business_data)
        jobs_db[job_id]['status'] = 'completed'
        jobs_db[job_id]['result'] = result
        logger.info(f"Analysis job {job_id} completed")
    except Exception as e:
        jobs_db[job_id]['status'] = 'failed'
        jobs_db[job_id]['error'] = str(e)
        logger.error(f"Analysis job {job_id} failed: {str(e)}")


@app.post("/api/v1/retell/webhook")
async def retell_webhook(request: dict):
    """
    Retell AI webhook endpoint for handling function calls and events
    
    This endpoint receives:
    - Function calls from the AI agent (e.g., send_payment_link)
    - Call lifecycle events (started, ended)
    
    Args:
        request: Webhook payload from Retell AI
        
    Returns:
        Response data for Retell AI
    """
    try:
        event_type = request.get("event")
        
        logger.info(f"Retell webhook received: {event_type}")
        
        if event_type == "function_call":
            # Handle function calls from the agent
            function_name = request.get("function_name")
            parameters = request.get("parameters", {})
            call_data = request.get("call", {})
            
            logger.info(f"Function call: {function_name} with params: {parameters}")
            
            result = webhook_handler.handle_function_call(
                function_name=function_name,
                parameters=parameters,
                call_data=call_data
            )
            
            return {
                "response": result.get("message", "Function executed"),
                "success": result.get("success", True)
            }
            
        elif event_type == "call_started":
            result = webhook_handler.handle_call_started(request.get("call", {}))
            return result
            
        elif event_type == "call_ended":
            result = webhook_handler.handle_call_ended(request.get("call", {}))
            return result
            
        else:
            logger.warning(f"Unknown webhook event: {event_type}")
            return {"status": "unknown_event"}
            
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chamber-partnership")
async def chamber_partnership():
    """Serve the Chamber & Tourism partnership page"""
    import os
    file_path = os.path.join(os.path.dirname(__file__), "static", "chamber-partnership.html")
    return FileResponse(file_path)

# Mount static files after all routes
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    pass  # Static files may not exist in all environments


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


@app.post("/api/v1/import-urls")
async def import_urls(google_sheets_url: Optional[str] = None):
    """
    Import URLs from Google Sheets
    
    Args:
        google_sheets_url: Google Sheets share URL
        
    Returns:
        List of extracted URLs
    """
    try:
        import re
        
        if not google_sheets_url:
            raise HTTPException(status_code=400, detail="Google Sheets URL required")
        
        # Extract sheet ID
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', google_sheets_url)
        if not match:
            raise HTTPException(status_code=400, detail="Invalid Google Sheets URL")
        
        sheet_id = match.group(1)
        csv_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
        
        # Fetch CSV
        response = requests.get(csv_url, timeout=10)
        response.raise_for_status()
        
        # Extract URLs
        urls = []
        for line in response.text.split('\n'):
            # Find all URLs in the line
            found_urls = re.findall(r'https?://[^\s,;"\'<>]+', line)
            urls.extend(found_urls)
        
        # Remove duplicates and clean
        urls = list(set([url.strip() for url in urls if url.strip()]))
        
        logger.info(f"Imported {len(urls)} URLs from Google Sheets")
        
        return {
            'success': True,
            'urls': urls,
            'count': len(urls),
            'message': f'Successfully imported {len(urls)} URLs'
        }
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=400,
                detail="Google Sheet not found or not publicly accessible. Make sure it's set to 'Anyone with the link can view'"
            )
        raise HTTPException(status_code=400, detail=f"Failed to fetch Google Sheet: {str(e)}")
    
    except Exception as e:
        logger.error(f"Failed to import URLs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
