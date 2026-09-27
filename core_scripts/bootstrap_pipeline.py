#!/usr/bin/env python3
"""
bootstrap_pipeline.py — Kanban Video Orchestrator project generator.

Generates a complete multi-agent video production workspace from a brief +
team design JSON. Creates:

  <workspace>/
    brief.md              — creative pitch and project scoping
    TEAM.md               — 7-agent role profiles and task graph
    plan.json             — machine-readable project manifest
    VISUAL_SPEC.md        — global visual language + per-scene specs
    audio/                — raw sound assets, voiceover cuts, master tracks
    scenes/               — sandboxed directories per scene
    output/               — render deliverables
    taste/                — brand-guide.md, emotional-dna.md
    scripts/              — pipeline automation utilities (copied from core_scripts/)

Usage:
  python bootstrap_pipeline.py --brief brief.md --team team.json --workspace /path/to/project

Or programmatically:
  from bootstrap_pipeline import bootstrap
  bootstrap(brief_path="brief.md", team_path="team.json", workspace="/path/to/project")
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


CORE_SCRIPTS_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = CORE_SCRIPTS_DIR.parent / "templates"


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text(path: str, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def copy_template(template_name: str, dest_path: str, **kwargs) -> None:
    src = TEMPLATES_DIR / template_name
    if not src.exists():
        print(f"[WARN] Template not found: {src}", file=sys.stderr)
        return
    content = load_text(str(src))
    for key, value in kwargs.items():
        content = content.replace("{" + key + "}", str(value))
    write_text(dest_path, content)


def bootstrap(brief_path: str, team_path: str, workspace: str) -> None:
    """Generate a full kanban video project workspace."""
    workspace = Path(workspace).resolve()
    print(f"[bootstrap] Creating workspace: {workspace}")

    # Load inputs
    brief_text = load_text(brief_path) if os.path.exists(brief_path) else ""
    team_data = load_json(team_path) if os.path.exists(team_path) else {}

    slug = team_data.get("slug", "new-project")
    tenant = team_data.get("tenant", slug)

    # Create directory structure
    dirs = [
        workspace,
        workspace / "audio",
        workspace / "audio" / "voiceover",
        workspace / "audio" / "sfx",
        workspace / "scenes",
        workspace / "output",
        workspace / "taste",
        workspace / "scripts",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"[bootstrap]   created: {d}")

    # Write templates
    print("[bootstrap] Writing templates...")
    copy_template("brief.md", str(workspace / "brief.md"))
    copy_template("TEAM.md", str(workspace / "TEAM.md"))
    copy_template("plan.json", str(workspace / "plan.json"))
    copy_template("VISUAL_SPEC.md", str(workspace / "VISUAL_SPEC.md"))

    # Write taste files
    write_text(
        str(workspace / "taste" / "brand-guide.md"),
        "# Brand Guide\n\nTBD — fill in brand colors, typography, logos.\n",
    )
    write_text(
        str(workspace / "taste" / "emotional-dna.md"),
        "# Emotional DNA\n\nTBD — define the emotional arc of this piece.\n",
    )

    # Copy core scripts into project
    scripts_src = CORE_SCRIPTS_DIR
    scripts_dst = workspace / "scripts"
    for item in scripts_src.iterdir():
        if item.is_file() and item.name != "__pycache__":
            shutil.copy2(item, scripts_dst / item.name)
            print(f"[bootstrap]   copied script: {item.name}")

    # Write plan.json with team data if provided
    if team_data:
        plan_path = workspace / "plan.json"
        existing = load_json(str(plan_path))
        existing.update({k: v for k, v in team_data.items() if k != "team"})
        if "team" in team_data:
            existing["team"] = team_data["team"]
        write_text(str(plan_path), json.dumps(existing, indent=2))

    print(f"[bootstrap] Done. Workspace ready at: {workspace}")
    print(f"[bootstrap] Tenant: {tenant}")
    print(f"[bootstrap] Next: assign director profile and fire initial kanban task.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bootstrap a Kanban Video Orchestrator project workspace."
    )
    parser.add_argument(
        "--brief", required=True, help="Path to brief.md template or existing brief file"
    )
    parser.add_argument(
        "--team", required=True, help="Path to team JSON manifest (plan.json or team design)"
    )
    parser.add_argument(
        "--workspace", required=True, help="Absolute path to create the project workspace"
    )
    args = parser.parse_args()
    bootstrap(args.brief, args.team, args.workspace)


if __name__ == "__main__":
    main()
