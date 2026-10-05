import streamlit as st
import requests
from datetime import date, datetime, timedelta

API_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbwtCP3CVsbAg3BcoDVa0YvbkLEwPjYFQvCYMAvB2lAWeGXg2fp1nsNbGoETWsnIAJx0gQ/exec"
)

st.set_page_config(
    page_title="Daily Work Tracker",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# Styling
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background: #0f172a;
        color: #e5e7eb;
    }

    [data-testid="stHeader"] {
        background: #0f172a;
    }

    [data-testid="stToolbar"] {
        visibility: hidden;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #f8fafc !important;
    }

    .tracker-subtitle {
        color: #94a3b8;
        margin-top: -10px;
        margin-bottom: 24px;
    }

    .section-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 22px;
    }

    .metric-card {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px 10px;
        text-align: center;
        min-height: 100px;
    }

    .metric-number {
        color: #60a5fa;
        font-size: 28px;
        font-weight: 700;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 13px;
        margin-top: 4px;
    }

    .entry-card {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
    }

    .entry-project {
        color: #60a5fa;
        font-weight: 700;
        font-size: 15px;
    }

    .entry-status {
        color: #93c5fd;
        background: #172554;
        border-radius: 20px;
        padding: 4px 10px;
        font-size: 12px;
        font-weight: 600;
    }

    .entry-work {
        color: #f1f5f9;
        font-size: 16px;
        margin: 10px 0;
    }

    .entry-meta {
        color: #94a3b8;
        font-size: 13px;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stDateInput"] input,
    div[data-testid="stTimeInput"] input {
        background: #0f172a;
        color: #f8fafc;
    }

    div[data-baseweb="select"] > div {
        background: #0f172a;
        color: #f8fafc;
        border-color: #475569;
    }

    div[data-testid="stButton"] button {
        border-radius: 9px;
        font-weight: 600;
    }

    .stCaption {
        color: #94a3b8 !important;
    }

    @media (max-width: 700px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# API helpers
# ---------------------------------------------------------

@st.cache_data(ttl=30)
def fetch_entries():
    response = requests.get(API_URL, timeout=20)
    response.raise_for_status()
    data = response.json()

    entries = []
    for index, item in enumerate(data):
        entries.append(
            {
                "id": item.get("_row", index),
                "row": item.get("_row"),
                "date": item.get("Date", ""),
                "time": item.get("Time", ""),
                "project": item.get("Project", ""),
                "workDone": item.get("Work Done", ""),
                "timeSpent": item.get("Time Spent", ""),
                "status": item.get("Status", ""),
                "notes": item.get("Notes", ""),
            }
        )

    return entries


@st.cache_data(ttl=30)
def fetch_projects():
    response = requests.get(
        API_URL,
        params={"type": "projects"},
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()

    return [
        item.get("Project", "")
        for item in data
        if item.get("Project")
    ]


def post_data(payload):
    response = requests.post(
        API_URL,
        json=payload,
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def refresh_data():
    fetch_entries.clear()
    fetch_projects.clear()


# ---------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------

def parse_minutes(value):
    if not value:
        return 0

    text = str(value).lower().strip()

    hours = 0
    minutes = 0

    import re

    hour_match = re.search(r"(\d+(?:\.\d+)?)\s*h", text)
    minute_match = re.search(r"(\d+(?:\.\d+)?)\s*m", text)

    if hour_match:
        hours = float(hour_match.group(1))

    if minute_match:
        minutes = float(minute_match.group(1))

    if not hour_match and not minute_match:
        try:
            hours = float(text)
        except ValueError:
            return 0

    return int(round(hours * 60 + minutes))


def format_total_time(entries):
    total = sum(parse_minutes(entry["timeSpent"]) for entry in entries)

    hours = total // 60
    minutes = total % 60

    if hours and minutes:
        return f"{hours}h {minutes}m"

    if hours:
        return f"{hours}h"

    if minutes:
        return f"{minutes}m"

    return "0h"


def metric(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-number">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_entry(entry):
    st.markdown(
        f"""
        <div class="entry-card">
            <div style="display:flex;justify-content:space-between;gap:12px;">
                <span class="entry-project">{entry["project"]}</span>
                <span class="entry-status">{entry["status"]}</span>
            </div>
            <div class="entry-work">{entry["workDone"]}</div>
            <div class="entry-meta">
                {entry["date"]} · {entry["time"]} ·
                {entry["timeSpent"] or "Time not specified"}
            </div>
            {
                f'<div class="entry-meta" style="margin-top:6px;">Notes: {entry["notes"]}</div>'
                if entry["notes"]
                else ""
            }
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

if "history_date" not in st.session_state:
    st.session_state.history_date = date.today()

if "editing_entry" not in st.session_state:
    st.session_state.editing_entry = None

if "form_key" not in st.session_state:
    st.session_state.form_key = 0


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

try:
    entries = fetch_entries()
    projects = fetch_projects()
except Exception as error:
    st.error(f"Could not connect to the Google Sheet API: {error}")
    st.stop()


today_string = date.today().isoformat()

today_entries = [
    entry for entry in entries
    if entry["date"] == today_string
]


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("📋 Daily Work Tracker")
st.markdown(
    '<div class="tracker-subtitle">Track what you work on each day.</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Today's Dashboard
# ---------------------------------------------------------

st.markdown('<div class="section-card">', unsafe_allow_html=True)

st.subheader("Today's Dashboard")
st.caption(today_string)

dashboard_columns = st.columns(5)

with dashboard_columns[0]:
    metric("Work Entries", len(today_entries))

with dashboard_columns[1]:
    metric(
        "Done",
        sum(1 for e in today_entries if e["status"] == "Done"),
    )

with dashboard_columns[2]:
    metric(
        "In Progress",
        sum(
            1
            for e in today_entries
            if e["status"] == "In Progress"
        ),
    )

with dashboard_columns[3]:
    metric(
        "Blocked",
        sum(
            1
            for e in today_entries
            if e["status"] == "Blocked"
        ),
    )

with dashboard_columns[4]:
    metric("Total Time", format_total_time(today_entries))

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# Add / Edit Work
# ---------------------------------------------------------

editing_entry = st.session_state.editing_entry

st.markdown('<div class="section-card">', unsafe_allow_html=True)

st.subheader(
    "Edit Work" if editing_entry else "Add Work"
)

if not projects:
    st.warning("No active projects found in the Projects sheet.")
    st.stop()

project_options = list(projects)

if (
    editing_entry
    and editing_entry["project"]
    and editing_entry["project"] not in project_options
):
    project_options.insert(0, editing_entry["project"])


form_key = f"work_form_{st.session_state.form_key}"

with st.form(form_key):

    default_date = (
        datetime.strptime(
            editing_entry["date"],
            "%Y-%m-%d",
        ).date()
        if editing_entry and editing_entry["date"]
        else date.today()
    )

    default_time = (
        datetime.strptime(
            editing_entry["time"],
            "%H:%M",
        ).time()
        if editing_entry and editing_entry["time"]
        else datetime.now().time().replace(second=0, microsecond=0)
    )

    selected_date = st.date_input(
        "Date",
        value=default_date,
    )

    selected_time = st.time_input(
        "Time",
        value=default_time,
    )

    work_done = st.text_area(
        "What did you work on?",
        value=editing_entry["workDone"] if editing_entry else "",
        placeholder="Describe the work you did...",
    )

    selected_project = st.selectbox(
        "Project",
        options=project_options,
        index=(
            project_options.index(editing_entry["project"])
            if editing_entry
            and editing_entry["project"] in project_options
            else 0
        ),
    )

    time_spent = st.text_input(
        "Time Spent",
        value=editing_entry["timeSpent"] if editing_entry else "",
        placeholder="e.g. 1h 30m",
    )

    selected_status = st.selectbox(
        "Status",
        options=["Done", "In Progress", "Blocked"],
        index=(
            ["Done", "In Progress", "Blocked"].index(
                editing_entry["status"]
            )
            if editing_entry
            and editing_entry["status"]
            in ["Done", "In Progress", "Blocked"]
            else 0
        ),
    )

    notes = st.text_area(
        "Notes",
        value=editing_entry["notes"] if editing_entry else "",
        placeholder="Optional notes...",
    )

    submit_label = (
        "Save Changes"
        if editing_entry
        else "Add Work"
    )

    submitted = st.form_submit_button(
        submit_label,
        type="primary",
        use_container_width=True,
    )


if submitted:
    if not work_done.strip():
        st.error("Please enter what you worked on.")
    else:
        payload = {
            "date": selected_date.isoformat(),
            "time": selected_time.strftime("%H:%M"),
            "project": selected_project,
            "workDone": work_done.strip(),
            "timeSpent": time_spent.strip(),
            "status": selected_status,
            "notes": notes.strip(),
        }

        if editing_entry:
            payload["action"] = "update"
            payload["row"] = editing_entry["row"]

        try:
            result = post_data(payload)

            if result.get("success"):
                st.success(
                    "Work entry updated successfully."
                    if editing_entry
                    else "Work saved successfully."
                )

                st.session_state.editing_entry = None
                st.session_state.form_key += 1

                refresh_data()
                st.rerun()
            else:
                st.error(
                    result.get(
                        "error",
                        "The operation could not be completed.",
                    )
                )

        except Exception as error:
            st.error(f"Could not save the work entry: {error}")


if editing_entry:
    if st.button("Cancel Edit", use_container_width=True):
        st.session_state.editing_entry = None
        st.session_state.form_key += 1
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------
# Work History
# ---------------------------------------------------------

history_date = st.session_state.history_date
history_string = history_date.isoformat()

history_entries = [
    entry
    for entry in entries
    if entry["date"] == history_string
]

history_done = sum(
    1 for entry in history_entries
    if entry["status"] == "Done"
)

history_in_progress = sum(
    1 for entry in history_entries
    if entry["status"] == "In Progress"
)

history_blocked = sum(
    1 for entry in history_entries
    if entry["status"] == "Blocked"
)

st.markdown('<div class="section-card">', unsafe_allow_html=True)

history_header_left, history_header_right = st.columns(
    [4, 1]
)

with history_header_left:
    st.subheader("Work History")
    st.caption(
        history_date.strftime("%d %B %Y")
    )

with history_header_right:
    if st.button(
        "Today",
        use_container_width=True,
    ):
        st.session_state.history_date = date.today()
        st.rerun()


# Date navigation

previous_col, date_col, next_col = st.columns(
    [1, 1, 1]
)

with previous_col:
    if st.button(
        "← Previous Day",
        use_container_width=True,
    ):
        st.session_state.history_date = (
            history_date - timedelta(days=1)
        )
        st.rerun()

with date_col:
    chosen_history_date = st.date_input(
        "History Date",
        value=history_date,
        label_visibility="collapsed",
    )

    if chosen_history_date != history_date:
        st.session_state.history_date = chosen_history_date
        st.rerun()

with next_col:
    if st.button(
        "Next Day →",
        use_container_width=True,
    ):
        st.session_state.history_date = (
            history_date + timedelta(days=1)
        )
        st.rerun()


# History summary

summary_columns = st.columns(5)

with summary_columns[0]:
    metric("Entries", len(history_entries))

with summary_columns[1]:
    metric("Done", history_done)

with summary_columns[2]:
    metric("In Progress", history_in_progress)

with summary_columns[3]:
    metric("Blocked", history_blocked)

with summary_columns[4]:
    metric(
        "Total Time",
        format_total_time(history_entries),
    )


st.divider()


# History entries

if not history_entries:
    st.info("No work entries found for this date.")
else:
    for entry in history_entries:
        render_entry(entry)

        edit_col, delete_col, spacer = st.columns(
            [1, 1, 4]
        )

        with edit_col:
            if st.button(
                "Edit",
                key=f"edit_{entry['id']}",
                use_container_width=True,
            ):
                st.session_state.editing_entry = entry
                st.session_state.form_key += 1
                st.rerun()

        with delete_col:
            if st.button(
                "Delete",
                key=f"delete_{entry['id']}",
                use_container_width=True,
            ):
                st.session_state.delete_confirmation = entry["id"]

        if st.session_state.get("delete_confirmation") == entry["id"]:
            st.warning(
                f"Delete this entry?\n\n{entry['workDone']}"
            )

            confirm_col, cancel_col, _ = st.columns(
                [1, 1, 4]
            )

            with confirm_col:
                if st.button(
                    "Confirm Delete",
                    key=f"confirm_{entry['id']}",
                    type="primary",
                ):
                    try:
                        result = post_data(
                            {
                                "action": "delete",
                                "row": entry["row"],
                            }
                        )

                        if result.get("success"):
                            st.session_state.delete_confirmation = None
                            refresh_data()
                            st.rerun()
                        else:
                            st.error(
                                result.get(
                                    "error",
                                    "Could not delete the entry.",
                                )
                            )

                    except Exception as error:
                        st.error(
                            f"Could not delete the work entry: {error}"
                        )

            with cancel_col:
                if st.button(
                    "Cancel",
                    key=f"cancel_delete_{entry['id']}",
                ):
                    st.session_state.delete_confirmation = None
                    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
