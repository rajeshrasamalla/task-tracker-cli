import json
import os
import sys
from pathlib import Path
from datetime import datetime

DB_FILENAME = "tasks.json"

VALID_STATUSES = {"todo", "in-progress", "done"}

def now_iso():
    return datetime.now().isoformat(timespec="seconds")

def db_path():
    return Path(os.getcwd()) / DB_FILENAME

def load_tasks():
    path = db_path()
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                print("Warning: tasks.json is not a list; starting with an empty list.", file=sys.stderr)
                return []
    except json.JSONDecodeError:
        backup = path.with_suffix(".json.bak")
        try:
            path.rename(backup)
            print(f"Warning: tasks.json was corrupt. Backed up to {backup.name}. Starting fresh.", file=sys.stderr)
        except Exception:
            print("Warning: tasks.json was corrupt and could not be backed up. Starting fresh.", file=sys.stderr)
        return []

def save_tasks(tasks):
    path = db_path()
    tmp = path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)

def next_id(tasks):
    return (max((t.get("id", 0) for t in tasks), default=0) + 1) if tasks else 1

def print_task(task):
    print(f'[{task["id"]}] {task["title"]} | {task["status"]} | created: {task["created_at"]} | updated: {task["updated_at"]}')
    desc = task.get("description")
    if desc:
        print(f'    {desc}')

def cmd_add(args):
    if len(args) < 2:
        print("Usage: add <title> <description(optional)>", file=sys.stderr)
        sys.exit(1)
    title = args[1]
    description = args[2] if len(args) >= 3 else ""
    tasks = load_tasks()
    tid = next_id(tasks)
    task = {
        "id": tid,
        "title": title,
        "description": description,
        "status": "todo",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task #{tid}.")
    print_task(task)

def find_task(tasks, tid):
    for t in tasks:
        if t.get("id") == tid:
            return t
    return None

def parse_int(value, name="id"):
    try:
        return int(value)
    except ValueError:
        print(f"Error: {name} must be an integer.", file=sys.stderr)
        sys.exit(1)

def cmd_update(args):
    if len(args) < 4:
        print("Usage: update <id> <new_title> <new_description(optional)>", file=sys.stderr)
        sys.exit(1)
    tid = parse_int(args[1])
    title = args[2]
    description = args[3] if len(args) >= 4 else ""
    tasks = load_tasks()
    task = find_task(tasks, tid)
    if not task:
        print(f"Error: task #{tid} not found.", file=sys.stderr)
        sys.exit(1)
    task["title"] = title
    task["description"] = description
    task["updated_at"] = now_iso()
    save_tasks(tasks)
    print(f"Updated task #{tid}.")
    print_task(task)

def cmd_delete(args):
    if len(args) < 2:
        print("Usage: delete <id>", file=sys.stderr)
        sys.exit(1)
    tid = parse_int(args[1])
    tasks = load_tasks()
    before = len(tasks)
    tasks = [t for t in tasks if t.get("id") != tid]
    if len(tasks) == before:
        print(f"Error: task #{tid} not found.", file=sys.stderr)
        sys.exit(1)
    save_tasks(tasks)
    print(f"Deleted task #{tid}.")

def cmd_mark(args):
    if len(args) < 3:
        print("Usage: mark <id> <todo|in-progress|done>", file=sys.stderr)
        sys.exit(1)
    tid = parse_int(args[1])
    status = args[2].lower()
    if status not in VALID_STATUSES:
        print("Error: status must be one of: todo, in-progress, done.", file=sys.stderr)
        sys.exit(1)
    tasks = load_tasks()
    task = find_task(tasks, tid)
    if not task:
        print(f"Error: task #{tid} not found.", file=sys.stderr)
        sys.exit(1)
    task["status"] = status
    task["updated_at"] = now_iso()
    save_tasks(tasks)
    print(f"Marked task #{tid} as {status}.")
    print_task(task)

def cmd_list(args):
    if len(args) < 2:
        print("Usage: list <all|todo|in-progress|done>", file=sys.stderr)
        sys.exit(1)
    flt = args[1].lower()
    if flt != "all" and flt not in VALID_STATUSES:
        print("Error: filter must be one of: all, todo, in-progress, done.", file=sys.stderr)
        sys.exit(1)
    tasks = load_tasks()
    if flt != "all":
        tasks = [t for t in tasks if t.get("status") == flt]
    if not tasks:
        print("No tasks to show.")
        return
    for t in sorted(tasks, key=lambda x: (x.get("status"), x.get("id"))):
        print_task(t)

def cmd_details(args):
    if len(args) < 2:
        print("Usage: details <id>", file=sys.stderr)
        sys.exit(1)
    tid = parse_int(args[1])
    tasks = load_tasks()
    task = find_task(tasks, tid)
    if not task:
        print(f"Error: task #{tid} not found.", file=sys.stderr)
        sys.exit(1)
    print_task(task)

def print_help():
    help_text = """
Task Tracker CLI

Usage:
  python task_tracker-cli.py <command> [args]

Commands (positional, no flags):
  add <title> <description(optional)>
  update <id> <new_title> <new_description(optional)>
  delete <id>
  mark <id> <todo|in-progress|done>
  list <all|todo|in-progress|done>
  details <id>

Examples:
  python task_tracker-cli.py add "Buy milk" "Remember lactose-free"
  python task_tracker-cli.py list all
  python task_tracker-cli.py mark 1 in-progress
  python task_tracker-cli.py update 1 "Buy milk and bread" "Both from local store"
  python task_tracker-cli.py list done
  python task_tracker-cli.py delete 1
"""
    print(help_text.strip())

def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)
    cmd = sys.argv[1].lower()
    args = sys.argv[1:]  # pass command and subsequent args
    if cmd == "add":
        cmd_add(args)
    elif cmd == "update":
        cmd_update(args)
    elif cmd == "delete":
        cmd_delete(args)
    elif cmd == "mark":
        cmd_mark(args)
    elif cmd == "list":
        cmd_list(args)
    elif cmd == "details":
        cmd_details(args)
    elif cmd in {"help", "-h", "--help"}:
        print_help()
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print_help()
        sys.exit(1)

if __name__ == "_main_":
    main()