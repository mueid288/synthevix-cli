"""Forge module — project scaffolding engine."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

from synthevix.core.database import SYNTHEVIX_DIR

# Built-in template definitions (path is relative to assets/templates/)
BUILTIN_TEMPLATES = {
    "python-basic": {
        "description": "Python project with venv, pyproject.toml, src layout, pre-commit hooks",
        "files": {
            "pyproject.toml": '[tool.poetry]\nname = "{name}"\nversion = "0.1.0"\ndescription = ""\n',
            "README.md": "# {name}\n\nA Python project.\n",
            "src/{name}/__init__.py": '"""Package init."""\n',
            ".gitignore": "__pycache__/\n*.py[cod]\n.venv/\ndist/\n",
        },
    },
    "fastapi": {
        "description": "FastAPI app with Docker, Alembic migrations, and structured endpoints",
        "files": {
            "app/main.py": 'from fastapi import FastAPI\n\napp = FastAPI(title="{name}")\n\n@app.get("/")\ndef root():\n    return {{"message": "Hello from {name}"}}\n',
            "app/__init__.py": "",
            "requirements.txt": "fastapi\nuvicorn[standard]\nsqlalchemy\nalembic\n",
            "Dockerfile": 'FROM python:3.11-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install -r requirements.txt\nCOPY . .\nCMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]\n',
            "README.md": "# {name}\n\nFastAPI project.\n",
            ".gitignore": "__pycache__/\n*.py[cod]\n.env\n",
        },
    },
    "react-ts": {
        "description": "React + TypeScript with Vite, Tailwind, ESLint, and Prettier",
        "files": {
            "README.md": "# {name}\n\nReact + TypeScript project.\n",
            ".gitignore": "node_modules/\ndist/\n.env\n",
        },
        "post_init": "npx -y create-vite@latest . --template react-ts",
    },
    "cli-tool": {
        "description": "Python CLI with Typer, Rich, tests, and publish-ready setup",
        "files": {
            "pyproject.toml": '[tool.poetry]\nname = "{name}"\nversion = "0.1.0"\n\n[tool.poetry.dependencies]\npython = "^3.11"\ntyper = {extras = ["all"], version = "^0.12.0"}\nrich = "^13.0.0"\n\n[tool.poetry.scripts]\n{name} = "{name}.main:app"\n',
            "{name}/main.py": 'import typer\nfrom rich.console import Console\n\napp = typer.Typer()\nconsole = Console()\n\n@app.command()\ndef main():\n    """My CLI tool."""\n    console.print("[bold green]Hello![/bold green]")\n',
            "{name}/__init__.py": "",
            "tests/__init__.py": "",
            "tests/test_main.py": 'def test_placeholder():\n    assert True\n',
            "README.md": "# {name}\n\nA Python CLI tool.\n",
        },
    },
}


def scaffold_project(template_id: str, dest_path: Path, project_name: str) -> None:
    """
    Create project files from a built-in template into dest_path.
    Placeholders {name} in filenames and content are replaced with project_name.
    """
    template = BUILTIN_TEMPLATES.get(template_id)
    if not template:
        # Try custom templates dir
        custom_dir = SYNTHEVIX_DIR / "templates" / template_id
        if custom_dir.exists():
            shutil.copytree(str(custom_dir), str(dest_path), dirs_exist_ok=True)
            return
        raise ValueError(f"Template '{template_id}' not found.")

    dest_path.mkdir(parents=True, exist_ok=True)

    for rel_path, content in template.get("files", {}).items():
        # Replace {name} placeholders in path and content
        rel_path = rel_path.replace("{name}", project_name)
        content = content.replace("{name}", project_name)

        file_path = dest_path / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    # Run post-init command if defined
    post_init = template.get("post_init")
    if post_init:
        import subprocess
        subprocess.run(post_init.split(), cwd=str(dest_path))


def list_builtin_templates() -> dict:
    return {k: v["description"] for k, v in BUILTIN_TEMPLATES.items()}
