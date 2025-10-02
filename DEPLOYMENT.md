# Deploying SentinelHub MCP Server to Railway

This guide will help you deploy the SentinelHub MCP Server to Railway and configure it to work with Cursor.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Account**: For hosting your code repository
3. **SentinelHub Credentials**: Get your OAuth credentials from [SentinelHub](https://apps.sentinel-hub.com/)

## Step 1: Prepare Your Repository

### 1.1 Create a GitHub Repository
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit: SentinelHub MCP Server"

# Create GitHub repository and push
gh repo create sentinelhub-mcp --public
git remote add origin https://github.com/YOUR_USERNAME/sentinelhub-mcp.git
git push -u origin main
```

### 1.2 Repository Structure
Your repository should have these files:
```
sentinelhub-mcp/
├── sentinelhub_mcp.py      # Main MCP server
├── requirements.txt        # Python dependencies
├── railway.json           # Railway configuration
├── Procfile              # Railway process file
├── .env.example          # Environment variables template
├── README.md             # Documentation
├── examples.py           # Example EVALSCRIPTS
└── test_mcp.py          # Test suite
```

## Step 2: Deploy to Railway

### 2.1 Connect Railway to GitHub
1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `sentinelhub-mcp` repository
5. Railway will automatically detect it's a Python project

### 2.2 Configure Environment Variables
In your Railway project dashboard:

1. Go to the "Variables" tab
2. Add these environment variables:
   ```
   SENTINELHUB_CLIENT_ID=your_client_id_here
   SENTINELHUB_CLIENT_SECRET=your_client_secret_here
   ```

### 2.3 Deploy
1. Railway will automatically start building and deploying
2. Wait for the deployment to complete (usually 2-3 minutes)
3. Your app will be available at a Railway-generated URL

## Step 3: Verify Deployment

### 3.1 Check Health Endpoint
Visit your Railway app URL + `/health`:
```
https://your-app-name.railway.app/health
```

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "version": "1.0.0",
  "credentials_configured": true,
  "mcp_tools": [
    "get_satellite_statistics",
    "process_satellite_imagery",
    "get_available_data_sources", 
    "validate_evalscript"
  ]
}
```

### 3.2 Check Web Interface
Visit your Railway app URL to see the web interface with server information.

## Step 4: Configure Cursor Integration

### 4.1 Update MCP Configuration
Create or update your Cursor MCP configuration file:

**For macOS/Linux**: `~/.config/cursor/mcp.json`
**For Windows**: `%APPDATA%\Cursor\mcp.json`

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

### 4.2 Alternative: Direct HTTP Integration
If the above doesn't work, you can use a custom MCP client:

```json
{
  "mcpServers": {
    "sentinelhub": {
      "command": "python",
      "args": ["-m", "mcp_client", "--url", "https://your-app-name.railway.app"],
      "env": {}
    }
  }
}
```

## Step 5: Test Integration

### 5.1 Restart Cursor
After updating the MCP configuration, restart Cursor to load the new server.

### 5.2 Test MCP Tools
In Cursor, you should now be able to use the SentinelHub MCP tools:

```
# Test getting available data sources
@sentinelhub get_available_data_sources

# Test EVALSCRIPT validation
@sentinelhub validate_evalscript "//VERSION=3\nfunction setup() { return { input: ['B04', 'B08'], output: { bands: 1 } }; }"
```

## Troubleshooting

### Common Issues

#### 1. Deployment Fails
- Check that all dependencies are in `requirements.txt`
- Verify `railway.json` and `Procfile` are correct
- Check Railway build logs for specific errors

#### 2. Health Check Fails
- Verify environment variables are set correctly
- Check that SentinelHub credentials are valid
- Review Railway application logs

#### 3. MCP Integration Not Working
- Ensure Cursor is restarted after configuration changes
- Check MCP configuration file syntax
- Verify the Railway app URL is accessible

#### 4. Authentication Errors
- Double-check SentinelHub OAuth credentials
- Ensure credentials are properly set in Railway environment variables
- Test credentials locally first

### Debugging Commands

```bash
# Test local deployment
python sentinelhub_mcp.py

# Test with Railway environment
RAILWAY_ENVIRONMENT=true python sentinelhub_mcp.py

# Check Railway logs
railway logs

# Test health endpoint
curl https://your-app-name.railway.app/health
```

## Custom Domain (Optional)

### Set Up Custom Domain
1. In Railway dashboard, go to "Settings" → "Domains"
2. Add your custom domain
3. Update DNS records as instructed
4. Update Cursor MCP configuration with new domain

## Monitoring and Maintenance

### Health Monitoring
- Railway provides built-in health monitoring
- Set up alerts for deployment failures
- Monitor usage and performance metrics

### Updates
To update your deployment:
1. Push changes to your GitHub repository
2. Railway will automatically redeploy
3. Test the new deployment before using in production

### Scaling
Railway automatically handles scaling, but you can:
- Upgrade to a paid plan for better performance
- Configure resource limits in `railway.json`
- Monitor usage patterns and optimize accordingly

## Security Considerations

1. **Environment Variables**: Never commit credentials to your repository
2. **API Limits**: Monitor SentinelHub API usage to avoid rate limits
3. **Access Control**: Consider adding authentication to your MCP server if needed
4. **HTTPS**: Railway provides HTTPS by default

## Cost Optimization

1. **Free Tier**: Railway offers a generous free tier
2. **Sleep Mode**: Apps sleep after inactivity to save resources
3. **Monitoring**: Keep track of usage to avoid unexpected charges

## Support

- **Railway Issues**: Check [Railway Documentation](https://docs.railway.app/)
- **MCP Issues**: Check [MCP Documentation](https://modelcontextprotocol.io/)
- **SentinelHub Issues**: Check [SentinelHub Documentation](https://docs.sentinel-hub.com/)

## Example URLs

After deployment, your app will be available at:
- **Web Interface**: `https://your-app-name.railway.app/`
- **Health Check**: `https://your-app-name.railway.app/health`
- **Tools List**: `https://your-app-name.railway.app/tools`
- **MCP Endpoint**: `https://your-app-name.railway.app` (for MCP clients)
