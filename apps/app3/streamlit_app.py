import streamlit as st
import pandas as pd
import json
import datetime

if "update_message" in st.session_state:
    st.success(st.session_state["update_message"])
    del st.session_state["update_message"]


st.set_page_config(page_title="Incident Management", layout="wide")

DATA_FILE = "data.json"
with open(DATA_FILE, "r") as f:
    data = json.load(f)
df = pd.DataFrame(data)

def is_tagged(row):
    cols = [c for c in df.columns if c not in ["incident_id", "incident_number"]]
    return any(str(row[c]).strip() not in ["", "None", "nan", "NaN", None] for c in cols)

df["tagged"] = df.apply(is_tagged, axis=1)

# Sidebar filters
st.sidebar.header("Filters")
filter_type = st.sidebar.radio("Show", ["All", "Tagged", "Untagged"])
custodian_teams = df["custodian_team"].dropna().unique().tolist()
selected_teams = st.sidebar.multiselect("Custodian Team", custodian_teams, default=custodian_teams)

# --- Date range filter ---
max_date = datetime.datetime.today() + datetime.timedelta(days=1)
min_date = max_date - datetime.timedelta(days=31)
date_range = st.sidebar.date_input(
    "Record Created On (Date Range)",
    value=(min_date.date() if pd.notnull(min_date) else datetime.date.today(),
           max_date.date() if pd.notnull(max_date) else datetime.date.today())
)

filtered_df = df.copy()
if filter_type == "Tagged":
    filtered_df = filtered_df[filtered_df["tagged"]]
elif filter_type == "Untagged":
    filtered_df = filtered_df[~filtered_df["tagged"]]
if selected_teams:
    filtered_df = filtered_df[filtered_df["custodian_team"].isin(selected_teams)]

# --- Apply date range filter ---
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    filtered_df = filtered_df[
        (pd.to_datetime(filtered_df["record_created_on"], errors="coerce") >= start_ts) &
        (pd.to_datetime(filtered_df["record_created_on"], errors="coerce") <= end_ts)
    ]

# --- Advanced Multi-Column Filter ---
multi_filter_cols = st.sidebar.multiselect(
    "Select columns to filter",
    options=[c for c in df.columns if c not in ["incident_id", "incident_number", "tagged", "record_created_on", "record_updated_on"]],
    key="multi_filter_columns"  # <-- Add a unique key here
)
multi_filter_values = {}
for col in multi_filter_cols:
    unique_vals = df[col].dropna().unique().tolist()
    multi_filter_values[col] = st.sidebar.multiselect(
        f"Filter {col.replace('_', ' ').title()}",
        options=unique_vals,
        default=[],
        key=f"multi_filter_{col}"  # <-- Unique key for each column
    )
for col, vals in multi_filter_values.items():
    if vals:
        filtered_df = filtered_df[filtered_df[col].isin(vals)]

# Convert date columns to datetime
for date_col in ["record_created_on", "record_updated_on"]:
    if date_col in filtered_df.columns:
        filtered_df[date_col] = pd.to_datetime(filtered_df[date_col], errors="coerce")

st.title("🚨 Incident Management Dashboard")
st.caption("Bulk or individual edit of incidents. Select rows and update fields for all selected.")

# Toggle for table editability
editable = st.toggle("Enable Table Editing", value=False)

edit_cols = [c for c in df.columns if c not in ["tagged"]]

# Set column config for data_editor
column_config = {}
for col in edit_cols:
    if col == "incident_id":
        column_config[col] = st.column_config.NumberColumn(
            col.replace("_", " ").title(),
            disabled=True
        )
    elif col == "incident_number":
        column_config[col] = st.column_config.TextColumn(
            col.replace("_", " ").title(),
            disabled=True
        )
    elif col == "failure_category":
        column_config[col] = st.column_config.SelectboxColumn(
            col.replace("_", " ").title(),
            options=["Hardware", "Software"]
        )
    elif col in [
        "record_created_on",
        "record_updated_on"
    ]:
        column_config[col] = st.column_config.DatetimeColumn(
            col.replace("_", " ").title()
        )
    elif col == "comments":
        column_config[col] = st.column_config.TextColumn(
            col.replace("_", " ").title(),
            width="large"
        )
    elif col == "actual_time_spent_in_minutes":
        column_config[col] = st.column_config.NumberColumn(
            col.replace("_", " ").title(),
            step=1,
            format="%.2f"
        )
    else:
        column_config[col] = st.column_config.TextColumn(
            col.replace("_", " ").title()
        )

st.write("### Incident Table (Edit single rows directly below)")
edited_df = st.data_editor(
    filtered_df[edit_cols],
    column_config=column_config,
    disabled=not editable,
    use_container_width=True,
    hide_index=True,
    num_rows="fixed"
)

