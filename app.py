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
st.markdown("Upload your file, set parameters, and generate replenishment recommendations.")

# =========================
# CARD 1 — PARAMETERS
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

st.markdown("### ⚙️ Parameters")

col1, col2 = st.columns(2)

with col2:
    divisor = st.number_input(
        "Divisor (months)",
        min_value=1.0,
        value=13.0,
        step=0.5,
        format="%.1f"
    )

    safety_factor = st.number_input(
        "Safety Stock Factor",
        min_value=0.0,
        value=1.0,
        step=0.1
    )

with col1:
    st.markdown("#### ℹ️ About")
    st.write(
        f"""
This tool calculates the recommended stock to order based on sales history.

- **Divisor:** {divisor} months (used to compute average demand)
- **Safety Factor:** {safety_factor} (applied to all items)
- Both values support decimals for flexibility
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
    # VALIDATION
    # -------------------------
    required_columns = [
        "Item No.1",
        "Description",
        "Unit Price",
        "Stock Reserved",
        "Stock Available Quantity",
        "Qty Sold",
        "Qty Sold PYear"
    ]

    missing_cols = [c for c in required_columns if c not in df.columns]

    if missing_cols:
        st.error(f"❌ Missing columns: {missing_cols}")
        st.write("Detected columns:", df.columns.tolist())
        st.stop()

    df = df[required_columns]

    # -------------------------
    # ADD GLOBAL SAFETY FACTOR
    # -------------------------
    df["Safety stock factor"] = safety_factor

    # -------------------------
    # CALCULATIONS
    # -------------------------
    df["Total Qty Sold"] = df["Qty Sold"] + df["Qty Sold PYear"]

    df["Safety stock"] = (
        (df["Total Qty Sold"] / divisor) * df["Safety stock factor"]
    ).round(0)

    df["To order"] = df["Safety stock"] - df["Stock Available Quantity"]

    # -------------------------
    # COLUMN ORDER
    # -------------------------
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
    # CARD 3 — KPI
    # =========================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown("### 📊 Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Items", len(df))
    col2.metric("Avg Safety Stock", int(df["Safety stock"].mean()))
    col3.metric("Items to Order", int((df["To order"] > 0).sum()))

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
