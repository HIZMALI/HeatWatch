"""
Page renderers for HEATWATCH+ Demo.
Each function renders a complete page in the Streamlit app.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, Any

from src.ui.components import (
    render_top_bar, kpi_card, alert_banner, map_panel,
    actions_panel, trend_chart_env, trend_chart_micro, drivers_footer,
)
from src.ui.theme import COLORS, get_plotly_layout
from src.actions.recommender import get_all_actions
from src.models.signal_fusion import fuse_signals, compute_signal_convergence


def render_overview(kpis: Dict[str, Any], df_env: pd.DataFrame,
                    df_micro: pd.DataFrame, df_vuln: pd.DataFrame,
                    geojson: Dict):
    """Render the main Overview page."""

    # Top bar
    render_top_bar(kpis)

    kpi_data = kpis.get("kpis", {})

    # Alert Banner
    alert = kpi_data.get("alert_level", {})
    alert_banner(alert.get("value", "WATCH"), alert.get("reason", ""))

    # --- KPI Cards Row ---
    cols = st.columns(5)

    with cols[0]:
        hr = kpi_data.get("heat_respiratory_risk_index", {})
        kpi_card(
            title="Heat-Respiratory Risk Index",
            value=hr.get("value", 0),
            level=hr.get("level", ""),
            delta=f"↑ +{hr.get('delta_48h', 0)} / 48h",
            bar_value=hr.get("value", 0),
            scale_hint="Scale: 0–100 normalized composite index",
        )

    with cols[1]:
        sp = kpi_data.get("respiratory_disease_surge_probability", {})
        kpi_card(
            title="Respiratory Disease Surge Probability",
            value=sp.get("value_pct", 0),
            unit="%",
            subtitle=sp.get("subtitle", ""),
            delta=f"↑ +{sp.get('delta_48h', 0)} / 48h",
            bar_value=sp.get("value_pct", 0),
            scale_hint="Probability (%), model-calibrated (0–100)",
        )

    with cols[2]:
        cs = kpi_data.get("combined_respiratory_stress_index", {})
        conv_text = "Converging ⬆" if cs.get("convergence") else "Stable"
        kpi_card(
            title="Combined Respiratory Stress Index",
            value=cs.get("value", 0),
            subtitle=conv_text,
            bar_value=int(cs.get("value", 0) * 100),
            scale_hint="Scale: 0.0–1.0 weighted fusion",
        )

    with cols[3]:
        icu = kpi_data.get("icu_dual_load_risk", {})
        kpi_card(
            title="ICU Dual Load Risk",
            value=icu.get("icu_strain_pct", 0),
            unit="%",
            subtitle=f"Peak: {icu.get('peak_date', 'N/A')}",
            bar_value=int(icu.get("icu_strain_pct", 0) * 2.5),  # scale 0-40 to 0-100
            scale_hint="ICU strain %, projected (0–40)",
        )

    with cols[4]:
        al = kpi_data.get("alert_level", {})
        alert_val = al.get("value", "WATCH")
        bar_val = {"NORMAL": 15, "WATCH": 40, "WARNING": 70, "EMERGENCY": 95}.get(alert_val, 15)
        kpi_card(
            title="Alert Level",
            value=alert_val,
            subtitle=al.get("reason", ""),
            bar_value=bar_val,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Map + Actions Row ---
    col_map, col_actions = st.columns([3, 2])

    with col_map:
        st.markdown(f'<div style="color:{COLORS["text_primary"]};font-size:16px;font-weight:600;margin-bottom:12px;padding-bottom:6px;border-bottom:2px solid {COLORS["accent_blue"]};display:inline-block;">🗺️ Elderly Vulnerability Map — Ankara</div>', unsafe_allow_html=True)

        layer_mode = st.radio(
            "Map Layer",
            ["Vulnerability", "Heat Stress", "PM2.5", "Combined Risk"],
            horizontal=True,
            key="map_layer",
            label_visibility="collapsed",
        )
        map_panel(geojson, df_vuln, layer_mode)

    with col_actions:
        # Get actions
        alert_level = kpi_data.get("alert_level", {}).get("value", "WARNING")
        drivers_list = kpis.get("drivers", [])
        top_districts = (
            df_vuln.sort_values("vulnerability_score", ascending=False)["district_name"].tolist()[:5]
        )
        icu_strain = kpi_data.get("icu_dual_load_risk", {}).get("icu_strain_pct", 15)

        all_actions = get_all_actions(alert_level, drivers_list, top_districts, icu_strain, kpis)
        actions_panel(all_actions, kpis)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Trend Charts Row ---
    col_env, col_micro = st.columns(2)

    with col_env:
        trend_chart_env(df_env)

    with col_micro:
        trend_chart_micro(df_micro)

    # --- Drivers Footer ---
    drivers_footer(kpis.get("drivers", []))


def render_heat_air(kpis: Dict[str, Any], df_env: pd.DataFrame, df_vuln: pd.DataFrame, geojson: Dict):
    """Render Heat & Air Quality page."""
    render_top_bar(kpis)

    st.markdown("## 🌡️ Heat & Air Quality Analysis")

    # Temperature analysis
    col1, col2 = st.columns(2)

    with col1:
        layout = get_plotly_layout("Temperature Trends")
        fig = go.Figure(layout=layout)
        fig.add_trace(go.Scatter(
            x=df_env["date"], y=df_env["temp_c"],
            name="Daytime Temp (°C)", mode="lines+markers",
            line=dict(color="#ef5350", width=2.5),
            fill="tozeroy", fillcolor="rgba(239,83,80,0.1)",
        ))
        fig.add_trace(go.Scatter(
            x=df_env["date"], y=df_env["nighttime_temp_c"],
            name="Nighttime Temp (°C)", mode="lines+markers",
            line=dict(color="#ff8a65", width=2, dash="dash"),
        ))
        # WHO threshold line
        fig.add_hline(y=25, line_dash="dot", line_color="#ffa726",
                      annotation_text="Nighttime Heat Threshold (25°C)")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        layout = get_plotly_layout("Air Quality — PM2.5")
        fig = go.Figure(layout=layout)
        fig.add_trace(go.Bar(
            x=df_env["date"], y=df_env["pm25_ugm3"],
            name="PM2.5 (µg/m³)",
            marker_color=["#f44336" if v > 55 else "#ff9800" if v > 35 else "#4caf50"
                          for v in df_env["pm25_ugm3"]],
        ))
        fig.add_hline(y=35, line_dash="dot", line_color="#ff9800",
                      annotation_text="WHO 24h Guideline (35 µg/m³)")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    # Humidity
    layout = get_plotly_layout("Humidity Trend")
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Scatter(
        x=df_env["date"], y=df_env["humidity_pct"],
        name="Humidity (%)", mode="lines+markers",
        line=dict(color="#42a5f5", width=2),
        fill="tozeroy", fillcolor="rgba(66,165,245,0.1)",
    ))
    fig.update_layout(height=250)
    st.plotly_chart(fig, use_container_width=True)

    # District heatmap
    st.markdown("### 🗺️ Heat Stress by District")
    map_panel(geojson, df_vuln, "Heat Stress")


def render_respiratory_signals(kpis: Dict[str, Any], df_env: pd.DataFrame,
                                df_micro: pd.DataFrame, df_vuln: pd.DataFrame):
    """Render Respiratory Signals page."""
    render_top_bar(kpis)

    st.markdown("## 🫁 Respiratory Signals Analysis")

    kpi_data = kpis.get("kpis", {})
    sp = kpi_data.get("respiratory_disease_surge_probability", {})

    # KPI row
    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card(
            "Surge Probability", f"{sp.get('value_pct', 0)}%", "",
            f"↑ +{sp.get('delta_48h', 0)} / 48h",
            bar_value=sp.get("value_pct", 0),
        )
    with col2:
        cs = kpi_data.get("combined_respiratory_stress_index", {})
        kpi_card(
            "Combined Stress Index", cs.get("value", 0), "",
            "Converging" if cs.get("convergence") else "Stable",
            bar_value=int(cs.get("value", 0) * 100),
        )
    with col3:
        hr = kpi_data.get("heat_respiratory_risk_index", {})
        kpi_card(
            "Heat-Respiratory Risk", hr.get("value", 0), "",
            hr.get("level", ""),
            bar_value=hr.get("value", 0),
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Signal fusion
    df_fused = fuse_signals(df_env, df_micro)
    convergence = compute_signal_convergence(df_fused)

    col1, col2 = st.columns(2)

    with col1:
        trend_chart_micro(df_micro)

    with col2:
        # Fusion chart
        layout = get_plotly_layout("Signal Fusion — Convergence Analysis")
        fig = go.Figure(layout=layout)
        fig.add_trace(go.Scatter(
            x=df_fused["date"], y=df_fused["env_stress_index"],
            name="Env Stress Index", mode="lines+markers",
            line=dict(color="#ef5350", width=2),
        ))
        fig.add_trace(go.Scatter(
            x=df_fused["date"], y=df_fused["pop_signal_index"],
            name="Pop Signal Index", mode="lines+markers",
            line=dict(color="#26c6da", width=2),
        ))
        fig.add_trace(go.Scatter(
            x=df_fused["date"], y=df_fused["fusion_score"],
            name="Fusion Score", mode="lines+markers",
            line=dict(color="#ffa726", width=2.5, dash="dash"),
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Convergence status
    st.info(
        f"**Signal Convergence:** {convergence['trend'].replace('_', ' ').title()} | "
        f"Env trend: {convergence['env_trend_rate']:+.1f}/day | "
        f"Pop trend: {convergence['pop_trend_rate']:+.1f}/day"
    )

    drivers_footer(kpis.get("drivers", []))


def render_icu_capacity(kpis: Dict[str, Any], df_env: pd.DataFrame,
                        df_micro: pd.DataFrame):
    """Render ICU / Capacity page."""
    render_top_bar(kpis)

    st.markdown("## 🏥 ICU & Capacity Projection")

    kpi_data = kpis.get("kpis", {})
    icu = kpi_data.get("icu_dual_load_risk", {})

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card(
            "ICU Strain", f"{icu.get('icu_strain_pct', 0)}%", "",
            f"Peak: {icu.get('peak_date', 'N/A')}",
            bar_value=int(icu.get("icu_strain_pct", 0) * 2.5),
        )
    with col2:
        hr = kpi_data.get("heat_respiratory_risk_index", {})
        kpi_card(
            "Heat-Resp Risk Driver", hr.get("value", 0), "",
            hr.get("level", ""), bar_value=hr.get("value", 0),
        )
    with col3:
        sp = kpi_data.get("respiratory_disease_surge_probability", {})
        kpi_card(
            "Surge Driver", f"{sp.get('value_pct', 0)}%", "",
            "", bar_value=sp.get("value_pct", 0),
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Projected ICU load over time
    df_fused = fuse_signals(df_env, df_micro)

    # Simulate ICU projection per day
    from src.models.risk_engine import compute_icu_strain, compute_heat_respiratory_risk_index, compute_heat_score, compute_pollution_score, compute_micro_signal_score, compute_respiratory_surge_probability
    import numpy as np

    icu_projection = []
    for _, row in df_fused.iterrows():
        hs = compute_heat_score(row["temp_c"], row["nighttime_temp_c"])
        ps = compute_pollution_score(row["pm25_ugm3"])
        ms = compute_micro_signal_score(
            row["symptom_search_index"],
            row["pharmacy_visits_index"],
            row["clinic_cases_index"],
        )
        avg_vuln = 55  # approximate
        hrr = compute_heat_respiratory_risk_index(hs, ps, avg_vuln, ms)
        sp = compute_respiratory_surge_probability(ms, row["pm25_ugm3"], row["nighttime_temp_c"])
        strain = compute_icu_strain(hrr, sp)
        icu_projection.append(strain)

    layout = get_plotly_layout("Projected ICU Strain Over Forecast Period")
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Scatter(
        x=df_fused["date"], y=icu_projection,
        name="ICU Strain (%)", mode="lines+markers",
        line=dict(color="#ef5350", width=2.5),
        fill="tozeroy", fillcolor="rgba(239,83,80,0.15)",
    ))
    fig.add_hline(y=30, line_dash="dot", line_color="#d50000",
                  annotation_text="Emergency Threshold (30%)")
    fig.add_hline(y=20, line_dash="dot", line_color="#ff9800",
                  annotation_text="Warning Threshold (20%)")
    fig.update_layout(height=350, yaxis=dict(range=[0, 45]))
    st.plotly_chart(fig, use_container_width=True)

    # Capacity table
    st.markdown(f'<div style="color:{COLORS["text_primary"]};font-size:16px;font-weight:600;margin-bottom:12px;padding-bottom:6px;border-bottom:2px solid {COLORS["accent_blue"]};display:inline-block;">📊 Capacity Indicators</div>', unsafe_allow_html=True)

    cap_data = [
        ("ICU Beds (est.)", f"{icu.get('icu_strain_pct', 15)}%", f"{min(40, icu.get('icu_strain_pct', 15) + 10)}%", "⚠️ Watch", COLORS["risk_med"]),
        ("Respiratory Ventilators", "18%", "28%", "✅ Normal", COLORS["risk_low"]),
        ("Oxygen Supply", "65%", "75%", "⚠️ Watch", COLORS["risk_med"]),
        ("ER Triage Capacity", "45%", "60%", "✅ Normal", COLORS["risk_low"]),
    ]

    th_style = f'padding:10px 14px;text-align:left;color:{COLORS["text_muted"]};font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;border-bottom:2px solid {COLORS["border"]};'
    rows_html = ""
    for name, current, peak, status, color in cap_data:
        rows_html += (
            f'<tr style="border-bottom:1px solid {COLORS["border"]};">'
            f'<td style="padding:12px 14px;color:{COLORS["text_primary"]};font-weight:500;">{name}</td>'
            f'<td style="padding:12px 14px;color:{COLORS["text_secondary"]};">{current}</td>'
            f'<td style="padding:12px 14px;color:{COLORS["text_secondary"]};">{peak}</td>'
            f'<td style="padding:12px 14px;color:{color};font-weight:600;">{status}</td>'
            f'</tr>'
        )

    table_html = (
        f'<div style="background:{COLORS["bg_card"]};border:1px solid {COLORS["border"]};border-radius:12px;overflow:hidden;margin-bottom:16px;">'
        f'<table style="width:100%;border-collapse:collapse;">'
        f'<thead><tr style="background:{COLORS["bg_sidebar"]};">'
        f'<th style="{th_style}">Indicator</th>'
        f'<th style="{th_style}">Current Load</th>'
        f'<th style="{th_style}">Projected Peak</th>'
        f'<th style="{th_style}">Status</th>'
        f'</tr></thead>'
        f'<tbody>{rows_html}</tbody></table></div>'
    )
    st.markdown(table_html, unsafe_allow_html=True)


def render_actions_playbooks(kpis: Dict[str, Any], df_vuln: pd.DataFrame):
    """Render Actions & Playbooks page."""
    render_top_bar(kpis)

    st.markdown("## 📋 Actions & Playbooks")

    kpi_data = kpis.get("kpis", {})
    alert_level = kpi_data.get("alert_level", {}).get("value", "WARNING")
    drivers_list = kpis.get("drivers", [])
    top_districts = (
        df_vuln.sort_values("vulnerability_score", ascending=False)["district_name"].tolist()[:5]
    )
    icu_strain = kpi_data.get("icu_dual_load_risk", {}).get("icu_strain_pct", 15)

    all_actions = get_all_actions(alert_level, drivers_list, top_districts, icu_strain, kpis)
    actions_panel(all_actions, kpis)

    st.markdown("---")
    st.markdown("### 📱 Dispatch Center")
    st.caption("Send alerts and briefing notes to relevant stakeholders.")

    from src.actions.playbooks import generate_sms_alert, generate_briefing_note

    # ── Callback functions for buttons ────────────────────────
    def _do_send_sms():
        st.session_state["sms_sent"] = True

    def _do_reset_sms():
        st.session_state["sms_sent"] = False

    def _do_send_briefing():
        st.session_state["briefing_sent"] = True

    def _do_reset_briefing():
        st.session_state["briefing_sent"] = False

    sms_col, brief_col = st.columns(2)

    # ── SMS DISPATCH ──────────────────────────────────────────
    with sms_col:
        st.markdown("**📱 SMS Alert**")

        template_target = st.radio(
            "Target Audience",
            ["🏙️ Public (General)", "👴 65+ Elderly"],
            key="sms_template_target",
            horizontal=True,
        )
        target_key = "elderly" if "Elderly" in template_target else "public"
        sms_text = generate_sms_alert(alert_level, kpis, target=target_key)

        st.text_area(
            "Message Preview",
            value=sms_text,
            height=180,
            key="sms_preview_ta",
            label_visibility="collapsed",
        )

        recipients = {"🏙️ Public (General)": "142,600", "👴 65+ Elderly": "18,450"}
        rec_count = recipients.get(template_target, "—")
        st.caption(f"Recipients: **{rec_count} subscribers**")

        if st.session_state.get("sms_sent", False):
            st.success("✅ SMS alert dispatched successfully!")
            st.button("↺ Reset", key="sms_reset_btn", on_click=_do_reset_sms)
        else:
            st.button(
                "🚀 Send SMS Alert Now",
                key="send_sms_now",
                use_container_width=True,
                type="primary",
                on_click=_do_send_sms,
            )

    # ── BRIEFING NOTE ─────────────────────────────────────────
    with brief_col:
        st.markdown("**📋 Briefing Note**")

        note = generate_briefing_note(kpis, top_districts, all_actions)
        with st.expander("📄 View Briefing Note", expanded=st.session_state.get("briefing_open", False)):
            st.text_area(
                "Briefing Note Content",
                value=note,
                height=200,
                key="briefing_ta",
                label_visibility="collapsed",
            )

        st.caption("Send to: **Municipal Health Authority**")

        if st.session_state.get("briefing_sent", False):
            st.success("✅ Briefing Note sent successfully!")
            st.button("↺ Reset", key="brief_reset_btn", on_click=_do_reset_briefing)
        else:
            st.button(
                "📤 Send Briefing Note",
                key="send_briefing_now",
                use_container_width=True,
                on_click=_do_send_briefing,
            )

    # Reset open flags after first render
    st.session_state.pop("sms_open", None)
    st.session_state.pop("briefing_open", None)



def render_data_ethics(kpis: Dict[str, Any]):
    """Render Data & Ethics page."""
    render_top_bar(kpis)

    st.markdown("## 🔒 Data & Ethics")

    st.markdown("### Data Sources & Privacy")
    st.markdown("**HEATWATCH+** is designed with privacy and ethical use at its core.")

    st.markdown("#### Data Used")
    st.markdown("""
