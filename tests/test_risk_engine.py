"""
Tests for risk engine calculations.
"""

import os
import sys
import pytest

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.risk_engine import (
    compute_heat_score,
    compute_pollution_score,
    compute_micro_signal_score,
    compute_heat_respiratory_risk_index,
    compute_respiratory_surge_probability,
    compute_combined_stress,
    compute_icu_strain,
    compute_alert_level,
    identify_drivers,
    compute_all_kpis,
)
from src.data.loaders import load_env_timeseries, load_micro_signals, load_vulnerability


class TestHeatScore:
    """Test heat score computation."""

    def test_heat_score_in_range(self):
        score = compute_heat_score(35, 22)
        assert 0 <= score <= 100

    def test_heat_score_increases_with_temp(self):
        low = compute_heat_score(25, 15)
        high = compute_heat_score(40, 28)
        assert high > low

    def test_heat_score_nighttime_weight(self):
        # Higher nighttime temp should increase score
        low_night = compute_heat_score(35, 15)
        high_night = compute_heat_score(35, 28)
        assert high_night > low_night


class TestPollutionScore:
    """Test pollution score computation."""

    def test_pollution_score_in_range(self):
        score = compute_pollution_score(50)
        assert 0 <= score <= 100

    def test_pollution_score_increases_with_pm25(self):
        low = compute_pollution_score(15)
        high = compute_pollution_score(70)
        assert high > low


class TestMicroSignalScore:
    """Test micro signal score computation."""

    def test_micro_signal_in_range(self):
        score = compute_micro_signal_score(50, 50, 50)
        assert 0 <= score <= 100

    def test_micro_signal_weighted(self):
        # Search has highest weight (0.4)
        high_search = compute_micro_signal_score(100, 0, 0)
        high_pharmacy = compute_micro_signal_score(0, 100, 0)
        assert high_search > high_pharmacy


class TestHeatRespiratoryRiskIndex:
    """Test heat-respiratory risk index."""

    def test_risk_index_in_range(self):
        risk = compute_heat_respiratory_risk_index(50, 50, 50, 50)
        assert 0 <= risk <= 100

    def test_risk_index_all_high(self):
        risk = compute_heat_respiratory_risk_index(100, 100, 100, 100)
        assert risk == 100

    def test_risk_index_all_low(self):
        risk = compute_heat_respiratory_risk_index(0, 0, 0, 0)
        assert risk == 0


class TestSurgeProbability:
    """Test respiratory surge probability."""

    def test_surge_prob_in_range(self):
        prob = compute_respiratory_surge_probability(50, 50, 22)
        assert 0 <= prob <= 100

    def test_surge_prob_increases_with_inputs(self):
        low = compute_respiratory_surge_probability(20, 20, 15)
        high = compute_respiratory_surge_probability(80, 70, 28)
        assert high > low


class TestCombinedStress:
    """Test combined respiratory stress index."""

    def test_combined_in_range(self):
        combined = compute_combined_stress(80, 70)
        assert 0 <= combined <= 1.0

    def test_combined_weights(self):
        # HeatResp has higher weight (0.6)
        combined = compute_combined_stress(100, 0)
        assert combined == 0.6


class TestICUStrain:
    """Test ICU strain computation."""

    def test_icu_strain_in_range(self):
        strain = compute_icu_strain(80, 70)
        assert 0 <= strain <= 40

    def test_icu_strain_increases_with_risk(self):
        low = compute_icu_strain(10, 10)
        high = compute_icu_strain(80, 70)
        assert high > low


class TestAlertLevel:
    """Test alert level determination."""

    def test_emergency_level(self):
        result = compute_alert_level(90, 75, 0.9, 35)
        assert result["value"] == "EMERGENCY"

    def test_warning_level(self):
        result = compute_alert_level(72, 50, 0.67, 15)
        assert result["value"] == "WARNING"

    def test_watch_level(self):
        result = compute_alert_level(60, 30, 0.45, 10)
        assert result["value"] == "WATCH"

    def test_alert_has_reason(self):
        result = compute_alert_level(90, 75, 0.9, 35)
        assert "reason" in result
        assert len(result["reason"]) > 0


class TestComputeAllKPIs:
    """Test full KPI computation pipeline."""

    def test_all_kpis_structure(self):
        df_env = load_env_timeseries()
        df_micro = load_micro_signals()
        df_vuln = load_vulnerability()

        kpis = compute_all_kpis(df_env, df_micro, df_vuln)

        assert "location" in kpis
        assert "period" in kpis
        assert "kpis" in kpis
        assert "drivers" in kpis

        kpi_data = kpis["kpis"]
        assert 0 <= kpi_data["heat_respiratory_risk_index"]["value"] <= 100
        assert 0 <= kpi_data["respiratory_disease_surge_probability"]["value_pct"] <= 100
        assert 0 <= kpi_data["combined_respiratory_stress_index"]["value"] <= 1.0
        assert 0 <= kpi_data["icu_dual_load_risk"]["icu_strain_pct"] <= 40
        assert kpi_data["alert_level"]["value"] in ["WATCH", "WARNING", "EMERGENCY"]
