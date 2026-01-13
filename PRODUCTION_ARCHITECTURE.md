# ScrapeX Production Architecture Recommendations

**Author:** Manus AI  
**Date:** January 13, 2026

## Current Situation Analysis

Your current setup uses Render's Starter plan with in-memory job storage. This works for testing but has critical limitations for production with multiple customers.

### Critical Issues to Address

**Memory Management:** When multiple customers scrape large directories simultaneously, the server will run out of memory and crash. Current in-memory storage cannot handle concurrent large jobs.

**No Job Persistence:** If the server restarts or crashes, all in-progress jobs are lost. Customers lose their data and have to start over.

**No Concurrency Control:** Multiple customers can trigger resource-intensive scraping jobs simultaneously, overwhelming the server.

**No Rate Limiting:** Without rate limiting, a single customer can monopolize all server resources, causing crashes for other customers.

## Recommended Production Architecture

### Architecture Overview

The production system should use a job queue architecture with persistent storage. This separates the API server from the processing workers, preventing crashes and enabling horizontal scaling.

| Component | Technology | Purpose |
|:----------|:-----------|:--------|
| **API Server** | FastAPI on Render | Receives requests, validates input, creates jobs |
| **Job Queue** | Redis (Upstash free tier) | Manages job queue, prevents overload |
| **Background Workers** | Celery workers | Process scraping jobs asynchronously |
| **Database** | Supabase (already set up) | Store job results, business data, user info |
| **File Storage** | Supabase Storage or S3 | Store CSV/JSON exports for large datasets |

### Why This Architecture

**Crash Prevention:** API server never does heavy processing. It only creates jobs and returns immediately. Workers process jobs independently. If a worker crashes, it does not affect the API or other workers.

**Scalability:** You can run multiple workers to handle more customers. Jobs are processed in order from the queue. Each customer gets fair processing time.

**Data Safety:** All jobs and results are stored in the database. If the server restarts, jobs resume automatically. Customers can always retrieve their results.

**Resource Control:** You can limit how many jobs run simultaneously. Rate limiting prevents abuse. Each customer has usage quotas.

## Implementation Recommendations

### Immediate Actions (Required for Production)

**Set up Redis for job queue.** Use Upstash free tier which provides 10,000 commands per day at no cost. This is sufficient for 50 to 100 customers doing moderate scraping.

**Move job storage to Supabase.** Create a jobs table in your existing Supabase database. Store job status, progress, and results. This prevents data loss on server restart.

**Implement batch size limits.** Set maximum batch size to 50 businesses per request. For larger directories, automatically split into multiple jobs. This prevents memory overload.

**Add rate limiting.** Limit each customer to 5 concurrent jobs maximum. Limit API requests to 100 per minute per customer. This prevents resource monopolization.

### Recommended Settings for Production

| Setting | Value | Reason |
|:--------|:------|:-------|
| **Batch Size** | 50 businesses | Optimal balance of speed and memory usage |
| **Max Concurrent Jobs per User** | 3 | Prevents single user from monopolizing resources |
| **Max Workers** | 5 parallel per batch | Efficient without overwhelming target websites |
| **Job Timeout** | 30 minutes | Prevents stuck jobs from blocking queue |
| **Results Retention** | 30 days | Balances storage costs with user needs |

### Cost Analysis

**Current Setup (Render Starter):** $7 per month. Limited to single server. No job persistence. Will crash with multiple users.

**Recommended Production Setup:**

Render Standard plan for API server costs $25 per month and provides guaranteed uptime and no cold starts.

Upstash Redis free tier costs $0 per month and handles up to 10,000 commands per day.

Supabase free tier costs $0 per month and provides 500 MB database and 1 GB storage.

Total monthly cost is $25 per month and supports 50 to 100 active customers safely.

**When to Upgrade:**

If you exceed 10,000 Redis commands per day, upgrade to Upstash paid tier at $10 per month for 100,000 commands.

If you exceed 500 MB database, upgrade Supabase to Pro at $25 per month for 8 GB.

If you need faster processing, add dedicated worker servers at $7 per month each.

## What I Recommend You Do Now

### Option 1: Quick Fix for MVP (Can Deploy Today)

Keep current architecture but add safety limits. Set maximum 50 businesses per request. Add simple rate limiting to prevent abuse. Store results in Supabase instead of memory. Add job timeout to prevent stuck processes.

**Pros:** No architecture changes needed. Can deploy immediately. Costs stay at $7 per month.

**Cons:** Still vulnerable to crashes with multiple users. Limited to approximately 10 concurrent customers. Not suitable for scaling beyond 20 to 30 customers.

### Option 2: Production Ready Architecture (Recommended)

Implement full job queue system with Redis. Move all job storage to Supabase. Add proper rate limiting and resource management. Deploy on Render Standard plan.

**Pros:** Handles 50 to 100 customers safely. No crash risk. Scalable architecture. Professional grade reliability.

**Cons:** Requires 2 to 3 hours of development work. Increases monthly cost to $25.

## My Recommendation

Implement Option 1 immediately to make the system safe for your first 10 to 20 customers. This gives you time to validate product market fit and generate revenue. Once you have 15 to 20 paying customers or $2,000 per month in revenue, upgrade to Option 2. The additional $18 per month cost will be easily covered by revenue.

### Specific Actions for Option 1

I will implement the following safety measures right now. Set batch size limit to 50 businesses maximum. Add job timeout of 30 minutes. Store all results in Supabase database. Add simple rate limiting for 5 concurrent jobs per user. Add memory monitoring and automatic cleanup.

These changes will make your system safe for initial customers without requiring architectural changes. You can deploy this today and start selling.
