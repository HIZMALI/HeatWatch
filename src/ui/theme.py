"""
Theme and custom CSS for HEATWATCH+ Demo.
Dark navy/blue professional theme matching the reference design.
"""

# Color palette
COLORS = {
    "bg_dark": "#0f1629",
    "bg_card": "#182040",
    "bg_card_hover": "#1e2850",
    "bg_sidebar": "#0d1230",
    "text_primary": "#e8eaf6",
    "text_secondary": "#9fa8da",
    "text_muted": "#7986cb",
    "accent_blue": "#42a5f5",
    "accent_cyan": "#26c6da",
    "accent_orange": "#ffa726",
    "border": "#1e2a5a",
    "risk_low": "#4caf50",
    "risk_med": "#ff9800",
    "risk_high": "#f44336",
    "risk_emergency": "#d50000",
    "watch": "#ff9800",
    "warning": "#ff5722",
    "emergency": "#d50000",
    "gradient_green": "#43a047",
    "gradient_yellow": "#fdd835",
    "gradient_orange": "#fb8c00",
    "gradient_red": "#e53935",
}

# Alert level colors
ALERT_COLORS = {
    "NORMAL": {"bg": "#4caf5015", "border": "#4caf50", "text": "#66bb6a"},
    "WATCH": {"bg": "#ff980015", "border": "#ff9800", "text": "#ffa726"},
    "WARNING": {"bg": "#ff572215", "border": "#ff5722", "text": "#ff7043"},
    "EMERGENCY": {"bg": "#d5000015", "border": "#d50000", "text": "#ef5350"},
}

# Risk level colors
LEVEL_COLORS = {
    "High": "#f44336",
    "Med": "#ff9800",
    "Low": "#4caf50",
}


