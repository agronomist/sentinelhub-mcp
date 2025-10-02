#!/usr/bin/env python3
"""
SentinelHub MCP Server using FastMCP

This MCP server provides access to SentinelHub's Statistical and Processing APIs
through the Model Context Protocol, enabling AI assistants to interact with
satellite imagery data and statistics.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, date
import requests
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("SentinelHub MCP Server")

# Initialize FastAPI for web interface
web_app = FastAPI(
    title="SentinelHub MCP Server",
    description="MCP Server for SentinelHub's Statistical and Processing APIs",
    version="1.0.0"
)

# SentinelHub API configuration
SENTINELHUB_BASE_URL = "https://services.sentinel-hub.com/api/v1"
SENTINELHUB_OAUTH_URL = "https://services.sentinel-hub.com/oauth/token"

class SentinelHubConfig:
    """Configuration for SentinelHub API access"""
    
    def __init__(self):
        self.client_id = os.getenv("SENTINELHUB_CLIENT_ID")
        self.client_secret = os.getenv("SENTINELHUB_CLIENT_SECRET")
        self.access_token = None
        self.token_expires_at = None
    
    def get_access_token(self) -> str:
        """Get or refresh access token for SentinelHub API"""
        if (self.access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at):
            return self.access_token
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "SentinelHub credentials not found. Please set SENTINELHUB_CLIENT_ID "
                "and SENTINELHUB_CLIENT_SECRET environment variables."
            )
        
        # Request new token
        token_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        response = requests.post(SENTINELHUB_OAUTH_URL, data=token_data)
        response.raise_for_status()
        
        token_info = response.json()
        self.access_token = token_info["access_token"]
        expires_in = token_info.get("expires_in", 3600)
        self.token_expires_at = datetime.now().timestamp() + expires_in - 60  # 1 minute buffer
        
        return self.access_token

# Global configuration instance
config = SentinelHubConfig()

# Pydantic models for request validation
class Geometry(BaseModel):
    """Geometry specification for area of interest"""
    type: str = Field(..., description="Geometry type (e.g., 'Polygon', 'Point')")
    coordinates: List[Any] = Field(..., description="Geometry coordinates")

class BBox(BaseModel):
    """Bounding box specification"""
    bbox: List[float] = Field(..., description="Bounding box as [minX, minY, maxX, maxY]")
    crs: str = Field(default="EPSG:4326", description="Coordinate reference system")

class TimeRange(BaseModel):
    """Time range specification"""
    from_: str = Field(alias="from", description="Start date (ISO format)")
    to: str = Field(description="End date (ISO format)")

class StatisticalRequest(BaseModel):
    """Request model for Statistical API"""
    geometry: Optional[Geometry] = Field(None, description="Area of interest geometry")
    bbox: Optional[BBox] = Field(None, description="Bounding box specification")
    time: TimeRange = Field(..., description="Time range for analysis")
    evalscript: str = Field(..., description="EVALSCRIPT for data processing")
    data: List[Dict[str, Any]] = Field(..., description="Data source specifications")
    aggregation: Optional[Dict[str, Any]] = Field(None, description="Aggregation parameters")
    calculations: Optional[Dict[str, Any]] = Field(None, description="Calculation parameters")

class ProcessingRequest(BaseModel):
    """Request model for Processing API"""
    geometry: Optional[Geometry] = Field(None, description="Area of interest geometry")
    bbox: Optional[BBox] = Field(None, description="Bounding box specification")
    time: TimeRange = Field(..., description="Time range for processing")
    evalscript: str = Field(..., description="EVALSCRIPT for data processing")
    data: List[Dict[str, Any]] = Field(..., description="Data source specifications")
    width: Optional[int] = Field(None, description="Output image width")
    height: Optional[int] = Field(None, description="Output image height")
    format: str = Field(default="image/png", description="Output format")

@mcp.tool()
def get_satellite_statistics(
    geometry: Optional[Dict[str, Any]] = None,
    bbox: Optional[List[float]] = None,
    time_from: str = None,
    time_to: str = None,
    evalscript: str = None,
    data_sources: List[Dict[str, Any]] = None,
    aggregation: Optional[Dict[str, Any]] = None,
    calculations: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get statistical data from satellite imagery using SentinelHub's Statistical API.
    
    Args:
        geometry: Area of interest as GeoJSON geometry (optional if bbox provided)
        bbox: Bounding box as [minX, minY, maxX, maxY] (optional if geometry provided)
        time_from: Start date in ISO format (e.g., "2023-01-01")
        time_to: End date in ISO format (e.g., "2023-12-31")
        evalscript: JavaScript code for data processing
        data_sources: List of data source specifications
        aggregation: Aggregation parameters (optional)
        calculations: Calculation parameters (optional)
    
    Returns:
        Dictionary containing statistical results from SentinelHub
    """
    try:
        # Validate required parameters
        if not time_from or not time_to:
            raise ValueError("time_from and time_to are required")
        if not evalscript:
            raise ValueError("evalscript is required")
        if not data_sources:
            raise ValueError("data_sources is required")
        if not geometry and not bbox:
            raise ValueError("Either geometry or bbox must be provided")
        
        # Prepare request payload
        payload = {
            "time": {
                "from": time_from,
                "to": time_to
            },
            "evalscript": evalscript,
            "data": data_sources
        }
        
        # Add geometry or bbox
        if geometry:
            payload["geometry"] = geometry
        elif bbox:
            payload["bbox"] = bbox
        
        # Add optional parameters
        if aggregation:
            payload["aggregation"] = aggregation
        if calculations:
            payload["calculations"] = calculations
        
        # Get access token
        access_token = config.get_access_token()
        
        # Make API request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{SENTINELHUB_BASE_URL}/statistics"
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Statistical API request successful: {len(result.get('data', []))} data points")
        
        return {
            "success": True,
            "data": result,
            "request_info": {
                "time_range": f"{time_from} to {time_to}",
                "data_sources": len(data_sources),
                "has_geometry": geometry is not None,
                "has_bbox": bbox is not None
            }
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return {
            "success": False,
            "error": f"API request failed: {str(e)}",
            "error_type": "api_error"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unexpected_error"
        }

@mcp.tool()
def process_satellite_imagery(
    geometry: Optional[Dict[str, Any]] = None,
    bbox: Optional[List[float]] = None,
    time_from: str = None,
    time_to: str = None,
    evalscript: str = None,
    data_sources: List[Dict[str, Any]] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    output_format: str = "image/png"
) -> Dict[str, Any]:
    """
    Process satellite imagery using SentinelHub's Processing API.
    
    Args:
        geometry: Area of interest as GeoJSON geometry (optional if bbox provided)
        bbox: Bounding box as [minX, minY, maxX, maxY] (optional if geometry provided)
        time_from: Start date in ISO format (e.g., "2023-01-01")
        time_to: End date in ISO format (e.g., "2023-12-31")
        evalscript: JavaScript code for data processing
        data_sources: List of data source specifications
        width: Output image width (optional)
        height: Output image height (optional)
        output_format: Output format (default: "image/png")
    
    Returns:
        Dictionary containing processing results and image data from SentinelHub
    """
    try:
        # Validate required parameters
        if not time_from or not time_to:
            raise ValueError("time_from and time_to are required")
        if not evalscript:
            raise ValueError("evalscript is required")
        if not data_sources:
            raise ValueError("data_sources is required")
        if not geometry and not bbox:
            raise ValueError("Either geometry or bbox must be provided")
        
        # Prepare request payload
        payload = {
            "time": {
                "from": time_from,
                "to": time_to
            },
            "evalscript": evalscript,
            "data": data_sources,
            "format": output_format
        }
        
        # Add geometry or bbox
        if geometry:
            payload["geometry"] = geometry
        elif bbox:
            payload["bbox"] = bbox
        
        # Add optional parameters
        if width:
            payload["width"] = width
        if height:
            payload["height"] = height
        
        # Get access token
        access_token = config.get_access_token()
        
        # Make API request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{SENTINELHUB_BASE_URL}/process"
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        # Handle different response types
        content_type = response.headers.get('content-type', '')
        
        if 'image/' in content_type:
            # Image response - return base64 encoded data
            import base64
            image_data = base64.b64encode(response.content).decode('utf-8')
            result = {
                "success": True,
                "image_data": image_data,
                "content_type": content_type,
                "size_bytes": len(response.content),
                "request_info": {
                    "time_range": f"{time_from} to {time_to}",
                    "data_sources": len(data_sources),
                    "has_geometry": geometry is not None,
                    "has_bbox": bbox is not None,
                    "output_format": output_format
                }
            }
        else:
            # JSON response
            result_data = response.json()
            result = {
                "success": True,
                "data": result_data,
                "content_type": content_type,
                "request_info": {
                    "time_range": f"{time_from} to {time_to}",
                    "data_sources": len(data_sources),
                    "has_geometry": geometry is not None,
                    "has_bbox": bbox is not None,
                    "output_format": output_format
                }
            }
        
        logger.info(f"Processing API request successful: {content_type}")
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return {
            "success": False,
            "error": f"API request failed: {str(e)}",
            "error_type": "api_error"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unexpected_error"
        }

@mcp.tool()
def get_available_data_sources() -> Dict[str, Any]:
    """
    Get information about available data sources in SentinelHub.
    
    Returns:
        Dictionary containing available data sources and their specifications
    """
    try:
        # Get access token
        access_token = config.get_access_token()
        
        # Make API request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{SENTINELHUB_BASE_URL}/data"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data_sources = response.json()
        
        return {
            "success": True,
            "data_sources": data_sources,
            "count": len(data_sources) if isinstance(data_sources, list) else 1
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return {
            "success": False,
            "error": f"API request failed: {str(e)}",
            "error_type": "api_error"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "error_type": "unexpected_error"
        }

def _validate_evalscript_impl(evalscript: str) -> Dict[str, Any]:
    """
    Validate an EVALSCRIPT for SentinelHub processing.
    
    Args:
        evalscript: JavaScript code to validate
    
    Returns:
        Dictionary containing validation results
    """
    try:
        if not evalscript or not evalscript.strip():
            return {
                "success": False,
                "error": "EVALSCRIPT cannot be empty",
                "error_type": "validation_error"
            }
        
        # Basic validation checks
        validation_results = {
            "success": True,
            "checks": {
                "not_empty": bool(evalscript.strip()),
                "has_return_statement": "return" in evalscript,
                "has_function_definition": any(keyword in evalscript for keyword in ["function", "=>", "evalPixel"]),
                "length": len(evalscript),
                "line_count": len(evalscript.split('\n'))
            }
        }
        
        # Check for common SentinelHub patterns
        common_patterns = {
            "uses_sample": "sample" in evalscript.lower(),
            "uses_index": any(index in evalscript.lower() for index in ["ndvi", "ndwi", "ndbi", "evi"]),
            "uses_bands": any(band in evalscript.lower() for band in ["b01", "b02", "b03", "b04", "b05", "b06", "b07", "b08", "b8a", "b09", "b10", "b11", "b12"]),
            "uses_visualize": "visualize" in evalscript.lower()
        }
        
        validation_results["checks"].update(common_patterns)
        
        # Provide recommendations
        recommendations = []
        if not validation_results["checks"]["has_return_statement"]:
            recommendations.append("EVALSCRIPT should include a return statement")
        if not validation_results["checks"]["has_function_definition"]:
            recommendations.append("EVALSCRIPT should define a function (e.g., evalPixel)")
        if validation_results["checks"]["length"] < 50:
            recommendations.append("EVALSCRIPT seems too short - ensure it contains proper processing logic")
        
        validation_results["recommendations"] = recommendations
        
        return validation_results
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return {
            "success": False,
            "error": f"Validation error: {str(e)}",
            "error_type": "validation_error"
        }

@mcp.tool()
def validate_evalscript(evalscript: str) -> Dict[str, Any]:
    """
    Validate an EVALSCRIPT for SentinelHub processing.
    
    Args:
        evalscript: JavaScript code to validate
    
    Returns:
        Dictionary containing validation results
    """
    return _validate_evalscript_impl(evalscript)

# MCP Protocol endpoints
@web_app.post("/mcp")
async def mcp_endpoint(request: Request):
    """Handle MCP protocol requests"""
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        
        if method == "tools/list":
            return {
                "tools": [
                    {
                        "name": "get_satellite_statistics",
                        "description": "Get statistical data from satellite imagery using SentinelHub's Statistical API",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "geometry": {"type": "object", "description": "GeoJSON geometry for area of interest"},
                                "bbox": {"type": "array", "description": "Bounding box as [minX, minY, maxX, maxY]"},
                                "time_from": {"type": "string", "description": "Start date in ISO format"},
                                "time_to": {"type": "string", "description": "End date in ISO format"},
                                "evalscript": {"type": "string", "description": "JavaScript code for data processing"},
                                "data_sources": {"type": "array", "description": "List of data source specifications"},
                                "aggregation": {"type": "object", "description": "Aggregation parameters"},
                                "calculations": {"type": "object", "description": "Calculation parameters"}
                            },
                            "required": ["time_from", "time_to", "evalscript", "data_sources"]
                        }
                    },
                    {
                        "name": "process_satellite_imagery",
                        "description": "Generate processed images from satellite data using SentinelHub's Processing API",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "geometry": {"type": "object", "description": "GeoJSON geometry for area of interest"},
                                "bbox": {"type": "array", "description": "Bounding box as [minX, minY, maxX, maxY]"},
                                "time_from": {"type": "string", "description": "Start date in ISO format"},
                                "time_to": {"type": "string", "description": "End date in ISO format"},
                                "evalscript": {"type": "string", "description": "JavaScript code for data processing"},
                                "data_sources": {"type": "array", "description": "List of data source specifications"},
                                "width": {"type": "integer", "description": "Output image width"},
                                "height": {"type": "integer", "description": "Output image height"},
                                "output_format": {"type": "string", "description": "Output format"}
                            },
                            "required": ["time_from", "time_to", "evalscript", "data_sources"]
                        }
                    },
                    {
                        "name": "get_available_data_sources",
                        "description": "Get information about available data sources in SentinelHub",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "validate_evalscript",
                        "description": "Validate an EVALSCRIPT for SentinelHub processing",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "evalscript": {"type": "string", "description": "JavaScript code to validate"}
                            },
                            "required": ["evalscript"]
                        }
                    }
                ]
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "get_satellite_statistics":
                # Call the underlying function implementation
                try:
                    # Validate required parameters
                    time_from = arguments.get("time_from")
                    time_to = arguments.get("time_to")
                    evalscript = arguments.get("evalscript")
                    data_sources = arguments.get("data_sources")
                    geometry = arguments.get("geometry")
                    bbox = arguments.get("bbox")
                    
                    if not time_from or not time_to:
                        raise ValueError("time_from and time_to are required")
                    if not evalscript:
                        raise ValueError("evalscript is required")
                    if not data_sources:
                        raise ValueError("data_sources are required")
                    if not geometry and not bbox:
                        raise ValueError("Either geometry or bbox must be provided")
                    
                    # Prepare request payload
                    payload = {
                        "time": {
                            "from": time_from,
                            "to": time_to
                        },
                        "evalscript": evalscript,
                        "data": data_sources
                    }
                    
                    # Add geometry or bbox
                    if geometry:
                        payload["geometry"] = geometry
                    elif bbox:
                        payload["bbox"] = bbox
                    
                    # Add optional parameters
                    if arguments.get("aggregation"):
                        payload["aggregation"] = arguments.get("aggregation")
                    if arguments.get("calculations"):
                        payload["calculations"] = arguments.get("calculations")
                    
                    # Get access token
                    access_token = config.get_access_token()
                    
                    # Make API request
                    headers = {
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                    
                    url = f"{SENTINELHUB_BASE_URL}/statistics"
                    response = requests.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    
                    result_data = response.json()
                    result = {
                        "success": True,
                        "data": result_data,
                        "request_info": {
                            "time_range": f"{time_from} to {time_to}",
                            "data_sources": len(data_sources),
                            "has_geometry": geometry is not None,
                            "has_bbox": bbox is not None
                        }
                    }
                except Exception as e:
                    result = {
                        "success": False,
                        "error": f"Error: {str(e)}",
                        "error_type": "api_error"
                    }
                return {"content": [{"type": "text", "text": str(result)}]}
            elif tool_name == "process_satellite_imagery":
                # Call the underlying function implementation
                try:
                    # Validate required parameters
                    time_from = arguments.get("time_from")
                    time_to = arguments.get("time_to")
                    evalscript = arguments.get("evalscript")
                    data_sources = arguments.get("data_sources")
                    geometry = arguments.get("geometry")
                    bbox = arguments.get("bbox")
                    
                    if not time_from or not time_to:
                        raise ValueError("time_from and time_to are required")
                    if not evalscript:
                        raise ValueError("evalscript is required")
                    if not data_sources:
                        raise ValueError("data_sources are required")
                    if not geometry and not bbox:
                        raise ValueError("Either geometry or bbox must be provided")
                    
                    # Prepare request payload
                    payload = {
                        "time": {
                            "from": time_from,
                            "to": time_to
                        },
                        "evalscript": evalscript,
                        "data": data_sources,
                        "format": arguments.get("output_format", "image/png")
                    }
                    
                    # Add geometry or bbox
                    if geometry:
                        payload["geometry"] = geometry
                    elif bbox:
                        payload["bbox"] = bbox
                    
                    # Add optional parameters
                    if arguments.get("width"):
                        payload["width"] = arguments.get("width")
                    if arguments.get("height"):
                        payload["height"] = arguments.get("height")
                    
                    # Get access token
                    access_token = config.get_access_token()
                    
                    # Make API request
                    headers = {
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                    
                    url = f"{SENTINELHUB_BASE_URL}/process"
                    response = requests.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    
                    # Handle different response types
                    content_type = response.headers.get('content-type', '')
                    
                    if 'image/' in content_type:
                        # Image response - return base64 encoded data
                        import base64
                        image_data = base64.b64encode(response.content).decode('utf-8')
                        result = {
                            "success": True,
                            "image_data": image_data,
                            "content_type": content_type,
                            "size_bytes": len(response.content),
                            "request_info": {
                                "time_range": f"{time_from} to {time_to}",
                                "data_sources": len(data_sources),
                                "has_geometry": geometry is not None,
                                "has_bbox": bbox is not None,
                                "output_format": arguments.get("output_format", "image/png")
                            }
                        }
                    else:
                        # JSON response
                        result_data = response.json()
                        result = {
                            "success": True,
                            "data": result_data,
                            "content_type": content_type,
                            "request_info": {
                                "time_range": f"{time_from} to {time_to}",
                                "data_sources": len(data_sources),
                                "has_geometry": geometry is not None,
                                "has_bbox": bbox is not None,
                                "output_format": arguments.get("output_format", "image/png")
                            }
                        }
                except Exception as e:
                    result = {
                        "success": False,
                        "error": f"Error: {str(e)}",
                        "error_type": "api_error"
                    }
                return {"content": [{"type": "text", "text": str(result)}]}
            elif tool_name == "get_available_data_sources":
                # Call the underlying function implementation
                try:
                    # Get access token
                    access_token = config.get_access_token()
                    
                    # Make API request
                    headers = {
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                    
                    url = f"{SENTINELHUB_BASE_URL}/data"
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    
                    data_sources = response.json()
                    
                    result = {
                        "success": True,
                        "data_sources": data_sources,
                        "count": len(data_sources) if isinstance(data_sources, list) else 1
                    }
                except requests.exceptions.RequestException as e:
                    result = {
                        "success": False,
                        "error": f"API request failed: {str(e)}",
                        "error_type": "api_error"
                    }
                except Exception as e:
                    result = {
                        "success": False,
                        "error": f"Unexpected error: {str(e)}",
                        "error_type": "unexpected_error"
                    }
                return {"content": [{"type": "text", "text": str(result)}]}
            elif tool_name == "validate_evalscript":
                result = _validate_evalscript_impl(arguments.get("evalscript", ""))
                return {"content": [{"type": "text", "text": str(result)}]}
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        else:
            return {"error": f"Unknown method: {method}"}
            
    except Exception as e:
        return {"error": str(e)}

# Web interface endpoints
@web_app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    try:
        # Test configuration
        config = SentinelHubConfig()
        has_credentials = bool(config.client_id and config.client_secret)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "credentials_configured": has_credentials,
            "mcp_tools": [
                "get_satellite_statistics",
                "process_satellite_imagery", 
                "get_available_data_sources",
                "validate_evalscript"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@web_app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with server information"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SentinelHub MCP Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; }
            .status { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .tools { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .tool { margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #3498db; }
            .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛰️ SentinelHub MCP Server</h1>
            
            <div class="status">
                <h3>✅ Server Status: Running</h3>
                <p>This MCP server provides access to SentinelHub's Statistical and Processing APIs through the Model Context Protocol.</p>
            </div>
            
            <div class="tools">
                <h3>🔧 Available MCP Tools</h3>
                <div class="tool">
                    <strong>get_satellite_statistics</strong> - Get statistical data from satellite imagery
                </div>
                <div class="tool">
                    <strong>process_satellite_imagery</strong> - Generate processed images from satellite data
                </div>
                <div class="tool">
                    <strong>get_available_data_sources</strong> - Get information about available data sources
                </div>
                <div class="tool">
                    <strong>validate_evalscript</strong> - Validate JavaScript processing scripts
                </div>
            </div>
            
            <div class="footer">
                <p><strong>Version:</strong> 1.0.0</p>
                <p><strong>Documentation:</strong> <a href="https://github.com/your-repo/sentinelhub-mcp">GitHub Repository</a></p>
                <p><strong>Health Check:</strong> <a href="/health">/health</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@web_app.get("/tools")
async def list_tools():
    """List available MCP tools"""
    return {
        "tools": [
            {
                "name": "get_satellite_statistics",
                "description": "Get statistical data from satellite imagery using SentinelHub's Statistical API",
                "parameters": ["geometry", "bbox", "time_from", "time_to", "evalscript", "data_sources", "aggregation", "calculations"]
            },
            {
                "name": "process_satellite_imagery", 
                "description": "Generate processed images from satellite data using SentinelHub's Processing API",
                "parameters": ["geometry", "bbox", "time_from", "time_to", "evalscript", "data_sources", "width", "height", "output_format"]
            },
            {
                "name": "get_available_data_sources",
                "description": "Get information about available data sources in SentinelHub",
                "parameters": []
            },
            {
                "name": "validate_evalscript",
                "description": "Validate an EVALSCRIPT for SentinelHub processing",
                "parameters": ["evalscript"]
            }
        ]
    }

def run_server():
    """Run both MCP and web servers"""
    import threading
    import asyncio
    
    # Run MCP server in a separate thread
    def run_mcp():
        mcp.run()
    
    # Run web server in main thread
    def run_web():
        port = int(os.getenv("PORT", 8000))
        uvicorn.run(web_app, host="0.0.0.0", port=port)
    
    # Start MCP server in background thread
    mcp_thread = threading.Thread(target=run_mcp, daemon=True)
    mcp_thread.start()
    
    # Run web server in main thread
    run_web()

if __name__ == "__main__":
    # Check if we should run in web mode (for Railway deployment)
    if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PORT"):
        run_server()
    else:
        # Run MCP server only (for local development)
        mcp.run()
