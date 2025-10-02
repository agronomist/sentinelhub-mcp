# SentinelHub MCP Server

A Model Context Protocol (MCP) server built with FastMCP that provides access to SentinelHub's Statistical and Processing APIs. This enables AI assistants to interact with satellite imagery data and perform various analysis tasks.

## Features

- **Statistical API Integration**: Get statistical data from satellite imagery without downloading images
- **Processing API Integration**: Generate processed images from satellite data
- **Authentication Management**: Automatic OAuth token handling
- **Data Source Discovery**: Get information about available satellite data sources
- **EVALSCRIPT Validation**: Validate JavaScript processing scripts
- **Comprehensive Error Handling**: Robust error handling and validation

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up SentinelHub credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your SentinelHub credentials
   ```

## SentinelHub Setup

1. Create a SentinelHub account at [https://apps.sentinel-hub.com/](https://apps.sentinel-hub.com/)
2. Go to your account settings and create OAuth credentials
3. Add your `CLIENT_ID` and `CLIENT_SECRET` to the `.env` file

## Usage

### Running the MCP Server

```bash
python sentinelhub_mcp.py
```

### Available Tools

#### 1. `get_satellite_statistics`
Get statistical data from satellite imagery.

**Parameters:**
- `geometry` (optional): GeoJSON geometry for area of interest
- `bbox` (optional): Bounding box as [minX, minY, maxX, maxY]
- `time_from`: Start date in ISO format (e.g., "2023-01-01")
- `time_to`: End date in ISO format (e.g., "2023-12-31")
- `evalscript`: JavaScript code for data processing
- `data_sources`: List of data source specifications
- `aggregation` (optional): Aggregation parameters
- `calculations` (optional): Calculation parameters

**Example:**
```python
result = get_satellite_statistics(
    bbox=[13.0, 45.0, 13.5, 45.5],  # Rome area
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
    }],
    aggregation={
        "timeAggregation": "P1M",
        "aggregationFunction": "mean"
    }
)
```

#### 2. `process_satellite_imagery`
Generate processed images from satellite data.

**Parameters:**
- `geometry` (optional): GeoJSON geometry for area of interest
- `bbox` (optional): Bounding box as [minX, minY, maxX, maxY]
- `time_from`: Start date in ISO format
- `time_to`: End date in ISO format
- `evalscript`: JavaScript code for data processing
- `data_sources`: List of data source specifications
- `width` (optional): Output image width
- `height` (optional): Output image height
- `output_format`: Output format (default: "image/png")

**Example:**
```python
result = process_satellite_imagery(
    bbox=[13.0, 45.0, 13.5, 45.5],
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

#### 3. `get_available_data_sources`
Get information about available data sources.

**Example:**
```python
sources = get_available_data_sources()
```

#### 4. `validate_evalscript`
Validate an EVALSCRIPT for SentinelHub processing.

**Parameters:**
- `evalscript`: JavaScript code to validate

**Example:**
```python
validation = validate_evalscript("""
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08", "dataMask"],
    output: { bands: 1 }
  };
}
function evaluatePixel(sample) {
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  return [ndvi];
}
""")
```

## Common EVALSCRIPTS

### NDVI (Normalized Difference Vegetation Index)
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

### NDWI (Normalized Difference Water Index)
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

### True Color RGB
```javascript
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
```

## Data Sources

Common data sources include:
- `sentinel-2-l2a`: Sentinel-2 Level-2A data
- `sentinel-1-grd`: Sentinel-1 GRD data
- `landsat-8-l1c`: Landsat 8 Level-1C data
- `modis`: MODIS data

## Error Handling

The server includes comprehensive error handling:
- API authentication errors
- Invalid request parameters
- Network connectivity issues
- SentinelHub API errors
- EVALSCRIPT validation errors

All errors are returned in a structured format with error types and descriptive messages.

## Examples

See `examples.py` for complete examples including:
- Common EVALSCRIPTS for different analysis tasks
- Example data source configurations
- Usage patterns for different scenarios
- Test areas for experimentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. Please check SentinelHub's terms of service for API usage.

## Support

For issues related to:
- This MCP server: Create an issue in this repository
- SentinelHub APIs: Check [SentinelHub documentation](https://docs.sentinel-hub.com/)
- FastMCP: Check [FastMCP documentation](https://fastmcp.me/)
