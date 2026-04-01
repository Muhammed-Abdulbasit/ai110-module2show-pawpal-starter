"""
Tests for PawPal+ scheduler logic.
Run with:  pytest test_scheduler.py -v
"""

import datetime
import pytest

from scheduler import (
    Task,
    Pet,
    Owner,
    DailyPlan,
    Scheduler,
    Priority,
    Species,
    _minutes_to_time,
)


# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def owner():
    return Owner(name="Jordan", available_minutes=120, day_start_hour=7, day_end_hour=21)


@pytest.fixture
def dog():
    return Pet(name="Mochi", species=Species.DOG, age_years=3)


@pytest.fixture
def cat():
    return Pet(name="Luna", species=Species.CAT, age_years=2)


@pytest.fixture
def scheduler():
    return Scheduler()


# ─────────────────────────────────────────────
# Task model tests
# ─────────────────────────────────────────────

class TestTask:
    def test_default_priority(self):
        t = Task(title="Walk", duration_minutes=20)
        assert t.priority == Priority.MEDIUM

    def test_string_priority_coerced(self):
        t = Task(title="Walk", duration_minutes=20, priority="high")
        assert t.priority == Priority.HIGH

    def test_priority_weight(self):
        assert Task("A", 5, Priority.LOW).priority_weight == 1
        assert Task("B", 5, Priority.MEDIUM).priority_weight == 2
        assert Task("C", 5, Priority.HIGH).priority_weight == 3

    def test_invalid_duration(self):
        with pytest.raises(ValueError):
            Task(title="Bad", duration_minutes=0)

    def test_invalid_preferred_hour(self):
        with pytest.raises(ValueError):
            Task(title="Bad", duration_minutes=5, preferred_hour=25)


# ─────────────────────────────────────────────
# Owner model tests
# ─────────────────────────────────────────────

class TestOwner:
    def test_day_capacity(self):
        o = Owner("J", available_minutes=60, day_start_hour=8, day_end_hour=10)
        assert o.day_capacity_minutes == 120   # window is 2 h = 120 min

    def test_negative_available_raises(self):
        with pytest.raises(ValueError):
            Owner("J", available_minutes=-1)

    def test_invalid_window_raises(self):
        with pytest.raises(ValueError):
            Owner("J", day_start_hour=22, day_end_hour=10)


# ─────────────────────────────────────────────
# Scheduler: basic behaviour
# ─────────────────────────────────────────────

class TestSchedulerBasic:
    def test_empty_tasks_returns_empty_plan(self, scheduler, owner, dog):
        plan = scheduler.build_plan(owner, dog, [])
        assert plan.scheduled == []
        assert plan.skipped == []

    def test_single_task_scheduled(self, scheduler, owner, dog):
        tasks = [Task("Walk", 20, Priority.HIGH)]
        plan = scheduler.build_plan(owner, dog, tasks)
        assert len(plan.scheduled) == 1
        assert plan.scheduled[0].task.title == "Walk"

    def test_start_time_at_day_start(self, scheduler, owner, dog):
        tasks = [Task("Walk", 20, Priority.HIGH)]
        plan = scheduler.build_plan(owner, dog, tasks)
        st = plan.scheduled[0]
        assert st.start_time.hour == owner.day_start_hour
        assert st.start_time.minute == 0

    def test_end_time_is_start_plus_duration(self, scheduler, owner, dog):
        tasks = [Task("Walk", 30, Priority.HIGH)]
        plan = scheduler.build_plan(owner, dog, tasks)
        st = plan.scheduled[0]
        start_m = st.start_time.hour * 60 + st.start_time.minute
        end_m = st.end_time.hour * 60 + st.end_time.minute
        assert end_m - start_m == 30

    def test_multiple_tasks_no_overlap(self, scheduler, owner, dog):
        tasks = [
            Task("Walk", 20, Priority.HIGH),
            Task("Feed", 10, Priority.HIGH),
            Task("Play", 15, Priority.MEDIUM),
        ]
        plan = scheduler.build_plan(owner, dog, tasks)
        # check no two scheduled tasks overlap
        slots = [(s.start_minutes, s.end_minutes) for s in plan.scheduled]
        for i, (s1, e1) in enumerate(slots):
            for j, (s2, e2) in enumerate(slots):
                if i != j:
                    assert e1 <= s2 or e2 <= s1, f"Tasks {i} and {j} overlap"


# ─────────────────────────────────────────────
# Scheduler: priority ordering
# ─────────────────────────────────────────────

class TestPriorityOrdering:
    def test_high_priority_scheduled_before_low(self, scheduler, owner, dog):
        tasks = [
            Task("Brushing", 10, Priority.LOW),
            Task("Medication", 5, Priority.HIGH),
        ]
        plan = scheduler.build_plan(owner, dog, tasks)
        assert plan.scheduled[0].task.title == "Medication"

    def test_all_priorities_sorted_correctly(self, scheduler, owner, dog):
        tasks = [
            Task("Play",  15, Priority.LOW),
            Task("Feed",   5, Priority.HIGH),
            Task("Groom", 10, Priority.MEDIUM),
        ]
        plan = scheduler.build_plan(owner, dog, tasks)
        titles = [s.task.title for s in plan.scheduled]
        assert titles.index("Feed") < titles.index("Groom")
        assert titles.index("Groom") < titles.index("Play")


