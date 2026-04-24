"""Workflow tests for FortiAnalyzer report tools."""

from unittest.mock import AsyncMock

import pytest

from fortianalyzer_mcp.utils.config import get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Clear cached settings so per-test env overrides apply."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


class TestRunAndWaitReport:
    """Tests for final report completion confirmation."""

    @pytest.mark.asyncio
    async def test_run_and_wait_report_returns_error_when_fetch_reports_failed(
        self, monkeypatch
    ):
        monkeypatch.setenv("FORTIANALYZER_HOST", "test-faz.example.com")
        monkeypatch.setenv("FORTIANALYZER_API_TOKEN", "dummy")
        monkeypatch.setenv("DEFAULT_ADOM", "root")

        from fortianalyzer_mcp.tools import report_tools

        mock_client = AsyncMock()
        mock_client.get_report_schedules = AsyncMock(return_value={"data": [{"layout-id": 1}]})
        mock_client.report_run = AsyncMock(return_value={"tid": "report-uuid-123"})
        mock_client.get_running_reports = AsyncMock(return_value={"data": []})
        mock_client.report_fetch = AsyncMock(return_value={"state": "failed", "progress": 100})

        monkeypatch.setattr(report_tools, "_get_client", lambda: mock_client)

        result = await report_tools.run_and_wait_report(layout="1", adom="root", timeout=1)

        assert result["status"] == "error"
        assert "failed" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_run_and_wait_report_confirms_success_via_fetch(self, monkeypatch):
        monkeypatch.setenv("FORTIANALYZER_HOST", "test-faz.example.com")
        monkeypatch.setenv("FORTIANALYZER_API_TOKEN", "dummy")
        monkeypatch.setenv("DEFAULT_ADOM", "root")

        from fortianalyzer_mcp.tools import report_tools

        mock_client = AsyncMock()
        mock_client.get_report_schedules = AsyncMock(return_value={"data": [{"layout-id": 1}]})
        mock_client.report_run = AsyncMock(return_value={"tid": "report-uuid-456"})
        mock_client.get_running_reports = AsyncMock(return_value={"data": []})
        mock_client.report_fetch = AsyncMock(return_value={"state": "generated", "progress": 100})

        monkeypatch.setattr(report_tools, "_get_client", lambda: mock_client)

        result = await report_tools.run_and_wait_report(layout="1", adom="root", timeout=1)

        assert result["status"] == "success"
        assert result["tid"] == "report-uuid-456"
