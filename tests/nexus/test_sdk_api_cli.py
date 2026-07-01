"""Tests for nexus.sdk and nexus.api and nexus.cli."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from nexus.api.app import app, set_nexus
from nexus.providers.dummy import DummyProvider
from nexus.sdk import Nexus


@pytest.fixture
def nexus_instance() -> Nexus:
    return Nexus(provider=DummyProvider(responder="SDK test answer."))


class TestNexusSDK:
    def test_quickstart_creates_instance(self) -> None:
        from nexus.sdk import quickstart

        nx = quickstart()
        assert nx is not None
        assert "literature" in nx.list_agents()

    def test_interpret_returns_interpretation(self, nexus_instance: Nexus) -> None:
        result = nexus_instance.interpret("What is BRCA1?")
        assert result.answer == "SDK test answer."
        assert result.confidence.value > 0.0

    def test_interpret_unknown_agent_raises(self, nexus_instance: Nexus) -> None:
        from nexus.core.orchestrator import AgentNotRegisteredError

        with pytest.raises(AgentNotRegisteredError):
            nexus_instance.interpret("x", agent="nonexistent")

    def test_index_text_then_search(self, nexus_instance: Nexus) -> None:
        nexus_instance.index_text(
            "pubmed:1",
            "Test document",
            "This document discusses BRCA1 and DNA repair.",
        )
        results = nexus_instance.retriever.retrieve("BRCA1", limit=5)
        assert len(results) > 0
        assert results[0].document.title == "Test document"

    def test_generate_report(self, nexus_instance: Nexus) -> None:
        nexus_instance.interpret("Question 1")
        nexus_instance.interpret("Question 2")
        report = nexus_instance.generate_report("Test report")
        assert "Test report" in report.to_markdown()
        assert len(report.sections) > 0

    def test_list_agents(self, nexus_instance: Nexus) -> None:
        agents = nexus_instance.list_agents()
        assert "literature" in agents
        assert "validation" in agents
        assert "experiment" in agents
        assert "workflow" in agents
        assert "report" in agents


class TestAPI:
    @pytest.fixture
    def client(self, nexus_instance: Nexus) -> TestClient:
        set_nexus(nexus_instance)
        return TestClient(app)

    def test_health(self, client: TestClient) -> None:
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "literature" in data["agents"]

    def test_agents(self, client: TestClient) -> None:
        response = client.get("/api/agents")
        assert response.status_code == 200
        assert "literature" in response.json()

    def test_interpret(self, client: TestClient) -> None:
        response = client.post(
            "/api/interpret",
            json={"question": "What is BRCA1?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "SDK test answer."

    def test_validate(self, client: TestClient) -> None:
        response = client.post(
            "/api/validate",
            json={"claim": "BRCA1 is unrelated to DNA repair."},
        )
        assert response.status_code == 200

    def test_index_and_search(self, client: TestClient) -> None:
        client.post(
            "/api/index",
            json={
                "source_uri": "pubmed:1",
                "title": "BRCA1 paper",
                "content": "BRCA1 is involved in DNA repair.",
            },
        )
        response = client.get("/api/search", params={"q": "BRCA1", "limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert any("BRCA1" in r["title"] for r in data["results"])

    def test_report(self, client: TestClient) -> None:
        response = client.post(
            "/api/report",
            json={"title": "API report", "questions": ["What is BRCA1?"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert "API report" in data["markdown"]


class TestCLI:
    def test_version_command(self) -> None:
        from nexus.cli.main import app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Nexus Ω" in result.output

    def test_providers_command(self) -> None:
        from nexus.cli.main import app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(app, ["providers"])
        assert result.exit_code == 0
        assert "dummy" in result.output

    def test_agents_command(self) -> None:
        from nexus.cli.main import app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(app, ["agents"])
        assert result.exit_code == 0
        assert "literature" in result.output

    def test_interpret_command(self) -> None:
        from nexus.cli.main import app
        from typer.testing import CliRunner

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["interpret", "--question", "What is DNA?", "--provider", "dummy"],
        )
        assert result.exit_code == 0

    def test_index_and_search_commands(self, tmp_path: pytest.TempPathFactory) -> None:
        from nexus.cli.main import app
        from typer.testing import CliRunner

        runner = CliRunner()
        # Index a document
        result = runner.invoke(
            app,
            [
                "index",
                "--uri",
                "pubmed:1",
                "--title",
                "BRCA1 paper",
                "--content",
                "BRCA1 is involved in DNA repair.",
            ],
        )
        assert result.exit_code == 0
        # Search
        result = runner.invoke(app, ["search", "--query", "BRCA1"])
        assert result.exit_code == 0
