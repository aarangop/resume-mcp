"""
MCP Server Module - Centralizes all MCP components
"""

import logging

# # Import the base server first
from .base import mcp

# # Import all modules to register their decorators with the mcp instance
# # This is CRITICAL - without these imports, the decorators won't be applied!
# from .prompts import resume_tailoring, career_guidance
# from .tools import cv, management_tools, validation_tools, obsidian_tools

logger = logging.getLogger(__name__)

# try:
#     from .resources import resources
#     logger.info("✅ General resources imported successfully")
# except ImportError as e:
#     logger.info("ℹ️ No general resources module found, skipping")


# Export the configured mcp instance
__all__ = ['mcp']

logger.info("MCP server module initialized with all components")
