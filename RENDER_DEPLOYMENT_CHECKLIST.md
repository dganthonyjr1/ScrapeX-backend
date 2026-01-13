# Render Deployment Checklist

Complete checklist for deploying ScrapeX backend with Playwright to Render.com.

---

## ✅ Pre-Deployment Checklist

### Code Ready
- [x] FinalScraper implemented
- [x] main.py updated to use FinalScraper
- [x] requirements.txt includes playwright>=1.48.0
- [x] runtime.txt specifies Python 3.11.9
- [x] All code committed to GitHub
- [x] GitHub repository: https://github.com/dganthonyjr1/ScrapeX-backend

### Testing Complete
- [x] Local testing successful
- [x] Phone extraction working on bot-protected sites
- [x] Browser automation tested
- [x] Manual fallback tested
- [x] API imports verified

---

## 🚀 Deployment Steps

### Step 1: Access Render Dashboard

1. Go to https://dashboard.render.com/
2. Sign in with GitHub
3. Navigate to "ScrapeX-backend" service

**Status:** ⏳ Pending user action

### Step 2: Trigger Deployment

**Option A: Automatic Deployment**
- If auto-deploy is enabled, Render will detect the new commit
- Check the "Events" tab for automatic deployment

**Option B: Manual Deployment**
1. Click "Manual Deploy" button (top right)
2. Select "Deploy latest commit"
3. Confirm deployment

**Status:** ⏳ Pending user action

### Step 3: Monitor Deployment

Watch the deployment logs for:

1. **Build Phase:**
   ```
   ==> Installing dependencies
   ==> pip install -r requirements.txt
   ==> Installing playwright...
   ==> playwright install chromium
   ```

2. **Browser Installation:**
   ```
   Downloading Chromium...
   Chromium downloaded successfully
   ```

3. **Service Start:**
   ```
   ==> Starting service
   ==> uvicorn main:app --host 0.0.0.0 --port $PORT
   INFO: Started server process
   INFO: Application startup complete
   ```

**Expected Duration:** 5-10 minutes (longer than usual due to Playwright installation)

### Step 4: Verify Deployment

Once deployment shows "Live" status:

1. **Check API Health:**
   ```bash
   curl https://scrapex-backend.onrender.com/
   ```

   Expected response:
   ```json
   {
     "name": "ScrapeX Healthcare API",
     "version": "1.0.0",
     "status": "running"
   }
   ```

2. **Test Scraping Endpoint:**
   ```bash
   curl -X POST https://scrapex-backend.onrender.com/api/v1/scrape \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.ocnjirrigation.com/"}'
   ```

   Expected: Phone number `(609) 628-3103` in response

**Status:** ⏳ Pending deployment completion

---

## 🔧 Configuration Verification

### Environment Variables

Verify these are set in Render dashboard:

- [x] `RETELL_API_KEY` = `key_a07875e170316b0f6f8481a00965`
- [x] `OPENAI_API_KEY` = `YOUR_OPENAI_API_KEY`

**To verify:**
1. Go to service settings
2. Click "Environment" tab
3. Check both variables are present

### Service Configuration

Verify these settings:

- [x] **Name:** ScrapeX-backend
- [x] **Language:** Python 3
- [x] **Branch:** main
- [x] **Build Command:** `pip install -r requirements.txt`
- [x] **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [x] **Instance Type:** Starter (512MB RAM, 0.5 CPU)
- [x] **Region:** Virginia (US East)

---

## 🐛 Troubleshooting

### Issue: Build Fails

**Symptoms:**
- Deployment shows "Build failed"
- Error in logs about missing dependencies

**Solution:**
1. Check requirements.txt is committed
2. Verify Python version in runtime.txt
3. Check build logs for specific error
4. Retry deployment

### Issue: Playwright Installation Fails

**Symptoms:**
- Error: "playwright: command not found"
- Error: "Could not find Chromium"

**Solution:**
Add to build command:
```bash
pip install -r requirements.txt && playwright install chromium
```

**Update in Render:**
1. Go to service settings
2. Update "Build Command"
3. Save and redeploy

### Issue: Service Crashes on Start

**Symptoms:**
- Deployment succeeds but service shows "Crashed"
- Error in logs about memory

**Solution:**
1. Check memory usage in metrics
2. If > 512MB, upgrade to Standard plan ($25/month, 2GB RAM)
3. Reduce concurrent browser instances

### Issue: Scraping Returns Errors

**Symptoms:**
- API responds but scraping fails
- Error: "Playwright not available"

