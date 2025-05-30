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
- Docker or Podman (for LaTeX compilation service)
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

3. Start the LaTeX compilation server (required for PDF generation):

   ```bash
   # Using Docker
   cd latex-compilation-server
   docker-compose up -d
   cd ..

   # OR using Podman
   cd latex-compilation-server
   podman-compose up -d
   cd ..
   ```

   You can verify the server is running with:

   ```bash
   curl http://localhost:7474/health
   ```

4. Install the MCP Inspector (for debugging/development):
   ```bash
   npm install -g @modelcontextprotocol/inspector
   ```

### Initial Repository Setup

If you cloned the repository without the `--recursive` flag, you might need to
initialize the LaTeX compilation server submodule:

```bash
git submodule init
git submodule update
```

This ensures that you have the complete LaTeX compilation server code in the
`latex-compilation-server` directory.

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

# LaTeX compilation server configuration
LATEX_SERVER_URL="http://localhost:7474"
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
npx @modelcontextprotocol/inspector uv run main.py
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

The easiest way to interact with the server is through the provided prompts:

1. **Tailor CV** - Create a customized resume based on a job description
2. **Career Guidance** - Get career advice and resume feedback

These prompts need templates to be present in your system, and configured
through an .env file.

Alternatively, you can modify the prompts to make the LLM ask you for the
required input. You can also make use of the MCP tools to access files in your
file system with relevant information, such as your baseline resume or job
descriptions.

### Tools

1. **Management Tools**:

   - `list_templates`: List available templates
   - `get_baseline_resume`: Retrieve your baseline resume

2. **Validation Tools**:

   - `validate_latex_template`: Check if your LaTeX template is valid
   - `check_latex_server`: Check if the LaTeX compilation server is available
   - `check_latex_server_status`: Get detailed status of the LaTeX server
   - `start_latex_server_help`: Get instructions for starting the LaTeX server

3. **Obsidian Tools**:

   - `search_obsidian`: Search files in your Obsidian vault
   - `read_obsidian_file`: Read content from an Obsidian file

4. **CV Tools**:
   - `save_tailored_cv`: Save a tailored CV in Markdown format
   - `generate_latex_cv`: Convert a tailored CV to LaTeX/PDF using the secure
     containerized LaTeX compilation server

## 🖨️ LaTeX Compilation Server

This project includes a containerized LaTeX compilation service that securely
generates PDF files from LaTeX documents without requiring LaTeX installation on
your local system. The service runs as a separate microservice in a Docker
container and is included in this repository as a submodule in the
`latex-compilation-server` directory.

### Benefits:

- **Security**: Isolates LaTeX compilation in a Docker container, preventing
  potential system command exploitation
- **Consistency**: Works the same across all platforms (macOS, Windows, Linux)
- **Simplified Setup**: No need to install LaTeX and its dependencies locally

### How it Works:

1. The MCP server sends LaTeX content to the containerized HTTP service
2. The service compiles the document in an isolated environment
3. The compiled PDF is returned to the MCP server
4. The PDF is saved to your specified output directory

For detailed architecture information, see
[LaTeX Server Architecture](/docs/latex_server_architecture.md)

### Management:

Start/stop the service with Docker:

```bash
cd latex-compilation-server
docker-compose up -d    # Start server
docker-compose down     # Stop server
docker-compose logs -f  # View logs
```

Or with Podman:

```bash
cd latex-compilation-server
podman-compose up -d    # Start server
podman-compose down     # Stop server
podman-compose logs -f  # View logs
```

## 🛡️ Security Considerations

### LaTeX Compilation Security

This project uses a containerized LaTeX compilation service rather than direct
system calls for several security reasons:

1. **Isolation**: The LaTeX compilation process runs in a Docker container,
   isolated from the host system
2. **No Shell Commands**: The MCP server never executes shell commands directly,
   preventing potential command injection
3. **Sandboxed Environment**: LaTeX code runs in a controlled environment with
   limited permissions
4. **API-based Interaction**: All communication happens through a well-defined
   HTTP API rather than shell execution
