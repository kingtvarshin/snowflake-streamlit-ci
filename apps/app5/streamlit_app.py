import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Load data from JSON file
DATA_FILE = "data.json"
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = []

# Load supplier list from supplier_list.json
SUPPLIER_FILE = "supplier_list.json"
if os.path.exists(SUPPLIER_FILE):
    with open(SUPPLIER_FILE, "r") as f:
        supplier_list = json.load(f)[0]['supplier']
    if not isinstance(supplier_list, list):
        supplier_list = []
else:
    supplier_list = []

st.set_page_config(page_title="Supplier Interaction Records", layout="wide")
st.title("Supplier Interaction Records")

def add_record_dialog():
    @st.dialog("Add New Record")
    def dialog():
        col1, col2 = st.columns(2)
        with col1:
            collibra_name = st.text_input("Collibra Data set name", key="collibra_name")
            supplier = st.selectbox("Supplier", supplier_list, key="supplier") if supplier_list else st.text_input("Supplier", key="supplier_text")
            datetime_contact = st.date_input("Date of contact - Observed (EST)", value=datetime.now().date(), key="date_contact")
            time_contact = st.time_input("Time of contact - Observed (EST)", value=datetime.now().time(), key="time_contact")
            time_spent = st.number_input("Time spent in supplier Interaction (mins)", min_value=0, step=1, key="time_spent")
            point_of_contact = st.text_input("Point of contact", key="point_of_contact")
        with col2:
            who_involved = st.text_input("Who from company_name was involved?", key="who_involved")
            reason = st.text_input("Reason", key="reason")
            category = st.text_input("Category", key="category")
            supplier_inputs = st.text_input("Supplier Inputs", key="supplier_inputs")
            closing_remarks = st.text_input("Closing Remarks company_name", key="closing_remarks")

        datetime_str = f"{datetime_contact}T{time_contact}"
        fields = [
            collibra_name,
            supplier if supplier_list else st.session_state.get("supplier_text", ""),
            str(datetime_contact),
            str(time_contact),
            point_of_contact,
            who_involved,
            reason,
            category,
            supplier_inputs,
            closing_remarks,
        ]
        if st.button("Add Record", key="add_record_btn"):
            if any(str(f).strip() for f in fields):
                # Ensure time_spent is 0 if empty or NaN
                try:
                    time_spent_val = float(time_spent)
                    if pd.isna(time_spent_val):
                        time_spent_val = 0
                except Exception:
                    time_spent_val = 0

                new_record = {
                    "Collibra Data set name": collibra_name,
                    "Supplier": supplier if supplier_list else st.session_state.get("supplier_text", ""),
                    "Date & time of contact - Observed (EST)": datetime_str,
                    "Time spent in supplier Interaction (mins)": time_spent_val,
                    "Point of contact": point_of_contact,
                    "Who from company_name was involved?": who_involved,
                    "Reason": reason,
                    "Category": category,
                    "Supplier Inputs": supplier_inputs,
                    "Closing Remarks company_name": closing_remarks,
                }
                data.append(new_record)
                with open(DATA_FILE, "w") as f:
                    json.dump(data, f, indent=2)
                st.success("Record added!")
                st.rerun()
            else:
                st.warning("Please fill at least one field before adding a record.")
        if st.button("Cancel", key="cancel_btn"):
            st.rerun()
    dialog()

if st.button("➕ Add New Record"):
    add_record_dialog()

# Convert to DataFrame and show table
df = pd.DataFrame(data)

# --- Sidebar filters ---
st.sidebar.header("Filter Records")
# Supplier filter
supplier_options = sorted(df["Supplier"].dropna().unique()) if not df.empty and "Supplier" in df else []
selected_supplier = st.sidebar.multiselect("Supplier", supplier_options, default=supplier_options)

# Data set name filter
dataset_options = sorted(df["Collibra Data set name"].dropna().unique()) if not df.empty and "Collibra Data set name" in df else []
selected_dataset = st.sidebar.multiselect("Data Set Name", dataset_options, default=dataset_options)

# Date range filter
if not df.empty and "Date & time of contact - Observed (EST)" in df:
    # Parse datetime column
    df["_parsed_date"] = pd.to_datetime(df["Date & time of contact - Observed (EST)"], errors="coerce")
    min_date = df["_parsed_date"].min()
    max_date = df["_parsed_date"].max()
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date.date() if pd.notnull(min_date) else datetime.now().date(),
               max_date.date() if pd.notnull(max_date) else datetime.now().date())
    )
    # Filter by date range
    if isinstance(date_range, tuple) and len(date_range) == 2:
        df = df[(df["_parsed_date"].dt.date >= date_range[0]) & (df["_parsed_date"].dt.date <= date_range[1])]
    df = df.drop(columns=["_parsed_date"], errors="ignore")

# Apply supplier and dataset filters
if selected_supplier:
    df = df[df["Supplier"].isin(selected_supplier)]
if selected_dataset:
    df = df[df["Collibra Data set name"].isin(selected_dataset)]

# Add an "Enable Table Editing" toggle
edit_mode = st.toggle("Enable Table Editing", value=False)

# Prepare editable columns config
column_config = {
    "Date & time of contact - Observed (EST)": st.column_config.DatetimeColumn(
        "Date & time of contact - Observed (EST)",
        format="YYYY-MM-DD HH:mm:ss",
        step=60
    ),
    "Supplier": st.column_config.SelectboxColumn(
        "Supplier",
        options=supplier_list if supplier_list else [],
        required=False
    )
}

# Convert to datetime for editing
if "Date & time of contact - Observed (EST)" in df:
    df["Date & time of contact - Observed (EST)"] = pd.to_datetime(
        df["Date & time of contact - Observed (EST)"], errors="coerce"
    )

if not df.empty:
    if edit_mode:
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            key="edit_table",
            column_config=column_config
        )
        if st.button("Save Changes"):
            if not edited_df.equals(df):
                # Convert datetime to string before saving to JSON
                edited_data = edited_df.copy()
                if "Date & time of contact - Observed (EST)" in edited_data:
                    edited_data["Date & time of contact - Observed (EST)"] = edited_data["Date & time of contact - Observed (EST)"].astype(str)
                if "Time spent in supplier Interaction (mins)" in edited_data:
                    edited_data["Time spent in supplier Interaction (mins)"] = edited_data["Time spent in supplier Interaction (mins)"].apply(
                        lambda x: 0 if pd.isna(x) or x is None else x
                    )
                with open(DATA_FILE, "w") as f:
                    json.dump(edited_data.to_dict(orient="records"), f, indent=2)
                st.success("Changes saved!")
                st.rerun()
    else:
        st.dataframe(df, use_container_width=True)
else:
    st.info("No records to display.")


