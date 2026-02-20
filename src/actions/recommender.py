"""
Action Recommender for HEATWATCH+ Demo.
Generates action recommendations per spec section 7.
"""

from typing import Dict, List, Any


def get_severity(alert_level: str) -> str:
    """Map alert level to default action severity."""
    mapping = {
        "EMERGENCY": "High",
        "WARNING": "High",
        "WATCH": "Med",
    }
    return mapping.get(alert_level, "Low")


def get_municipality_actions(alert_level: str, drivers: List[str], top_districts: List[str]) -> List[Dict[str, Any]]:
    """Generate municipality action recommendations."""
    severity = get_severity(alert_level)

    actions = [
        {
            "action": "Open Cooling Centers",
            "description": f"Activate cooling centers in high-risk districts: {', '.join(top_districts[:3])}",
            "severity": severity,
            "owner": "City",
            "eta": "24h",
        },
        {
            "action": "Issue Heat Alerts",
            "description": "Broadcast heat-health advisories via SMS, social media, and local media",
            "severity": severity,
            "owner": "City",
            "eta": "12h",
        },
        {
            "action": "Mobilize Outreach Teams",
            "description": f"Deploy community health workers to vulnerable neighborhoods in {', '.join(top_districts[:2])}",
            "severity": "High" if alert_level in ["EMERGENCY", "WARNING"] else "Med",
            "owner": "City",
            "eta": "24h",
        },
        {
            "action": "Coordinate Air Quality Advisories",
            "description": "Issue PM2.5 advisories and coordinate with environmental agencies" if "PM2.5" in drivers else "Monitor air quality levels and prepare advisories if needed",
            "severity": "High" if "PM2.5" in drivers else "Med",
            "owner": "City",
            "eta": "24h",
        },
    ]
    return actions


def get_primary_care_actions(alert_level: str, drivers: List[str], top_districts: List[str]) -> List[Dict[str, Any]]:
    """Generate primary care action recommendations."""
    severity = get_severity(alert_level)

    actions = [
        {
            "action": "Proactive Calls to 65+ and COPD/Asthma Patients",
            "description": "Contact registered elderly and chronic respiratory patients for wellness checks",
            "severity": severity,
            "owner": "MoH",
            "eta": "24h",
        },
        {
            "action": "Home Visit Scheduling",
            "description": f"Schedule home visits for immobile patients in {', '.join(top_districts[:2])}",
            "severity": "High" if alert_level == "EMERGENCY" else "Med",
            "owner": "MoH",
            "eta": "48h",
        },
        {
            "action": "Vaccination Reminders",
            "description": "Send influenza/pneumococcal vaccination reminders to eligible patients (if applicable)",
            "severity": "Med",
            "owner": "MoH",
            "eta": "48h",
        },
        {
            "action": "Early Referral Guidance",
            "description": "Distribute updated respiratory distress referral protocols to family physicians",
            "severity": severity,
            "owner": "MoH",
            "eta": "24h",
        },
    ]
    return actions


def get_hospital_actions(alert_level: str, drivers: List[str], icu_strain: int) -> List[Dict[str, Any]]:
    """Generate hospital action recommendations."""
    severity = get_severity(alert_level)

    actions = [
        {
            "action": "Increase Respiratory Triage Staffing",
            "description": "Add respiratory-specialized triage nurses to ER during peak hours",
            "severity": severity,
            "owner": "Hosp",
            "eta": "24h",
        },
        {
            "action": "Check Oxygen Supplies",
            "description": f"Verify oxygen tank inventory and order additional supplies (current ICU strain: {icu_strain}%)",
            "severity": "High" if icu_strain >= 25 else "Med",
            "owner": "Hosp",
            "eta": "24h",
        },
        {
            "action": "Review ICU Staffing Roster",
            "description": "Ensure adequate ICU nursing coverage for projected surge period",
            "severity": "High" if icu_strain >= 20 else "Med",
            "owner": "Hosp",
            "eta": "48h",
        },
        {
            "action": "Prepare Surge Beds",
            "description": "Identify and prepare overflow bed capacity in case of respiratory surge",
            "severity": "High" if alert_level == "EMERGENCY" else "Med",
            "owner": "Hosp",
            "eta": "48h",
        },
    ]
    return actions


def get_all_actions(
    alert_level: str,
    drivers: List[str],
    top_districts: List[str],
    icu_strain: int,
) -> Dict[str, List[Dict[str, Any]]]:
    """Generate all action recommendations grouped by tab."""
    return {
        "Municipality": get_municipality_actions(alert_level, drivers, top_districts),
        "Primary Care": get_primary_care_actions(alert_level, drivers, top_districts),
        "Hospitals": get_hospital_actions(alert_level, drivers, icu_strain),
    }
