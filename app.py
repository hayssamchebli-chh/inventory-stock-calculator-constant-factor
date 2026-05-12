import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Inventory Calculator", layout="wide")

# =========================
# CSS (Card UI)
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
st.title("📦 Inventory Safety Stock Calculator")
st.markdown("Upload your file, set months and factor, and generate replenishment recommendations.")

# =========================
# CARD 1 — PARAMETERS
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown("### ⚙️ Parameters")

col1, col2 = st.columns(2)

with col2:
    months = st.number_input(
        "Months",
        min_value=1.0,
        value=13.0,
        step=0.5,
        format="%.1f"
    )

    factor = st.number_input(
        "FACTOR",
        min_value=0.0,
        value=1.0,
        step=0.1,
        format="%.1f"
    )

with col1:
    st.markdown("#### ℹ️ About")
    st.write(
        f"""
This tool calculates safety stock and recommended order quantity.

- **Months:** {months}
- **FACTOR:** {factor}
- **Safety:** ROUND(Sales 25&26 / Months) × FACTOR
- **Order:** Safety - Forcasted
"""
    )

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# CARD 2 — FILE UPLOAD
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
    # REQUIRED INPUT COLUMNS
    # -------------------------
    required_columns = [
        "Item No.1",
        "Description",
        "Stock Available Quantity",
        "Advanced Reserved",
        "PR Approved Qty",
        "Qty Sold",
        "Qty Sold PYear",
        "PO not Shipped",
        "Cons. Qty",
        "Cons. Qty New"
    ]

    missing_cols = [c for c in required_columns if c not in df.columns]

    if missing_cols:
        st.error(f"❌ Missing columns: {missing_cols}")
        st.write("Detected columns:", df.columns.tolist())
        st.stop()

    # Keep only needed source columns first
    df = df[required_columns].copy()

    # -------------------------
    # NUMERIC CONVERSION
    # -------------------------
    numeric_columns = [
        "Stock Available Quantity",
        "Advanced Reserved",
        "PR Approved Qty",
        "Qty Sold",
        "Qty Sold PYear",
        "PO not Shipped",
        "Cons. Qty",
        "Cons. Qty New"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # -------------------------
    # CALCULATIONS
    # -------------------------
    df["In order"] = df["PO not Shipped"] - df["Advanced Reserved"]

    df["Forcasted"] = df["Stock Available Quantity"] + df["In order"]

    df["Sales 25&26"] = (
        df["Qty Sold"]
        + df["Qty Sold PYear"]
        + df["Cons. Qty"]
        + df["Cons. Qty New"]
    )

    df["Safety"] = ((df["Sales 25&26"] / months).round(0) * factor)

    df["FACTOR"] = factor

    df["order"] = df["Safety"] - df["Forcasted"]

    # -------------------------
    # FINAL COLUMN ORDER
    # -------------------------
    final_columns = [
        "Item No.1",
        "Description",
        "Stock Available Quantity",
        "In order",
        "Advanced Reserved",
        "Forcasted",
        "PR Approved Qty",
        "Qty Sold",
        "Qty Sold PYear",
        "PO not Shipped",
        "Cons. Qty",
        "Cons. Qty New",
        "Sales 25&26",
        "Safety",
        "FACTOR",
        "order"
    ]

    df = df[final_columns]

    # -------------------------
    # REMOVE COLUMNS THAT CONTAIN ONLY 0
    # Keep text/id columns even if blank.
    # -------------------------
    protected_columns = ["Item No.1", "Description"]

    for col in df.columns.tolist():
        if col not in protected_columns:
            numeric_col = pd.to_numeric(df[col], errors="coerce").fillna(0)

            if (numeric_col == 0).all():
                df.drop(columns=[col], inplace=True)

    # =========================
    # CARD 3 — KPI
    # =========================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown("### 📊 Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Items", len(df))

    if "Safety" in df.columns:
        col2.metric("Total Safety", int(df["Safety"].sum()))
    else:
        col2.metric("Total Safety", "Removed")

    if "order" in df.columns:
        col3.metric("Items to Order", int((df["order"] > 0).sum()))
    else:
        col3.metric("Items to Order", "Removed")

    st.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # CARD 4 — RESULTS
    # =========================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown("### 📋 Results")

    st.dataframe(df, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # CARD 5 — EXPORT
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
