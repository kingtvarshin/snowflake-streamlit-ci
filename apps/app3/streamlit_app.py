import streamlit as st
import pandas as pd
import json
import datetime

st.set_page_config(page_title="Incident Management", layout="wide")

DATA_FILE = "data.json"
with open(DATA_FILE, "r") as f:
    data = json.load(f)
df = pd.DataFrame(data)

def is_tagged(row):
    cols = [c for c in df.columns if c not in ["incident_id", "incident_number"]]
    return any(str(row[c]).strip() not in ["", "None", "nan", "NaN"] for c in cols)

df["tagged"] = df.apply(is_tagged, axis=1)

# Sidebar filters
st.sidebar.header("Filters")
filter_type = st.sidebar.radio("Show", ["All", "Tagged", "Untagged"])
custodian_teams = df["custodian_team"].dropna().unique().tolist()
selected_teams = st.sidebar.multiselect("Custodian Team", custodian_teams, default=custodian_teams)
filter_col = st.sidebar.selectbox("Filter by column", df.columns)
filter_val = st.sidebar.text_input("Value contains")

filtered_df = df.copy()
if filter_type == "Tagged":
    filtered_df = filtered_df[filtered_df["tagged"]]
elif filter_type == "Untagged":
    filtered_df = filtered_df[~filtered_df["tagged"]]
if selected_teams:
    filtered_df = filtered_df[filtered_df["custodian_team"].isin(selected_teams)]
if filter_val:
    filtered_df = filtered_df[filtered_df[filter_col].astype(str).str.contains(filter_val, case=False, na=False)]

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
    for idx, row in edited_df.iterrows():
        df.loc[df["incident_id"] == row["incident_id"], edit_cols] = row[edit_cols].values
    df_save = df.drop(columns=["tagged"]).copy()
    for date_col in ["record_created_on", "record_updated_on"]:
        if date_col in df_save.columns:
            df_save[date_col] = df_save[date_col].apply(
                lambda x: x.isoformat() if pd.notnull(x) else ""
            )

    with open(DATA_FILE, "w") as f:
        json.dump(df_save.to_dict(orient="records"), f, indent=2)
    st.success("Table changes saved!")
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
            if col == "incident_number":
                continue  # skip editing incident_number in bulk
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
            for eid in selected_ids:
                for col in edit_cols:
                    if col == "incident_number":
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
                            val = float(val)
                        except:
                            val = None
                    df.loc[df["incident_id"] == eid, col] = val
            df_save = df.drop(columns=["tagged"]).copy()
            for date_col in ["record_created_on", "record_updated_on"]:
                if date_col in df_save.columns:
                    df_save[date_col] = df_save[date_col].apply(
                        lambda x: x.isoformat() if pd.notnull(x) and isinstance(x, (datetime.datetime, pd.Timestamp)) else ""
                    )

            with open(DATA_FILE, "w") as f:
                json.dump(df_save.to_dict(orient="records"), f, indent=2)
            st.success("Bulk update successful!")
            st.rerun()

st.write("---")