def get_custom_css() -> str:
    """Return custom CSS for the entire Streamlit app."""
    return f"""
    <style>
        /* ===== GLOBAL ===== */
        .stApp {{
            background-color: {COLORS['bg_dark']};
            color: {COLORS['text_primary']};
        }}

        /* ===== SIDEBAR ===== */
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {COLORS['bg_sidebar']} 0%, #080c20 100%);
            border-right: 1px solid {COLORS['border']};
        }}
        section[data-testid="stSidebar"] .stMarkdown {{
            color: {COLORS['text_primary']};
        }}

        /* Sidebar toggle button — keep visible and styled */
        button[data-testid="stSidebarCollapseButton"],
        button[data-testid="stSidebarNavCollapseButton"],
        button[kind="header"] {{
            color: {COLORS['text_secondary']} !important;
            background: transparent !important;
        }}

        /* ===== HEADERS ===== */
        h1, h2, h3, h4 {{
            color: {COLORS['text_primary']} !important;
        }}

        /* ===== RADIO BUTTONS (Navigation) ===== */
        div[data-testid="stRadio"] > div[role="radiogroup"] {{
            gap: 6px !important;
        }}
        div[data-testid="stRadio"] > div[role="radiogroup"] > label {{
            background: transparent !important;
            padding: 12px 16px !important;
            border-radius: 8px !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
            border-left: 3px solid transparent !important;
        }}
        /* Hide the default radio circle */
        div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {{
            display: none !important;
        }}
        /* Structure the inner text div to align icons and text properly */
        div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:last-child {{
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
        }}
        /* Style the actual text */
        div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:last-child > div > p {{
            font-size: 16px !important;
            font-weight: 600 !important;
            color: #ffffff !important; /* Pure white for maximum readability */
            display: flex !important;
            align-items: center !important;
            margin: 0 !important;
            white-space: pre-wrap !important;
        }}
        div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {{
            background: {COLORS['bg_card_hover']} !important;
        }}
        /* Selected State */
        div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {{
            background: {COLORS['accent_blue']}25 !important;
            border-left: 3px solid {COLORS['accent_blue']} !important;
        }}
        div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) > div:last-child > div > p {{
            color: {COLORS['accent_cyan']} !important;
            font-weight: 700 !important;
        }}

        /* ===== BUTTONS ===== */
        .stButton > button {{
            background: linear-gradient(135deg, {COLORS['accent_blue']}30, {COLORS['accent_blue']}15) !important;
            color: {COLORS['text_primary']} !important;
            border: 1px solid {COLORS['accent_blue']}50 !important;
            border-radius: 8px !important;
            padding: 8px 20px !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            transition: all 0.2s ease !important;
        }}
        .stButton > button:hover {{
            background: linear-gradient(135deg, {COLORS['accent_blue']}50, {COLORS['accent_blue']}30) !important;
            border-color: {COLORS['accent_blue']} !important;
            box-shadow: 0 4px 12px {COLORS['accent_blue']}30 !important;
            transform: translateY(-1px) !important;
        }}
        .stButton > button:active {{
            transform: translateY(0) !important;
        }}

        /* ===== SELECT / INPUT WIDGETS ===== */
        div[data-baseweb="select"] {{
            background-color: {COLORS['bg_card']} !important;
            border-radius: 8px !important;
        }}
        div[data-baseweb="select"] > div {{
            background-color: {COLORS['bg_card']} !important;
            border: 1px solid {COLORS['border']} !important;
            border-radius: 8px !important;
            color: #ffffff !important;
            font-size: 14px !important;
        }}
        /* Dropdown popover container (aggressive to fix white background) */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] > div,
        div[data-baseweb="popover"] ul,
        ul[role="listbox"],
        div[role="listbox"],
        ul[data-testid="stSelectboxVirtualDropdown"] {{
            background-color: {COLORS['bg_card']} !important;
            border-color: {COLORS['border']} !important;
        }}
        /* Dropdown items (options) */
        ul[role="listbox"] li,
        ul[data-testid="stSelectboxVirtualDropdown"] li,
        div[role="option"] {{
            color: #ffffff !important;
            font-size: 14px !important;
            padding: 10px 16px !important;
            background-color: {COLORS['bg_card']} !important; 
        }}
        ul[role="listbox"] li:hover,
        ul[data-testid="stSelectboxVirtualDropdown"] li:hover,
        div[role="option"]:hover {{
            background-color: {COLORS['accent_blue']}40 !important;
            color: #ffffff !important;
        }}

        /* Multi-select tags */
        span[data-baseweb="tag"] {{
            background: {COLORS['accent_blue']}25 !important;
            color: {COLORS['accent_blue']} !important;
            border: 1px solid {COLORS['accent_blue']}40 !important;
            border-radius: 6px !important;
        }}

        /* Date input */
        input[type="text"],
        input[type="number"],
        div[data-baseweb="input"] > div {{
            background-color: {COLORS['bg_card']} !important;
            color: {COLORS['text_primary']} !important;
            border: 1px solid {COLORS['border']} !important;
            border-radius: 6px !important;
        }}

        /* ===== DATE PICKER CALENDAR - FULL DARK OVERRIDE ===== */
        div[data-baseweb="calendar"],
        div[data-baseweb="datepicker"],
        div[data-baseweb="calendar"] > div,
        [data-baseweb="calendar"] * {{
            background-color: {COLORS['bg_card']} !important;
            color: #ffffff !important;
        }}
        /* Day cells */
        div[data-baseweb="calendar"] button {{
            background-color: {COLORS['bg_card']} !important;
            color: #ffffff !important;
            border: none !important;
        }}
        div[data-baseweb="calendar"] button:hover {{
            background-color: {COLORS['accent_blue']}60 !important;
            color: #ffffff !important;
        }}
        /* Selected day */
        div[data-baseweb="calendar"] [aria-selected="true"],
        div[data-baseweb="calendar"] [aria-selected="true"] * {{
            background-color: {COLORS['accent_blue']} !important;
            color: #ffffff !important;
        }}
        /* Month/year header text */
        div[data-baseweb="calendar"] [data-baseweb="typo-label-medium"],
        div[data-baseweb="calendar"] [data-baseweb="typo-paragraph-medium"],
        div[data-baseweb="calendar"] span {{
            color: #ffffff !important;
        }}
        /* Day-of-week labels (Mon, Tue, etc.) */
        div[data-baseweb="calendar"] [role="columnheader"] {{
            color: {COLORS['text_muted']} !important;
        }}
        /* Popover wrapper */
        div[data-baseweb="popover"] > div {{
            background-color: {COLORS['bg_card']} !important;
            border: 1px solid {COLORS['border']} !important;
            border-radius: 10px !important;
        }}


        /* ===== TABS ===== */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0px;
            background-color: {COLORS['bg_card']};
            border-radius: 8px;
            padding: 4px;
            border: 1px solid {COLORS['border']};
        }}
        .stTabs [data-baseweb="tab"] {{
            color: {COLORS['text_secondary']};
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {COLORS['accent_blue']}25 !important;
            color: {COLORS['accent_blue']} !important;
            font-weight: 600;
        }}

        /* ===== EXPANDER (SMS/Briefing) ===== */
        .streamlit-expanderHeader {{
            background-color: {COLORS['bg_card']} !important;
            border-radius: 8px !important;
            color: {COLORS['text_primary']} !important;
        }}
        details[data-testid="stExpander"] {{
            background-color: {COLORS['bg_card']} !important;
            border: 1px solid {COLORS['border']} !important;
            border-radius: 10px !important;
        }}
        details[data-testid="stExpander"] summary {{
            color: {COLORS['text_primary']} !important;
        }}
        details[data-testid="stExpander"] > div {{
            background-color: {COLORS['bg_card']} !important;
        }}

        /* ===== CODE BLOCKS (SMS templates etc.) ===== */
        pre, code {{
            background-color: {COLORS['bg_dark']} !important;
            color: {COLORS['text_primary']} !important;
            border: 1px solid {COLORS['border']} !important;
            border-radius: 8px !important;
        }}
        .stCodeBlock {{
            background-color: {COLORS['bg_dark']} !important;
        }}
        .stCodeBlock pre {{
            background-color: {COLORS['bg_dark']} !important;
            color: {COLORS['text_primary']} !important;
            font-family: 'Consolas', 'Monaco', monospace !important;
            font-size: 13px !important;
            line-height: 1.6 !important;
        }}
        /* Override Streamlit's code block inner container */
        [data-testid="stCodeBlock"] {{
            background-color: {COLORS['bg_dark']} !important;
        }}
        [data-testid="stCodeBlock"] > div {{
            background-color: {COLORS['bg_dark']} !important;
        }}
        [data-testid="stCodeBlock"] pre {{
            background-color: {COLORS['bg_dark']} !important;
            color: {COLORS['text_primary']} !important;
        }}
        [data-testid="stCodeBlock"] code {{
            background-color: {COLORS['bg_dark']} !important;
            color: {COLORS['text_primary']} !important;
        }}

        /* ===== DATAFRAME ===== */
        .stDataFrame {{
            border: 1px solid {COLORS['border']} !important;
            border-radius: 8px !important;
        }}

        /* ===== METRIC CARDS ===== */
        [data-testid="stMetric"] {{
            background-color: {COLORS['bg_card']};
            border: 1px solid {COLORS['border']};
            border-radius: 10px;
            padding: 16px;
        }}

        /* ===== SLIDER ===== */
        .stSlider > div > div > div {{
            color: {COLORS['text_primary']} !important;
        }}

        /* ===== INFO/WARNING/ERROR BOXES ===== */
        .stAlert {{
            background-color: {COLORS['bg_card']} !important;
            border-radius: 8px !important;
            color: {COLORS['text_primary']} !important;
        }}

        /* ===== DIVIDERS ===== */
        hr {{
            border-color: {COLORS['border']} !important;
        }}

        /* ===== LABELS ===== */
        .stSelectbox label, .stMultiSelect label, .stSlider label, .stNumberInput label, .stDateInput label {{
            color: {COLORS['text_muted']} !important;
            font-size: 12px !important;
            font-weight: 600 !important;
        }}

        /* ===== HIDE DEFAULT ELEMENTS ===== */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}

        /* ===== FOLIUM MAP CONTAINER ===== */
        iframe {{
            border-radius: 12px !important;
            border: 1px solid {COLORS['border']} !important;
        }}

        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: {COLORS['bg_dark']};
        }}
        ::-webkit-scrollbar-thumb {{
            background: {COLORS['border']};
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: {COLORS['accent_blue']}60;
        }}
    </style>
    """


def get_plotly_layout(title: str = "") -> dict:
    """Get consistent Plotly layout for dark theme."""
    return {
        "template": "plotly_dark",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "title": {
            "text": title,
            "font": {"color": COLORS["text_primary"], "size": 14},
        },
        "font": {"color": COLORS["text_primary"], "family": "Inter, sans-serif"},
        "xaxis": {
            "gridcolor": COLORS["border"],
            "linecolor": COLORS["border"],
        },
        "yaxis": {
            "gridcolor": COLORS["border"],
            "linecolor": COLORS["border"],
        },
        "margin": {"l": 40, "r": 20, "t": 50, "b": 40},
        "hovermode": "x unified",
        "hoverlabel": {
            "bgcolor": COLORS["bg_card"],
            "font": {"color": "#ffffff", "size": 13, "family": "Inter, sans-serif"}
        },
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
    }
