import streamlit as st
import pandas as pd
from io import BytesIO

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Inventory Calculator",
    page_icon="📦",
    layout="wide"
)

# =========================
# PROFESSIONAL CSS
# =========================
st.markdown("""
<style>
/* =========================
   REMOVE WHITE TOP BAR LOOK
   ========================= */

/* Main app background */
.stApp {
    background: linear-gradient(180deg, #f5f7fb 0%, #eef2f7 100%);
}

/* Streamlit header / toolbar */
[data-testid="stHeader"] {
    background: #f5f7fb;
    height: 0rem;
}

/* Optional: hide the top decoration line */
[data-testid="stDecoration"] {
    display: none;
}

/* Remove extra top padding */
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

/* =========================
   SIDEBAR WIDTH
   ========================= */

/* Sidebar container width */
section[data-testid="stSidebar"] {
    width: 400px !important;
    min-width: 400px !important;
    max-width: 400px !important;
}

/* Sidebar inner content */
section[data-testid="stSidebar"] > div {
    width: 400px !important;
    min-width: 400px !important;
    max-width: 400px !important;
    background: #f1f4f8;
    padding-top: 2rem;
}

/* Main page shifts according to sidebar width */
section[data-testid="stSidebar"] ~ div {
    margin-left: 0;
}

/* Sidebar text */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #1f2937;
    font-weight: 800;
}

/* =========================
   HERO SECTION
   ========================= */

.hero {
    background: linear-gradient(135deg, #102a43 0%, #243b53 100%);
    padding: 34px 38px;
    border-radius: 0 0 22px 22px;
    color: white;
    margin-bottom: 26px;
    box-shadow: 0 12px 30px rgba(16, 42, 67, 0.22);
}

.hero h1 {
    margin: 0;
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -0.5px;
}

.hero p {
    margin-top: 10px;
    font-size: 16px;
    color: #d9e2ec;
}

/* =========================
   CARDS
   ========================= */

.card {
    background: #ffffff;
    padding: 24px;
    border-radius: 18px;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
    border: 1px solid rgba(226, 232, 240, 0.9);
    margin-bottom: 22px;
}

.section-title {
    font-size: 20px;
    font-weight: 750;
    color: #102a43;
    margin-bottom: 6px;
}

.section-subtitle {
    font-size: 14px;
    color: #627d98;
    margin-bottom: 18px;
}

.info-box {
    background: #f0f7ff;
    border-left: 5px solid #2f80ed;
    padding: 16px 18px;
    border-radius: 14px;
    color: #243b53;
    font-size: 14px;
}

/* =========================
   METRIC CARDS
   ========================= */

.metric-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
}

.metric-label {
    font-size: 13px;
    color: #627d98;
    font-weight: 600;
    margin-bottom: 8px;
}

.metric-value {
    font-size: 28px;
    color: #102a43;
    font-weight: 800;
}

/* =========================
   TABLE + BUTTONS
   ========================= */

[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
}

.stDownloadButton > button {
    background: linear-gradient(135deg, #1f7aec 0%, #155bd5 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.65rem 1rem;
    font-weight: 700;
    box-shadow: 0 8px 16px rgba(31, 122, 236, 0.22);
}

.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #155bd5 0%, #0f4bb8 100%);
    color: white;
}

/* Hide Streamlit footer */
footer {
    visibility: hidden;
}

hr {
    display: none;
}
</style>
""", unsafe_allow_html=True)
# =========================
# HEADER / HERO
# =========================
st.markdown("""
<div class="hero">
    <h1>📦 Inventory Safety Stock Calculator</h1>
    <p>Upload your inventory file, adjust planning parameters, review calculated stock recommendations, and export a clean Excel report.</p>
</div>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR PARAMETERS
# =========================
with st.sidebar:
    st.markdown("## ⚙️ Parameters")
    st.markdown("Adjust the values below before or after uploading your file.")

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

    st.markdown("---")

    st.markdown("### Formula")
    st.markdown(
        """
        **Sales 25&26**  
        Qty Sold + Qty Sold PYear + Cons. Qty + Cons. Qty New

        **Safety**  
        ROUND(Sales 25&26 / Months) × FACTOR

        **Order**  
        Safety - Forcasted
        """
    )

# =========================
# UPLOAD CARD
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

left, right = st.columns([1, 1])

with left:
    st.markdown('<div class="section-title">📂 Upload Inventory File</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Upload the Excel file generated from your inventory report.</div>',
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Main Inventory File",
        type=["xlsx"],
        label_visibility="collapsed"
    )

with right:
    st.markdown("""
    <div class="info-box">
        <strong>Expected file type:</strong> Excel .xlsx<br>
        <strong>Output:</strong> Cleaned inventory recommendation file<br>
        <strong>Zero-only columns:</strong> Removed automatically
    </div>
    """, unsafe_allow_html=True)

if uploaded_file:
    st.success("✅ File uploaded successfully. Results are ready below.")
else:
    st.warning("⚠️ Upload an Excel file to generate the inventory report.")

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
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.error(f"❌ Missing columns: {missing_cols}")
        st.write("Detected columns:", df.columns.tolist())
        st.markdown('</div>', unsafe_allow_html=True)
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
    # SUMMARY SECTION
    # =========================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown('<div class="section-title">📊 Report Summary</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">A quick overview of the processed inventory file.</div>',
        unsafe_allow_html=True
    )

    total_items = len(df)
    total_safety = int(df["Safety"].sum()) if "Safety" in df.columns else 0
    items_to_order = int((df["order"] > 0).sum()) if "order" in df.columns else 0
    total_order_qty = int(df.loc[df["order"] > 0, "order"].sum()) if "order" in df.columns else 0

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Items</div>
            <div class="metric-value">{total_items:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Safety</div>
            <div class="metric-value">{total_safety:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Items to Order</div>
            <div class="metric-value">{items_to_order:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Order Qty</div>
            <div class="metric-value">{total_order_qty:,}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # RESULTS SECTION
    # =========================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    top_left, top_right = st.columns([2, 1])

    with top_left:
        st.markdown('<div class="section-title">📋 Processed Results</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Review the calculated inventory recommendations before exporting.</div>',
            unsafe_allow_html=True
        )

    with top_right:
        search_text = st.text_input(
            "Search item or description",
            placeholder="Type to filter...",
            label_visibility="collapsed"
        )

    display_df = df.copy()

    if search_text:
        search_text = search_text.lower()

        display_df = display_df[
            display_df["Item No.1"].astype(str).str.lower().str.contains(search_text, na=False)
            | display_df["Description"].astype(str).str.lower().str.contains(search_text, na=False)
        ]

    st.dataframe(
        display_df,
        use_container_width=True,
        height=520
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # EXPORT SECTION
    # =========================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    export_left, export_right = st.columns([2, 1])

    with export_left:
        st.markdown('<div class="section-title">⬇️ Export Report</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Download the complete processed file as Excel.</div>',
            unsafe_allow_html=True
        )

    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    with export_right:
        st.download_button(
            label="📥 Download Excel Report",
            data=output,
            file_name="processed_inventory.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.markdown('</div>', unsafe_allow_html=True)
