"""Forge module — git workflow automation helpers."""

from __future__ import annotations

import subprocess
from datetime import datetime
from typing import List, Optional


def _run(args: List[str], cwd: Optional[str] = None) -> str:
    """Run a git command and return stdout, or error message on failure."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30,
        )
        if result.returncode != 0:
            return result.stderr.strip() or "Command failed."
        return result.stdout.strip()
    except FileNotFoundError:
        return "git not found in PATH."
    except subprocess.TimeoutExpired:
        return "git command timed out."


def quicksave(fmt: str = "quicksave: {date} {time}", cwd: Optional[str] = None) -> str:
    """Stage all changes and commit with a formatted timestamp message."""
    now = datetime.now()
    msg = fmt.format(date=now.strftime("%Y-%m-%d"), time=now.strftime("%H:%M"))
    add = _run(["git", "add", "-A"], cwd=cwd)
    if "error" in add.lower() or "fatal" in add.lower():
        return add
    return _run(["git", "commit", "-m", msg], cwd=cwd)


def undo_last(cwd: Optional[str] = None) -> str:
    """Undo the last commit but keep changes staged."""
    return _run(["git", "reset", "--soft", "HEAD~1"], cwd=cwd)


def cleanup_branches(cwd: Optional[str] = None) -> str:
    """Delete local branches that have been merged into the current branch."""
    merged = _run(["git", "branch", "--merged"], cwd=cwd)
    if not merged:
        return "No merged branches to clean up."
    deleted = []
    for branch in merged.splitlines():
        branch = branch.strip()
        if branch and not branch.startswith("*") and branch not in ("main", "master", "dev", "develop"):
            result = _run(["git", "branch", "-d", branch], cwd=cwd)
            deleted.append(f"  Deleted: {branch}")
    return "\n".join(deleted) if deleted else "No merged branches to clean up."


def show_today(cwd: Optional[str] = None) -> str:
    """Show commits made today."""
    return _run(["git", "log", "--since=midnight", "--oneline", "--no-walk=unsorted",
                 "--all"], cwd=cwd)


def count_today_commits(repos: List[str]) -> int:
    """Count commits across all tracked repos made today."""
    total = 0
    for repo in repos:
        output = _run(["git", "log", "--since=midnight", "--oneline"], cwd=repo)
        if output and "not a git repository" not in output.lower():
            total += len([l for l in output.splitlines() if l.strip()])
    return total


def get_all_repos_commits(repos: List[str]) -> dict:
    """Return {repo_path: commit_count_today} for all configured repos."""
    result = {}
    for repo in repos:
        output = _run(["git", "log", "--since=midnight", "--oneline"], cwd=repo)
        if output and "not a git repository" not in output.lower():
            count = len([l for l in output.splitlines() if l.strip()])
        else:
            count = 0
        result[repo] = count
    return result
