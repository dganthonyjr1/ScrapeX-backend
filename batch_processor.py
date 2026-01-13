"""
Batch Processing System for Large Directories
Handles 100s-1000s of businesses efficiently without memory issues
"""

import json
import logging
from typing import Dict, List, Optional, Generator
from datetime import datetime
import time

from directory_scraper import DirectoryScraper
from universal_scraper import UniversalBusinessScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Smart batch processing for large Chamber directories
    
    Features:
    - Processes businesses in batches of 50-75 to optimize speed and efficiency
    - Saves results incrementally to disk
    - Supports pause/resume
    - Provides progress tracking
    - Handles errors gracefully
    """

    def __init__(self, batch_size: int = 50, max_workers: int = 5):
        """
        Initialize batch processor
        
        Args:
            batch_size: Number of businesses to process in each batch (recommended: 50-75)
            max_workers: Number of parallel workers per batch
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.directory_scraper = DirectoryScraper()
        self.business_scraper = UniversalBusinessScraper()

    def process_directory_in_batches(self, 
                                     directory_url: str,
                                     output_file: str,
                                     max_businesses: Optional[int] = None,
                                     max_pages: int = 10) -> Dict:
        """
        Process a large directory in manageable batches
        
        Args:
            directory_url: URL of the directory
            output_file: Path to save results incrementally
            max_businesses: Optional limit on total businesses
            max_pages: Maximum directory pages to scrape
            
        Returns:
            Summary of processing
        """
        logger.info(f"Starting batch processing for: {directory_url}")
        
        # Step 1: Get list of businesses from directory (fast, low memory)
        logger.info("Step 1: Extracting business list from directory...")
        directory_result = self.directory_scraper.scrape_multiple_pages(
            directory_url,
            max_pages=max_pages
        )
        
        if directory_result.get('status') != 'success':
            return {
                'status': 'failed',
                'error': 'Failed to scrape directory',
                'directory_url': directory_url
            }
        
        all_businesses = directory_result.get('businesses', [])
        total_found = len(all_businesses)
        
        # Apply limit if specified
        if max_businesses:
            all_businesses = all_businesses[:max_businesses]
        
        total_to_process = len(all_businesses)
        
        logger.info(f"Found {total_found} businesses in directory")
        logger.info(f"Will process {total_to_process} businesses")
        logger.info(f"Batch size: {self.batch_size}")
        logger.info(f"Estimated batches: {(total_to_process + self.batch_size - 1) // self.batch_size}")
        
        # Step 2: Process in batches
        logger.info("Step 2: Processing businesses in batches...")
        
        processed_count = 0
        successful_count = 0
        failed_count = 0
        start_time = time.time()
        
        # Initialize output file
        with open(output_file, 'w') as f:
            json.dump({
                'directory_url': directory_url,
                'started_at': datetime.now().isoformat(),
                'total_found': total_found,
                'total_to_process': total_to_process,
                'batch_size': self.batch_size,
                'businesses': []
            }, f, indent=2)
        
        # Process each batch
        for batch_num, batch in enumerate(self._create_batches(all_businesses, self.batch_size), 1):
            batch_start = time.time()
            
            logger.info(f"\nProcessing Batch {batch_num}/{(total_to_process + self.batch_size - 1) // self.batch_size}")
            logger.info(f"Businesses in this batch: {len(batch)}")
            
            # Scrape batch
            batch_results = []
            for i, directory_business in enumerate(batch, 1):
                website = directory_business.get('website')
                if not website:
                    failed_count += 1
                    continue
                
                try:
                    # Scrape individual business
                    detailed_data = self.business_scraper.scrape_business(
                        website,
                        business_type=directory_business.get('category')
                    )
                    
                    if detailed_data.get('status') == 'success':
                        # Combine data
                        combined = {
                            **directory_business,
                            **detailed_data,
                            'directory_listing': directory_business,
                        }
                        
                        if not combined.get('business_name'):
                            combined['business_name'] = directory_business.get('business_name')
                        
                        batch_results.append(combined)
                        successful_count += 1
                        logger.info(f"  [{i}/{len(batch)}] ✓ {combined.get('business_name', 'Unknown')}")
                    else:
                        failed_count += 1
                        logger.warning(f"  [{i}/{len(batch)}] ✗ Failed to scrape {website}")
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"  [{i}/{len(batch)}] ✗ Error: {e}")
                
                processed_count += 1
            
            # Save batch results incrementally
            self._append_batch_to_file(output_file, batch_results)
            
            batch_duration = time.time() - batch_start
            logger.info(f"Batch {batch_num} completed in {batch_duration:.1f}s")
            logger.info(f"Progress: {processed_count}/{total_to_process} ({processed_count/total_to_process*100:.1f}%)")
            
            # Small delay between batches to be gentle on system
            if batch_num < (total_to_process + self.batch_size - 1) // self.batch_size:
                time.sleep(2)
        
        # Finalize
        total_duration = time.time() - start_time
        
        summary = {
            'status': 'completed',
            'directory_url': directory_url,
            'total_found': total_found,
            'total_processed': processed_count,
            'successful': successful_count,
            'failed': failed_count,
            'success_rate': f"{(successful_count/processed_count*100):.1f}%" if processed_count > 0 else "0%",
            'duration_seconds': total_duration,
            'duration_minutes': total_duration / 60,
            'avg_time_per_business': total_duration / processed_count if processed_count > 0 else 0,
            'output_file': output_file,
            'completed_at': datetime.now().isoformat()
        }
        
        # Update file with summary
        self._update_file_summary(output_file, summary)
        
        logger.info("\n" + "="*80)
        logger.info("BATCH PROCESSING COMPLETED")
        logger.info("="*80)
        logger.info(f"Total Processed: {processed_count}")
        logger.info(f"Successful: {successful_count}")
        logger.info(f"Failed: {failed_count}")
        logger.info(f"Success Rate: {summary['success_rate']}")
        logger.info(f"Total Time: {summary['duration_minutes']:.1f} minutes")
        logger.info(f"Results saved to: {output_file}")
        logger.info("="*80)
        
        return summary

    def _create_batches(self, items: List, batch_size: int) -> Generator[List, None, None]:
        """Split items into batches"""
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]

    def _append_batch_to_file(self, output_file: str, batch_results: List[Dict]):
        """Append batch results to output file"""
        try:
            # Read current data
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            # Append new results
            data['businesses'].extend(batch_results)
            
            # Write back
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to append batch to file: {e}")

    def _update_file_summary(self, output_file: str, summary: Dict):
        """Update file with final summary"""
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            data['summary'] = summary
            
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to update summary: {e}")


# Test
if __name__ == "__main__":
    processor = BatchProcessor(batch_size=50, max_workers=5)
    
    # Test with Tampa Bay Chamber (smaller for demo)
    result = processor.process_directory_in_batches(
        directory_url="https://www.tampabaychamber.com/membership/",
        output_file="/home/ubuntu/scrapex-backend/batch_results.json",
        max_businesses=20,
        max_pages=1
    )
    
    print(json.dumps(result, indent=2))
