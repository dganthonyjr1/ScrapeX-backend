# Custom Domain Setup Guide for ScrapeX Backend API

## Goal
Configure `api.suddenimpactagency.io` to point to your Render backend at `https://scrapex-backend.onrender.com`

## Prerequisites
- Access to Ionos DNS management for suddenimpactagency.io
- Render account with ScrapeX-backend service deployed

## Steps

### Part 1: Configure DNS in Ionos

1. Log in to your Ionos account at https://www.ionos.com/
2. Navigate to **Domains & SSL** → **suddenimpactagency.io** → **DNS**
3. Add a new **CNAME record**:
   - **Subdomain:** `api`
   - **Points to:** `scrapex-backend.onrender.com`
   - **TTL:** 3600 (1 hour)
4. Save the DNS record

### Part 2: Configure Custom Domain in Render

1. Log in to Render at https://dashboard.render.com/
2. Navigate to your **ScrapeX-backend** service
3. Go to **Settings** → **Custom Domains**
4. Click **Add Custom Domain**
5. Enter: `api.suddenimpactagency.io`
6. Click **Save**
7. Render will automatically provision an SSL certificate (takes 5-10 minutes)

### Part 3: Verify Configuration

1. Wait 10-15 minutes for DNS propagation
2. Test the custom domain:
   ```bash
   curl https://api.suddenimpactagency.io/health
   ```
3. You should see a JSON response confirming the API is running

### Part 4: Update Frontend Configuration

Once the custom domain is working, update your frontend to use the new API URL:
- **Old URL:** `https://scrapex-backend.onrender.com`
- **New URL:** `https://api.suddenimpactagency.io`

## Troubleshooting

**DNS not resolving?**
- Wait up to 24 hours for full DNS propagation
- Use `nslookup api.suddenimpactagency.io` to check DNS status

**SSL certificate error?**
- Render automatically provisions Let's Encrypt certificates
- This process can take up to 30 minutes
- Check the Render dashboard for certificate status

**Connection refused?**
- Verify the CNAME record points to `scrapex-backend.onrender.com` (not the full HTTPS URL)
- Ensure the Render service is running and not in a failed state

## Expected Timeline
- DNS record creation: 2 minutes
- DNS propagation: 10-60 minutes
- SSL certificate provisioning: 5-30 minutes
- **Total time:** 15-90 minutes

## Benefits of Custom Domain
- Professional branded API endpoint
- Easier to remember and communicate
- Flexibility to change hosting providers without changing API URLs
- Better for marketing and customer-facing documentation
