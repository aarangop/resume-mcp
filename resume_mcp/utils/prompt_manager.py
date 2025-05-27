#!/usr/bin/env python3
"""
Prompt template management for resume tailoring
"""

import logging
from pathlib import Path
from string import Template

# Configure logging
logger = logging.getLogger(__name__)


class PromptTemplateManager:
    """Handles prompt template loading and variable substitution"""

    def __init__(self, template_path: str):
        self.template_path = Path(template_path)
        self._template_content = None
        self._load_template()

    def _load_template(self):
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

    def _get_default_template(self) -> str:
        """Fallback default template"""
        return """# Advanced CV Tailoring Prompt Template

## System Prompt / Role Definition
You are an experienced hiring manager and career strategist with 15+ years of experience in tech recruiting, specializing in AI/ML, software engineering, and aerospace/defense industries. You have reviewed thousands of CVs and know exactly what makes candidates stand out for specific roles.

## CRITICAL CONSTRAINTS
❌ ABSOLUTELY FORBIDDEN - DO NOT:
- Add companies, roles, or positions I never held
- Invent projects, achievements, or experiences  
- Create fictional metrics, team sizes, or responsibilities
- Add technologies or skills I don't possess

## My Professional Information:
$baseline_resume

## Job Description to Tailor For:
$job_description

## Your Task:
Create a tailored CV that emphasizes the most relevant aspects of my experience for this specific role while maintaining 100% authenticity.

Please provide:
1. **ANALYSIS SUMMARY**: Key requirements and how my experience maps to them
2. **TAILORED CV**: The optimized resume
3. **VERIFICATION**: Confirm no fictional content was added
"""

    def substitute_variables(self, variables: dict[str, str]) -> str:
        """Substitute variables in the template"""
        try:
            if not self._template_content:
                return ""
            template = Template(self._template_content)
            return template.safe_substitute(variables)
        except Exception as e:
            logger.error(f"Error substituting template variables: {e}")
            raise

    def reload_template(self):
        """Reload template from file (useful for development)"""
        self._load_template()
