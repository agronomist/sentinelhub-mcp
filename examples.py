#!/usr/bin/env python3
"""
Example usage of the SentinelHub MCP Server

This file contains example EVALSCRIPTS and usage patterns for common
satellite imagery analysis tasks.
"""

# Example EVALSCRIPTS for different use cases

# 1. NDVI (Normalized Difference Vegetation Index) calculation
NDVI_EVALSCRIPT = """
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
"""

# 2. NDWI (Normalized Difference Water Index) calculation
NDWI_EVALSCRIPT = """
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
"""

# 3. True Color RGB visualization
TRUE_COLOR_EVALSCRIPT = """
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
"""

# 4. False Color NIR visualization
FALSE_COLOR_NIR_EVALSCRIPT = """
//VERSION=3
function setup() {
  return {
    input: ["B08", "B04", "B03", "dataMask"],
    output: { bands: 4 }
  };
}

function evaluatePixel(sample) {
  return [sample.B08, sample.B04, sample.B03, sample.dataMask];
}
"""

# 5. Statistical analysis - NDVI statistics
NDVI_STATISTICS_EVALSCRIPT = """
//VERSION=3
function setup() {
  return {
    input: ["B04", "B08", "dataMask"],
    output: { 
      bands: 1, 
      sampleType: "FLOAT32"
    }
  };
}

function evaluatePixel(sample) {
  if (sample.dataMask === 0) {
    return {
      ndvi: [NaN],
      dataMask: [0]
    };
  }
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
  return {
    ndvi: [ndvi],
    dataMask: [1]
  };
}
"""

# Example data source configurations
SENTINEL2_DATA_SOURCE = {
    "type": "sentinel-2-l2a",
    "dataFilter": {
        "timeRange": {
            "from": "2023-01-01T00:00:00Z",
            "to": "2023-12-31T23:59:59Z"
        },
        "maxCloudCoverage": 20
    }
}

LANDSAT8_DATA_SOURCE = {
    "type": "landsat-8-l1c",
    "dataFilter": {
        "timeRange": {
            "from": "2023-01-01T00:00:00Z",
            "to": "2023-12-31T23:59:59Z"
        },
        "maxCloudCoverage": 30
    }
}

# Example usage patterns
EXAMPLE_USAGE = {
    "get_ndvi_statistics": {
        "description": "Get NDVI statistics for a specific area and time period",
        "parameters": {
            "bbox": [12.4, 41.8, 12.6, 42.0],  # Rome area (more precise)
            "time_from": "2023-06-01",
            "time_to": "2023-08-31",
            "evalscript": NDVI_STATISTICS_EVALSCRIPT,
            "data_sources": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": "2023-06-01T00:00:00Z",
                        "to": "2023-08-31T23:59:59Z"
                    },
                    "maxCloudCoverage": 20
                }
            }],
            "aggregation": {
                "timeAggregation": "P1M",  # Monthly aggregation
                "aggregationFunction": "mean"
            }
        }
    },
    
    "get_water_mask": {
        "description": "Generate a water mask using NDWI",
        "parameters": {
            "bbox": [12.4, 41.8, 12.6, 42.0],  # Rome area
            "time_from": "2023-07-01",
            "time_to": "2023-07-31",
            "evalscript": NDWI_EVALSCRIPT,
            "data_sources": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": "2023-07-01T00:00:00Z",
                        "to": "2023-07-31T23:59:59Z"
                    },
                    "maxCloudCoverage": 30
                }
            }],
            "width": 512,
            "height": 512
        }
    },
    
    "get_true_color_image": {
        "description": "Generate a true color RGB image",
        "parameters": {
            "bbox": [12.4, 41.8, 12.6, 42.0],  # Rome area
            "time_from": "2023-07-15",
            "time_to": "2023-07-15",
            "evalscript": TRUE_COLOR_EVALSCRIPT,
            "data_sources": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": "2023-07-15T00:00:00Z",
                        "to": "2023-07-15T23:59:59Z"
                    },
                    "maxCloudCoverage": 10
                }
            }],
            "width": 1024,
            "height": 1024
        }
    }
}

# Common geographic areas for testing
TEST_AREAS = {
    "rome": {
        "bbox": [12.4, 41.8, 12.6, 42.0],
        "description": "Rome, Italy area"
    },
    "amazon": {
        "bbox": [-70.0, -10.0, -60.0, 0.0],
        "description": "Amazon rainforest area"
    },
    "california": {
        "bbox": [-122.5, 37.0, -121.5, 38.0],
        "description": "San Francisco Bay Area"
    },
    "sahara": {
        "bbox": [0.0, 20.0, 10.0, 30.0],
        "description": "Sahara Desert area"
    }
}

if __name__ == "__main__":
    print("SentinelHub MCP Server Examples")
    print("=" * 40)
    print("\nAvailable EVALSCRIPTS:")
    print("- NDVI calculation")
    print("- NDWI calculation") 
    print("- True Color RGB")
    print("- False Color NIR")
    print("- NDVI Statistics")
    
    print("\nExample usage patterns:")
    for name, example in EXAMPLE_USAGE.items():
        print(f"\n{name}:")
        print(f"  {example['description']}")
    
    print("\nTest areas:")
    for name, area in TEST_AREAS.items():
        print(f"- {name}: {area['description']}")
