import logging
import os
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from fuzzywuzzy import fuzz
import numpy as np
from resume_mcp.config import OBSIDIAN_VAULT

logger = logging.getLogger(__name__)


def save_file_to_vault(content: str, rel_dest: str) -> Optional[str]:
    """
    Save content to a file within the Obsidian vault, or to a folder in the file system specified by the user through the OBSIDIAN_VAULT environment variable.

    Args:
        content (str): The content to write to the file.
        rel_dest (str): The name of the destination file to create or overwrite, relative to the OBSIDIAN_VAULT path.

    Returns:
        Optional[str]: The full path to the created file if successful, None otherwise.

    Raises:
        No exceptions are raised directly; exceptions during file writing are caught
        and result in a None return value.
    """
    full_path = os.path.join(OBSIDIAN_VAULT, rel_dest)
    try:
        with open(full_path, mode="w", encoding='utf-8') as f:
            f.write(content)
    except:
        return None

    return full_path


def read_vault_file(filename: str, min_score=70) -> str:
    """
    Reads the contents of a file in the vault based on fuzzy matching of the filename.

    This function searches for a file in the vault using fuzzy matching and returns its contents.
    If no match is found with a score of at least 80, an exception is raised.

    Args:
        filename (str): The name of the file to search for in the vault.

    Returns:
        str: The contents of the matched file.

    Raises:
        Exception: If no files in the vault match the given filename with the minimum score.

    Example:
        >>> content = read_vault_file("my_note.md")
    """

    root, _ = os.path.splitext(filename)
    match = fuzzy_search_vault_files(filename, min_score=min_score, limit=1)

    if not match:
        raise Exception(f"No files matched '{root}' in Obsidian vault")

    match = match[0]["path"]

    with open(match, mode='r', encoding='utf-8') as f:
        content = f.read()

    return content


def fuzzy_search_vault_files(
        search_term: str,
        min_score: int = 60,
        subdir: Optional[str] = None,
        limit: int = 10) -> List[Dict[str, str]]:
    """
    Search for files in the Obsidian vault using fuzzy string matching on filenames.

    Args:
        search_term (str): The term to search for
        min_score (int, optional): Minimum fuzzy match score (0-100). Defaults to 60.
        limit (int, optional): Maximum number of results to return. Defaults to 10.

    Returns:
        List[Dict[str, str]]: List of matching files with score and path
    """
    path = Path(OBSIDIAN_VAULT)

    if subdir:
        path /= subdir

    # Get all markdown files in the vault
    all_md_files = list(path.rglob("*.md"))

    logger.info(f"Found {len(all_md_files)} markdown files")

    # Calculate fuzzy match scores
    scores = np.array([
        max(
            fuzz.ratio(search_term.lower(), str(filename.stem).lower()),
            fuzz.partial_ratio(search_term.lower(), str(filename.stem).lower())
        )
        for filename in all_md_files
    ])

    matched_files = zip(all_md_files, scores)

    matches = [{
        "score": score,
        "path": str(match),
        "filename": match.stem,
        "relative_path": str(match.relative_to(path))
    } for match, score in matched_files if score > min_score]
    logger.info(
        f"Found {len(matches)} matching files for search term '{search_term}'")
    # Sort by score descending
    matches.sort(key=lambda x: x["score"], reverse=True)

    # Return limited number of results
    return matches[:limit]
