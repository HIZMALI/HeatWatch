"""
HEATWATCH+ Demo — Main Application Entry Point
Heat-Respiratory Risk Intelligence Platform for Ankara, Turkey
"""

import sys
import os
import streamlit as st
import yaml
from datetime import datetime, timedelta

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data.loaders import load_vulnerability, load_geojson
from src.data.real_data_fetcher import fetch_and_prepare
from src.models.risk_engine import compute_all_kpis
from src.ui.theme import get_custom_css, COLORS
from src.ui.pages import (
    render_overview,
    render_heat_air,
    render_respiratory_signals,
    render_icu_capacity,
    render_actions_playbooks,
    render_data_ethics,
    render_settings,
)


def load_config():
    """Load app configuration."""
    config_path = os.path.join(PROJECT_ROOT, "config", "app_config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    # Page config
    st.set_page_config(
        page_title="HEATWATCH+ Demo",
        page_icon="🌡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject custom CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)

    # --- Sidebar ---
    with st.sidebar:
        # Logo & title
        st.markdown(
            f'<div style="text-align:center;padding:20px 0 8px 0;">'
            f'<div style="font-size:28px;margin-bottom:4px;">🌡️</div>'
            f'<h2 style="color:{COLORS["accent_cyan"]};margin:0;font-size:20px;font-weight:700;">HEATWATCH+</h2>'
            f'<p style="color:{COLORS["text_muted"]};font-size:11px;margin:4px 0 0 0;">'
            f'Heat-Respiratory Risk Intelligence</p></div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Navigation menu
        page = st.radio(
            "Navigation",
            [
                "🏠  Overview",
                "🌡️  Heat & Air",
                "🫁  Respiratory Signals",
                "🏥  ICU / Capacity",
                "📋  Actions & Playbooks",
                "🔒  Data & Ethics",
                "⚙️  Settings",
            ],
            key="nav_page",
            label_visibility="collapsed",
        )

        st.markdown("---")

        # --- Date Range Picker ---
        st.markdown(
            f'<p style="color:{COLORS["text_muted"]};font-size:11px;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">📅 Tarih Aralığı</p>',
            unsafe_allow_html=True,
        )

        # Initialize defaults FIRST (before buttons and inputs)
        _today = datetime.now().date()
        if "date_input_start" not in st.session_state:
            st.session_state["date_input_start"] = _today - timedelta(days=7)
        if "date_input_end" not in st.session_state:
            st.session_state["date_input_end"] = _today - timedelta(days=1)

        # Quick presets — set the DATE INPUT widget keys directly
        preset_cols = st.columns(3)
        with preset_cols[0]:
            if st.button("Son 7 Gün", key="preset_7d", use_container_width=True):
                st.session_state["date_input_end"] = _today - timedelta(days=1)
                st.session_state["date_input_start"] = st.session_state["date_input_end"] - timedelta(days=6)
                st.rerun()
        with preset_cols[1]:
            if st.button("Son 14 Gün", key="preset_14d", use_container_width=True):
                st.session_state["date_input_end"] = _today - timedelta(days=1)
                st.session_state["date_input_start"] = st.session_state["date_input_end"] - timedelta(days=13)
                st.rerun()
        with preset_cols[2]:
            if st.button("Son 30 Gün", key="preset_30d", use_container_width=True):
                st.session_state["date_input_end"] = _today - timedelta(days=1)
                st.session_state["date_input_start"] = st.session_state["date_input_end"] - timedelta(days=29)
                st.rerun()

        date_start = st.date_input(
            "Başlangıç",
            key="date_input_start",
        )
        date_end = st.date_input(
            "Bitiş",
            key="date_input_end",
        )

        st.markdown("---")

        # Sidebar filters
        st.markdown(
            f'<p style="color:{COLORS["text_muted"]};font-size:11px;font-weight:700;'
            f'text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Filters</p>',
            unsafe_allow_html=True,
        )

        scenario = st.selectbox(
            "Scenario",
            ["Heatwave + PM2.5 Spike (Default)", "Moderate Heat", "Baseline"],
            key="sidebar_scenario",
        )

        district_filter = st.multiselect(
            "Focus Districts",
            [
                "Altındağ", "Çankaya", "Keçiören", "Yenimahalle", "Mamak",
                "Etimesgut", "Sincan", "Gölbaşı", "Pursaklar", "Polatlı",
            ],
            default=["Altındağ", "Keçiören", "Mamak"],
            key="sidebar_districts",
        )

        st.markdown("---")

        # Footer
        st.markdown(
            f'<div style="text-align:center;padding:12px 0;">'
            f'<p style="color:{COLORS["accent_cyan"]};font-size:11px;font-weight:600;margin:0 0 4px 0;">'
            f'HEATWATCH+ 2026 for MIT Solve Submission</p>'
            f'<p style="color:{COLORS["text_muted"]};font-size:11px;margin:0;">'
            f'1-2-3 Tıp Team</p></div>',
            unsafe_allow_html=True,
        )

    # --- Fetch Real Data ---
    start_dt = datetime.combine(date_start, datetime.min.time())
    end_dt = datetime.combine(date_end, datetime.min.time())

    # Validate date range
    if start_dt >= end_dt:
        end_dt = start_dt + timedelta(days=7)

    df_env, df_micro = fetch_real_data_cached(start_dt, end_dt)

    # Load static data
    df_vuln = load_vuln_data()
    geojson = load_geo_data()

    # Compute KPIs live from real data
    kpis = compute_all_kpis(df_env, df_micro, df_vuln)

    # Override last_update with current time
    kpis["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- Apply District Filter ---
    if district_filter:
        df_vuln_filtered = df_vuln[df_vuln["district_name"].isin(district_filter)].copy()
        import copy
        geojson_filtered = copy.deepcopy(geojson)
        geojson_filtered["features"] = [
            f for f in geojson_filtered["features"]
            if f["properties"]["district_name"] in district_filter
        ]
    else:
        df_vuln_filtered = df_vuln.copy()
        geojson_filtered = geojson

    # --- Apply Scenario Scaling ---
    df_env_scaled = df_env.copy()
    df_micro_scaled = df_micro.copy()
    if scenario == "Moderate Heat":
        df_env_scaled["temp_c"] = (df_env["temp_c"] * 0.85).round(1)
        df_env_scaled["nighttime_temp_c"] = (df_env["nighttime_temp_c"] * 0.85).round(1)
        df_env_scaled["pm25_ugm3"] = (df_env["pm25_ugm3"] * 0.7).round(1)
        df_micro_scaled["symptom_search_index"] = (df_micro["symptom_search_index"] * 0.7).round(1)
        df_micro_scaled["pharmacy_visits_index"] = (df_micro["pharmacy_visits_index"] * 0.7).round(1)
        df_micro_scaled["clinic_cases_index"] = (df_micro["clinic_cases_index"] * 0.65).round(1)
    elif scenario == "Baseline":
        df_env_scaled["temp_c"] = (df_env["temp_c"] * 0.7).round(1)
        df_env_scaled["nighttime_temp_c"] = (df_env["nighttime_temp_c"] * 0.7).round(1)
        df_env_scaled["pm25_ugm3"] = (df_env["pm25_ugm3"] * 0.5).round(1)
        df_env_scaled["humidity_pct"] = (df_env["humidity_pct"] * 1.4).clip(0, 100).round(1)
        df_micro_scaled["symptom_search_index"] = (df_micro["symptom_search_index"] * 0.4).round(1)
        df_micro_scaled["pharmacy_visits_index"] = (df_micro["pharmacy_visits_index"] * 0.4).round(1)
        df_micro_scaled["clinic_cases_index"] = (df_micro["clinic_cases_index"] * 0.35).round(1)

    # Store vulnerability data for actions panel
    st.session_state["vuln_df"] = df_vuln_filtered

    # Parse page name
    page_name = page.split("  ", 1)[1] if "  " in page else page

    if page_name in ["Overview", "🏠  Overview"]:
        render_overview(kpis, df_env_scaled, df_micro_scaled, df_vuln_filtered, geojson_filtered)
    elif page_name in ["Heat & Air", "🌡️  Heat & Air"]:
        render_heat_air(kpis, df_env_scaled, df_vuln_filtered, geojson_filtered)
    elif page_name in ["Respiratory Signals", "🫁  Respiratory Signals"]:
        render_respiratory_signals(kpis, df_env_scaled, df_micro_scaled, df_vuln_filtered)
    elif page_name in ["ICU / Capacity", "🏥  ICU / Capacity"]:
        render_icu_capacity(kpis, df_env_scaled, df_micro_scaled)
    elif page_name in ["Actions & Playbooks", "📋  Actions & Playbooks"]:
        render_actions_playbooks(kpis, df_vuln_filtered)
    elif page_name in ["Data & Ethics", "🔒  Data & Ethics"]:
        render_data_ethics(kpis)
    elif page_name in ["Settings", "⚙️  Settings"]:
        render_settings(kpis)
    else:
        render_overview(kpis, df_env_scaled, df_micro_scaled, df_vuln_filtered, geojson_filtered)


@st.cache_data(ttl=300)
def fetch_real_data_cached(_start_dt, _end_dt):
    """Fetch real data with 5-minute cache."""
    return fetch_and_prepare(_start_dt, _end_dt)


@st.cache_data
def load_vuln_data():
    """Load vulnerability data (cached)."""
    return load_vulnerability()


@st.cache_data
def load_geo_data():
    """Load GeoJSON (cached)."""
    return load_geojson()


if __name__ == "__main__":
    main()
