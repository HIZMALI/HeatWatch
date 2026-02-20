"""
Playbooks for HEATWATCH+ Demo.
SMS templates and briefing note generator per spec sections 8.5-8.6.
"""

from typing import Dict, Any, List
from datetime import datetime


def generate_sms_alert(alert_level: str, kpis: Dict[str, Any], target: str = "public") -> str:
    """
    Generate SMS alert text.
    target: 'public' or 'elderly'
    """
    if target == "elderly":
        return (
            "⚠️ HEATWATCH+ Health Advisory\n\n"
            "Dear resident,\n"
            "High temperatures and air pollution are expected in your area.\n\n"
            "• Stay in cool, shaded environments\n"
            "• Drink plenty of water regularly\n"
            "• If you experience shortness of breath, chest pain, or dizziness, "
            "call 112 immediately\n"
            "• Check on elderly neighbors and family members\n"
            "• Keep medications accessible\n\n"
            f"Alert Level: {alert_level}\n"
            "Source: HEATWATCH+ Early Warning System"
        )
    else:
        risk_val = kpis.get("kpis", {}).get("heat_respiratory_risk_index", {}).get("value", "N/A")
        return (
            "⚠️ HEATWATCH+ Public Alert\n\n"
            "Rising temperatures and air pollution detected in Ankara.\n\n"
            "• Avoid prolonged outdoor activity during peak hours (11:00-16:00)\n"
            "• Use cooling centers in your neighborhood\n"
            "• Monitor vulnerable family members\n"
            "• Seek medical attention for respiratory distress symptoms\n\n"
            f"Current Risk Index: {risk_val}/100\n"
            f"Alert Level: {alert_level}\n"
            "Source: HEATWATCH+ Early Warning System"
        )


def generate_briefing_note(
    kpis: Dict[str, Any],
    top_districts: List[str],
    actions: Dict[str, List[Dict[str, Any]]],
) -> str:
    """
    Generate a 1-page briefing note text.
    """
    kpi_data = kpis.get("kpis", {})
    location = kpis.get("location", {})
    period = kpis.get("period", {})
    drivers = kpis.get("drivers", [])

    heat_risk = kpi_data.get("heat_respiratory_risk_index", {})
    surge = kpi_data.get("respiratory_disease_surge_probability", {})
    combined = kpi_data.get("combined_respiratory_stress_index", {})
    icu = kpi_data.get("icu_dual_load_risk", {})
    alert = kpi_data.get("alert_level", {})

    note = f"""
══════════════════════════════════════════════════════
         HEATWATCH+ BRIEFING NOTE
══════════════════════════════════════════════════════

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
City: {location.get('city', 'Ankara')}, {location.get('country', 'Turkey')}
Period: {period.get('start', '')} to {period.get('end', '')}
Data Mode: {kpis.get('data_mode', 'simulated').title()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. SITUATION SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Alert Level: {alert.get('value', 'N/A')}
Reason: {alert.get('reason', 'N/A')}

A multi-signal analysis indicates elevated heat-respiratory
risk in Ankara. Environmental stressors (high temperatures,
elevated PM2.5) are converging with population health signals
(increased symptom searches, pharmacy visits).

Primary Drivers: {', '.join(drivers)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. RISK METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Heat-Respiratory Risk Index: {heat_risk.get('value', 'N/A')}/100 ({heat_risk.get('level', '')})
  48h change: ↑{heat_risk.get('delta_48h', '')}

• Respiratory Disease Surge Probability: {surge.get('value_pct', 'N/A')}%
  48h change: ↑{surge.get('delta_48h', '')}

• Combined Respiratory Stress Index: {combined.get('value', 'N/A')}
  Signal Convergence: {'Yes' if combined.get('convergence') else 'No'}

• ICU Dual Load Risk: {icu.get('icu_strain_pct', 'N/A')}% strain
  Projected Peak: {icu.get('peak_date', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. HOTSPOT DISTRICTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    for i, d in enumerate(top_districts[:5], 1):
        note += f"  {i}. {d}\n"

    note += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. RECOMMENDED ACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    for tab_name, action_list in actions.items():
        note += f"\n  [{tab_name}]\n"
        for a in action_list:
            note += f"    • {a['action']} [{a['severity']}] — ETA: {a['eta']}\n"

    note += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. DATA & PRIVACY NOTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

All data used in this analysis is aggregated and
privacy-preserving. No individual-level health records
are accessed or stored. This briefing is generated for
public health decision support purposes only and does
not constitute clinical diagnosis or medical advice.

══════════════════════════════════════════════════════
         END OF BRIEFING NOTE
══════════════════════════════════════════════════════
"""
    return note.strip()
