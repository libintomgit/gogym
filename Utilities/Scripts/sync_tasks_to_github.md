# GoGym Tasks → GitHub Issues Sync Script

Reads tasks from a `tasks.json` file and creates GitHub Issues with labels, milestones, and optional GitHub Project board integration.

## Files

| File | Description |
|---|---|
| `tasks.json` | Source of truth — all tasks in structured JSON format |
| `sync_tasks_to_github.py` | Script that reads `tasks.json` and creates GitHub Issues |

## Prerequisites

1. **GitHub CLI** (`gh`) installed:
   ```bash
   brew install gh
   ```

2. **Authenticate** with your GitHub account:
   ```bash
   gh auth login
   ```

3. **Python 3.10+** (uses modern type hints).

## Usage

### Dry run (preview without creating anything)

```bash
python sync_tasks_to_github.py \
  --repo your-username/gogym-api \
  --tasks tasks.json \
  --dry-run
```

### Create issues

```bash
python sync_tasks_to_github.py \
  --repo your-username/gogym-api \
  --tasks tasks.json
```

### Create issues and add to a GitHub Project board

```bash
python sync_tasks_to_github.py \
  --repo your-username/gogym-api \
  --tasks tasks.json \
  --project 1
```

> The `--project` value is the project number visible in the URL: `github.com/users/you/projects/1`

### Custom milestone name

```bash
python sync_tasks_to_github.py \
  --repo your-username/gogym-api \
  --tasks tasks.json \
  --milestone "Sprint 1 - MVP"
```

### Skip optional tasks

```bash
python sync_tasks_to_github.py \
  --repo your-username/gogym-api \
  --tasks tasks.json \
  --skip-optional
```

## Options

| Flag | Required | Description |
|---|---|---|
| `--repo` | Yes | GitHub repository in `owner/repo` format |
| `--tasks` | Yes | Path to the `tasks.json` file |
| `--project` | No | GitHub Project number to add issues to |
| `--milestone` | No | Milestone name (overrides `default_milestone` from JSON) |
| `--skip-optional` | No | Exclude optional sub-tasks from issue bodies |
| `--dry-run` | No | Preview commands without executing |

## JSON format

The `tasks.json` file follows this structure:

```json
{
  "project": "Project Name",
  "default_milestone": "Milestone Name",
  "tasks": [
    {
      "id": "1",
      "title": "Task title",
      "label": "label-name",
      "is_checkpoint": false,
      "details": [],
      "subtasks": [
        {
          "id": "1.1",
          "title": "Sub-task title",
          "optional": false,
          "requirements": "1.1, 1.2",
          "details": ["Detail line 1", "Detail line 2"]
        }
      ]
    }
  ]
}
```

To adapt this for a different project, just create a new `tasks.json` with your tasks and point the script at it.

## Troubleshooting

- **`gh: command not found`** → Install with `brew install gh`
- **`HTTP 401`** → Run `gh auth login` to re-authenticate
- **`HTTP 422 (Validation Failed)`** → The milestone or label may already exist, which is fine
- **Issues not appearing in project** → Verify the project number matches your GitHub Project URL
