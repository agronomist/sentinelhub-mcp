#!/usr/bin/env python3
"""
Test script for the SentinelHub MCP Server

This script tests the basic functionality of the MCP server without
requiring actual SentinelHub credentials.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sentinelhub_mcp import SentinelHubConfig

# Import the actual function implementations
import sentinelhub_mcp
from examples import NDVI_EVALSCRIPT, NDWI_EVALSCRIPT, TRUE_COLOR_EVALSCRIPT

def test_evalscript_validation():
    """Test EVALSCRIPT validation functionality"""
    print("Testing EVALSCRIPT validation...")
    
    # Test valid EVALSCRIPT
    result = sentinelhub_mcp._validate_evalscript_impl(NDVI_EVALSCRIPT)
    print(f"NDVI EVALSCRIPT validation: {result['success']}")
    if not result['success']:
        print(f"Error: {result['error']}")
    
    # Test empty EVALSCRIPT
    result = sentinelhub_mcp._validate_evalscript_impl("")
    print(f"Empty EVALSCRIPT validation: {result['success']}")
    if not result['success']:
        print(f"Expected error: {result['error']}")
    
    # Test invalid EVALSCRIPT
    result = sentinelhub_mcp._validate_evalscript_impl("invalid javascript code")
    print(f"Invalid EVALSCRIPT validation: {result['success']}")
    if not result['success']:
        print(f"Expected error: {result['error']}")
    
    print("EVALSCRIPT validation tests completed.\n")

def test_config_initialization():
    """Test configuration initialization"""
    print("Testing configuration initialization...")
    
    try:
        config = SentinelHubConfig()
        print(f"Configuration initialized successfully")
        print(f"Client ID set: {config.client_id is not None}")
        print(f"Client Secret set: {config.client_secret is not None}")
        print(f"Access token: {config.access_token is not None}")
    except Exception as e:
        print(f"Configuration error: {e}")
    
    print("Configuration tests completed.\n")

def test_evalscript_examples():
    """Test example EVALSCRIPTS"""
    print("Testing example EVALSCRIPTS...")
    
    evalscripts = {
        "NDVI": NDVI_EVALSCRIPT,
        "NDWI": NDWI_EVALSCRIPT,
        "True Color": TRUE_COLOR_EVALSCRIPT
    }
    
    for name, script in evalscripts.items():
        result = sentinelhub_mcp._validate_evalscript_impl(script)
        print(f"{name} EVALSCRIPT: {'✓' if result['success'] else '✗'}")
        if result['success']:
            checks = result['checks']
            print(f"  - Length: {checks['length']} characters")
            print(f"  - Lines: {checks['line_count']}")
            print(f"  - Has return: {checks['has_return_statement']}")
            print(f"  - Has function: {checks['has_function_definition']}")
        else:
            print(f"  - Error: {result['error']}")
    
    print("Example EVALSCRIPT tests completed.\n")

def main():
    """Run all tests"""
    print("SentinelHub MCP Server Tests")
    print("=" * 40)
    print()
    
    test_evalscript_validation()
    test_config_initialization()
    test_evalscript_examples()
    
    print("All tests completed!")
    print("\nNote: To test API functionality, you need to:")
    print("1. Set up SentinelHub credentials in .env file")
    print("2. Run the MCP server: python sentinelhub_mcp.py")
    print("3. Use an MCP client to interact with the server")

if __name__ == "__main__":
    main()
