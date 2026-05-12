import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Inventory Calculator", layout="wide")

# =========================
# CSS
# =========================
st.markdown("""
<style>
.stApp {
    background-color: #f7f9fc;
}
.card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
hr {display:none;}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.title("📦 Inventory File Processor")
st.markdown("Upload your Excel file, keep the required columns, remove zero-only columns, and calculate inventory metrics.")

# =========================
# FILE UPLOAD
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown("### 📂 Upload File")

uploaded_file = st.file_uploader("Main Inventory File", type=["xlsx"])

if uploaded_file:
    st.success("✅ File uploaded successfully")
else:
    st.warning("⚠️ Please upload a file to proceed")

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# MAIN LOGIC
# =========================
if uploaded_file:

    # -------------------------
    # LOAD DATA
    # -------------------------
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    # -------------------------
    # COLUMNS TO KEEP
    # -------------------------
    keep_columns = [
        "Item No.1",
        "Description",
        "Stock Available Quantity",
        "Stock Reserved",
        "Advanced Reserved",
        "PR Approved Qty",
        "Qty Sold",
        "Qty Sold PYear",
        "Blanket PO Qty",
        "PO Qty",
        "PO not Shipped",
        "Qty to Recieve",
        "Cons. Qty",
        "Cons. Qty New"
    ]

    # -------------------------
    # VALIDATION
    # -------------------------
    missing_cols = [col for col in keep_columns if col not in df.columns]

    if missing_cols:
        st.error(f"❌ Missing columns: {missing_cols}")
        st.write("Detected columns:", df.columns.tolist())
        st.stop()

    df = df[keep_columns].copy()

    # -------------------------
    # CONVERT NUMERIC COLUMNS
    # -------------------------
    numeric_columns = [
        "Stock Available Quantity",
        "Stock Reserved",
        "Advanced Reserved",
        "PR Approved Qty",
        "Qty Sold",
        "Qty Sold PYear",
        "Blanket PO Qty",
        "PO Qty",
        "PO not Shipped",
        "Qty to Recieve",
        "Cons. Qty",
        "Cons. Qty New"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # -------------------------
    # CALCULATIONS
    # -------------------------
    df["In order"] = df["PO not Shipped"] - df["Advanced Reserved"]

    df["Forecasted"] = df["Stock Available Quantity"] + df["In order"]

    df["Sales25&26"] = (
        df["Qty Sold"]
        + df["Qty Sold PYear"]
        + df["Cons. Qty"]
        + df["Cons. Qty New"]
    )

    # -------------------------
    # REMOVE COLUMNS THAT CONTAIN ONLY 0
    # Do not remove item/description columns.
    # -------------------------
    protected_columns = ["Item No.1", "Description"]

    for col in df.columns.tolist():
        if col not in protected_columns:
            numeric_col = pd.to_numeric(df[col], errors="coerce").fillna(0)
            if (numeric_col == 0).all():
                df.drop(columns=[col], inplace=True)

    # =========================
    # SUMMARY CARD
    # =========================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown("### 📊 Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Items", len(df))

    if "Forecasted" in df.columns:
        col2.metric("Total Forecasted", int(df["Forecasted"].sum()))
    else:
        col2.metric("Total Forecasted", "Removed")

    if "Sales25&26" in df.columns:
        col3.metric("Total Sales25&26", int(df["Sales25&26"].sum()))
    else:
        col3.metric("Total Sales25&26", "Removed")

    st.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # RESULTS CARD
    # =========================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown("### 📋 Results")

    st.dataframe(df, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # EXPORT CARD
    # =========================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown("### ⬇️ Export")

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    st.download_button(
        label="📥 Download Processed File",
        data=output,
        file_name="processed_inventory.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown('</div>', unsafe_allow_html=True)
