"""
PawPal+ — Streamlit frontend
"""

import datetime
import streamlit as st

from scheduler import (
    Task,
    Pet,
    Owner,
    Scheduler,
    Priority,
    Species,
    DEFAULT_TASKS,
)

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="PawPal+",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
}

h1, h2, h3 {
    font-family: 'Fredoka One', cursive;
    letter-spacing: 0.5px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #ffa8f0 0%, #ffecd2 100%);
    border-right: 2px solid #ffd39e;
}

/* Cards */
.task-card {
    background: white;
    border-radius: 16px;
    padding: 14px 18px;
    margin-bottom: 10px;
    border-left: 5px solid #ff8c42;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}

.task-card.high   { border-left-color: #e63946; }
.task-card.medium { border-left-color: #f4a261; }
.task-card.low    { border-left-color: #57cc99; }

.schedule-row {
    background: white;
    border-radius: 14px;
    padding: 12px 18px;
    margin-bottom: 8px;
    display: flex;
    align-items: flex-start;
    gap: 14px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}

.time-badge {
    background: #fff3e0;
    border-radius: 10px;
    padding: 4px 10px;
    font-weight: 700;
    color: #e65100;
    font-size: 0.85rem;
    white-space: nowrap;
    font-family: 'Nunito', sans-serif;
}

.priority-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
}
.dot-high   { background: #e63946; }
.dot-medium { background: #f4a261; }
.dot-low    { background: #57cc99; }

.skipped-card {
    background: #fff5f5;
    border-radius: 12px;
    padding: 10px 16px;
    margin-bottom: 6px;
    border-left: 4px solid #ff6b6b;
    color: #c0392b;
    font-size: 0.9rem;
}

.stat-box {
    background: white;
    border-radius: 14px;
    padding: 18px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.stat-number {
    font-family: 'Fredoka One', cursive;
    font-size: 2.2rem;
    color: #ff8c42;
    line-height: 1;
}

.stat-label {
    font-size: 0.8rem;
    color: #888;
    margin-top: 4px;
}

.reason-text {
    font-size: 0.82rem;
    color: #666;
    margin-top: 4px;
    font-style: italic;
}

.header-band {
    background: linear-gradient(90deg, #ff8c42, #ff6b35);
    border-radius: 18px;
    padding: 24px 32px;
    margin-bottom: 24px;
    color: white;
}

.header-band h1 { color: white; font-size: 2.4rem; margin: 0; }
.header-band p  { margin: 4px 0 0 0; opacity: 0.9; font-size: 1rem; }

div[data-testid="stButton"] > button {
    border-radius: 12px;
    font-family: 'Nunito', sans-serif;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Session state init
# ─────────────────────────────────────────────

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "plan" not in st.session_state:
    st.session_state.plan = None

# ─────────────────────────────────────────────
# Sidebar — Owner + Pet info
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 👤 Owner Info")
    owner_name = st.text_input("Your name", value="Jordan")
    available_minutes = st.slider(
        "Free time today (minutes)", min_value=15, max_value=480, value=120, step=15
    )
    day_start = st.slider("Day starts (hour)", min_value=5, max_value=12, value=7)
    day_end = st.slider("Day ends (hour)", min_value=16, max_value=23, value=21)

    st.markdown("---")
    st.markdown("## 🐾 Pet Info")
    pet_name = st.text_input("Pet name", value="Mochi")
    species_str = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age (years)", min_value=0.0, max_value=30.0, value=3.0, step=0.5)

    st.markdown("---")
    if st.button("📋 Load default tasks for this pet", use_container_width=True):
        defaults = DEFAULT_TASKS.get(species_str, DEFAULT_TASKS["other"])
        st.session_state.tasks = [dict(t) for t in defaults]
        st.session_state.plan = None
        st.rerun()

    if st.button("🗑️ Clear all tasks", use_container_width=True):
        st.session_state.tasks = []
        st.session_state.plan = None
        st.rerun()

# Build domain objects
try:
    owner = Owner(
        name=owner_name,
        available_minutes=available_minutes,
        day_start_hour=day_start,
        day_end_hour=day_end,
    )
    pet = Pet(name=pet_name, species=Species(species_str), age_years=age)
except ValueError as e:
    st.error(f"Configuration error: {e}")
    st.stop()

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────

st.markdown(f"""
<div class="header-band">
  <h1>🐾 PawPal+</h1>
  <p>Daily care planner for <strong>{pet_name}</strong> the {species_str} · {owner_name}'s schedule</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Two-column layout
# ─────────────────────────────────────────────

left_col, right_col = st.columns([1, 1.4], gap="large")

# ── LEFT: Task management ─────────────────────

with left_col:
    st.markdown("### ➕ Add a Task")

    with st.container():
        task_title = st.text_input("Task name", value="Morning walk", key="task_title")

        c1, c2 = st.columns(2)
        with c1:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with c2:
            priority_str = st.selectbox("Priority", ["high", "medium", "low"])

        pref_hour_enabled = st.checkbox("Set a preferred time?")
        preferred_hour = None
        if pref_hour_enabled:
            preferred_hour = st.slider("Preferred hour", min_value=day_start, max_value=day_end - 1, value=day_start)

        notes = st.text_input("Notes (optional)", value="", key="task_notes")

        if st.button("➕ Add Task", use_container_width=True, type="primary"):
            new_task = {
                "title": task_title.strip() or "Unnamed task",
                "duration_minutes": int(duration),
                "priority": priority_str,
                "preferred_hour": preferred_hour,
                "notes": notes,
            }
            st.session_state.tasks.append(new_task)
            st.session_state.plan = None
            st.rerun()

    st.markdown("---")
    st.markdown(f"### 📋 Task List  `{len(st.session_state.tasks)} tasks`")

    if not st.session_state.tasks:
        st.info("No tasks yet. Add one above or load defaults from the sidebar.")
    else:
        for i, t in enumerate(st.session_state.tasks):
            priority_class = t["priority"]
            pref = f" · ⏰ {t['preferred_hour']}:00" if t.get("preferred_hour") is not None else ""
            notes_text = f"<br><small style='color:#999'>{t['notes']}</small>" if t.get("notes") else ""

            dot_class = f"dot-{priority_class}"
            st.markdown(f"""
            <div class="task-card {priority_class}">
              <span class="priority-dot {dot_class}"></span>
              <strong>{t['title']}</strong>
              <span style="float:right; color:#aaa; font-size:0.85rem">{t['duration_minutes']} min · {t['priority']}{pref}</span>
              {notes_text}
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"🗑 Remove", key=f"del_{i}"):
                st.session_state.tasks.pop(i)
                st.session_state.plan = None
                st.rerun()

# ── RIGHT: Schedule ───────────────────────────

with right_col:
    st.markdown("### 🗓 Daily Schedule")

    total_task_minutes = sum(t["duration_minutes"] for t in st.session_state.tasks)

    # Stats bar
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""
        <div class="stat-box">
          <div class="stat-number">{len(st.session_state.tasks)}</div>
          <div class="stat-label">Tasks queued</div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="stat-box">
          <div class="stat-number">{available_minutes}</div>
          <div class="stat-label">Min available</div>
        </div>""", unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="stat-box">
          <div class="stat-number">{total_task_minutes}</div>
          <div class="stat-label">Min needed</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    generate_clicked = st.button("🚀 Generate Schedule", use_container_width=True, type="primary")

    if generate_clicked:
        if not st.session_state.tasks:
            st.warning("Add at least one task first!")
        else:
            try:
                task_objs = [
                    Task(
                        title=t["title"],
                        duration_minutes=t["duration_minutes"],
                        priority=Priority(t["priority"]),
                        preferred_hour=t.get("preferred_hour"),
                        notes=t.get("notes", ""),
                    )
                    for t in st.session_state.tasks
                ]
                sched = Scheduler()
                plan = sched.build_plan(owner, pet, task_objs)
                st.session_state.plan = plan
            except Exception as e:
                st.error(f"Scheduling failed: {e}")

    plan = st.session_state.plan

    if plan is not None:
        pct = plan.utilization_pct
        colour = "#57cc99" if pct <= 80 else "#f4a261" if pct <= 100 else "#e63946"

        st.markdown(f"""
        <div style="background:{colour}22; border-radius:12px; padding:12px 18px; margin:12px 0;
             border-left:4px solid {colour}; color:{colour}; font-weight:700;">
          📊 {plan.total_scheduled_minutes} / {owner.available_minutes} min scheduled
          &nbsp;·&nbsp; {pct:.0f}% of time budget
        </div>
        """, unsafe_allow_html=True)

        if plan.scheduled:
            st.markdown("#### ✅ Scheduled Tasks")
            for st_task in plan.scheduled:
                start_str = st_task.start_time.strftime("%I:%M %p").lstrip("0")
                end_str   = st_task.end_time.strftime("%I:%M %p").lstrip("0")
                p = st_task.task.priority.value
                dot = f"dot-{p}"
                st.markdown(f"""
                <div class="schedule-row">
                  <span class="time-badge">{start_str} – {end_str}</span>
                  <div>
                    <span class="priority-dot {dot}"></span>
                    <strong>{st_task.task.title}</strong>
                    <span style="color:#aaa; font-size:0.8rem"> · {st_task.task.duration_minutes} min · {p}</span>
                    <div class="reason-text">💡 {st_task.reason}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

        if plan.skipped:
            st.markdown("#### ⏭ Skipped Tasks")
            for skipped_task, reason in plan.skipped:
                st.markdown(f"""
                <div class="skipped-card">
                  ❌ <strong>{skipped_task.title}</strong> — {reason}
                </div>
                """, unsafe_allow_html=True)

    elif not generate_clicked:
        st.markdown("""
        <div style="background:#fff8f0; border-radius:16px; padding:32px; text-align:center; color:#bbb; margin-top:16px;">
          <div style="font-size:3rem">🐾</div>
          <div style="font-size:1rem; margin-top:8px;">Add tasks, then click <strong>Generate Schedule</strong></div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<small style='color:#bbb'>PawPal+ · Module 2 Project · Greedy priority-first scheduler</small>",
    unsafe_allow_html=True,
)