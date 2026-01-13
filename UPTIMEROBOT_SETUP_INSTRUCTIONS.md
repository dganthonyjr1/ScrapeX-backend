# UptimeRobot Setup Instructions

## Account Creation

1. Go to https://uptimerobot.com/
2. Click "Register for FREE"
3. Enter email: support@suddenimpactagency.io
4. Complete registration form:
   - Name: Sudden Impact Agency
   - Password: ScrapeX2026!
   - How did you find us: Search engine
5. Complete CAPTCHA verification
6. Verify email address

## Add Monitors

### Monitor 1: Frontend Website

1. Click "Add New Monitor"
2. Monitor Type: HTTP(s)
3. Friendly Name: ScrapeX Frontend
4. URL: https://scrapex.suddenimpactagency.io/
5. Monitoring Interval: 5 minutes (free tier)
6. Alert Contacts: support@suddenimpactagency.io
7. Click "Create Monitor"

### Monitor 2: Backend API

1. Click "Add New Monitor"
2. Monitor Type: HTTP(s)
3. Friendly Name: ScrapeX Backend API
4. URL: https://scrapex-backend.onrender.com/health
5. Monitoring Interval: 5 minutes (free tier)
6. Alert Contacts: support@suddenimpactagency.io
7. Click "Create Monitor"

## Configure Alerts

1. Go to Settings → Alert Contacts
2. Verify email address is confirmed
3. Set up alert preferences:
   - Send alert when down
   - Send alert when back up
   - Alert after 2 failed checks (to reduce false positives)

## Test Alerts

1. Wait for first monitoring cycle (5 minutes)
2. Verify both monitors show "Up" status
3. Check email for confirmation of monitoring setup

## Monitoring Dashboard

Access your monitoring dashboard at: https://dashboard.uptimerobot.com/

### Key Metrics to Monitor

- Uptime percentage (target: 99.9%)
- Response time (target: < 2 seconds for frontend, < 5 seconds for backend)
- Downtime incidents (target: 0 per month)

## Free Tier Limitations

- 50 monitors maximum
- 5-minute monitoring interval
- Email alerts only (SMS requires paid plan)
- Basic status pages

## Upgrade Recommendations

Consider upgrading to Solo plan ($7/month) when:
- You need 1-minute monitoring intervals
- You want SMS alerts for critical downtime
- You need more than 50 monitors

## Integration with Other Tools

UptimeRobot can integrate with:
- Slack (for team notifications)
- Discord (for team notifications)
- Webhooks (for custom integrations)
- Zapier (for advanced automation)

## Status: Pending Manual Completion

Account registration started but requires CAPTCHA verification and email confirmation.

**Action Required:** Complete the registration and add the two monitors as described above.
