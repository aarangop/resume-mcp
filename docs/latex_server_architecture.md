# LaTeX Compilation Server Architecture

## Overview

The Resume MCP Server uses a containerized LaTeX compilation service to securely
generate PDF files from LaTeX documents. This architecture eliminates the need
for direct shell commands and local LaTeX installation, providing a more secure
and portable solution.

```
┌─────────────────┐       ┌───────────────────┐       ┌─────────────────────┐
│                 │       │                   │       │                     │
│  MCP Server     │       │  HTTP Request     │       │  LaTeX Container    │
│  (Python)       │──────▶│  (LaTeX Content)  │──────▶│  (Docker/Podman)    │
│                 │       │                   │       │                     │
└─────────────────┘       └───────────────────┘       └─────────────────────┘
        │                                                      │
        │                                                      │
        │                 ┌───────────────────┐                │
        │                 │                   │                │
        └────────────────▶│  Compiled PDF     │◀───────────────┘
                          │                   │
                          └───────────────────┘
```

## Components

1. **MCP Server**: The core server that handles AI interactions and CV
   generation
2. **HTTP API**: RESTful interface between the MCP server and LaTeX container
3. **LaTeX Container**: Docker/Podman container with full LaTeX environment

## Communication Flow

1. User requests PDF generation via MCP tool
2. MCP server prepares LaTeX content
3. HTTP POST request to LaTeX server with LaTeX content
4. LaTeX server compiles the document in isolated container
5. Compiled PDF is returned as HTTP response
6. MCP server saves PDF to specified location
7. User receives confirmation or error message

## Security Advantages

- No direct shell command execution
- Container isolation for LaTeX processing
- Limited file system access for container
- Clear separation of responsibilities
- API-based communication only

## Configuration

The LaTeX server URL is configured in `.env`:

```
LATEX_SERVER_URL="http://localhost:7474"
```

## Docker Compose Configuration

The server uses the following Docker Compose configuration:

```yaml
services:
  latex-server:
    build: .
    ports:
      - "7474:8000"
    container_name: latex-server
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      # Optional: mount a directory for logs
      - ./logs:/app/logs
    networks:
      - latex-network

networks:
  latex-network:
    driver: bridge
```
