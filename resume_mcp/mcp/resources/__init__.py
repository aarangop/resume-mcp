"""
Resources Module - Obsidian and other data resources
"""

import logging

# Import all resource modules to ensure decorators are applied

try:
    from . import resources
    logger = logging.getLogger(__name__)
    logger.info("✅ General resources loaded")
except ImportError as e:
    logging.getLogger(__name__).info("ℹ️ No general resources module found")

__all__ = ['resources']
