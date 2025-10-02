# Getting Started with SentinelHub MCP Server

This guide will help you set up and use the SentinelHub MCP Server to access satellite imagery data through AI assistants.

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get SentinelHub Credentials
1. Go to [https://apps.sentinel-hub.com/](https://apps.sentinel-hub.com/)
2. Create an account or sign in
3. Navigate to Account Settings → OAuth Credentials
4. Create new OAuth credentials
5. Copy your `CLIENT_ID` and `CLIENT_SECRET`

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your credentials:
# SENTINELHUB_CLIENT_ID=your_client_id_here
# SENTINELHUB_CLIENT_SECRET=your_client_secret_here
```

### 4. Test the Setup
```bash
python test_mcp.py
```

### 5. Run the MCP Server
```bash
python sentinelhub_mcp.py
```

## Basic Usage Examples

### Get NDVI Statistics
```python
# Example: Get vegetation index statistics for Rome area
result = get_satellite_statistics(
    bbox=[12.4, 41.8, 12.6, 42.0],  # Rome bounding box
    time_from="2023-06-01",
    time_to="2023-08-31",
    evalscript="""
    //VERSION=3
    function setup() {
      return {
        input: ["B04", "B08", "dataMask"],
        output: { bands: 1, sampleType: "FLOAT32" }
      };
    }
    function evaluatePixel(sample) {
      if (sample.dataMask === 0) return [NaN];
      let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
      return [ndvi];
    }
    """,
    data_sources=[{
        "type": "sentinel-2-l2a",
        "dataFilter": {
            "timeRange": {
                "from": "2023-06-01T00:00:00Z",
                "to": "2023-08-31T23:59:59Z"
            },
            "maxCloudCoverage": 20
        }
    }]
)
```

### Generate True Color Image
```python
# Example: Generate a true color RGB image
result = process_satellite_imagery(
    bbox=[12.4, 41.8, 12.6, 42.0],
    time_from="2023-07-15",
    time_to="2023-07-15",
    evalscript="""
    //VERSION=3
    function setup() {
      return {
        input: ["B04", "B03", "B02", "dataMask"],
        output: { bands: 4 }
      };
    }
    function evaluatePixel(sample) {
      return [sample.B04, sample.B03, sample.B02, sample.dataMask];
    }
    """,
    data_sources=[{
        "type": "sentinel-2-l2a",
        "dataFilter": {
            "timeRange": {
                "from": "2023-07-15T00:00:00Z",
                "to": "2023-07-15T23:59:59Z"
            },
            "maxCloudCoverage": 10
        }
    }],
    width=1024,
    height=1024
)
```

## Common EVALSCRIPTS

### NDVI (Vegetation Index)
```javascript
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08", "dataMask"],
    output: { bands: 4 }
  };
}
function evaluatePixel(sample) {
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  return [sample.B04, sample.B08, ndvi, sample.dataMask];
}
```

### NDWI (Water Index)
```javascript
//VERSION=3
function setup() {
  return {
    input: ["B03", "B08", "dataMask"],
    output: { bands: 4 }
  };
}
function evaluatePixel(sample) {
  let ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08);
  return [sample.B03, sample.B08, ndwi, sample.dataMask];
}
```

## Available Tools

1. **`get_satellite_statistics`** - Get statistical data from satellite imagery
2. **`process_satellite_imagery`** - Generate processed images from satellite data
3. **`get_available_data_sources`** - Get information about available data sources
4. **`validate_evalscript`** - Validate JavaScript processing scripts

## Data Sources

Common satellite data sources:
- `sentinel-2-l2a` - Sentinel-2 Level-2A (optical)
- `sentinel-1-grd` - Sentinel-1 GRD (radar)
- `landsat-8-l1c` - Landsat 8 Level-1C
- `modis` - MODIS data

## Troubleshooting

### Authentication Issues
- Verify your credentials in the `.env` file
- Check that your SentinelHub account is active
- Ensure OAuth credentials are properly configured

### API Errors
- Check your EVALSCRIPT syntax
- Verify data source availability for your time range
- Ensure bounding box coordinates are valid

### Performance Tips
- Use appropriate cloud coverage filters
- Limit time ranges for faster processing
- Use smaller bounding boxes for testing

## Next Steps

1. Explore the examples in `examples.py`
2. Try different EVALSCRIPTS for various analysis tasks
3. Experiment with different data sources and time ranges
4. Check the full documentation in `README.md`

## Support

- For MCP server issues: Check this repository
- For SentinelHub API questions: [SentinelHub Documentation](https://docs.sentinel-hub.com/)
- For FastMCP questions: [FastMCP Documentation](https://fastmcp.me/)
