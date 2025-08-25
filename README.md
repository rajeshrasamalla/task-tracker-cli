# Task Tracker (CLI)

Simple CLI to track tasks using a local `tasks.json`.

## Commands (positional, no flags)
- `add <title> <description(optional)>`
- `update <id> <new_title> <new_description(optional)>`
- `delete <id>`
- `mark <id> <todo|in-progress|done>`
- `list <all|todo|in-progress|done>`
- `details <id>`

## Run
```bash
python task_tracker.py add "Buy milk" "Lactose-free"
python task_tracker.py list all
python task_tracker.py mark 1 in-progress
python task_tracker.py list "in-progress"
https://roadmap.sh/projects/task-tracker
