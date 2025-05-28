#!/usr/bin/env python3
"""
Debug script to test MCP server components
"""

import sys
import logging
from pathlib import Path

from resume_mcp.mcp.tools import management

# Configure logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def debug_imports():
    """Test all imports to find issues"""
    logger.info("Testing imports...")

    try:
        logger.info("✅ Testing config import...")
        from resume_mcp.config import SERVER_NAME, BASELINE_RESUME_PATH
        logger.info(f"   Server name: {SERVER_NAME}")
        logger.info(f"   Resume path: {BASELINE_RESUME_PATH}")

        logger.info("✅ Testing utils imports...")
        from resume_mcp.utils.prompt_manager import PromptTemplateManager
        from resume_mcp.utils.resume_manager import ResumeManager
        logger.info("   Utils imported successfully")

        logger.info("✅ Testing base MCP server...")
        from resume_mcp.mcp.base import mcp, get_app_context
        logger.info(f"   MCP server created: {mcp}")

        logger.info("✅ Testing prompts...")
        from resume_mcp.mcp.prompts import resume_tailoring, career_guidance
        logger.info("   Prompts imported successfully")

        logger.info("✅ Testing tools...")
        from resume_mcp.mcp.tools import validation
        logger.info("   Tools imported successfully")

        logger.info("✅ Testing main MCP module...")
        from resume_mcp.mcp import mcp as main_mcp
        logger.info(f"   Main MCP instance: {main_mcp}")

        # Check if prompts and tools are registered
        logger.info("✅ Checking registered components...")

        # This will help us see what's actually registered
        logger.info(f"   MCP instance type: {type(main_mcp)}")

        return True

    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        logger.error(f"   Error type: {type(e)}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")
        return False


def debug_files():
    """Check if required files exist"""
    logger.info("Checking required files...")

    files_to_check = [
        "./templates/baseline_resume.md",
        "./templates/prompt_template.md",
        "./templates/latex_template.tex",
        "./resume_mcp/__init__.py",
        "./resume_mcp/config.py",
        "./resume_mcp/mcp/__init__.py",
        "./resume_mcp/mcp/base.py",
        "./resume_mcp/utils/prompt_manager.py",
        "./resume_mcp/utils/resume_manager.py"
    ]

    missing_files = []
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            logger.info(f"✅ Found: {file_path}")
        else:
            logger.error(f"❌ Missing: {file_path}")
            missing_files.append(file_path)

    return len(missing_files) == 0


def main():
    """Main debug function"""
    logger.info("🔍 Starting MCP Server Debug...")

    # Check Python path
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Current working directory: {Path.cwd()}")

    # Check files
    files_ok = debug_files()

    # Check imports
    imports_ok = debug_imports()

    if files_ok and imports_ok:
        logger.info("🎉 All checks passed! Server should work.")

        # Try to get the MCP instance
        try:
            from resume_mcp.mcp import mcp
            logger.info(f"✅ MCP server ready: {mcp}")

            # You could add more specific checks here

        except Exception as e:
            logger.error(f"❌ Failed to get MCP instance: {e}")

    else:
        logger.error("❌ Some checks failed. Fix the issues above.")


if __name__ == "__main__":
    main()
