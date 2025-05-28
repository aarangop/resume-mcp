"""
Enhanced Prompt Template Manager with LaTeX support
"""

import logging
from pathlib import Path
from string import Template
from typing import Dict, Optional, Tuple
import resume_mcp.utils.prompt_templates as default_templates

logger = logging.getLogger(__name__)


class PromptTemplateManager:
    """Handles prompt template loading and variable substitution for both Markdown and LaTeX"""

    def __init__(self, template_path: str, latex_template_path: Optional[str] = None):
        self.template_path = Path(template_path)
        self.latex_template_path = Path(
            latex_template_path) if latex_template_path else None

        self._template_content = None
        self._latex_template_content = None

        self._load_templates()

    def _load_templates(self):
        """Load both prompt and LaTeX templates"""
        self._load_prompt_template()
        if self.latex_template_path:
            self._load_latex_template()

    def _load_prompt_template(self):
        """Load the prompt template from file"""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                self._template_content = f.read()
            logger.info(f"Loaded prompt template from {self.template_path}")
        except FileNotFoundError:
            logger.error(
                f"Prompt template file not found: {self.template_path}")
            self._template_content = self._get_default_template()
        except Exception as e:
            logger.error(f"Error loading prompt template: {e}")
            self._template_content = self._get_default_template()

    def _load_latex_template(self):
        """Load the LaTeX template from file"""
        try:
            if not self.latex_template_path:
                raise Exception("LaTeX template path not provided")
            with open(self.latex_template_path, 'r', encoding='utf-8') as f:
                self._latex_template_content = f.read()
            logger.info(
                f"Loaded LaTeX template from {self.latex_template_path}")
        except FileNotFoundError:
            logger.warning(
                f"LaTeX template file not found: {self.latex_template_path}")
            self._latex_template_content = self._get_default_latex_template()
        except Exception as e:
            logger.error(f"Error loading LaTeX template: {e}")
            self._latex_template_content = self._get_default_latex_template()

    def _get_default_template(self) -> str:
        """Enhanced default template with LaTeX support"""
        return default_templates.default_template

    def _get_default_latex_template(self) -> str:
        """Default LaTeX CV template"""
        return default_templates.default_latex_cv_template

    def substitute_variables(self, variables: Dict[str, str]) -> str:
        """
        Substitute variables in the prompt template.

        This method replaces placeholders in the template content with provided values.
        It automatically adds the LaTeX template to the variables if available.

        Args:
            variables: A dictionary mapping variable names to their values.
                       Must contain 'job_description', 'company', and 'position' keys.

        Returns:
            str: The prompt template with all variables substituted.

        Raises:
            ValueError: If any required variables are missing.
            Exception: If no template content is available.
        """
        """Substitute variables in the prompt template"""
        try:
            # Add LaTeX template to variables if available
            if self._latex_template_content:
                variables['latex_template'] = self._latex_template_content
            else:
                variables['latex_template'] = "No LaTeX template provided"

            required_variables = ['company', 'position']

            for required in required_variables:
                if not required in variables:
                    raise ValueError(f"Missing '{required}' in variables.")

            if not self._template_content:
                raise Exception("No template content found")

            template = Template(self._template_content)
            return template.safe_substitute(variables)
        except Exception as e:
            logger.error(f"Error substituting template variables: {e}")
            raise

    def substitute_latex_variables(self, variables: Dict[str, str]) -> str:
        """Substitute variables in the LaTeX template"""
        if not self._latex_template_content:
            raise ValueError("No LaTeX template loaded")

        try:
            template = Template(self._latex_template_content)
            return template.safe_substitute(variables)
        except Exception as e:
            logger.error(f"Error substituting LaTeX template variables: {e}")
            raise

    def get_latex_template(self) -> Optional[str]:
        """Get the raw LaTeX template content"""
        return self._latex_template_content

    def reload_templates(self):
        """Reload both templates from files"""
        self._load_templates()

    def validate_latex_template(self) -> Tuple[bool, str]:
        """Validate LaTeX template has required placeholders"""
        if not self._latex_template_content:
            return False, "No LaTeX template loaded"

        required_placeholders = ['$name', '$email', '$professional_experience']
        missing = []

        for placeholder in required_placeholders:
            if placeholder not in self._latex_template_content:
                missing.append(placeholder)

        if missing:
            return False, f"Missing required placeholders: {', '.join(missing)}"

        return True, "LaTeX template is valid"
