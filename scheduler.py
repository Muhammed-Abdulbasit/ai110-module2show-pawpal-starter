"""
PawPal+ Scheduler — core domain models and scheduling logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import datetime


# ─────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @property
    def weight(self) -> int:
        return {"low": 1, "medium": 2, "high": 3}[self.value]


class Species(str, Enum):
    DOG = "dog"
    CAT = "cat"
    OTHER = "other"


# ─────────────────────────────────────────────
# Domain models
# ─────────────────────────────────────────────

@dataclass
class Task:
    """A single pet-care task."""
    title: str
    duration_minutes: int
    priority: Priority = Priority.MEDIUM
    # Optional hard time window (24-h clock, e.g. 8 for 8 AM)
    preferred_hour: Optional[int] = None
    notes: str = ""

    def __post_init__(self):
        if isinstance(self.priority, str):
            self.priority = Priority(self.priority)
        if self.duration_minutes < 1:
            raise ValueError("duration_minutes must be ≥ 1")
        if self.preferred_hour is not None and not (0 <= self.preferred_hour <= 23):
            raise ValueError("preferred_hour must be 0-23")

    @property
    def priority_weight(self) -> int:
        return self.priority.weight


@dataclass
class Pet:
    """Represents a pet."""
    name: str
    species: Species = Species.OTHER
    age_years: float = 0.0
    notes: str = ""

    def __post_init__(self):
        if isinstance(self.species, str):
            self.species = Species(self.species)


@dataclass
class Owner:
    """Represents the pet owner and their daily constraints."""
    name: str
    available_minutes: int = 120          # total free time in the day
    day_start_hour: int = 7               # earliest task can start (24-h)
    day_end_hour: int = 21                # latest a task can *end* by (24-h)

    def __post_init__(self):
        if self.available_minutes < 0:
            raise ValueError("available_minutes must be ≥ 0")
        if not (0 <= self.day_start_hour < self.day_end_hour <= 24):
            raise ValueError("day_start_hour must be < day_end_hour")

    @property
    def day_capacity_minutes(self) -> int:
        return (self.day_end_hour - self.day_start_hour) * 60


# ─────────────────────────────────────────────
# Schedule output
# ─────────────────────────────────────────────

@dataclass
class ScheduledTask:
    """A task placed into a specific time slot."""
    task: Task
    start_time: datetime.time
    end_time: datetime.time
    reason: str = ""

    @property
    def start_minutes(self) -> int:
        return self.start_time.hour * 60 + self.start_time.minute

    @property
    def end_minutes(self) -> int:
        return self.end_time.hour * 60 + self.end_time.minute


@dataclass
class DailyPlan:
    """The full output of the scheduler."""
    owner: Owner
    pet: Pet
    scheduled: list[ScheduledTask] = field(default_factory=list)
    skipped: list[tuple[Task, str]] = field(default_factory=list)   # (task, reason)

    @property
    def total_scheduled_minutes(self) -> int:
        return sum(st.task.duration_minutes for st in self.scheduled)

    @property
    def utilization_pct(self) -> float:
        if self.owner.available_minutes == 0:
            return 0.0
        return min(100.0, self.total_scheduled_minutes / self.owner.available_minutes * 100)


# ─────────────────────────────────────────────
# Scheduler
# ─────────────────────────────────────────────

class Scheduler:
    """
    Greedy priority-first scheduler.

    Algorithm:
    1. Sort tasks by priority (desc), then by preferred_hour (tasks with a
       preferred_hour come before those without when priority ties).
    2. Walk through sorted tasks and place each one in the first available
       time slot that fits within the owner's day window and time budget.
    3. Tasks that cannot fit are recorded in DailyPlan.skipped.
    """

    GAP_MINUTES = 5   # buffer between tasks

    def build_plan(self, owner: Owner, pet: Pet, tasks: list[Task]) -> DailyPlan:
        plan = DailyPlan(owner=owner, pet=pet)

        if not tasks:
            return plan

        sorted_tasks = self._sort_tasks(tasks)

        # Track how many owner minutes remain
        remaining = owner.available_minutes
        # Current cursor in the day (minutes since midnight)
        cursor = owner.day_start_hour * 60
        day_end = owner.day_end_hour * 60

        for task in sorted_tasks:
            needed = task.duration_minutes

            # Try to honour preferred_hour
            if task.preferred_hour is not None:
                preferred_start = task.preferred_hour * 60
                # Snap cursor forward if preferred slot is later
                candidate = max(cursor, preferred_start)
            else:
                candidate = cursor

            end_candidate = candidate + needed

            # Check all constraints
            if needed > remaining:
                plan.skipped.append((
                    task,
                    f"Not enough time budget ({remaining} min left, needs {needed} min)"
                ))
                continue

            if end_candidate > day_end:
                # Try from current cursor as fallback (ignore preferred_hour)
                end_candidate = cursor + needed
                if end_candidate > day_end:
                    plan.skipped.append((
                        task,
                        f"Doesn't fit in the day window (ends after {owner.day_end_hour}:00)"
                    ))
                    continue
                candidate = cursor

            start_t = _minutes_to_time(candidate)
            end_t = _minutes_to_time(candidate + needed)

            reason = _build_reason(task, owner, pet)

            plan.scheduled.append(ScheduledTask(
                task=task,
                start_time=start_t,
                end_time=end_t,
                reason=reason,
            ))

            remaining -= needed
            cursor = candidate + needed + self.GAP_MINUTES

        return plan

    # ── helpers ──────────────────────────────

    @staticmethod
    def _sort_tasks(tasks: list[Task]) -> list[Task]:
        """
        Primary: priority descending.
        Secondary: tasks with a preferred_hour first (predictable timing helps owners).
        Tertiary: duration ascending (shorter tasks first among equals → more tasks fit).
        """
        def sort_key(t: Task):
            has_pref = 0 if t.preferred_hour is not None else 1
            return (-t.priority_weight, has_pref, t.duration_minutes)

        return sorted(tasks, key=sort_key)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _minutes_to_time(minutes: int) -> datetime.time:
    h, m = divmod(int(minutes), 60)
    h = min(h, 23)
    return datetime.time(h, m)


def _build_reason(task: Task, owner: Owner, pet: Pet) -> str:
    lines = []
    priority_text = {
        Priority.HIGH: "high-priority — essential for well-being",
        Priority.MEDIUM: "medium priority — important for routine",
        Priority.LOW: "low priority — nice to include when time allows",
    }[task.priority]

    lines.append(f"Scheduled because it is {priority_text}.")

    if task.preferred_hour is not None:
        lines.append(f"Placed near {task.preferred_hour}:00 as requested.")

    if task.notes:
        lines.append(f"Note: {task.notes}")

    # Species-specific tips
    if pet.species == Species.DOG and "walk" in task.title.lower():
        lines.append("Dogs benefit from consistent walk timing for bathroom and mental health.")
    elif pet.species == Species.CAT and "play" in task.title.lower():
        lines.append("Interactive play reduces stress and keeps indoor cats stimulated.")

    return " ".join(lines)


# ─────────────────────────────────────────────
# Default task templates
# ─────────────────────────────────────────────

DEFAULT_TASKS: dict[str, list[dict]] = {
    "dog": [
        {"title": "Morning walk",       "duration_minutes": 20, "priority": "high",   "preferred_hour": 7},
        {"title": "Feeding (breakfast)", "duration_minutes": 5,  "priority": "high",   "preferred_hour": 7},
        {"title": "Feeding (dinner)",    "duration_minutes": 5,  "priority": "high",   "preferred_hour": 18},
        {"title": "Evening walk",        "duration_minutes": 20, "priority": "high",   "preferred_hour": 18},
        {"title": "Playtime",            "duration_minutes": 15, "priority": "medium", "preferred_hour": None},
        {"title": "Brushing",            "duration_minutes": 10, "priority": "low",    "preferred_hour": None},
    ],
    "cat": [
        {"title": "Feeding (morning)",   "duration_minutes": 5,  "priority": "high",   "preferred_hour": 7},
        {"title": "Feeding (evening)",   "duration_minutes": 5,  "priority": "high",   "preferred_hour": 18},
        {"title": "Litter box cleaning", "duration_minutes": 5,  "priority": "high",   "preferred_hour": 8},
        {"title": "Interactive play",    "duration_minutes": 15, "priority": "medium", "preferred_hour": None},
        {"title": "Grooming",            "duration_minutes": 10, "priority": "low",    "preferred_hour": None},
    ],
    "other": [
        {"title": "Feeding",             "duration_minutes": 5,  "priority": "high",   "preferred_hour": 8},
        {"title": "Enrichment activity", "duration_minutes": 15, "priority": "medium", "preferred_hour": None},
        {"title": "Habitat cleaning",    "duration_minutes": 10, "priority": "medium", "preferred_hour": None},
    ],
}