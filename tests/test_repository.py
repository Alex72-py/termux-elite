import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_manifest_points_to_existing_skills():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    assert manifest["schema_version"] == 1
    assert manifest["skills"]
    for item in manifest["skills"]:
        path = ROOT / item["path"]
        assert path.exists(), item["name"]
        assert "## Purpose" in path.read_text()
        assert item["risk_level"] in {"low", "medium", "high"}


def test_environment_script_is_read_only_and_runs():
    script = ROOT / "skills/termux-environment/scripts/detect-environment.sh"
    assert os.access(script, os.X_OK)
    result = subprocess.run([str(script)], capture_output=True, text=True, check=True)
    assert "architecture:" in result.stdout
    assert "package_managers:" in result.stdout
