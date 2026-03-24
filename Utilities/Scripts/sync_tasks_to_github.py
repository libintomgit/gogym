#!/usr/bin/env python3
"""
sync_tasks_to_github.py

Reads tasks from a JSON file and creates GitHub Issues + optionally
adds them to a GitHub Project board using the `gh` CLI.

Usage:
    python sync_tasks_to_github.py --repo owner/repo --tasks tasks.json [--project NUMBER] [--milestone NAME] [--dry-run]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


# ── GitHub CLI helpers ───────────────────────────────────────────────────────

def run_gh(args: list[str], dry_run: bool = False) -> str:
    """Run a gh CLI command and return stdout."""
    cmd = ["gh"] + args
    if dry_run:
        print(f"  [DRY RUN] {' '.join(cmd)}")
        return ""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ⚠ gh error: {result.stderr.strip()}", file=sys.stderr)
    return result.stdout.strip()


def ensure_labels(repo: str, labels: set[str], dry_run: bool):
    """Create all labels if they don't exist."""
    print("Creating labels...")
    for label in sorted(labels):
        run_gh(["label", "create", label, "--repo", repo,
                "--force", "--color", "0E8A16"], dry_run)


def ensure_milestone(repo: str, milestone: str, dry_run: bool):
    """Create milestone if it doesn't exist."""
    print(f"Creating milestone '{milestone}'...")
    run_gh(["api", f"repos/{repo}/milestones",
            "-f", f"title={milestone}",
            "-f", "description=Auto-created from tasks.json"], dry_run)


# ── Issue body builder ───────────────────────────────────────────────────────

def build_issue_body(task: dict) -> str:
    """Build a GitHub issue body from a task dict."""
    sections: list[str] = []
    subtasks = task.get("subtasks", [])

    if task.get("is_checkpoint"):
        sections.append("## Checkpoint\n")
        if task.get("details"):
            sections.append("\n".join(f"- {d}" for d in task["details"]))
        return "\n".join(sections)

    # Checklist summary
    if subtasks:
        sections.append("## Sub-tasks\n")
        for st in subtasks:
            opt = " *(optional)*" if st.get("optional") else ""
            sections.append(f"- [ ] **{st['id']}**{opt} {st['title']}")

        # Detailed breakdown
        sections.append("\n---\n\n## Details\n")
        for st in subtasks:
            opt_tag = " *(optional)*" if st.get("optional") else ""
            sections.append(f"### {st['id']}{opt_tag} {st['title']}\n")
            for d in st.get("details", []):
                sections.append(f"- {d}")
            if st.get("requirements"):
                sections.append(f"\n> Requirements: {st['requirements']}")
            sections.append("")

    elif task.get("details"):
        for d in task["details"]:
            sections.append(f"- {d}")

    return "\n".join(sections)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Sync tasks.json to GitHub Issues and Projects"
    )
    parser.add_argument("--repo", required=True, help="GitHub repo (owner/repo)")
    parser.add_argument("--tasks", required=True, help="Path to tasks.json file")
    parser.add_argument("--project", type=int, default=None,
                        help="GitHub Project number to add issues to")
    parser.add_argument("--milestone", default=None,
                        help="Milestone name (overrides default from JSON)")
    parser.add_argument("--skip-optional", action="store_true",
                        help="Skip optional sub-tasks in issue bodies")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print commands without executing")

    args = parser.parse_args()
    owner = args.repo.split("/")[0]

    # Load JSON
    tasks_path = Path(args.tasks)
    if not tasks_path.exists():
        print(f"Error: {tasks_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(tasks_path) as f:
        data = json.load(f)

    tasks = data["tasks"]
    milestone = args.milestone or data.get("default_milestone", "MVP")

    print(f"Loaded {len(tasks)} tasks from {tasks_path}")
    print(f"Milestone: {milestone}\n")

    # Collect all unique labels
    all_labels = {t["label"] for t in tasks if t.get("label")}

    # Setup
    ensure_labels(args.repo, all_labels, args.dry_run)
    ensure_milestone(args.repo, milestone, args.dry_run)
    print()

    # Filter optional subtasks if requested
    if args.skip_optional:
        for task in tasks:
            task["subtasks"] = [
                st for st in task.get("subtasks", [])
                if not st.get("optional")
            ]

    # Create issues
    created = 0
    for task in tasks:
        title = f"Task {task['id']}: {task['title']}"
        body = build_issue_body(task)
        labels = [task["label"]] if task.get("label") else []

        print(f"Creating issue: {title}")
        gh_args = ["issue", "create", "--repo", args.repo,
                   "--title", title, "--body", body,
                   "--milestone", milestone]
        for lbl in labels:
            gh_args.extend(["--label", lbl])

        issue_url = run_gh(gh_args, args.dry_run)

        if issue_url:
            print(f"  ✓ {issue_url}")
            if args.project:
                run_gh(["project", "item-add", str(args.project),
                        "--owner", owner, "--url", issue_url], args.dry_run)
                print(f"  ✓ Added to project #{args.project}")
        created += 1

    print(f"\nDone. {created} issues {'would be ' if args.dry_run else ''}created.")


if __name__ == "__main__":
    main()
