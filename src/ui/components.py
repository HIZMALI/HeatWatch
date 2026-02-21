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
             level: str = "", bar_value: int = 0, unit: str = "",
             scale_hint: str = ""):
    """Render a single KPI card with value, level, delta, risk bar, and optional scale hint."""
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

    # Scale hint line (e.g. "Scale: 0–100 normalized composite index")
    scale_html = ""
    if scale_hint:
        scale_html = (
            f'<div style="font-size:9px;color:{COLORS["text_muted"]};margin-top:2px;'
            f'font-style:italic;opacity:0.7;">{scale_hint}</div>'
        )

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
            f'<div style="margin-top:6px;">'
            f'<div style="width:100%;height:6px;background:linear-gradient(to right,'
            f'{COLORS["gradient_green"]} 0%,{COLORS["gradient_yellow"]} 33%,'
            f'{COLORS["gradient_orange"]} 66%,{COLORS["gradient_red"]} 100%);'
            f'border-radius:3px;position:relative;">'
            f'<div style="position:absolute;top:-4px;left:{marker_pos}%;width:4px;height:14px;'
            f'background:white;border-radius:2px;box-shadow:0 0 4px rgba(255,255,255,0.5);"></div></div>'
            f'<div style="display:flex;justify-content:space-between;font-size:10px;color:{COLORS["text_muted"]};margin-top:4px;">'
            f'<span>0</span><span>100</span></div></div>'
        )

    html = (
        f'<div style="background:linear-gradient(145deg,{COLORS["bg_card"]} 0%,#0f1540 100%);'
        f'border:1px solid {COLORS["border"]};border-radius:12px;padding:18px 16px 14px 16px;'
        f'text-align:center;height:100%;">'
        f'<div style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;'
        f'color:{COLORS["text_muted"]};margin-bottom:8px;">{title}</div>'
        f'{scale_html}'
        f'<div style="font-size:36px;font-weight:700;color:{value_color};margin:4px 0;">{value}{unit}</div>'
        f'{level_html}{delta_html}{subtitle_html}{bar_html}</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def alert_banner(level: str, reason: str):
    """Render colored alert banner with threshold legend."""
    colors = ALERT_COLORS.get(level, ALERT_COLORS.get("WATCH", {"bg": "#1a237e20", "border": "#42a5f5", "text": "#42a5f5"}))
    icons = {"NORMAL": "✅", "WATCH": "👁️", "WARNING": "⚠️", "EMERGENCY": "🚨"}
    icon = icons.get(level, "ℹ️")

    # Threshold legend items
    legend_items = [
        ("✅", "NORMAL", "0–34", "#4caf50"),
        ("👁️", "WATCH", "35–69", "#42a5f5"),
        ("⚠️", "WARNING", "70–84", "#ff9800"),
        ("🚨", "EMERGENCY", "85–100", "#f44336"),
    ]
    legend_html = "".join([
        f'<span style="display:inline-flex;align-items:center;gap:3px;margin-right:14px;'
        f'font-size:11px;color:{c};{"font-weight:700;text-decoration:underline;" if lbl == level else "opacity:0.7;"}'
        f'">{ic} {lbl} ({rng})</span>'
        for ic, lbl, rng, c in legend_items
    ])

    html = (
        f'<div style="background:{colors["bg"]};border:2px solid {colors["border"]};'
        f'border-radius:10px;padding:14px 20px;margin-bottom:16px;font-weight:600;">'
        f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">'
        f'<span style="font-size:24px;">{icon}</span>'
        f'<div><span style="color:{colors["text"]};font-size:18px;font-weight:700;">{level}</span>'
        f'<span style="color:{COLORS["text_secondary"]};margin-left:12px;">{reason}</span></div></div>'
        f'<div style="display:flex;flex-wrap:wrap;padding-top:6px;border-top:1px solid {COLORS["border"]};">{legend_html}</div>'
        f'</div>'
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


def actions_panel(actions_by_tab: Dict[str, List[Dict[str, Any]]], kpis: Dict[str, Any], compact: bool = False):

    """Render the actions panel with tabs and action rows."""
    st.markdown(
        f'<div style="margin-bottom:12px;">'
        f'<div style="color:{COLORS["text_primary"]};font-size:16px;font-weight:600;margin-bottom:6px;'
        f'padding-bottom:6px;border-bottom:2px solid {COLORS["accent_blue"]};display:inline-block;">'
        f'🎯 Action Recommendations (Next 72 Hours)</div>'
        f'<div style="display:flex;gap:12px;font-size:11px;color:{COLORS["text_secondary"]}; background:{COLORS["bg_card"]}80; padding:6px 12px; border-radius:6px; border:1px solid {COLORS["border"]};">'
        f'<span style="display:flex;align-items:center;gap:4px;"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#f44336;"></span> <b>High:</b> Emergency / Warning</span>'
        f'<span style="display:flex;align-items:center;gap:4px;"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#ff9800;"></span> <b>Med:</b> Watch</span>'
        f'<span style="display:flex;align-items:center;gap:4px;"><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#4caf50;"></span> <b>Low:</b> Normal</span>'
        f'</div></div>',
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

                trigger = action.get("trigger", "")
                trigger_html = ""
                if trigger:
                    trigger_html = (
                        f'<div style="font-size:10px;color:{COLORS["text_muted"]};margin-top:4px;'
                        f'padding-top:4px;border-top:1px solid {COLORS["border"]};font-style:italic;">'
                        f'⚡ {trigger}</div>'
                    )

                html = (
                    f'<div style="background:{COLORS["bg_card"]};border:1px solid {COLORS["border"]};'
                    f'border-radius:8px;padding:12px 16px;margin-bottom:8px;">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;">'
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
                    f'{trigger_html}</div>'
                )
                st.markdown(html, unsafe_allow_html=True)

    # ── Shortcut buttons ──────────────────────────────────────
    def _open_sms():
        st.session_state["sms_open"] = True
        st.session_state["sms_sent"] = False
        st.session_state["nav_page"] = "📋  Actions & Playbooks"

    def _open_briefing():
        st.session_state["briefing_open"] = True
        st.session_state["nav_page"] = "📋  Actions & Playbooks"

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        st.button(
            "📱 Send SMS Alert",
            key="btn_sms",
            use_container_width=True,
            on_click=_open_sms,
        )
    with col2:
        st.button(
            "📋 Generate Briefing Note",
            key="btn_briefing",
            use_container_width=True,
            on_click=_open_briefing,
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


def drivers_footer(drivers):
    """Render primary risk drivers section — XAI explainability panel.
    Accepts either list of strings (legacy) or list of dicts with rich data.
    """
    if not drivers:
        return

    # Handle both old (list of strings) and new (list of dicts) format
    if isinstance(drivers[0], str):
        # Legacy format — simple tags
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
        return

    # Rich XAI format
    rows_html = ""
    for d in drivers:
        name = d.get("name", "")
        value = d.get("value", "")
        change = d.get("change_pct", 0)
        direction = d.get("direction", "→")

        # Color based on direction
        if change > 5:
            change_color = COLORS["risk_high"]
        elif change > 0:
            change_color = COLORS["risk_med"]
        elif change < -5:
            change_color = COLORS["risk_low"]
        else:
            change_color = COLORS["text_secondary"]

        change_text = f"{direction} {change:+.1f}%" if change != 0 else "→ stable"

        rows_html += (
            f'<div style="display:flex;align-items:center;justify-content:space-between;'
            f'padding:8px 0;border-bottom:1px solid {COLORS["border"]};gap:12px;">'
            f'<span style="color:{COLORS["text_primary"]};font-size:13px;font-weight:500;flex:1;">{name}</span>'
            f'<span style="color:{COLORS["accent_cyan"]};font-size:13px;font-weight:600;min-width:80px;text-align:right;">{value}</span>'
            f'<span style="color:{change_color};font-size:12px;font-weight:600;min-width:70px;text-align:right;">{change_text}</span>'
            f'</div>'
        )

    html = (
        f'<div style="background:{COLORS["bg_card"]};border:1px solid {COLORS["border"]};'
        f'border-radius:10px;padding:16px 20px;margin-top:16px;">'
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
        f'<span style="font-size:14px;">🔍</span>'
        f'<span style="color:{COLORS["text_primary"]};font-size:14px;font-weight:600;">Primary Risk Drivers (Period Trend)</span>'
        f'</div>'
        f'<div style="font-size:10px;color:{COLORS["text_muted"]};font-style:italic;margin-bottom:10px;">'
        f'Ranked by contribution to composite risk index (last 72h) — Explainable AI • Model Transparency</div>'
        f'<div style="display:flex;align-items:center;justify-content:space-between;padding-bottom:6px;'
        f'border-bottom:2px solid {COLORS["border"]};margin-bottom:4px;">'
        f'<span style="color:{COLORS["text_muted"]};font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;flex:1;">Signal</span>'
        f'<span style="color:{COLORS["text_muted"]};font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;min-width:80px;text-align:right;">Latest</span>'
        f'<span style="color:{COLORS["text_muted"]};font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;min-width:70px;text-align:right;">Change</span>'
        f'</div>'
        f'{rows_html}</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