if editable and st.button("Save Table Changes"):
    updated_count = 0
    for idx, row in edited_df.iterrows():
        eid = row["incident_id"]
        orig_row = filtered_df[filtered_df["incident_id"] == eid].iloc[0]
        row_updated = False
        updated_cols = {}
        for col in edit_cols:
            if col in ["incident_id", "incident_number"]:
                continue  # skip non-editable columns
            old_val = orig_row[col]
            new_val = row[col]
            # Fix for actual_time_spent_in_minutes
            if col == "actual_time_spent_in_minutes":
                try:
                    if new_val in ["", None]:
                        new_val = None
                    else:
                        new_val = float(new_val)
                except:
                    new_val = None
            # Fix for date columns
            if col in ["record_created_on", "record_updated_on"]:
                if pd.notnull(new_val) and isinstance(new_val, (datetime.datetime, pd.Timestamp)):
                    new_val = new_val.isoformat()
                elif isinstance(new_val, str):
                    new_val = new_val
                else:
                    new_val = ""
            if pd.isnull(old_val) and new_val not in [None, ""]:
                row_updated = True
            elif new_val != old_val and new_val not in [None, ""]:
                row_updated = True
            if row_updated:
                updated_cols[col] = new_val
        # Only update if changed
        if row_updated:
            for col, val in updated_cols.items():
                df.loc[df["incident_id"] == eid, col] = val
            updated_count += 1
    df_save = df.drop(columns=["tagged"]).copy()
    df_save = df_save.where(pd.notnull(df_save), None)
    records = df_save.to_dict(orient="records")
    # Replace any NaN with None in the dicts
    for rec in records:
        for k, v in rec.items():
            if isinstance(v, float) and pd.isna(v):
                rec[k] = None
    with open(DATA_FILE, "w") as f:
        json.dump(records, f, indent=2)
    # st.session_state["update_message"] = f"Table changes saved! {updated_count} row(s) updated."
    st.rerun()

st.write("---")
st.write("### Bulk Edit Selected Incidents")
selected_ids = st.multiselect(
    "Select Incident(s) to Edit",
    filtered_df["incident_id"],
    format_func=lambda x: f"ID {x} - {df[df['incident_id']==x]['incident_number'].values[0]}"
)

if selected_ids:
    st.popover("Bulk Edit Selected Incidents", use_container_width=True)
    with st.form("bulk_edit_form"):
        st.write("Enter new values for fields you want to update. Leave blank to skip.")
        bulk_edit_values = {}
        for col in edit_cols:
            if col in ["incident_id", "incident_number"]:
                continue  # skip editing these in bulk
            if col == "failure_category":
                bulk_edit_values[col] = st.selectbox(
                    f"{col.replace('_', ' ').title()} (leave blank to skip)",
                    options=["", "Hardware", "Software"]
                )
            elif col in ["record_created_on", "record_updated_on"]:
                date_val = st.date_input(
                    f"{col.replace('_', ' ').title()} - Date (leave blank to skip)",
                    value=None
                )
                time_val = st.time_input(
                    f"{col.replace('_', ' ').title()} - Time (leave blank to skip)",
                    value=datetime.time(0, 0)
                )
                if date_val is not None:
                    bulk_edit_values[col] = datetime.datetime.combine(date_val, time_val)
                else:
                    bulk_edit_values[col] = None
            elif col == "comments":
                bulk_edit_values[col] = st.text_area(f"{col.replace('_', ' ').title()} (leave blank to skip)", value="")
            elif col == "actual_time_spent_in_minutes":
                bulk_edit_values[col] = st.text_input(f"{col.replace('_', ' ').title()} (leave blank to skip)", value="")
            else:
                bulk_edit_values[col] = st.text_input(f"{col.replace('_', ' ').title()} (leave blank to skip)", value="")
        submitted_bulk = st.form_submit_button("Apply Changes to All Selected")
        if submitted_bulk:
            updated_count = 0
            for eid in selected_ids:
                row_updated = False
                for col in edit_cols:
                    if col in ["incident_id", "incident_number"]:
                        continue
                    val = bulk_edit_values[col]
                    # Handle skip logic for dropdown and datetime
                    if col == "failure_category" and val == "":
                        continue
                    if col in ["record_created_on", "record_updated_on"] and val is None:
                        continue
                    if isinstance(val, str) and val.strip() == "":
                        continue
                    if col == "actual_time_spent_in_minutes":
                        try:
                            if val in ["", None]:
                                val = None
                            else:
                                val = float(val)
                        except:
                            val = None
                    # Only update if value is different
                    old_val = df.loc[df["incident_id"] == eid, col].values[0]
                    if pd.isnull(old_val) and val not in [None, ""]:
                        df.loc[df["incident_id"] == eid, col] = val
                        row_updated = True
                    elif val != old_val and val not in [None, ""]:
                        df.loc[df["incident_id"] == eid, col] = val
                        row_updated = True
                if row_updated:
                    updated_count += 1
            df_save = df.drop(columns=["tagged"]).copy()
            for date_col in ["record_created_on", "record_updated_on"]:
                if date_col in df_save.columns:
                    df_save[date_col] = df_save[date_col].apply(
                        lambda x: x.isoformat() if pd.notnull(x) and isinstance(x, (datetime.datetime, pd.Timestamp)) else (x if isinstance(x, str) else "")
                    )
            df_save = df_save.where(pd.notnull(df_save), None)
            df_save = df_save.astype(object)  # Ensure all columns can hold None
            df_save = df_save.where(pd.notnull(df_save), None)

            with open(DATA_FILE, "w") as f:
                json.dump(df_save.to_dict(orient="records"), f, indent=2)
            st.session_state["update_message"] = f"Bulk update successful! {updated_count} row(s) updated."
            st.rerun()

st.write("---")