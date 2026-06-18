APP_STYLE = """
<style>
/* ── Sleek Dark Theme Elements ─────────────────────────── */

/* Make the Metric components look like actual dashboard cards */
div[data-testid="metric-container"] {
    background-color: #151A22;
    border: 1px solid #1F2633;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

/* Hide the default Streamlit footer */
footer {visibility: hidden !important;}

/* Smooth out the tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: #151A22;
    border-radius: 4px 4px 0px 0px;
    gap: 1px;
    padding-top: 10px;
    padding-bottom: 10px;
}
.stTabs [aria-selected="true"] {
    background-color: #1F2633;
}

/* Style the Selectboxes and Inputs to match the dark theme */
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #151A22;
    border-color: #1F2633;
}
.stTextInput input {
    background-color: #151A22;
    border-color: #1F2633;
    color: #E0E6ED;
}

/* ── Mobile-responsive overrides ─────────────────────────── */

/* Tighter page padding on small screens */
@media (max-width: 768px) {
    [data-testid="block-container"] {
        padding: 1.5rem 0.75rem 2rem !important;
    }
}

/* Smaller title on mobile */
@media (max-width: 480px) {
    h1 { font-size: 1.55rem !important; line-height: 1.2 !important; }
    h2 { font-size: 1.25rem !important; }
    h3 { font-size: 1.05rem !important; }
}

/* Prevent iOS from zooming in when tapping inputs */
input, select, textarea {
    font-size: 16px !important;
}

/* Larger touch targets for radio buttons */
.stRadio label {
    min-height: 44px !important;
    display: flex !important;
    align-items: center !important;
    padding: 4px 6px !important;
}

/* Bigger tap area for selectbox */
[data-testid="stSelectbox"] > div[role="combobox"] {
    min-height: 44px !important;
}

/* Metric values: scale up slightly on small screens */
@media (max-width: 480px) {
    [data-testid="stMetricValue"] { font-size: 1.3rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.7rem !important; }
    [data-testid="stMetricDelta"] { font-size: 0.7rem !important; }
}

/* 4-column Greek rows: wrap to 2x2 on phones */
@media (max-width: 640px) {
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 0.5rem 0 !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        flex: 1 1 45% !important;
        min-width: 45% !important;
    }
}

/* On very small screens stack ALL columns to full width */
@media (max-width: 380px) {
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
}

/* Make dataframes horizontally scrollable instead of squishing */
[data-testid="stDataFrame"] {
    overflow-x: auto !important;
}

/* Sidebar: bigger touch targets for inputs */
[data-testid="stSidebar"] input {
    min-height: 44px !important;
}

/* Plotly toolbar: hide on mobile to reclaim space */
@media (max-width: 640px) {
    .modebar { display: none !important; }
}
</style>
"""
