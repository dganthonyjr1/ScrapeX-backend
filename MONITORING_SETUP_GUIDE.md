# Monitoring and Alerting Setup Guide for ScrapeX

## Overview

This guide provides instructions for setting up comprehensive monitoring, alerting, and error tracking for the ScrapeX platform to ensure high availability and rapid incident response.

## Monitoring Stack Recommendation

### 1. Uptime Monitoring: UptimeRobot (Free)

**Purpose:** Monitor website and API availability

**Setup Steps:**

1. Create a free account at https://uptimerobot.com/
2. Add monitors for:
   - Frontend: https://scrapex.suddenimpactagency.io/
   - Backend API: https://scrapex-backend.onrender.com/health
   - Custom domain (once configured): https://api.suddenimpactagency.io/health
3. Configure check interval: 5 minutes
4. Set up alert contacts:
   - Email notifications
   - SMS notifications (optional)
   - Slack integration (optional)

**Cost:** Free for up to 50 monitors

### 2. Error Tracking: Sentry (Free Tier)

**Purpose:** Track application errors and exceptions

**Setup Steps:**

1. Create account at https://sentry.io/
2. Create a new project for "ScrapeX Backend"
3. Install Sentry SDK in backend:
   ```bash
   pip install sentry-sdk
   ```
4. Add to main.py:
   ```python
   import sentry_sdk
   
   sentry_sdk.init(
       dsn="YOUR_SENTRY_DSN",
       traces_sample_rate=0.1,
       environment="production"
   )
   ```
5. Add SENTRY_DSN to Render environment variables

**Cost:** Free for up to 5,000 errors per month

### 3. Performance Monitoring: Render Built-in Metrics

**Purpose:** Monitor CPU, memory, and response times

**Setup Steps:**

1. Navigate to Render dashboard
2. Go to ScrapeX-backend service
3. Click on "Metrics" tab
4. Review:
   - CPU usage
   - Memory usage
   - HTTP response times
   - Request volume

**Cost:** Included with Render hosting

### 4. Database Monitoring: Supabase Built-in Metrics

**Purpose:** Monitor database performance and query times

**Setup Steps:**

1. Navigate to Supabase dashboard
2. Go to your project
3. Click on "Database" → "Reports"
4. Review:
   - Query performance
   - Connection count
   - Database size
   - Slow queries

**Cost:** Included with Supabase

## Alert Configuration

### Critical Alerts (Immediate Response Required)

- API downtime exceeding 2 minutes
- Database connection failures
- Payment processing errors
- TCPA compliance violations

### Warning Alerts (Review Within 1 Hour)

- API response time exceeding 5 seconds
- Error rate exceeding 5%
- Database query time exceeding 1 second
- Memory usage exceeding 80%

### Informational Alerts (Daily Review)

- New user signups
- Subscription changes
- API usage patterns
- System performance trends

## Implementation Checklist

### Phase 1: Basic Uptime Monitoring (15 minutes)

- [ ] Create UptimeRobot account
- [ ] Add frontend monitor
- [ ] Add backend API monitor
- [ ] Configure email alerts
- [ ] Test alert delivery

### Phase 2: Error Tracking (30 minutes)

- [ ] Create Sentry account
- [ ] Install Sentry SDK in backend
- [ ] Add Sentry DSN to environment variables
- [ ] Deploy updated backend
- [ ] Test error reporting

### Phase 3: Performance Monitoring (15 minutes)

- [ ] Review Render metrics dashboard
- [ ] Review Supabase reports
- [ ] Set up custom dashboards
- [ ] Document baseline performance metrics

### Phase 4: Alert Optimization (30 minutes)

- [ ] Configure alert thresholds
- [ ] Set up escalation policies
- [ ] Test alert workflows
- [ ] Document incident response procedures

## Monitoring Dashboard

Create a centralized monitoring dashboard that includes:

1. **System Health**
   - Frontend uptime percentage
   - Backend API uptime percentage
   - Database uptime percentage

2. **Performance Metrics**
   - Average API response time
   - Error rate
   - Request volume
   - Active users

3. **Business Metrics**
   - Total users
   - Active subscriptions
   - API calls per day
   - Revenue metrics

## Incident Response Workflow

### Step 1: Detection
- Alert received via email, SMS, or Slack
- Check monitoring dashboard for details

### Step 2: Assessment
- Determine severity (Critical, Warning, Informational)
- Identify affected systems
- Estimate impact on users

### Step 3: Response
- For critical issues: Immediate investigation
- For warnings: Schedule investigation within 1 hour
- For informational: Review during daily check

### Step 4: Resolution
- Implement fix
- Deploy to production
- Verify resolution
- Document root cause

### Step 5: Post-Mortem
- Document incident timeline
- Identify root cause
- Implement preventive measures
- Update monitoring and alerts

## Cost Summary

| Service | Plan | Monthly Cost |
|---------|------|--------------|
| UptimeRobot | Free | $0 |
| Sentry | Free | $0 |
| Render Metrics | Included | $0 |
| Supabase Metrics | Included | $0 |
| **Total** | | **$0** |

## Upgrade Path

As your business grows, consider upgrading to:

- **UptimeRobot Pro** ($7/month): 1-minute checks, more monitors
- **Sentry Team** ($26/month): More errors, better features
- **Datadog** ($15/host/month): Comprehensive APM and logging
- **PagerDuty** ($21/user/month): Advanced incident management

## Next Steps

1. Implement Phase 1 (Basic Uptime Monitoring) immediately
2. Implement Phase 2 (Error Tracking) within 1 week
3. Review metrics weekly and adjust alert thresholds
4. Conduct monthly performance reviews
5. Plan for monitoring upgrades as user base grows
