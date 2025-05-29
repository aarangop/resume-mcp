"""
MCP Server Module - Centralizes all MCP components
"""

import logging

# # Import the base server first
from .base import mcp

logger = logging.getLogger(__name__)

# Export the configured mcp instance
__all__ = ['mcp']

logger.info("MCP server module initialized with all components")
