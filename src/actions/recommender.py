"""
Action Recommender for HEATWATCH+ Demo.
Generates action recommendations per spec section 7.
Each action includes a 'trigger' field explaining the quantitative reason.
"""

from typing import Dict, List, Any


def get_severity(alert_level: str) -> str:
    """Map alert level to default action severity."""
    mapping = {
        "EMERGENCY": "High",
        "WARNING": "High",
        "WATCH": "Med",
        "NORMAL": "Low",
    }
    return mapping.get(alert_level, "Low")


def _alert_trigger(alert_level: str) -> str:
    """Return human-readable trigger reason for alert-based severity."""
    return {
        "EMERGENCY": "Alert Level = EMERGENCY (Risk ≥ 85 or ICU ≥ 30%)",
        "WARNING": "Alert Level = WARNING (Risk ≥ 70 or Surge ≥ 55%)",
        "WATCH": "Alert Level = WATCH (Risk ≥ 55 or Surge ≥ 35%)",
        "NORMAL": "Alert Level = NORMAL (all indicators below thresholds)",
    }.get(alert_level, f"Alert Level = {alert_level}")


def _driver_names(drivers) -> List[str]:
    """Extract plain driver names from either string list or dict list."""
    if not drivers:
        return []
    if isinstance(drivers[0], dict):
        return [d.get("name", "") for d in drivers]
    return drivers


def _metric_context(kpis: Dict = None) -> str:
    """Build metric context string from kpis for trigger explanations."""
    if not kpis:
        return ""
    kpi_data = kpis.get("kpis", {})
    sub = kpis.get("sub_scores", {})
    parts = []

    hr = kpi_data.get("heat_respiratory_risk_index", {})
    if hr.get("value") is not None:
        parts.append(f"Risk Index = {hr['value']}/100")

    sp = kpi_data.get("respiratory_disease_surge_probability", {})
    if sp.get("value_pct") is not None:
        parts.append(f"Surge Prob = {sp['value_pct']}%")

    icu = kpi_data.get("icu_dual_load_risk", {})
    if icu.get("icu_strain_pct") is not None:
        parts.append(f"ICU Strain = {icu['icu_strain_pct']}%")

    if sub.get("heat_score") is not None:
        parts.append(f"Heat Score = {sub['heat_score']}")
    if sub.get("pollution_score") is not None:
        parts.append(f"PM2.5 Score = {sub['pollution_score']}")

    return " • ".join(parts)


def _driver_context(drivers) -> str:
    """Build a short driver context from top 2 drivers."""
    if not drivers:
        return ""
    items = []
    for d in drivers[:2]:
        if isinstance(d, dict):
            name = d.get("name", "")
            change = d.get("change_pct", 0)
            direction = d.get("direction", "→")
            items.append(f"{name} {direction}{change:+.1f}%")
        else:
            items.append(d)
    return " • ".join(items)


def get_municipality_actions(alert_level: str, drivers, top_districts: List[str], kpis: Dict = None) -> List[Dict[str, Any]]:
    """Generate municipality action recommendations."""
    severity = get_severity(alert_level)
    base_trigger = _alert_trigger(alert_level)
    driver_names = _driver_names(drivers)
    metrics = _metric_context(kpis)
    drv_ctx = _driver_context(drivers)

    pm25_active = any("PM2.5" in d for d in driver_names)

    actions = [
        {
            "action": "Open Cooling Centers",
            "description": f"Activate cooling centers in high-risk districts: {', '.join(top_districts[:3])}",
            "severity": severity,
            "owner": "City",
            "eta": "24h",
            "trigger": f"{base_trigger} • {metrics}" if metrics else base_trigger,
        },
        {
            "action": "Issue Heat Alerts",
            "description": "Broadcast heat-health advisories via SMS, social media, and local media",
            "severity": severity,
            "owner": "City",
            "eta": "12h",
            "trigger": f"{base_trigger} • {metrics}" if metrics else base_trigger,
        },
        {
            "action": "Mobilize Outreach Teams",
            "description": f"Deploy community health workers to vulnerable neighborhoods in {', '.join(top_districts[:2])}",
            "severity": "High" if alert_level in ["EMERGENCY", "WARNING"] else "Med",
            "owner": "City",
            "eta": "24h",
            "trigger": f"Vulnerability elevated in {', '.join(top_districts[:2])} • {drv_ctx}" + (f" • {metrics}" if metrics else ""),
        },
        {
            "action": "Coordinate Air Quality Advisories",
            "description": "Issue PM2.5 advisories and coordinate with environmental agencies" if pm25_active else "Monitor air quality levels and prepare advisories if needed",
            "severity": "High" if pm25_active else "Med",
            "owner": "City",
            "eta": "24h",
            "trigger": f"PM2.5 anomaly detected ({drv_ctx})" if pm25_active else f"PM2.5 within normal range • {metrics}" if metrics else "PM2.5 within normal range — precautionary monitoring",
        },
    ]
    return actions


