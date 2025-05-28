#!/usr/bin/env python3
"""
Main entry point for running the resume tailoring MCP server
"""

import logging
# Import mcp server
from resume_mcp.mcp.base import mcp

# Import the tools, prompts, resources, etc. that you want to make available
import resume_mcp.mcp.prompts.resume_tailoring
import resume_mcp.mcp.resources
import resume_mcp.mcp.tools

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Allow a moment for all registrations to complete
    # This can help ensure initialization completes before accepting connections
    logging.info("Ensuring all components are registered...")

    # Run the server
    mcp.run(transport="stdio")
