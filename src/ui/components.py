"""
Reusable UI components for HEATWATCH+ Demo.
All HTML is rendered as single-line strings to prevent Streamlit markdown escaping.
"""

import streamlit as st
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import pandas as pd
import json
import copy
from typing import Dict, Any, List, Optional

from src.ui.theme import COLORS, LEVEL_COLORS, ALERT_COLORS, get_plotly_layout


def render_top_bar(kpis: Dict[str, Any]):
    """Render the top navigation/info bar."""
    from datetime import datetime as _dt
    location = kpis.get("location", {})
    period = kpis.get("period", {})
    data_mode = kpis.get("data_mode", "real")
    # Always show current time as last update for live feel
    last_update = _dt.now().strftime("%Y-%m-%d %H:%M:%S")

    breadcrumb = f"{location.get('country', '')} › {location.get('city', '')}"

    html = (
        f'<div style="background:linear-gradient(135deg,{COLORS["bg_card"]} 0%,#0d1845 100%);'
        f'border:1px solid {COLORS["border"]};border-radius:10px;padding:12px 20px;margin-bottom:16px;'
        f'display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">'
        f'<span style="color:{COLORS["text_secondary"]};font-size:13px;">📍 <strong style="color:{COLORS["text_primary"]};">{breadcrumb}</strong></span>'
        f'<span style="color:{COLORS["text_secondary"]};font-size:13px;">📅 {period.get("start", "")} → {period.get("end", "")}</span>'
        f'<span style="color:{COLORS["text_secondary"]};font-size:13px;">🔮 Forecast: <strong style="color:{COLORS["text_primary"]};">{period.get("forecast_days", 7)} days</strong></span>'
        f'<span style="color:{COLORS["text_secondary"]};font-size:13px;">💾 Data: <strong style="color:{COLORS["text_primary"]};">Meteostat + AQICN Pattern</strong></span>'
        f'<span style="color:{COLORS["text_secondary"]};font-size:13px;">🕐 Last Update: <strong style="color:{COLORS["accent_cyan"]};">{last_update}</strong></span>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)



def kpi_card(title: str, value: Any, subtitle: str = "", delta: str = "",
             level: str = "", bar_value: int = 0, unit: str = ""):
    """Render a single KPI card with value, level, delta, and risk bar."""
    level_color = LEVEL_COLORS.get(level, COLORS["text_secondary"])

    # Value color based on risk
    if isinstance(value, (int, float)):
        if bar_value >= 70:
            value_color = COLORS["risk_high"]
        elif bar_value >= 40:
            value_color = COLORS["risk_med"]
        else:
            value_color = COLORS["risk_low"]
    else:
        value_color = COLORS["text_primary"]

    # Build HTML parts
    level_html = ""
    if level:
        level_html = (
            f'<span style="display:inline-block;padding:2px 10px;border-radius:12px;font-size:11px;'
            f'font-weight:600;background:{level_color}20;color:{level_color};'
            f'border:1px solid {level_color}40;margin-bottom:6px;">{level}</span><br>'
        )

    delta_html = ""
    if delta:
        delta_html = f'<div style="font-size:12px;color:{COLORS["text_secondary"]};margin-bottom:6px;">{delta}</div>'

    subtitle_html = ""
    if subtitle:
        subtitle_html = f'<div style="font-size:10px;color:{COLORS["text_muted"]};margin-bottom:6px;line-height:1.3;">{subtitle}</div>'

    bar_html = ""
    if bar_value > 0:
        marker_pos = max(0, min(98, bar_value))
        bar_html = (
            f'<div style="width:100%;height:6px;background:linear-gradient(to right,'
            f'{COLORS["gradient_green"]} 0%,{COLORS["gradient_yellow"]} 33%,'
            f'{COLORS["gradient_orange"]} 66%,{COLORS["gradient_red"]} 100%);'
            f'border-radius:3px;position:relative;margin-top:6px;">'
            f'<div style="position:absolute;top:-4px;left:{marker_pos}%;width:4px;height:14px;'
            f'background:white;border-radius:2px;box-shadow:0 0 4px rgba(255,255,255,0.5);"></div></div>'
        )

    html = (
        f'<div style="background:linear-gradient(145deg,{COLORS["bg_card"]} 0%,#0f1540 100%);'
        f'border:1px solid {COLORS["border"]};border-radius:12px;padding:18px 16px 14px 16px;'
        f'text-align:center;height:100%;">'
        f'<div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;'
        f'color:{COLORS["text_muted"]};margin-bottom:8px;">{title}</div>'
        f'<div style="font-size:36px;font-weight:700;color:{value_color};margin:4px 0;">{value}{unit}</div>'
        f'{level_html}{delta_html}{subtitle_html}{bar_html}</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def alert_banner(level: str, reason: str):
    """Render colored alert banner."""
    colors = ALERT_COLORS.get(level, ALERT_COLORS["WATCH"])
    icons = {"WATCH": "👁️", "WARNING": "⚠️", "EMERGENCY": "🚨"}
    icon = icons.get(level, "ℹ️")

    html = (
        f'<div style="background:{colors["bg"]};border:2px solid {colors["border"]};'
        f'border-radius:10px;padding:14px 20px;margin-bottom:16px;font-weight:600;'
        f'display:flex;align-items:center;gap:12px;">'
        f'<span style="font-size:24px;">{icon}</span>'
        f'<div><span style="color:{colors["text"]};font-size:18px;font-weight:700;">{level}</span>'
        f'<span style="color:{COLORS["text_secondary"]};margin-left:12px;">{reason}</span></div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def map_panel(geojson_data: Dict, vuln_df: pd.DataFrame, layer_mode: str = "Vulnerability"):
    """
    Render folium choropleth map of Ankara districts.
    layer_mode: 'Vulnerability' | 'Heat Stress' | 'PM2.5' | 'Combined Risk'
    """
    # Deep copy to avoid mutating cached data
    geojson = copy.deepcopy(geojson_data)

    metric_map = {
        "Vulnerability": "vulnerability_score",
        "Heat Stress": "vulnerability_score",
        "PM2.5": "vulnerability_score",
        "Combined Risk": "current_risk_score",
    }
    metric_col = metric_map.get(layer_mode, "vulnerability_score")

    # Build lookup
    vuln_dict = {}
    for _, row in vuln_df.iterrows():
        vuln_dict[row["district_name"]] = {
            "vulnerability_score": float(row.get("vulnerability_score", 50)),
            "current_risk_score": float(row.get("current_risk_score", 50)),
            "elderly_pct": float(row.get("elderly_pct", 15)),
        }

    # Enrich GeoJSON
    for feature in geojson["features"]:
        name = feature["properties"]["district_name"]
        data = vuln_dict.get(name, {})
        score = data.get(metric_col, 50)
        feature["properties"]["score"] = score
        feature["properties"]["elderly_pct"] = data.get("elderly_pct", 15)
        feature["properties"]["vulnerability_score"] = data.get("vulnerability_score", 50)
        feature["properties"]["current_risk_score"] = data.get("current_risk_score", 50)

    def get_color(score):
        if score >= 75:
            return "#e53935"
        elif score >= 55:
            return "#fb8c00"
        elif score >= 35:
            return "#fdd835"
        else:
            return "#43a047"

    # Create folium map
    m = folium.Map(
        location=[39.93, 32.85],
        zoom_start=10,
        tiles="CartoDB dark_matter",
        control_scale=False,
    )

    # Add GeoJSON layer with custom style
    for feature in geojson["features"]:
        score = feature["properties"]["score"]
        color = get_color(score)
        name = feature["properties"]["district_name"]
        elderly = feature["properties"]["elderly_pct"]
        vuln = feature["properties"]["vulnerability_score"]
        risk = feature["properties"]["current_risk_score"]

        tooltip_text = (
            f"<b>District:</b> {name}<br>"
            f"<b>65+ Population:</b> {elderly}%<br>"
            f"<b>Vulnerability:</b> {vuln}<br>"
            f"<b>Risk Score:</b> {risk}"
        )

        folium.GeoJson(
            {"type": "Feature", "geometry": feature["geometry"], "properties": feature["properties"]},
            style_function=lambda x, c=color: {
                "fillColor": c,
                "color": "#ffffff",
                "weight": 1.5,
                "fillOpacity": 0.65,
            },
            tooltip=folium.Tooltip(tooltip_text),
        ).add_to(m)

    st_folium(m, use_container_width=True, height=400, returned_objects=[])


def actions_panel(actions_by_tab: Dict[str, List[Dict[str, Any]]], kpis: Dict[str, Any]):
    """Render the actions panel with tabs and action rows."""
    st.markdown(
        f'<div style="color:{COLORS["text_primary"]};font-size:16px;font-weight:600;margin-bottom:12px;'
        f'padding-bottom:6px;border-bottom:2px solid {COLORS["accent_blue"]};display:inline-block;">'
        f'🎯 Action Recommendations (Next 72 Hours)</div>',
        unsafe_allow_html=True,
    )

    tabs = st.tabs(list(actions_by_tab.keys()))

    for tab, (tab_name, action_list) in zip(tabs, actions_by_tab.items()):
        with tab:
            for action in action_list:
                sev = action["severity"]
                sev_color = LEVEL_COLORS.get(sev, "#9fa8da")

                # Severity badge
                if sev == "High":
                    badge_bg, badge_border = "#f4433620", "#f4433640"
                elif sev == "Med":
                    badge_bg, badge_border = "#ff980020", "#ff980040"
                else:
                    badge_bg, badge_border = "#4caf5020", "#4caf5040"

                html = (
                    f'<div style="background:{COLORS["bg_card"]};border:1px solid {COLORS["border"]};'
                    f'border-radius:8px;padding:12px 16px;margin-bottom:8px;display:flex;'
                    f'justify-content:space-between;align-items:center;">'
                    f'<div style="flex:1;"><span style="color:{sev_color};margin-right:8px;">●</span>'
                    f'<span style="color:{COLORS["text_primary"]};font-size:13px;font-weight:500;">{action["action"]}</span></div>'
                    f'<div style="display:flex;gap:6px;flex-shrink:0;">'
                    f'<span style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;'
                    f'font-weight:600;background:{badge_bg};color:{sev_color};border:1px solid {badge_border};">{sev}</span>'
                    f'<span style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;'
                    f'font-weight:600;background:#42a5f520;color:#42a5f5;border:1px solid #42a5f540;">{action["owner"]}</span>'
                    f'<span style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;'
                    f'font-weight:600;background:#9c27b020;color:#ce93d8;border:1px solid #9c27b040;">{action["eta"]}</span>'
                    f'</div></div>'
                )
                st.markdown(html, unsafe_allow_html=True)

    # Action buttons
    st.markdown("", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📱 Send SMS Alert", use_container_width=True, key="btn_sms"):
            st.session_state["show_sms"] = True

    with col2:
        if st.button("📋 Generate Briefing Note", use_container_width=True, key="btn_briefing"):
            st.session_state["show_briefing"] = True

    # SMS Modal
    if st.session_state.get("show_sms", False):
        from src.actions.playbooks import generate_sms_alert
        alert_level = kpis.get("kpis", {}).get("alert_level", {}).get("value", "WARNING")

        st.markdown(
            f'<div style="background:{COLORS["bg_card"]};border:1px solid {COLORS["border"]};'
            f'border-radius:10px;padding:16px 20px;margin-top:12px;">'
            f'<div style="color:{COLORS["accent_cyan"]};font-size:14px;font-weight:700;margin-bottom:12px;">'
            f'📱 SMS Alert Templates</div>',
            unsafe_allow_html=True,
        )
        tab_pub, tab_eld = st.tabs(["Public Alert", "65+ Targeted"])
        with tab_pub:
            sms_text = generate_sms_alert(alert_level, kpis, target="public")
            st.markdown(
                f'<pre style="background:{COLORS["bg_dark"]};color:{COLORS["text_primary"]};'
                f'border:1px solid {COLORS["border"]};border-radius:8px;padding:16px;'
                f'font-size:13px;line-height:1.7;font-family:monospace;white-space:pre-wrap;'
                f'margin:0;">{sms_text}</pre>',
                unsafe_allow_html=True,
            )
        with tab_eld:
            sms_text_eld = generate_sms_alert(alert_level, kpis, target="elderly")
            st.markdown(
                f'<pre style="background:{COLORS["bg_dark"]};color:{COLORS["text_primary"]};'
                f'border:1px solid {COLORS["border"]};border-radius:8px;padding:16px;'
                f'font-size:13px;line-height:1.7;font-family:monospace;white-space:pre-wrap;'
                f'margin:0;">{sms_text_eld}</pre>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Briefing Modal
    if st.session_state.get("show_briefing", False):
        from src.actions.playbooks import generate_briefing_note

        top_districts = []
        if "vuln_df" in st.session_state:
            top_districts = (
                st.session_state["vuln_df"]
                .sort_values("vulnerability_score", ascending=False)["district_name"]
                .tolist()[:5]
            )

        note = generate_briefing_note(kpis, top_districts, actions_by_tab)
        st.markdown(
            f'<div style="background:{COLORS["bg_card"]};border:1px solid {COLORS["border"]};'
            f'border-radius:10px;padding:16px 20px;margin-top:12px;">'
            f'<div style="color:{COLORS["accent_cyan"]};font-size:14px;font-weight:700;margin-bottom:12px;">'
            f'📋 Briefing Note</div>'
            f'<pre style="background:{COLORS["bg_dark"]};color:{COLORS["text_primary"]};'
            f'border:1px solid {COLORS["border"]};border-radius:8px;padding:16px;'
            f'font-size:12px;line-height:1.6;font-family:monospace;white-space:pre-wrap;'
            f'margin:0;">{note}</pre></div>',
            unsafe_allow_html=True,
        )


def trend_chart_env(df_env: pd.DataFrame):
    """Render environmental trends chart with Plotly."""
    layout = get_plotly_layout("Environmental Trends")

    fig = go.Figure(layout=layout)

    fig.add_trace(go.Scatter(
        x=df_env["date"], y=df_env["temp_c"],
        name="Temp (°C)", mode="lines+markers",
        line=dict(color="#ef5350", width=2),
        marker=dict(size=6),
    ))

    fig.add_trace(go.Scatter(
        x=df_env["date"], y=df_env["pm25_ugm3"],
        name="PM2.5 (µg/m³)", mode="lines+markers",
        line=dict(color="#ffa726", width=2),
        marker=dict(size=6),
    ))

    fig.add_trace(go.Scatter(
        x=df_env["date"], y=df_env["humidity_pct"],
        name="Humidity (%)", mode="lines+markers",
        line=dict(color="#42a5f5", width=2, dash="dot"),
        marker=dict(size=6),
    ))

    fig.update_layout(height=300, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)


def trend_chart_micro(df_micro: pd.DataFrame):
    """Render population micro-signals chart with Plotly."""
    layout = get_plotly_layout("Population Micro-Signals")

    fig = go.Figure(layout=layout)

    fig.add_trace(go.Scatter(
        x=df_micro["date"], y=df_micro["symptom_search_index"],
        name="Symptom Searches (index)", mode="lines+markers",
        line=dict(color="#26c6da", width=2),
        marker=dict(size=6),
    ))

    fig.add_trace(go.Scatter(
        x=df_micro["date"], y=df_micro["pharmacy_visits_index"],
        name="Pharmacy Visits (index)", mode="lines+markers",
        line=dict(color="#ab47bc", width=2),
        marker=dict(size=6),
    ))

    fig.add_trace(go.Scatter(
        x=df_micro["date"], y=df_micro["clinic_cases_index"],
        name="Clinic Cases (index)", mode="lines+markers",
        line=dict(color="#66bb6a", width=2),
        marker=dict(size=6),
    ))

    fig.update_layout(height=300, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)


def drivers_footer(drivers: List[str]):
    """Render primary drivers strip at the bottom."""
    tags = " ".join([
        f'<span style="display:inline-block;background:#42a5f515;color:{COLORS["accent_cyan"]};'
        f'padding:4px 12px;border-radius:16px;font-size:12px;font-weight:500;margin:2px 4px;'
        f'border:1px solid #42a5f530;">{d}</span>'
        for d in drivers
    ])
    html = (
        f'<div style="background:{COLORS["bg_card"]};border:1px solid {COLORS["border"]};'
        f'border-radius:10px;padding:12px 20px;margin-top:16px;">'
        f'<span style="color:{COLORS["text_muted"]};font-size:12px;font-weight:600;margin-right:12px;">'
        f'Primary Drivers:</span>{tags}</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
