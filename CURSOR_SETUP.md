# Setting Up SentinelHub MCP Server with Cursor

This guide will help you configure the SentinelHub MCP Server to work with Cursor IDE.

## Prerequisites

- Cursor IDE installed
- SentinelHub MCP Server deployed to Railway (see [DEPLOYMENT.md](DEPLOYMENT.md))
- Your Railway app URL

## Step 1: Configure Cursor MCP Settings

### 1.1 Locate Cursor Configuration Directory

**macOS/Linux:**
```bash
~/.config/cursor/mcp.json
```

**Windows:**
```bash
%APPDATA%\Cursor\mcp.json
```

### 1.2 Create or Update MCP Configuration

Create the configuration file with the following content:

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

**Replace `your-app-name.railway.app` with your actual Railway app URL.**

### 1.3 Alternative Configuration (If Above Doesn't Work)

If the fetch server doesn't work, try this alternative:

```json
{
  "mcpServers": {
    "sentinelhub": {
      "command": "python",
      "args": [
        "-c",
        "import requests; import json; import sys; response = requests.post('https://your-app-name.railway.app/mcp', json={'method': 'tools/list'}); print(json.dumps(response.json()))"
      ],
      "env": {}
    }
  }
}
```

## Step 2: Restart Cursor

After updating the MCP configuration:

1. **Close Cursor completely**
2. **Reopen Cursor**
3. **Wait for MCP servers to initialize** (check the status bar)

## Step 3: Verify MCP Integration

### 3.1 Check MCP Status
Look for MCP server status in Cursor's status bar. You should see:
- `sentinelhub` server connected
- Green indicator showing it's active

### 3.2 Test MCP Tools
Open a new chat in Cursor and try these commands:

```
# Test getting available data sources
@sentinelhub get_available_data_sources

# Test EVALSCRIPT validation
@sentinelhub validate_evalscript "//VERSION=3\nfunction setup() { return { input: ['B04', 'B08'], output: { bands: 1 } }; }"
```

## Step 4: Using SentinelHub Tools in Cursor

### 4.1 Get Satellite Statistics
```
@sentinelhub get_satellite_statistics
bbox: [12.4, 41.8, 12.6, 42.0]
time_from: "2023-06-01"
time_to: "2023-08-31"
evalscript: "//VERSION=3\nfunction setup() { return { input: ['B04', 'B08', 'dataMask'], output: { bands: 1, sampleType: 'FLOAT32' } }; }\nfunction evaluatePixel(sample) { if (sample.dataMask === 0) return [NaN]; let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04); return [ndvi]; }"
data_sources: [{"type": "sentinel-2-l2a", "dataFilter": {"timeRange": {"from": "2023-06-01T00:00:00Z", "to": "2023-08-31T23:59:59Z"}, "maxCloudCoverage": 20}}]
```

### 4.2 Process Satellite Imagery
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

### Common Issues

#### 1. MCP Server Not Connecting
- **Check Railway app URL**: Ensure it's correct and accessible
- **Verify Railway deployment**: Check that your app is running
- **Test health endpoint**: Visit `https://your-app-name.railway.app/health`

#### 2. Tools Not Available
- **Restart Cursor**: Close and reopen completely
- **Check MCP configuration**: Verify JSON syntax is correct
- **Check Cursor logs**: Look for MCP-related error messages

#### 3. Authentication Errors
- **Verify credentials**: Check that SentinelHub credentials are set in Railway
- **Test locally**: Try running the server locally first
- **Check Railway logs**: Look for authentication-related errors

#### 4. Network Issues
- **Check internet connection**: Ensure you can access external APIs
- **Firewall settings**: Make sure Cursor can make outbound connections
- **Proxy settings**: Configure if behind a corporate firewall

### Debugging Steps

1. **Test Railway App Directly**:
   ```bash
   curl https://your-app-name.railway.app/health
   ```

2. **Check Cursor MCP Logs**:
   - Open Cursor Developer Tools
   - Look for MCP-related console messages

3. **Verify Configuration File**:
   ```bash
   # Check if file exists and is valid JSON
   cat ~/.config/cursor/mcp.json | jq .
   ```

4. **Test MCP Server Locally**:
   ```bash
   # Run locally to test functionality
   python sentinelhub_mcp.py
   ```

## Advanced Configuration

### Custom MCP Client
If the default MCP integration doesn't work, you can create a custom client:

```json
{
  "mcpServers": {
    "sentinelhub": {
      "command": "python",
      "args": ["custom_mcp_client.py"],
      "env": {
        "SENTINELHUB_URL": "https://your-app-name.railway.app"
      }
    }
  }
}
```

### Multiple Environments
You can configure both local and remote servers:

```json
{
  "mcpServers": {
    "sentinelhub-local": {
      "command": "python",
      "args": ["sentinelhub_mcp.py"],
      "env": {
        "SENTINELHUB_CLIENT_ID": "${SENTINELHUB_CLIENT_ID}",
        "SENTINELHUB_CLIENT_SECRET": "${SENTINELHUB_CLIENT_SECRET}"
      }
    },
    "sentinelhub-remote": {
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

## Usage Examples

### Example 1: Vegetation Analysis
```
Analyze vegetation health in Rome using NDVI for summer 2023

@sentinelhub get_satellite_statistics
bbox: [12.4, 41.8, 12.6, 42.0]
time_from: "2023-06-01"
time_to: "2023-08-31"
evalscript: "//VERSION=3\nfunction setup() { return { input: ['B04', 'B08', 'dataMask'], output: { bands: 1, sampleType: 'FLOAT32' } }; }\nfunction evaluatePixel(sample) { if (sample.dataMask === 0) return [NaN]; let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04); return [ndvi]; }"
data_sources: [{"type": "sentinel-2-l2a", "dataFilter": {"timeRange": {"from": "2023-06-01T00:00:00Z", "to": "2023-08-31T23:59:59Z"}, "maxCloudCoverage": 20}}]
aggregation: {"timeAggregation": "P1M", "aggregationFunction": "mean"}
```

### Example 2: Water Body Detection
```
Generate a water mask for the Amazon region using NDWI

@sentinelhub process_satellite_imagery
bbox: [-70.0, -10.0, -60.0, 0.0]
time_from: "2023-07-01"
time_to: "2023-07-31"
evalscript: "//VERSION=3\nfunction setup() { return { input: ['B03', 'B08', 'dataMask'], output: { bands: 4 } }; }\nfunction evaluatePixel(sample) { let ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08); return [sample.B03, sample.B08, ndwi, sample.dataMask]; }"
data_sources: [{"type": "sentinel-2-l2a", "dataFilter": {"timeRange": {"from": "2023-07-01T00:00:00Z", "to": "2023-07-31T23:59:59Z"}, "maxCloudCoverage": 30}}]
width: 512
height: 512
```

## Support

- **Cursor MCP Issues**: Check [Cursor Documentation](https://cursor.sh/docs)
- **MCP Protocol**: Check [MCP Documentation](https://modelcontextprotocol.io/)
- **SentinelHub API**: Check [SentinelHub Documentation](https://docs.sentinel-hub.com/)
- **Railway Deployment**: Check [Railway Documentation](https://docs.railway.app/)