5. **Stateless Processing**: Files are not persisted in the container beyond
   compilation

This architecture ensures that even if a malicious LaTeX document were to be
submitted, it would not be able to access or affect your host system.

## 📄 Template Files

### Baseline Resume

Your starting resume in Markdown format from which tailored versions are
created. The project includes a sample baseline resume that you can modify with
your information.

### LaTeX Template

LaTeX template for generating professional PDFs. The template must include
required placeholders (like `$name`, `$profile`, `$technical_skills`, etc.) that
will be replaced with the corresponding sections from your tailored resume.

## 📚 Example Workflow

1. Set up your baseline resume in `templates/baseline_resume.md`
2. Configure your LaTeX template in `templates/latex_template.tex`
3. Start the LaTeX compilation server:
   ```bash
   cd latex-compilation-server
   docker-compose up -d
   cd ..
   ```
4. Run the MCP server: `python main.py`
5. Connect with an MCP client (such as an integrated LLM)
6. Submit a job description to the "Tailor CV" prompt
7. Generate a LaTeX/PDF version using the CV tools
8. Review and use your tailored resume!

## 🔍 Troubleshooting

### Common Issues & Solutions

#### LaTeX Template Issues

If you see warnings about missing placeholders in your LaTeX template, check
that it includes all required fields like `$name`, `$profile`,
`$technical_skills`, etc.

#### Initialization Problems

If you encounter
`RuntimeError: Received request before initialization was complete`:

1. Add a small delay after importing components
2. Check your import structure in `resume_mcp/mcp/__init__.py` - make sure all
   components are properly imported
3. Try running with the debug server to identify specific issues:
   ```python
   python debug_server.py
   ```

#### MCP Connection Issues

If clients cannot connect to the server:

1. Check that stdio transport is working correctly
2. Verify that all required components are imported
3. Run with the inspector for detailed logs:
   ```bash
   ./inspect.sh
   ```

#### Obsidian Integration Issues

If Obsidian integration isn't working:

1. Verify the `OBSIDIAN_VAULT` path in your `.env` file
2. Check file permissions for the Obsidian vault directory
3. Test basic Obsidian operations through the debug server

#### LaTeX Compilation Server Issues

If PDF generation is failing:

1. Check if the LaTeX server is running:

   ```bash
   curl http://localhost:7474/health
   ```

2. If not running, start it:

   ```bash
   cd latex-compilation-server
   docker-compose up -d
   ```

3. Check server logs if you encounter issues:

   ```bash
   docker-compose logs latex-server
   ```

4. If you need to restart the server:

   ```bash
   docker-compose restart latex-server
   ```

5. Verify your `.env` file has the correct server URL:
   ```
   LATEX_SERVER_URL="http://localhost:7474"
   ```

### Advanced Debugging

For more detailed debugging:

1. Set `LOG_LEVEL="DEBUG"` in your `.env` file
2. Run the server with the inspector to get detailed logs
3. Check `inspect.log` for error messages and execution flow
4. Use the `debug_server.py` script to verify component initialization

## 🧩 Extending the Server

### Adding New Prompts

Create new prompt files in the `resume_mcp/mcp/prompts` directory:

```python
from resume_mcp.mcp.base import mcp

@mcp.prompt(name="My Custom Prompt")
def my_custom_prompt():
    return {
        "description": "Description of what this prompt does",
        "prompt": "Your prompt template here"
    }
```

### Adding New Tools

Create new tool files in the `resume_mcp/mcp/tools` directory:

```python
from resume_mcp.mcp.base import mcp

@mcp.tool()
def my_custom_tool(param1, param2=None):
    """Documentation for the tool.

    Args:
        param1: Description of param1
        param2: Description of param2
    """
    # Tool implementation
    return {"result": "Tool output"}
```

### Custom Templates

You can create custom LaTeX templates in the `templates/` directory. Make sure
to:

1. Include all required placeholders
2. Test with the validation tool
3. Update your `.env` configuration to use the new template

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for
details.
