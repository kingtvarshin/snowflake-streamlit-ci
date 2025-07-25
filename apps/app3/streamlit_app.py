import streamlit as st
import pandas as pd
import json
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode

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

st.title("🚨 Incident Management Dashboard")
st.caption("Edit incidents directly in the table. Select multiple rows and apply changes to a column across all selected rows.")

# AG Grid setup
edit_cols = [c for c in df.columns if c not in ["tagged"]]
gb = GridOptionsBuilder.from_dataframe(filtered_df[edit_cols])
gb.configure_selection('multiple', use_checkbox=True)
for col in edit_cols:
    if col == "incident_id" or col == "incident_number":
        gb.configure_column(col, editable=False)
    else:
        gb.configure_column(col, editable=True)
grid_options = gb.build()

response = AgGrid(
    filtered_df[edit_cols],
    gridOptions=grid_options,
    update_mode=GridUpdateMode.MODEL_CHANGED | GridUpdateMode.SELECTION_CHANGED,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=True,
    enable_enterprise_modules=False,
    allow_unsafe_jscode=True,
    height=400,
    reload_data=False
)

# Get selected rows and edited data
selected_rows = response.get("selected_rows")
if not isinstance(selected_rows, list):
    selected_rows = []

edited_df = pd.DataFrame(response["data"])

st.write("Select rows and edit cells directly. To apply a value from one row to all selected rows in a column, use the controls below.")

if selected_rows:
    selected_ids = [row["incident_id"] for row in selected_rows]
    selected_ids = [row["incident_id"] for row in selected_rows]
    st.write(f"Selected Incident IDs: {selected_ids}")

    # Choose column to propagate
    col_to_apply = st.selectbox("Column to propagate", [c for c in edit_cols if c not in ["incident_id", "incident_number"]])
    row_to_copy = st.selectbox("Row to copy from", selected_ids, format_func=lambda x: f"ID {x}")
    if st.button("Apply value from selected row to all selected rows in this column"):
        value = edited_df.loc[edited_df["incident_id"] == row_to_copy, col_to_apply].values[0]
        for eid in selected_ids:
            edited_df.loc[edited_df["incident_id"] == eid, col_to_apply] = value
        st.success(f"Value '{value}' applied to column '{col_to_apply}' for all selected rows.")

    # Save changes
    if st.button("Save All Changes"):
        # Update the main df with edited_df
        for idx, row in edited_df.iterrows():
            df.loc[df["incident_id"] == row["incident_id"], edit_cols] = row[edit_cols].values
        df_save = df.drop(columns=["tagged"])
        with open(DATA_FILE, "w") as f:
            json.dump(df_save.to_dict(orient="records"), f, indent=2)
        st.success("All changes saved to JSON!")
        st.rerun()
else:
    # Save changes for all rows if edited
    if st.button("Save All Changes"):
        for idx, row in edited_df.iterrows():
            df.loc[df["incident_id"] == row["incident_id"], edit_cols] = row[edit_cols].values
        df_save = df.drop(columns=["tagged"])
        with open(DATA_FILE, "w") as f:
            json.dump(df_save.to_dict(orient="records"), f, indent=2)
        st.success("All changes saved to JSON!")
        st.rerun()