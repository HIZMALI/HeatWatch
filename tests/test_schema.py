"""
Tests for data schema validation.
"""

import json
import os
import sys
import pytest

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.validators import validate_kpi_json, validate_env_timeseries, validate_micro_signals, validate_vulnerability
from src.data.loaders import load_kpis, load_env_timeseries, load_micro_signals, load_vulnerability


class TestKPISchema:
    """Test KPI JSON schema."""

    def test_kpi_json_has_all_top_level_keys(self):
        kpis = load_kpis()
        errors = validate_kpi_json(kpis)
        assert len(errors) == 0, f"Validation errors: {errors}"

    def test_kpi_json_has_location(self):
        kpis = load_kpis()
        assert "location" in kpis
        assert kpis["location"]["city"] == "Ankara"
        assert kpis["location"]["country"] == "Turkey"

    def test_kpi_json_has_period(self):
        kpis = load_kpis()
        assert "period" in kpis
        assert "start" in kpis["period"]
        assert "end" in kpis["period"]
        assert "forecast_days" in kpis["period"]

    def test_kpi_json_has_all_kpi_fields(self):
        kpis = load_kpis()
        kpi_data = kpis["kpis"]
        assert "heat_respiratory_risk_index" in kpi_data
        assert "respiratory_disease_surge_probability" in kpi_data
        assert "combined_respiratory_stress_index" in kpi_data
        assert "icu_dual_load_risk" in kpi_data
        assert "alert_level" in kpi_data

    def test_heat_respiratory_risk_has_required_fields(self):
        kpis = load_kpis()
        hr = kpis["kpis"]["heat_respiratory_risk_index"]
        assert "value" in hr
        assert "level" in hr
        assert "delta_48h" in hr

    def test_surge_probability_has_subtitle(self):
        kpis = load_kpis()
        sp = kpis["kpis"]["respiratory_disease_surge_probability"]
        assert "subtitle" in sp
        assert "COPD" in sp["subtitle"]

    def test_drivers_is_list(self):
        kpis = load_kpis()
        assert isinstance(kpis["drivers"], list)
        assert len(kpis["drivers"]) > 0


class TestEnvTimeseriesSchema:
    """Test environmental timeseries CSV."""

    def test_env_csv_has_all_columns(self):
        df = load_env_timeseries()
        errors = validate_env_timeseries(df)
        assert len(errors) == 0, f"Validation errors: {errors}"

    def test_env_csv_has_24_days(self):
        df = load_env_timeseries()
        assert len(df) == 24


class TestMicroSignalsSchema:
    """Test micro signals CSV."""

    def test_micro_csv_has_all_columns(self):
        df = load_micro_signals()
        errors = validate_micro_signals(df)
        assert len(errors) == 0, f"Validation errors: {errors}"

    def test_micro_csv_has_24_days(self):
        df = load_micro_signals()
        assert len(df) == 24


class TestVulnerabilitySchema:
    """Test vulnerability CSV."""

    def test_vuln_csv_has_all_columns(self):
        df = load_vulnerability()
        errors = validate_vulnerability(df)
        assert len(errors) == 0, f"Validation errors: {errors}"

    def test_vuln_csv_has_10_districts(self):
        df = load_vulnerability()
        assert len(df) == 10
