"""
Obsidian Vault Tools (not Resources)
"""

import os
import logging
from pathlib import Path
from typing import Optional

from resume_mcp.utils.latex import compile_latex
from resume_mcp.utils.vault import fuzzy_search_vault_files

from ...config import OBSIDIAN_VAULT
from ..base import mcp

logger = logging.getLogger(__name__)


@mcp.tool(
    name="search_job_description",
    description="Search through the user's vault for notes matching a job description or term")
def search_job_description(search_param: str, limit=10) -> str:
    """
    Search through the user's vault for notes matching the job description.

    Args:
        job_description: Search term to match against filenames

    Returns:
        Content of matching notes or list of available files if no matches
    """

    if not search_param.strip():
        return "❌ Job description parameter cannot be empty"

    vault_path = Path(OBSIDIAN_VAULT)

    # Check if vault exists
    if not vault_path.exists():
        return f"❌ Obsidian vault not found at: {OBSIDIAN_VAULT}\nSet OBSIDIAN_VAULT environment variable to your vault path"

    if not vault_path.is_dir():
        return f"❌ Obsidian vault path is not a directory: {OBSIDIAN_VAULT}"

    results = fuzzy_search_vault_files(
        search_param, min_score=50, limit=20)

    if not results:
        files_list = [str(filename)
                      for filename in vault_path.rglob("*.md")]
        files_list_str = "\n\t- ".join(files_list)
        return f"""❌ No files matched '{search_param}'
## Available files in vault:
{files_list_str}

## Search Tips:
- Try partial matches (e.g., 'ml', 'engineer', 'python')
- File search is case-insensitive
- Only searches .md files in the vault
"""

    # Read and combine content from matched files
    combined_content = []

    for match in results[:limit]:
        file_path = match["path"]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            combined_content.append(f"""# {match['filename']}
**Path:** {match['relative_path']}

{content}
""")
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            combined_content.append(f"""# {match['filename']}
**Path:** {match['relative_path']}

❌ Error reading file: {str(e)}
""")

    result = f"""# Obsidian Vault Search Results

**Search term:** {search_param}
**Matches found:** {len(results)}
**Showing:** {len(combined_content)} files

{"="*50}

""" + "\n\n" + ("="*50 + "\n\n").join(combined_content)

    if len(results) > 5:
        result += f"\n\n**Note:** {len(results) - 5} additional matches not shown. Use more specific search terms."

    logger.info(
        f"Found {len(results)} matches for '{search_param}'")
    return result


@mcp.tool("read_vault_file", description="Read content of a specific file from the user's vault")
def read_vault_file(file_path: str) -> str:
    """
    Get content of a specific file from the Obsidian vault.

    Args:
        file_path: Path to the file within the vault (with or without .md extension)

    Returns:
        Content of the specified file
    """
    if not file_path.strip():
        return "❌ File path parameter cannot be empty"

    vault_path = Path(OBSIDIAN_VAULT)

    if not vault_path.exists():
        return f"❌ Obsidian vault not found at: {OBSIDIAN_VAULT}"

    # Add .md extension if not present
    if not file_path.endswith('.md'):
        file_path += '.md'

    full_path = os.path.join(vault_path, file_path)

    try:
        if not os.path.exists(full_path):
            return f"❌ File not found: {file_path}\n\nUse list_obsidian_files tool to see available files"

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return f"""# {full_path}
**Path:** {file_path}
**Vault:** {vault_path}

---

{content}
"""

    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return f"❌ Error reading file: {str(e)}"


@mcp.tool(
    name="save_file_to_vault",
    description="Saves the provided content into file into the user's vault"
)
def save_file_to_vault(content: str, filename: str, vault_dir: str,  replace: bool = True) -> str:
    """
    Saves the content of a file into the user's vault.

    Arguments:
        content (str): The file's content 
        filename (str): The name of the file to save to, including file extension.
    """

    vault_path = OBSIDIAN_VAULT

    full_path = os.path.join(vault_path, vault_dir, filename)

    if os.path.exists(full_path) and not replace:
        return "This file already exists and the `replace` flat has been set to false."

    with open(full_path, mode='w') as f:
        f.write(content)

    return f"The file has been successfully saved to {full_path}"


@mcp.tool(
    name="fuzzy_search_vault",
    description="Search user's vault for files with names similar to the search term using fuzzy matching"
)
def fuzzy_search_vault_tool(
    search_term: str,
    min_score: int = 60,
    subdir: str = "",
    limit: int = 10,
    include_content: bool = True
) -> str:
    """
    Search for files in the user's vault using fuzzy string matching on filenames.

    Args:
        search_term (str): The term to search for in filenames
        min_score (int, optional): Minimum fuzzy match score (0-100). Defaults to 60.
        subdir (str, optional): Subdirectory within vault to search. Defaults to "" (whole vault).
        limit (int, optional): Maximum number of results to return. Defaults to 10.
        include_content (bool, optional): Whether to include file contents in results. Defaults to False.

    Returns:
        str: Formatted results of the search
    """
    if not search_term.strip():
        return "❌ Search term parameter cannot be empty"

    vault_path = Path(OBSIDIAN_VAULT)

    # Check if vault exists
    if not vault_path.exists():
        return f"❌ Obsidian vault not found at: {OBSIDIAN_VAULT}\nSet OBSIDIAN_VAULT environment variable to your vault path"

    if not vault_path.is_dir():
        return f"❌ Obsidian vault path is not a directory: {OBSIDIAN_VAULT}"

    # Perform fuzzy search
    results = fuzzy_search_vault_files(
        search_term=search_term,
        min_score=min_score,
        subdir=subdir,
        limit=limit
    )

    if not results:
        # If no results, show available files to help user
        search_path = vault_path / subdir if subdir else vault_path
        files_list = [f.stem for f in search_path.rglob("*.md")][:20]

        return f"""❌ No files matched '{search_term}' with minimum score {min_score}

## Available files in {"subdirectory: " + subdir if subdir else "vault"}:
- {", ".join(files_list) if files_list else "No files found"}

## Search tips:
- Lower the min_score parameter (currently {min_score})
- Try more general search terms
- Check if the subdirectory path is correct
"""

    # Format results
    formatted_results = []

    for match in results:
        result_block = f"""## {match['filename']} (Score: {match['score']})
**Path:** {match['relative_path']}
"""

        # Add file content if requested
        if include_content:
            try:
                with open(match['path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                result_block += f"\n```markdown\n{content[:1000]}\n```"

                if len(content) > 1000:
                    result_block += "\n...(truncated)...\n"
            except Exception as e:
                logger.error(f"Error reading file {match['path']}: {e}")
                result_block += f"\n❌ Error reading file content: {str(e)}"

        formatted_results.append(result_block)

    # Build final output
    search_info = f"""# Obsidian Fuzzy Search Results

**Search term:** {search_term}
**Minimum score:** {min_score}
**Results found:** {len(results)}
**Subdirectory:** {subdir if subdir else "entire vault"}
**Content included:** {"Yes" if include_content else "No"}

"""

    full_results = search_info + "\n---\n\n".join(formatted_results)

    logger.info(
        f"Fuzzy search found {len(results)} matches for '{search_term}' (min_score: {min_score})")
    return full_results
