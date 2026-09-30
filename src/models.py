"""
Task Scheduler Optimization System
===================================
src/models.py - Data models for Tasks and Resources
"""

import csv
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class Task:
    """Represents a schedulable task with all constraints."""
    task_id: str
    duration_h: int          # Execution time in hours
    deadline_h: int          # Deadline (hours from t=0)
    priority: int            # 1 (low) to 5 (high)
    skill: str               # Required skill
    depends_on: List[str]    # List of task IDs this depends on
    profit: int              # Importance/profit score

    # Scheduled fields (filled after scheduling)
    start_h: Optional[int] = None
    end_h: Optional[int] = None
    assigned_resource: Optional[str] = None
    is_late: bool = False
    lateness_h: int = 0
    is_missed: bool = False

    def __repr__(self):
        return (f"Task({self.task_id}, prio={self.priority}, "
                f"ddl={self.deadline_h}h, dur={self.duration_h}h, profit={self.profit})")


@dataclass
class Resource:
    """Represents a worker/machine with skills and shift windows."""
    res_id: str
    skills: set
    shift_start_h: int       # Shift start (hours, repeated each day)
    shift_end_h: int         # Shift end
    max_hours_per_day: int

    # Scheduling state
    current_time_h: int = 0
    total_hours_assigned: int = 0

    def can_handle(self, skill: str) -> bool:
        return skill in self.skills

    def __repr__(self):
        return f"Resource({self.res_id}, skills={self.skills})"


def load_tasks(path: str = "data/tasks.csv") -> List[Task]:
    """Load tasks from CSV file."""
    tasks = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            deps = [d.strip() for d in (row.get("depends_on") or "").split("|") if d.strip()]
            task = Task(
                task_id=row["task_id"].strip(),
                duration_h=int(row["duration_h"]),
                deadline_h=int(row["deadline_h"]),
                priority=int(row["priority"]),
                skill=row["skill"].strip(),
                depends_on=deps,
                profit=int(row.get("profit", 100))
            )
            tasks.append(task)
    return tasks


def load_resources(path: str = "data/resources.csv") -> List[Resource]:
    """Load resources from CSV file."""
    resources = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            skills = set(s.strip() for s in (row["skills"] or "").split("|") if s.strip())
            res = Resource(
                res_id=row["res_id"].strip(),
                skills=skills,
                shift_start_h=int(row["shift_start_h"]),
                shift_end_h=int(row["shift_end_h"]),
                max_hours_per_day=int(row["max_hours_per_day"])
            )
            resources.append(res)
    return resources


def validate_tasks(tasks: List[Task]) -> Tuple[bool, List[str]]:
    """
    Validate a list of tasks for common input issues:
    - Empty task list
    - Duplicate task IDs
    - Invalid duration (<= 0)
    - Invalid deadline (<= 0)
    - Negative profit (< 0)
    - Priority outside 1..5
    - Missing dependency references
    Returns (is_valid, list_of_errors).
    """
    errors = []
    if not tasks:
        return False, ["Task list is empty."]

    seen_ids = set()
    for t in tasks:
        if not t.task_id or not t.task_id.strip():
            errors.append("Found task with empty or whitespace-only task_id.")
        elif t.task_id in seen_ids:
            errors.append(f"Duplicate task ID detected: '{t.task_id}'.")
        seen_ids.add(t.task_id)

        if t.duration_h <= 0:
            errors.append(f"Task '{t.task_id}' has invalid duration ({t.duration_h}h). Duration must be positive.")
        if t.deadline_h <= 0:
            errors.append(f"Task '{t.task_id}' has invalid deadline ({t.deadline_h}h). Deadline must be positive.")
        if t.profit < 0:
            errors.append(f"Task '{t.task_id}' has negative profit ({t.profit}). Profit must be >= 0.")
        if not (1 <= t.priority <= 5):
            errors.append(f"Task '{t.task_id}' has priority {t.priority}. Priority should be between 1 and 5.")

    # Check dependencies
    for t in tasks:
        for dep in t.depends_on:
            if dep not in seen_ids:
                errors.append(f"Task '{t.task_id}' depends on '{dep}', which does not exist in the task list.")

    return len(errors) == 0, errors