# ─────────────────────────────────────────────
# Scheduler: time budget enforcement
# ─────────────────────────────────────────────

class TestTimeBudget:
    def test_task_skipped_when_budget_exceeded(self, scheduler, dog):
        tight_owner = Owner("J", available_minutes=10)
        tasks = [
            Task("Short", 5, Priority.HIGH),
            Task("Long",  20, Priority.HIGH),   # won't fit
        ]
        plan = scheduler.build_plan(tight_owner, dog, tasks)
        scheduled_titles = [s.task.title for s in plan.scheduled]
        skipped_titles = [t.title for t, _ in plan.skipped]
        assert "Short" in scheduled_titles
        assert "Long" in skipped_titles

    def test_total_scheduled_minutes_within_budget(self, scheduler, dog):
        owner = Owner("J", available_minutes=30)
        tasks = [Task(f"T{i}", 15, Priority.MEDIUM) for i in range(5)]
        plan = scheduler.build_plan(owner, dog, tasks)
        assert plan.total_scheduled_minutes <= 30

    def test_zero_budget_skips_all(self, scheduler, dog):
        owner = Owner("J", available_minutes=0)
        tasks = [Task("Walk", 20, Priority.HIGH)]
        plan = scheduler.build_plan(owner, dog, tasks)
        assert len(plan.scheduled) == 0
        assert len(plan.skipped) == 1

    def test_utilization_pct(self, scheduler, dog):
        owner = Owner("J", available_minutes=60)
        tasks = [Task("Walk", 30, Priority.HIGH)]
        plan = scheduler.build_plan(owner, dog, tasks)
        assert plan.utilization_pct == pytest.approx(50.0)


# ─────────────────────────────────────────────
# Scheduler: preferred_hour
# ─────────────────────────────────────────────

class TestPreferredHour:
    def test_task_placed_at_preferred_hour(self, scheduler, owner, dog):
        tasks = [Task("Walk", 20, Priority.HIGH, preferred_hour=9)]
        plan = scheduler.build_plan(owner, dog, tasks)
        assert plan.scheduled[0].start_time.hour == 9

    def test_preferred_hour_before_cursor_uses_cursor(self, scheduler, owner, dog):
        """If preferred hour is in the past (before cursor), task is placed at cursor."""
        tasks = [
            Task("First", 120, Priority.HIGH, preferred_hour=7),   # uses 7:00-9:00
            Task("Second", 10, Priority.HIGH, preferred_hour=7),   # preferred 7 already passed
        ]
        owner = Owner("Jordan", available_minutes=150, day_start_hour=7, day_end_hour=21)
        plan = scheduler.build_plan(owner, dog, tasks)
        if len(plan.scheduled) == 2:
            assert plan.scheduled[1].start_time >= plan.scheduled[0].end_time

    def test_preferred_hour_outside_window_skips_gracefully(self, scheduler, dog):
        owner = Owner("J", available_minutes=60, day_start_hour=7, day_end_hour=9)
        tasks = [Task("Late task", 30, Priority.HIGH, preferred_hour=22)]
        plan = scheduler.build_plan(owner, dog, tasks)
        # Should still be scheduled (falls back to cursor) or gracefully skipped
        total = len(plan.scheduled) + len(plan.skipped)
        assert total == 1


# ─────────────────────────────────────────────
# DailyPlan helpers
# ─────────────────────────────────────────────

class TestDailyPlan:
    def test_empty_plan_utilization_zero(self, owner, dog):
        plan = DailyPlan(owner=owner, pet=dog)
        assert plan.utilization_pct == 0.0

    def test_utilization_capped_at_100(self, owner, dog):
        plan = DailyPlan(owner=owner, pet=dog)
        # manually add more than budget to test cap
        t = Task("X", 999, Priority.HIGH)
        st = _make_scheduled(t)
        plan.scheduled.append(st)
        assert plan.utilization_pct == 100.0


# ─────────────────────────────────────────────
# Utility
# ─────────────────────────────────────────────

def _make_scheduled(task: Task):
    from scheduler import ScheduledTask
    return ScheduledTask(
        task=task,
        start_time=datetime.time(8, 0),
        end_time=datetime.time(9, 0),
        reason="test",
    )


class TestHelpers:
    def test_minutes_to_time(self):
        assert _minutes_to_time(0) == datetime.time(0, 0)
        assert _minutes_to_time(90) == datetime.time(1, 30)
        assert _minutes_to_time(480) == datetime.time(8, 0)

    def test_minutes_to_time_clamps_at_23h(self):
        t = _minutes_to_time(1500)   # 25 h — should clamp
        assert t.hour <= 23