def get_primary_care_actions(alert_level: str, drivers, top_districts: List[str], kpis: Dict = None) -> List[Dict[str, Any]]:
    """Generate primary care action recommendations."""
    severity = get_severity(alert_level)
    base_trigger = _alert_trigger(alert_level)
    metrics = _metric_context(kpis)
    drv_ctx = _driver_context(drivers)

    actions = [
        {
            "action": "Proactive Calls to 65+ and COPD/Asthma Patients",
            "description": "Contact registered elderly and chronic respiratory patients for wellness checks",
            "severity": severity,
            "owner": "MoH",
            "eta": "24h",
            "trigger": f"{base_trigger} • {drv_ctx}" if drv_ctx else base_trigger,
        },
        {
            "action": "Home Visit Scheduling",
            "description": f"Schedule home visits for immobile patients in {', '.join(top_districts[:2])}",
            "severity": "High" if alert_level == "EMERGENCY" else "Med",
            "owner": "MoH",
            "eta": "48h",
            "trigger": f"EMERGENCY: immediate outreach required • {metrics}" if alert_level == "EMERGENCY" else f"{base_trigger} • Vulnerability in {', '.join(top_districts[:2])}",
        },
        {
            "action": "Vaccination Reminders",
            "description": "Send influenza/pneumococcal vaccination reminders to eligible patients (if applicable)",
            "severity": "Med",
            "owner": "MoH",
            "eta": "48h",
            "trigger": "Standing preventive care protocol • Not alert-level dependent",
        },
        {
            "action": "Early Referral Guidance",
            "description": "Distribute updated respiratory distress referral protocols to family physicians",
            "severity": severity,
            "owner": "MoH",
            "eta": "24h",
            "trigger": f"{base_trigger} • {metrics}" if metrics else base_trigger,
        },
    ]
    return actions


def get_hospital_actions(alert_level: str, drivers, icu_strain: int, kpis: Dict = None) -> List[Dict[str, Any]]:
    """Generate hospital action recommendations."""
    severity = get_severity(alert_level)
    base_trigger = _alert_trigger(alert_level)
    metrics = _metric_context(kpis)
    drv_ctx = _driver_context(drivers)

    actions = [
        {
            "action": "Increase Respiratory Triage Staffing",
            "description": "Add respiratory-specialized triage nurses to ER during peak hours",
            "severity": severity,
            "owner": "Hosp",
            "eta": "24h",
            "trigger": f"{base_trigger} • {metrics}" if metrics else base_trigger,
        },
        {
            "action": "Check Oxygen Supplies",
            "description": f"Verify oxygen tank inventory and order additional supplies (current ICU strain: {icu_strain}%)",
            "severity": "High" if icu_strain >= 25 else "Med",
            "owner": "Hosp",
            "eta": "24h",
            "trigger": f"ICU Strain = {icu_strain}% ≥ 25% threshold → High • {drv_ctx}" if icu_strain >= 25 else f"ICU Strain = {icu_strain}% (below 25% — precautionary) • {drv_ctx}",
        },
        {
            "action": "Review ICU Staffing Roster",
            "description": "Ensure adequate ICU nursing coverage for projected surge period",
            "severity": "High" if icu_strain >= 20 else "Med",
            "owner": "Hosp",
            "eta": "48h",
            "trigger": f"ICU Strain = {icu_strain}% ≥ 20% threshold → High • {metrics}" if icu_strain >= 20 else f"ICU Strain = {icu_strain}% (below 20% — monitoring) • {drv_ctx}",
        },
        {
            "action": "Prepare Surge Beds",
            "description": "Identify and prepare overflow bed capacity in case of respiratory surge",
            "severity": "High" if alert_level == "EMERGENCY" else "Med",
            "owner": "Hosp",
            "eta": "48h",
            "trigger": f"EMERGENCY: surge activation • {metrics}" if alert_level == "EMERGENCY" else f"{base_trigger} • Standby • {drv_ctx}",
        },
    ]
    return actions


def get_all_actions(
    alert_level: str,
    drivers,
    top_districts: List[str],
    icu_strain: int,
    kpis: Dict = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """Generate all action recommendations grouped by tab."""
    return {
        "Municipality": get_municipality_actions(alert_level, drivers, top_districts, kpis),
        "Primary Care": get_primary_care_actions(alert_level, drivers, top_districts, kpis),
        "Hospitals": get_hospital_actions(alert_level, drivers, icu_strain, kpis),
    }

