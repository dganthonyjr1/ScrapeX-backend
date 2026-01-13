"""
ScrapeX Backend API
FastAPI application for healthcare facility scraping, analysis, and autonomous calling
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import json
import logging
import os

from universal_scraper import UniversalBusinessScraper
from directory_scraper import DirectoryScraper
from integrated_scraper import IntegratedScrapingPipeline
from ai_analysis_engine import HealthcareAIAnalyzer
from autonomous_caller import AutonomousCallManager
from human_ai_caller import HumanAICaller

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
scraper = UniversalBusinessScraper()
directory_scraper = DirectoryScraper()
integrated_pipeline = IntegratedScrapingPipeline(max_workers=5)
analyzer = HealthcareAIAnalyzer()
call_manager = AutonomousCallManager()
human_caller = HumanAICaller()

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
            "health": "/health"
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
    
    Args:
        request: DirectoryScrapeRequest with directory URL
        
    Returns:
        Job ID for tracking
    """
    try:
        job_id = generate_job_id()
        
        # Create job record
        jobs_db[job_id] = {
            'id': job_id,
            'type': 'directory_scrape',
            'status': 'processing',
            'created_at': datetime.now().isoformat(),
            'directory_url': request.directory_url,
            'max_businesses': request.max_businesses,
            'max_pages': request.max_pages,
            'result': None,
            'error': None
        }
        
        # Process in background
        background_tasks.add_task(
            _process_directory_scrape_job,
            job_id,
            request.directory_url,
            request.max_businesses,
            request.max_pages
        )
        
        return {
            'job_id': job_id,
            'status': 'processing',
            'message': f'Directory scraping job started for {request.directory_url}'
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


# Background task functions
async def _process_scrape_job(job_id: str, url: str, business_type: Optional[str] = None):
    """Process scrape job in background"""
    try:
        result = scraper.scrape_business(url, business_type)
        jobs_db[job_id]['status'] = 'completed'
        jobs_db[job_id]['result'] = result
        logger.info(f"Scrape job {job_id} completed")
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
    """Process directory scrape job in background"""
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