| Source | Type | Privacy Level |
|--------|------|---------------|
| Temperature/Weather | Aggregated municipal data | Public |
| PM2.5 Air Quality | Government sensor network | Public |
| Symptom Search Trends | Anonymized, aggregated | De-identified |
| Pharmacy Sales | Aggregated regional data | De-identified |
| Clinic Visits | Aggregate counts only | De-identified |
| Demographics (65+) | Census-level data | Public |
""")

    st.markdown("#### Privacy Principles")
    st.markdown("""
- ✅ **No individual-level health records** are accessed or stored
- ✅ All data is **aggregated at district level** minimum
- ✅ **No personally identifiable information (PII)** in any layer
- ✅ Search/pharmacy data is **pre-anonymized** before ingestion
- ✅ System designed for **public health decision support**, not surveillance
""")

    st.markdown("#### Ethical Framework")
    st.markdown("""
- 🎯 **Beneficence**: Early warning to protect vulnerable populations
- 🛡️ **Non-maleficence**: No individual targeting or profiling
- ⚖️ **Justice**: Focus on underserved, high-vulnerability districts
- 🔓 **Transparency**: All algorithms and thresholds are documented
- 📊 **Accountability**: Clear audit trail for recommendations
""")

    st.markdown("#### Current Data Mode")
    st.info(f"**{kpis.get('data_mode', 'real').title()}** — This demo uses data patterns based on Meteostat and AQICN sources for Ankara, Turkey.")


def render_settings(kpis: Dict[str, Any]):
    """Render Settings page."""
    render_top_bar(kpis)

    st.markdown("## ⚙️ Settings")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'<div style="background:{COLORS["bg_card"]};border:1px solid {COLORS["border"]};border-radius:12px;padding:24px;margin-bottom:16px;"><h4 style="color:{COLORS["text_primary"]};margin:0;">🌍 Location Settings</h4></div>', unsafe_allow_html=True)

        st.selectbox("City", ["Ankara", "Istanbul", "Izmir"], key="setting_city")
        st.selectbox("Default District", [
            "Altındağ", "Çankaya", "Keçiören", "Yenimahalle", "Mamak",
            "Etimesgut", "Sincan", "Gölbaşı", "Pursaklar", "Polatlı",
        ], key="setting_district")

    with col2:
        st.markdown(f'<div style="background:{COLORS["bg_card"]};border:1px solid {COLORS["border"]};border-radius:12px;padding:24px;margin-bottom:16px;"><h4 style="color:{COLORS["text_primary"]};margin:0;">📊 Analysis Settings</h4></div>', unsafe_allow_html=True)

        st.slider("Forecast Horizon (days)", 3, 14, 7, key="setting_forecast")
        st.selectbox("Data Mode", ["Simulated", "Live (Coming Soon)"], key="setting_data_mode")
        st.number_input("Random Seed", value=42, key="setting_seed")

    st.markdown(f'<div style="background:{COLORS["bg_card"]};border:1px solid {COLORS["border"]};border-radius:12px;padding:24px;margin-top:16px;"><h4 style="color:{COLORS["text_primary"]};margin:0;">🎨 Threshold Configuration</h4></div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.number_input("NORMAL — Heat Risk <", value=35, key="thresh_normal_heat")
        st.number_input("NORMAL — Surge Prob <", value=20, key="thresh_normal_surge")
    with col2:
        st.number_input("WATCH — Heat Risk ≥", value=55, key="thresh_watch_heat")
        st.number_input("WATCH — Surge Prob ≥", value=35, key="thresh_watch_surge")
    with col3:
        st.number_input("WARNING — Heat Risk ≥", value=70, key="thresh_warn_heat")
        st.number_input("WARNING — Surge Prob ≥", value=55, key="thresh_warn_surge")
    with col4:
        st.number_input("EMERGENCY — Heat Risk ≥", value=85, key="thresh_emerg_heat")
        st.number_input("EMERGENCY — ICU Strain ≥", value=30, key="thresh_emerg_icu")

    st.caption("All thresholds operate on a 0–100 normalized scale unless otherwise stated. ICU Strain is expressed as a percentage (0–40%).")
    st.info("ℹ️ Settings changes are for demo purposes only and will reset on page reload.")
