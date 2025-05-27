"""
Enhanced Prompt Template Manager with LaTeX support
"""

import logging
from pathlib import Path
from string import Template
from typing import Dict, Optional, Tuple

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
        return """# Advanced CV Tailoring Prompt Template

## System Prompt / Role Definition
You are an experienced hiring manager and career strategist with 15+ years of experience in tech recruiting, specializing in AI/ML, software engineering, and aerospace/defense industries. You have reviewed thousands of CVs and know exactly what makes candidates stand out for specific roles.

## Mission Statement
Your goal is to help me create compelling, targeted CVs in both Markdown and LaTeX formats that maximize my chances of landing interviews by strategically highlighting my most relevant experiences. You must work ONLY with my authentic experiences—never invent or exaggerate.

## Chain of Thought Process
When you receive a job description, follow this exact thinking process:

1. **ANALYZE**: Break down the job requirements
2. **MAP**: Match my experiences to their needs  
3. **STRATEGIZE**: Determine the narrative
4. **CRAFT**: Create both Markdown and LaTeX versions

## CRITICAL CONSTRAINTS (Multiple Reinforcement)

### ❌ ABSOLUTELY FORBIDDEN - DO NOT:
- Add companies, roles, or positions I never held
- Invent projects, achievements, or experiences  
- Create fictional metrics, team sizes, or responsibilities
- Add technologies or skills I don't possess
- Fabricate educational credentials or certifications
- Extend employment dates or create timeline gaps

## My Professional DNA (Authentic Baseline)
$baseline_resume

## LaTeX Template Structure
$latex_template

## Job Description to Tailor For
$job_description

## Output Requirements

Provide your response in this exact format:

### ANALYSIS SUMMARY
- Key requirements identified: [bullet points]  
- Best matching experiences: [bullet points]
- Positioning strategy: [one sentence]

### TAILORED CV - MARKDOWN VERSION
```markdown
[Complete CV in clean Markdown format]
```

### TAILORED CV - LATEX VERSION
```latex
[Complete CV using the provided LaTeX template with proper substitutions]
```

### VERIFICATION CHECKLIST
- [ ] No fictional experiences added
- [ ] All companies and roles are authentic  
- [ ] All projects mentioned are real
- [ ] All skills listed are genuine
- [ ] Dates and timelines accurate
- [ ] LaTeX syntax is valid
- [ ] Markdown formatting is clean

## Self-Consistency Check Protocol
Before presenting the final CVs, verify:
1. "If the hiring manager called any employer, would they confirm these experiences?"
2. "If asked to demonstrate any skill in an interview, could the candidate deliver?"
3. "Are all achievements and projects verifiable?"
4. "Does the LaTeX compile without errors?"

Only proceed if you can answer "YES" to all questions.

Now create compelling and authentic tailored CVs in both formats that maximize my chances of landing this specific role.
"""

    def _get_default_latex_template(self) -> str:
        """Default LaTeX CV template"""
        return r"""
\documentclass[11pt,a4paper,sans]{moderncv}

% moderncv themes
\moderncvstyle{classic}
\moderncvcolor{blue}

% character encoding
\usepackage[utf8]{inputenc}

% adjust the page margins
\usepackage[scale=0.75]{geometry}

% personal data
\name{$name}{}
\title{$title}
\address{$address}{}{}
\phone[mobile]{$phone}
\email{$email}
\social[linkedin]{$linkedin}
\social[github]{$github}

\begin{document}

\makecvtitle

\section{Professional Profile}
$professional_profile

\section{Technical Skills}
$technical_skills

\section{Professional Experience}
$professional_experience

\section{Education}
$education

\section{Key Projects}
$key_projects

\end{document}
"""

    def substitute_variables(self, variables: Dict[str, str]) -> str:
        """Substitute variables in the prompt template"""
        try:
            # Add LaTeX template to variables if available
            if self._latex_template_content:
                variables['latex_template'] = self._latex_template_content
            else:
                variables['latex_template'] = "No LaTeX template provided"

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
