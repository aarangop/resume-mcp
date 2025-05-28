import logging
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Dict, Optional

from resume_mcp.config import OBSIDIAN_VAULT

logger = logging.getLogger(__name__)


def compile_latex(content: str, dest: str) -> Dict:

    dest_path = Path(dest)
    dest_stem = dest_path.stem
    # Create temporary directory for LaTeX compilation
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write LaTeX content to temporary file
        tex_file = os.path.join(temp_dir, f"{dest_stem}.tex")

        logger.info(f"Saving temp source file to '{tex_file}'")

        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(content)
            logger.info(f"LaTeX source written to '{tex_file}'")

        try:
            # Compile LaTeX to PDF
            logger.info(f"Compiling LaTeX to PDF: {tex_file}")

            process = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode",
                    "-output-directory", temp_dir, tex_file],
                capture_output=True,
                text=True
            )

            if process.returncode != 0:
                logger.error(f"LaTeX compilation error: {process.stderr}")
                return {"error": f"❌ LaTeX compilation failed: {process.stderr[:500]}..."}

            # Run twice to resolve references if needed
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode",
                    "-output-directory", temp_dir, tex_file],
                capture_output=True
            )

            # Copy the generated PDF to the target location
            temp_pdf = os.path.join(temp_dir, f"{dest_stem}.pdf")
            if os.path.exists(temp_pdf):
                shutil.copy2(temp_pdf, dest)
                logger.info(f"PDF saved to: {dest}")
                return {"success": {"dest": dest}}
            else:
                return {"error": "Error saving PDF."}

        except Exception as e:
            logger.error(f"Error creating PDF: {str(e)}")
            return {"error": f"❌ Error creating PDF: {str(e)}"}
