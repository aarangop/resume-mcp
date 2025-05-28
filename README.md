# Resume MCP Server

A Model Context Protocol (MCP) server for AI-powered resume tailoring. This
service lets you tailor your resume/CV for specific job descriptions
automatically, creating both Markdown and LaTeX/PDF versions optimized for ATS
systems.

## 🚀 Features

- **Resume Tailoring**: Generate custom resumes targeting specific job
  descriptions
- **LaTeX Support**: Export to professional PDF format using LaTeX templates
- **Obsidian Integration**: Search and manage files from your Obsidian vault
- **Career Guidance**: Get feedback on your resume and career options
- **MCP Protocol**: Follows the Model Context Protocol for seamless AI
  integration

## 📋 Prerequisites

- Python 3.10 or higher
- LaTeX installation (for PDF generation)
- Node.js/npm (for MCP Inspector)
- Obsidian (optional, for vault integration)
  - If not using Obsidian, you can use any directory on your file system, just
    make sure to set the `OBSIDIAN_VAULT` variable in your `.env` file.

## ⚙️ Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/resume-mcp.git
   cd resume-mcp
   ```

2. Install the required Python dependencies:

   ```bash
   pip install -r requirements.txt
   # Or using uv (recommended for better dependency resolution)
   uv pip install -e .
   ```

3. Install the MCP Inspector (for debugging/development):
   ```bash
   npm install -g @modelcontextprotocol/inspector
   ```

## 🔧 Configuration

Create a `.env` file in the root directory with the following variables (or
configure them in your environment):

```env
# Server configuration
SERVER_NAME="Resume Tailoring Server"

# File paths
BASELINE_RESUME_PATH="./templates/baseline_resume.md"
PROMPT_TEMPLATE_PATH="./templates/prompt_template.md"
LATEX_TEMPLATE_PATH="./templates/latex_template.tex"
OUTPUT_DIRECTORY="./templates/tailored_resumes"

# Obsidian vault configuration (optional)
OBSIDIAN_VAULT="/path/to/your/obsidian/vault"

# LaTeX configuration
LATEX_COMPILER="pdflatex"  # or xelatex, lualatex
LATEX_OUTPUT_DIR="./templates/latex_output"

# Logging
LOG_LEVEL="INFO"

# Anthropic API key (if using Anthropic models)
ANTHROPIC_API_KEY="your_anthropic_api_key"
```

## 🏃‍♂️ Running the Server

### Standard Mode

To run the server in standard mode:

```bash
python main.py
```

The server will start in stdio transport mode, which allows it to be connected
to any MCP-compatible client.

### With Inspector (Development/Debug Mode)

For development and testing, you can run the server with the MCP Inspector:

```bash
# Using the provided script
./inspect.sh

# Or manually
npx @modelcontextprotocol/inspector uv --directory /Users/andresap/repos/resume-mcp run main.py
```

### Debugging Issues

If you're experiencing server problems, you can run the debug script:

```bash
python debug_server.py
```

This will perform various checks on your setup and help identify any issues.

## 🧠 Using the Resume MCP Server

The server provides several prompts and tools for resume tailoring:

### Prompts

1. **Tailor CV** - Create a customized resume based on a job description
2. **Career Guidance** - Get career advice and resume feedback

### Tools

1. **Management Tools**:

   - `list_templates`: List available templates
   - `get_baseline_resume`: Retrieve your baseline resume

2. **Validation Tools**:

   - `validate_latex_template`: Check if your LaTeX template is valid

3. **Obsidian Tools**:

   - `search_obsidian`: Search files in your Obsidian vault
   - `read_obsidian_file`: Read content from an Obsidian file

4. **CV Tools**:
   - `save_tailored_cv`: Save a tailored CV in Markdown format
   - `generate_latex_cv`: Convert a tailored CV to LaTeX/PDF

## 📄 Template Files

### Baseline Resume

Your starting resume in Markdown format from which tailored versions are
created.

### Prompt Template

Template used for generating the resume tailoring instructions.

### LaTeX Template

LaTeX template for generating professional PDFs. Must include required
placeholders like `$name`.

## 📚 Example Workflow

1. Set up your baseline resume in `templates/baseline_resume.md`
2. Configure your LaTeX template in `templates/latex_template.tex`
3. Run the server: `python main.py`
4. Connect with an MCP client (such as an integrated LLM)
5. Submit a job description to the "Tailor CV" prompt
6. Generate a LaTeX/PDF version using the CV tools
7. Review and use your tailored resume!

## 🔍 Troubleshooting

### LaTeX Template Issues

If you see warnings about missing placeholders in your LaTeX template, check
that it includes all required fields like `$name`.

### Initialization Problems

If you encounter
`RuntimeError: Received request before initialization was complete`, try:

1. Adding a small delay after importing components
2. Using the debug server to identify issues
3. Make sure all imports are properly structured

### MCP Connection Issues

If clients cannot connect to the server:

1. Check that stdio transport is working correctly
2. Verify that all required components are imported
3. Run with the inspector for detailed logs

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for
details.
