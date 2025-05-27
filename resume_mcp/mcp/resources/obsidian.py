import os
from resume_mcp.config import OBSIDIAN_VAULT
from resume_mcp.mcp.base import mcp


@mcp.resource("file://job_description/{job_description}")
def job_description(job_description: str) -> str:
    """
    Goes through the Obsidian Vault to find notes matching the 
    job description parameter.

    Returns str: Content of the notes matching a job description. 
    """

    checked_files = []
    match_contents = []
    matched_files = []
    for dirpath, dirname, filenames in os.walk(OBSIDIAN_VAULT):
        matched_files = [os.path.join(
            dirpath, filename) for filename in filenames if filename.lower() in job_description.lower()]
        checked_files.append(filenames)

    for f in matched_files:
        content = os.path.basename(f)
        with open(f, '+r') as match:
            content += "\n" + match.read()
            match_contents.append(content)

    if not matched_files:
        available_files = ",\n".join(checked_files)
        return f"No files matched the job description: {job_description}, available files are: {available_files}"

    return "---\n---".join(matched_files)
