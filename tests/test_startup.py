"""Check the installed CLI and project discovery from a separate workspace."""

from pathlib import Path
import subprocess
import sys
from unittest.mock import AsyncMock

import pytest

from codewright.agents.loader import AgentLoader
from codewright.app import CodeWrightApp
from codewright.config import ProviderConfig, load_config
from codewright.memory.instructions import load_instructions
from codewright.skills.loader import SkillLoader


def test_installed_cli_runs_from_another_project(tmp_path):
    executable = Path(sys.executable).with_name("CodeWright")
    result = subprocess.run(
        [str(executable), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )

    assert "usage: CodeWright" in result.stdout
    assert "-p PROMPT" in result.stdout
    assert (tmp_path / ".codewright" / "debug.log").is_file()


def test_project_configuration_and_instructions_are_discovered(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "startup-test-key")
    configuration_dir = tmp_path / ".codewright"
    configuration_dir.mkdir()
    (configuration_dir / "config.local.yaml").write_text(
        "providers:\n"
        "  - name: local-test\n"
        "    protocol: anthropic\n"
        "    base_url: https://example.invalid\n"
        "    model: test-model\n",
        encoding="utf-8",
    )
    (tmp_path / "CODEWRIGHT.md").write_text(
        "Run the project's tests after editing code.", encoding="utf-8"
    )

    config = load_config()

    assert config.providers[0].name == "local-test"
    assert config.providers[0].resolve_api_key() == "startup-test-key"
    assert "Run the project's tests" in load_instructions(str(tmp_path))


def test_installed_package_can_load_builtin_resources(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))

    agents = AgentLoader(str(tmp_path)).load_all()
    skills = SkillLoader(str(tmp_path)).load_all()

    assert {"Explore", "general-purpose", "Plan"} <= agents.keys()
    assert {"commit", "review"} <= skills.keys()


@pytest.mark.asyncio
async def test_interactive_startup_in_another_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setattr("codewright.app.resolve_context_window", AsyncMock())
    provider = ProviderConfig(
        name="startup-test",
        protocol="anthropic",
        base_url="https://example.invalid",
        model="test-model",
        api_key="startup-test-key",
    )
    app = CodeWrightApp(providers=[provider])

    async with app.run_test(size=(100, 35)) as pilot:
        await pilot.pause()

        assert app.agent is not None
        assert app.agent.work_dir == str(tmp_path)
        assert app.TITLE == "CodeWright"
        assert (tmp_path / ".codewright").is_dir()
