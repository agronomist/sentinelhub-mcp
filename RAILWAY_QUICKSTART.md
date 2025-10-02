# 🚀 Railway Quick Start Guide

Get your SentinelHub MCP Server deployed to Railway in 5 minutes!

## Prerequisites
- [ ] GitHub account
- [ ] Railway account (free at [railway.app](https://railway.app))
- [ ] SentinelHub credentials (get from [apps.sentinel-hub.com](https://apps.sentinel-hub.com))

## Step 1: Deploy to Railway (2 minutes)

### 1.1 Create GitHub Repository
```bash
# In your project directory
git init
git add .
git commit -m "Initial commit: SentinelHub MCP Server"
gh repo create sentinelhub-mcp --public
git remote add origin https://github.com/YOUR_USERNAME/sentinelhub-mcp.git
git push -u origin main
```

### 1.2 Deploy to Railway
1. Go to [railway.app](https://railway.app) → "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `sentinelhub-mcp` repository
4. Railway auto-detects Python and starts building

### 1.3 Add Environment Variables
In Railway dashboard → "Variables" tab:
```
SENTINELHUB_CLIENT_ID=your_client_id_here
SENTINELHUB_CLIENT_SECRET=your_client_secret_here
```

## Step 2: Configure Cursor (1 minute)

### 2.1 Create MCP Configuration
Create `~/.config/cursor/mcp.json`:
```json
{
  "mcpServers": {
    "sentinelhub": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-fetch",
        "https://your-app-name.railway.app"
      ],
      "env": {}
    }
  }
}
```

**Replace `your-app-name.railway.app` with your actual Railway URL**

### 2.2 Restart Cursor
Close and reopen Cursor completely.

## Step 3: Test Integration (2 minutes)

### 3.1 Verify Deployment
Visit your Railway URL + `/health`:
```
https://your-app-name.railway.app/health
```

Should show:
```json
{
  "status": "healthy",
  "credentials_configured": true,
  "mcp_tools": ["get_satellite_statistics", "process_satellite_imagery", ...]
}
```

### 3.2 Test in Cursor
Open Cursor chat and try:
```
@sentinelhub get_available_data_sources
```

## 🎉 You're Done!

Your SentinelHub MCP Server is now:
- ✅ Deployed to Railway
- ✅ Configured in Cursor
- ✅ Ready to analyze satellite imagery!

## Quick Test Commands

### Get NDVI Statistics
```
@sentinelhub get_satellite_statistics
bbox: [12.4, 41.8, 12.6, 42.0]
time_from: "2023-06-01"
time_to: "2023-08-31"
evalscript: "//VERSION=3\nfunction setup() { return { input: ['B04', 'B08', 'dataMask'], output: { bands: 1, sampleType: 'FLOAT32' } }; }\nfunction evaluatePixel(sample) { if (sample.dataMask === 0) return [NaN]; let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04); return [ndvi]; }"
data_sources: [{"type": "sentinel-2-l2a", "dataFilter": {"timeRange": {"from": "2023-06-01T00:00:00Z", "to": "2023-08-31T23:59:59Z"}, "maxCloudCoverage": 20}}]
```

### Generate True Color Image
```
@sentinelhub process_satellite_imagery
bbox: [12.4, 41.8, 12.6, 42.0]
time_from: "2023-07-15"
time_to: "2023-07-15"
evalscript: "//VERSION=3\nfunction setup() { return { input: ['B04', 'B03', 'B02', 'dataMask'], output: { bands: 4 } }; }\nfunction evaluatePixel(sample) { return [sample.B04, sample.B03, sample.B02, sample.dataMask]; }"
data_sources: [{"type": "sentinel-2-l2a", "dataFilter": {"timeRange": {"from": "2023-07-15T00:00:00Z", "to": "2023-07-15T23:59:59Z"}, "maxCloudCoverage": 10}}]
width: 1024
height: 1024
```

## Troubleshooting

### ❌ Deployment Issues
- Check Railway build logs
- Verify `requirements.txt` includes all dependencies
- Ensure `railway.json` and `Procfile` exist

### ❌ MCP Not Connecting
- Verify Railway app URL is correct
- Check that app is running (visit the URL)
- Restart Cursor after configuration changes

### ❌ Authentication Errors
- Double-check SentinelHub credentials in Railway
- Test credentials locally first
- Check Railway environment variables

## Need Help?

- **Full Documentation**: [README.md](README.md)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Cursor Setup**: [CURSOR_SETUP.md](CURSOR_SETUP.md)
- **Getting Started**: [GETTING_STARTED.md](GETTING_STARTED.md)

## What's Next?

- Explore different EVALSCRIPTS in `examples.py`
- Try different satellite data sources
- Analyze various geographic areas
- Build custom analysis workflows

Happy satellite imagery analysis! 🛰️
