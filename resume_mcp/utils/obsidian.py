import logging
import os
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from fuzzywuzzy import fuzz
import numpy as np
from resume_mcp.config import OBSIDIAN_VAULT

logger = logging.getLogger(__name__)


def save_obsidian_file(content: str, filename: str) -> Optional[str]:
    root, _ = os.path.splitext(filename)
    full_path = os.path.join(OBSIDIAN_VAULT, f"{root}.md")
    try:
        with open(full_path, mode="w", encoding='utf-8') as f:
            f.write(content)
    except:
        return None

    return full_path


def read_obsidian_file(filename: str) -> str:
    obsidian_path = Path(OBSIDIAN_VAULT)

    root, _ = os.path.splitext(filename)
    match = next(obsidian_path.rglob(f"{root}.md"), None)

    if not match:
        raise Exception(f"No files matched '{root}' in Obsidian vault")

    with open(match, mode='r', encoding='utf-8') as f:
        content = f.read()

    return content


def fuzzy_search_files(
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
    scores = np.array([fuzz.ratio(search_term.lower(), str(filename.stem).lower())
                       for filename in all_md_files])

    matched_files = zip(all_md_files, scores)

    matches = [{
        "score": score,
        "path": str(match),
        "filename": match.stem,
        "relative_path": str(match.relative_to(path))
    } for match, score in matched_files if score > min_score]

    # Sort by score descending
    matches.sort(key=lambda x: x["score"], reverse=True)

    # Return limited number of results
    return matches[:limit]
