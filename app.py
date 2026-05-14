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
.stApp {
    background: linear-gradient(180deg, #f5f7fb 0%, #eef2f7 100%);
}

[data-testid="stHeader"] {
    background: #f5f7fb;
    height: 0rem;
}

[data-testid="stDecoration"] {
    display: none;
}

.block-container {
    padding-top: 45px;
    padding-bottom: 2rem;
    max-width: 1200px;
}

section[data-testid="stSidebar"] {
    width: 300px !important;
    min-width: 0 !important;
    max-width: 330px !important;
}

section[data-testid="stSidebar"] > div {
    width: 330px !important;
    min-width: 330px !important;
    max-width: 330px !important;
    background: #f1f4f8;
    padding-top: 2rem;
}

.hero {
    background: linear-gradient(135deg, #102a43 0%, #243b53 100%);
    padding: 34px 38px;
    border-radius: 22px;
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

.success-box {
    background: #ecfdf5;
    border-left: 5px solid #10b981;
    padding: 16px 18px;
    border-radius: 14px;
    color: #064e3b;
    font-size: 14px;
}

.warning-box {
    background: #fffbeb;
    border-left: 5px solid #f59e0b;
    padding: 16px 18px;
    border-radius: 14px;
    color: #78350f;
    font-size: 14px;
}

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

.metric-note {
    font-size: 12px;
    color: #829ab1;
    margin-top: 6px;
}

[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
}

.stButton > button {
    border-radius: 12px;
    font-weight: 700;
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

footer {
    visibility: hidden;
}

hr {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HERO
# =========================
st.markdown("""
<div class="hero">
    <h1>📦 Inventory Data into Order Recommendations</h1>
    <p>Upload your inventory file, choose a default safety factor, optionally upload item-level factors, and export a clean replenishment recommendation report.</p>
</div>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR PARAMETERS
# =========================
with st.sidebar:
    st.markdown("## ⚙️ Parameters")
    st.markdown("Set the planning values below.")

    months = st.number_input(
        "Months",
        min_value=1.0,
        value=17.0,
        step=0.5,
        format="%.1f"
    )

    default_factor = st.number_input(
        "Default FACTOR",
        min_value=0.0,
        value=6.0,
        step=0.1,
        format="%.1f"
    )

    st.markdown("---")

    st.markdown("### Factor Rule")
    st.markdown(
        f"""
        By default, the app applies this factor to all items: **Default FACTOR = {default_factor}**
        
        You may optionally upload a Safety Factor File to use different factors per item.
        """
    )

    st.markdown("---")

    st.markdown("### Formula")
    st.markdown(
        """
        **In order**  
        PO not Shipped - Advanced Reserved

        **Forcasted**  
        Stock Available Quantity + In order

        **Sales 25&26**  
        Qty Sold + Qty Sold PYear + Cons. Qty + Cons. Qty New

        **Safety**  
        ROUND(Sales 25&26 / Months) × FACTOR

        **Order**  
        Safety - Forcasted
        """
    )

# =========================
# FILE UPLOAD CARD
# =========================
st.markdown('<div class="card">', unsafe_allow_html=True)

left, right = st.columns([1.4, 1])

with left:
    st.markdown('<div class="section-title">📂 Upload Files</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Upload the main inventory file. The safety factor file is optional.</div>',
        unsafe_allow_html=True
    )

    upload_col1, upload_col2 = st.columns(2)

    with upload_col1:
        uploaded_file = st.file_uploader(
            "Main Inventory File",
            type=["xlsx"]
        )

    with upload_col2:
        sf_file = st.file_uploader(
            "Optional Safety Factor File",
            type=["xlsx"]
        )

with right:
    st.markdown("""
    <div class="info-box">
        <strong>Main file:</strong> Required inventory report<br>
        <strong>Safety file:</strong> Optional item-level factor file<br>
        <strong>Default behavior:</strong> One factor applied to all items<br>
        <strong>Zero-only columns:</strong> Removed automatically
    </div>
    """, unsafe_allow_html=True)

if uploaded_file and sf_file:
    st.success("✅ Main file and safety factor file uploaded. Item-level factors will be used.")
elif uploaded_file:
    st.info("ℹ️ Main file uploaded. The default FACTOR from the sidebar will be applied to all items.")
else:
    st.warning("⚠️ Please upload the main inventory file to generate the inventory report.")

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# MAIN LOGIC
# =========================
if uploaded_file:

    # -------------------------
    # LOAD MAIN DATA
    # -------------------------
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    # -------------------------
    # REQUIRED MAIN FILE COLUMNS
    # -------------------------
    required_columns = [
        "Item No.1",
        "Description",
        "Stock Available Quantity",
        "Advanced Reserved",
        "Qty Sold",
        "Qty Sold PYear",
        "PO not Shipped",
        "Cons. Qty",
        "Cons. Qty New"
    ]

    missing_cols = [c for c in required_columns if c not in df.columns]

    if missing_cols:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.error(f"❌ Missing columns in main file: {missing_cols}")
        st.write("Detected columns:", df.columns.tolist())
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # -------------------------
    # KEEP ONLY NEEDED COLUMNS
    # -------------------------
    df = df[required_columns].copy()

    # -------------------------
    # CLEAN ITEM NUMBER
    # -------------------------
    df["Item No.1"] = df["Item No.1"].astype(str).str.strip()

    # -------------------------
    # DEFAULT FACTOR MODE
    # -------------------------
    df["Safety stock factor"] = default_factor
    missing_factor_count = 0
    factor_source = "Default FACTOR"

    # -------------------------
    # OPTIONAL SAFETY FACTOR FILE
    # -------------------------
    if sf_file:
        safety_df = pd.read_excel(sf_file)
        safety_df.columns = safety_df.columns.str.strip()

        required_sf_cols = [
            "Item No.1",
            "Safety stock factor"
        ]

        missing_sf = [c for c in required_sf_cols if c not in safety_df.columns]

        if missing_sf:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.error(f"❌ Missing columns in safety factor file: {missing_sf}")
            st.write("Detected columns:", safety_df.columns.tolist())
            st.markdown('</div>', unsafe_allow_html=True)
            st.stop()

        safety_df = safety_df[required_sf_cols].copy()

        safety_df["Item No.1"] = safety_df["Item No.1"].astype(str).str.strip()

        safety_df["Safety stock factor"] = pd.to_numeric(
            safety_df["Safety stock factor"],
            errors="coerce"
        )

        safety_df = safety_df.drop_duplicates(
            subset=["Item No.1"],
            keep="first"
        )

        df = df.drop(columns=["Safety stock factor"]).merge(
            safety_df,
            on="Item No.1",
            how="left"
        )

        missing_factor_count = df["Safety stock factor"].isna().sum()

        df["Safety stock factor"] = df["Safety stock factor"].fillna(default_factor)

        factor_source = "Uploaded item-level FACTOR file"

    # -------------------------
    # NUMERIC CONVERSION
    # -------------------------
    numeric_columns = [
        "Stock Available Quantity",
        "Advanced Reserved",
        "Qty Sold",
        "Qty Sold PYear",
        "PO not Shipped",
        "Cons. Qty",
        "Cons. Qty New",
        "Safety stock factor"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # =========================
    # SAFETY FACTOR MANAGEMENT
    # =========================
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown('<div class="section-title">✏️ Safety Factor Management</div>', unsafe_allow_html=True)

    if sf_file:
        st.markdown(
            '<div class="section-subtitle">Item-level safety factors are loaded from the optional safety factor file. Missing factors use the default FACTOR from the sidebar.</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="section-subtitle">The default FACTOR from the sidebar is applied to all items. You can still edit factors before exporting.</div>',
            unsafe_allow_html=True
        )

    status_col1, status_col2 = st.columns(2)

    with status_col1:
        st.markdown(f"""
        <div class="success-box">
            <strong>Factor source:</strong> {factor_source}<br>
            <strong>Default FACTOR:</strong> {default_factor}
        </div>
        """, unsafe_allow_html=True)

    with status_col2:
        if sf_file and missing_factor_count > 0:
            st.markdown(f"""
            <div class="warning-box">
                <strong>Missing item factors:</strong> {missing_factor_count}<br>
                These items were filled with the default FACTOR.
            </div>
            """, unsafe_allow_html=True)
        elif sf_file:
            st.markdown("""
            <div class="success-box">
                <strong>Safety factor file:</strong> Uploaded<br>
                All matched items were processed successfully.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-box">
                <strong>Safety factor file:</strong> Not uploaded<br>
                The default FACTOR is applied to every item.
            </div>
            """, unsafe_allow_html=True)

    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    edit_button_label = "Hide Safety Factor Editor" if st.session_state.edit_mode else "Edit Safety Factors"

    if st.button(edit_button_label):
        st.session_state.edit_mode = not st.session_state.edit_mode

    if st.session_state.edit_mode:
        edit_df = df[
            [
                "Item No.1",
                "Description",
                "Safety stock factor"
            ]
        ].copy()

        edited = st.data_editor(
            edit_df,
            column_config={
                "Item No.1": st.column_config.TextColumn(
                    "Item No.1",
                    disabled=True
                ),
                "Description": st.column_config.TextColumn(
                    "Description",
                    disabled=True
                ),
                "Safety stock factor": st.column_config.NumberColumn(
                    "Safety stock factor",
                    min_value=0.0,
                    step=0.1,
                    format="%.2f"
                )
            },
            use_container_width=True,
            height=350,
            hide_index=True
        )

        df["Safety stock factor"] = pd.to_numeric(
            edited["Safety stock factor"],
            errors="coerce"
        ).fillna(default_factor).values

    st.markdown('</div>', unsafe_allow_html=True)

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

    df["Safety"] = ((df["Sales 25&26"] / months).round(0) * df["Safety stock factor"])

    df["FACTOR"] = df["Safety stock factor"]

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
    # Keep item and description columns.
    # -------------------------
    protected_columns = [
        "Item No.1",
        "Description"
    ]

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
            <div class="metric-note">Rows processed</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Missing Factors</div>
            <div class="metric-value">{missing_factor_count:,}</div>
            <div class="metric-note">Filled with default factor</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Items to Order</div>
            <div class="metric-value">{items_to_order:,}</div>
            <div class="metric-note">Items where order &gt; 0</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Order Qty</div>
            <div class="metric-value">{total_order_qty:,}</div>
            <div class="metric-note">Sum of positive order qty</div>
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
            '<div class="section-subtitle">Download the complete processed file as Excel. Search filtering does not affect the exported file.</div>',
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
