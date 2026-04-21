import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# Page Config
# =========================
st.set_page_config(page_title="Inventory Calculator", layout="wide")

st.title("📦 Inventory Safety Stock Calculator")
st.markdown("Upload your files, adjust parameters, and generate replenishment recommendations.")

st.divider()

# =========================
# Parameters Section
# =========================
st.subheader("⚙️ Parameters")

col1, col2 = st.columns([2, 1])

with col2:
    divisor = st.number_input(
        "Divisor (months)",
        min_value=1.0,
        value=13.0,
        step=0.5,
        format="%.1f"
    )

with col1:
    st.info(
        f"""
**How it works:**
- The divisor represents how many months are used to calculate average demand  
- Current value: **{divisor} months**
- You can use decimals (e.g. 16.5)
"""
    )

st.divider()

# =========================
# File Upload Section
# =========================
st.subheader("📂 Upload Files")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Main Inventory File", type=["xlsx"])

with col2:
    sf_file = st.file_uploader("Safety Factor File", type=["xlsx"])

# =========================
# Check Files
# =========================
if uploaded_file and sf_file:

    st.success("✅ Files uploaded successfully")

    # =========================
    # Load Data
    # =========================
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    safety_df = pd.read_excel(sf_file)
    safety_df.columns = safety_df.columns.str.strip()

    # =========================
    # Validate Main File
    # =========================
    required_columns = [
        "Item No.1",
        "Description",
        "Unit Price",
        "Stock Reserved",
        "Stock Available Quantity",
        "Qty Sold",
        "Qty Sold PYear"
    ]

    missing_cols = [col for col in required_columns if col not in df.columns]

    if missing_cols:
        st.error(f"❌ Missing columns in main file: {missing_cols}")
        st.stop()

    df = df[required_columns]

    # =========================
    # Validate Safety File
    # =========================
    required_sf_cols = ["Item No.1", "Safety stock factor"]

    missing_sf = [col for col in required_sf_cols if col not in safety_df.columns]

    if missing_sf:
        st.error(f"❌ Safety factor file missing columns: {missing_sf}")
        st.stop()

    # =========================
    # Merge
    # =========================
    df = df.merge(safety_df, on="Item No.1", how="left")

    missing_count = df["Safety stock factor"].isnull().sum()

    if missing_count > 0:
        st.warning(f"⚠️ {missing_count} items do not have a safety factor")

    # =========================
    # Edit Mode Toggle
    # =========================
    st.divider()

    col1, col2, col3 = st.columns([1,1,3])

    with col1:
        edit_clicked = st.button("✏️ Edit Safety Factors")

    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    if edit_clicked:
        st.session_state.edit_mode = not st.session_state.edit_mode

    # =========================
    # Editing Section
    # =========================
    if st.session_state.edit_mode:
        st.subheader("✏️ Edit Safety Factors")
        st.caption("Only safety factors can be modified")

        edit_df = df[[
            "Item No.1",
            "Description",
            "Safety stock factor"
        ]]

        edited_small_df = st.data_editor(
            edit_df,
            column_config={
                "Item No.1": st.column_config.TextColumn("Item", disabled=True),
                "Description": st.column_config.TextColumn("Description", disabled=True),
                "Safety stock factor": st.column_config.NumberColumn("Safety Factor")
            },
            use_container_width=True,
            height=400
        )

        df = df.drop(columns=["Safety stock factor"]).merge(
            edited_small_df[["Item No.1", "Safety stock factor"]],
            on="Item No.1",
            how="left"
        )

    # =========================
    # Calculations
    # =========================
    df["Total Qty Sold"] = df["Qty Sold"] + df["Qty Sold PYear"]

    df["Safety stock"] = (
        (df["Total Qty Sold"] / divisor) * df["Safety stock factor"]
    ).round(0)

    df["To order"] = df["Safety stock"] - df["Stock Available Quantity"]

    # =========================
    # Reorder Columns
    # =========================
    final_columns = [
        "Item No.1",
        "Description",
        "Unit Price",
        "Stock Reserved",
        "Stock Available Quantity",
        "Qty Sold",
        "Qty Sold PYear",
        "Total Qty Sold",
        "Safety stock factor",
        "Safety stock",
        "To order"
    ]

    df = df[final_columns]

    # =========================
    # KPIs
    # =========================
    st.divider()
    st.subheader("📊 Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Items", len(df))
    col2.metric("Missing Factors", missing_count)
    col3.metric("Avg Safety Stock", int(df["Safety stock"].mean()))

    # =========================
    # Results Table
    # =========================
    st.subheader("📋 Results")

    st.dataframe(df, use_container_width=True)

    # =========================
    # Download
    # =========================
    st.divider()
    st.subheader("⬇️ Export")

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    st.download_button(
        label="📥 Download Processed File",
        data=output,
        file_name="processed_inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.warning("⚠️ Please upload both files to proceed")
