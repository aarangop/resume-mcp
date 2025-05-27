#!/usr/bin/env python3
"""
Main entry point for running the resume tailoring MCP server
"""

import logging
from resume_mcp.server import mcp

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Run the server
    mcp.run(transport="stdio")