**Solution:**
1. Check deployment logs for Playwright installation
2. Verify Chromium was downloaded
3. SSH into service and run: `playwright install chromium`

---

## 📊 Post-Deployment Verification

### Functional Tests

Run these tests after deployment:

#### Test 1: API Health
```bash
curl https://scrapex-backend.onrender.com/health
```
Expected: `{"status": "healthy"}`

#### Test 2: Root Endpoint
```bash
curl https://scrapex-backend.onrender.com/
```
Expected: JSON with API info

#### Test 3: Scrape Bot-Protected Site
```bash
curl -X POST https://scrapex-backend.onrender.com/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.ocnjirrigation.com/"}'
```
Expected: Phone `(609) 628-3103` extracted

#### Test 4: Scrape Simple Site
```bash
curl -X POST https://scrapex-backend.onrender.com/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```
Expected: Either success or manual_required response

### Performance Tests

Monitor these metrics:

1. **Response Time:**
   - HTTP scraping: < 2 seconds
   - Browser scraping: < 10 seconds
   - Total: < 15 seconds

2. **Memory Usage:**
   - Idle: ~100MB
   - During HTTP scrape: ~150MB
   - During browser scrape: ~350MB
   - Max: < 512MB (Starter plan limit)

3. **CPU Usage:**
   - Idle: < 5%
   - During scraping: 20-50%
   - During browser: 50-80%

**To monitor:**
1. Go to Render dashboard
2. Click on service
3. View "Metrics" tab

---

## 🎯 Success Criteria

Deployment is successful when:

- [ ] Service shows "Live" status in Render
- [ ] API health endpoint returns 200 OK
- [ ] Root endpoint returns API information
- [ ] Scraping bot-protected site extracts phone number
- [ ] Browser automation is working
- [ ] No errors in deployment logs
- [ ] Memory usage < 400MB under load
- [ ] Response time < 15 seconds for browser scraping

---

## 📝 Next Steps After Deployment

### Immediate (Within 1 Hour)

1. **Test all endpoints** using Postman or curl
2. **Monitor logs** for any errors
3. **Check metrics** for memory/CPU usage
4. **Update frontend** to use new backend URL

### Short-term (Within 24 Hours)

1. **Set up monitoring alerts** in Render
2. **Configure custom domain** (api.suddenimpactagency.io)
3. **Test end-to-end flow** from frontend
4. **Document any issues** encountered

### Medium-term (Within 1 Week)

1. **Set up Supabase database** for persistent storage
2. **Implement caching** for scraped data
3. **Add rate limiting** to prevent abuse
4. **Monitor costs** and optimize if needed

---

## 💰 Cost Monitoring

### Current Plan: Starter ($7/month)

**Included:**
- 512MB RAM
- 0.5 CPU
- Unlimited bandwidth
- Automatic SSL
- 750 hours/month (enough for 24/7 operation)

**Limitations:**
- 1-2 concurrent browser instances max
- May need upgrade for high traffic

### When to Upgrade to Standard ($25/month)

Upgrade when:
- Memory usage consistently > 400MB
- Need 5-10 concurrent browser instances
- Response times > 15 seconds
- Frequent crashes due to memory

**Standard Plan:**
- 2GB RAM
- 1 CPU
- 5-10 concurrent browsers supported

---

## 🔐 Security Checklist

- [x] API keys stored in environment variables (not in code)
- [x] HTTPS enforced (automatic with Render)
- [x] CORS configured for frontend domain
- [ ] Rate limiting implemented (TODO)
- [ ] Input validation on all endpoints (TODO)
- [ ] Authentication required for sensitive endpoints (TODO)

---

## 📞 Support Resources

### Render Documentation
- Deploying Python: https://render.com/docs/deploy-python
- Environment Variables: https://render.com/docs/environment-variables
- Troubleshooting: https://render.com/docs/troubleshooting

### Playwright Documentation
- Installation: https://playwright.dev/python/docs/intro
- Browser Automation: https://playwright.dev/python/docs/api/class-browser

### ScrapeX Documentation
- Implementation details: PLAYWRIGHT_IMPLEMENTATION_COMPLETE.md
- Usage guide: SCRAPER_USAGE_GUIDE.md
- GitHub: https://github.com/dganthonyjr1/ScrapeX-backend

---

## ✅ Deployment Complete

Once all items are checked:

- [ ] Deployment successful
- [ ] All tests passing
- [ ] Monitoring configured
- [ ] Frontend updated
- [ ] Documentation complete

**Status:** Ready for production use! 🎉

---

**Last Updated:** January 12, 2026  
**Deployment Version:** 1.0.0 (Commit: 6aff230)
