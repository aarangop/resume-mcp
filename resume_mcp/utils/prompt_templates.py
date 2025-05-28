default_template = """# Advanced CV Tailoring Prompt Template

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

default_latex_cv_template = r"""
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


cv_generation_recipe_template = """
# CV Generation Recipe 🎯

*A comprehensive guide for generating tailored CVs using the resume-mcp server*

## 🚀 Quick Start (Automatic Generation)

**Input Required:**
- Job description (text or URL)
- Company name
- Position title

**Primary Command:**
```
generate_tailored_cv(job_description="[FULL_JOB_DESCRIPTION]", company="[COMPANY_NAME]", position="[POSITION_TITLE]")
```

This will automatically:
1. Analyze the job description
2. Search your Obsidian vault for relevant experience
3. Generate both markdown and PDF versions
4. Save to your Obsidian vault under appropriate naming

---

## 🔧 Manual Process (When Automatic Fails)

### Step 1: System Health Check
```
validate_configuration()
validate_latex_setup()
get_server_status()
```

**Troubleshooting Common Issues:**
- **LaTeX not found:** Install TeX Live/MacTeX for PDF generation
- **Template issues:** Use `reload_templates()` after fixes
- **Obsidian errors:** Check vault path and permissions

### Step 2: Research and Analysis

In this step we gather data about the job. We need to get:
- a job description
- a company, and
- a position

Example: Machine Learning Engineer at Twilio

In order to get this data we can leverage MCP tools to extract
data from the user's Obsidian vault (or local file system),
or ask for manual input.

In this step we also need the user's 'baseline experience'. This 
can be searched for in the obsidian vault under "Baseline Experience",
or can be provided by the user manually.

#### MCP tool
```
search_job_description(job_description="$position $company")
```

**What to look for:**
- Similar positions you've applied for
- Relevant projects and experiences
- Industry-specific keywords
- Technical skills alignment

### Step 3a: Automatic CV generation

With the experience baseline, a job description, a company and a position,
we can attempt to automatically generate a tailor-made CV using the 
anthropic API.

```
generate_tailored_cv(job_description="$job_description", company="$company", "$position")
```

### Step 3b: Generate Custom Prompt

If automatic generation fails, create content manually using this structure:

```
generate_cv_prompt(
    job_description="[FULL_DESCRIPTION]",
    company="[COMPANY]", 
    position="[POSITION]",
    prompt_name="[COMPANY]_[POSITION]_prompt"
)
```

### Step 4: Save and Compile
```
save_obsidian_file(content="[CV_CONTENT]", filename="[COMPANY]_[POSITION]_CV.md", vault_dir="CV")
save_cv_pdf(content="[LATEX_CONTENT]", filename="[COMPANY]_[POSITION]_CV", vault_dir="CV")
```

---

## 🎯 Optimization Strategies

### For Tech Roles:
- Emphasize relevant programming languages (Python, TypeScript)
- Highlight full-stack capabilities
- Include data science/AI projects
- Mention your Substack publication for thought leadership

### For Different Company Types:
- **Startups:** Emphasize versatility, rapid learning, full-stack skills
- **Large Corps:** Focus on scale, collaboration, specific tech stacks
- **AI/ML Companies:** Highlight data science background, AI experience
- **Media/Content:** Leverage your Substack writing experience

### Keyword Optimization:
1. Extract key terms from job description
2. Map to your experience using `search_job_description()`
3. Ensure 70%+ keyword match without keyword stuffing
4. Use variations and synonyms naturally

---

## 🔍 Quality Assurance Checklist

### Content Validation:
- [ ] All placeholder values filled correctly
- [ ] Company name and position title accurate
- [ ] Contact information current
- [ ] No spelling/grammar errors
- [ ] Quantified achievements where possible

### Technical Validation:
- [ ] LaTeX compiles without errors
- [ ] PDF formatting looks professional
- [ ] All sections render properly
- [ ] File saved in correct Obsidian location

### Alignment Check:
- [ ] Skills match job requirements
- [ ] Experience relevance is clear
- [ ] Professional summary is targeted
- [ ] Length appropriate (1-2 pages)

---

## 🆘 Emergency Procedures

### When Automatic Generation Fails:
1. Check `debug_resources()` for vault access
2. Verify job description isn't too long/short
3. Try breaking down into manual steps
4. Use `fuzzy_search_obsidian()` to find similar positions

### When LaTeX Compilation Fails:
1. Install missing LaTeX packages
2. Check template placeholders with `get_latex_template_info()`
3. Use markdown version as fallback
4. Manual PDF conversion if needed

### When Obsidian Integration Breaks:
1. Verify vault path in configuration
2. Check file permissions
3. Restart MCP server
4. Fall back to local file operations

---

## 💡 Advanced Tips

### Batch Processing:
For multiple applications, use consistent naming:
- `[COMPANY]_[POSITION]_[DATE]_CV.pdf`
- `[COMPANY]_[POSITION]_prompt.md`

### Template Customization:
- Modify LaTeX template for different industries
- Create industry-specific skill sections
- Adjust formatting for different role levels

### Content Reuse:
- Maintain a "master experiences" document
- Create reusable project descriptions
- Build a library of achievement statements

### Analytics:
- Track which CV versions get responses
- Note successful keyword combinations
- Iterate based on feedback

---

## 🔄 Continuous Improvement

1. **After Each Application:**
   - Save successful CV variants
   - Note effective customizations
   - Update master templates

2. **Monthly Review:**
   - Update baseline resume
   - Refresh skill keywords
   - Clean up Obsidian vault

3. **System Maintenance:**
   - Update LaTeX packages
   - Backup CV templates
   - Test all MCP functions

Since the automatic generation of CVs uses the anthropic API, it incurrs costs.
Try to avoid using this tool too much and default to manual methods if it fails
to avoid consuming too much user credits.

---

*Remember: The best CV is one that's specifically tailored to each opportunity while maintaining authenticity to your experience and career narrative.*
"""
