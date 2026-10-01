import json
import os
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
MANIFEST = json.loads((ROOT / "manifest.json").read_text())
SKILLS = MANIFEST["skills"]
RISKS = {"low", "medium", "high"}
REQUIRED_KEYS = {
    "name",
    "path",
    "description",
    "triggers",
    "required_capabilities",
    "platform",
    "risk_level",
}
SCRIPTS = sorted((ROOT / "skills").glob("*/scripts/*.sh"))
SECRET_PATTERNS = [
    r"ghp_[A-Za-z0-9]{36}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"AKIA[0-9A-Z]{16}",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
]
MUTATING = ("rm ", "pkg install", "apt install", "apt-get install", "pip install", "chmod ", "termux-setup-storage")


def parse_frontmatter(text):
    assert text.startswith("---\n"), "missing frontmatter"
    end = text.index("\n---\n", 4)
    fields = {}
    for line in text[4:end].splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields, text[end + 5:]


def test_manifest_points_to_existing_skills():
    assert MANIFEST["schema_version"] == 1
    assert SKILLS
    for item in SKILLS:
        path = ROOT / item["path"]
        assert path.exists(), item["name"]
        assert "## Purpose" in path.read_text()
        assert item["risk_level"] in RISKS


@pytest.mark.parametrize("item", SKILLS, ids=[s["name"] for s in SKILLS])
def test_manifest_entry_shape(item):
    assert REQUIRED_KEYS <= set(item), sorted(REQUIRED_KEYS - set(item))
    assert item["triggers"] and all(isinstance(t, str) and t for t in item["triggers"])
    assert item["required_capabilities"]
    assert item["path"] == "skills/%s/SKILL.md" % item["name"]


def test_skill_names_are_unique():
    names = [s["name"] for s in SKILLS]
    assert len(names) == len(set(names))


def test_every_skill_directory_is_listed():
    on_disk = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
    assert on_disk == {s["name"] for s in SKILLS}


@pytest.mark.parametrize("item", SKILLS, ids=[s["name"] for s in SKILLS])
def test_frontmatter_matches_manifest(item):
    fields, _ = parse_frontmatter((ROOT / item["path"]).read_text())
    assert fields["name"] == item["name"]
    assert fields["description"] == item["description"]
    assert [t.strip() for t in fields["triggers"].split(",")] == item["triggers"]
    assert fields["risk"] == item["risk_level"]


@pytest.mark.parametrize("item", SKILLS, ids=[s["name"] for s in SKILLS])
def test_skill_has_required_sections(item):
    _, body = parse_frontmatter((ROOT / item["path"]).read_text())
    assert "## Purpose" in body
    assert "## Decision tree" in body
    assert any(h in body for h in ("## Safety", "## Verification", "## Rollback"))


def test_environment_script_is_read_only_and_runs():
    script = ROOT / "skills/termux-environment/scripts/detect-environment.sh"
    assert os.access(script, os.X_OK)
    result = subprocess.run([str(script)], capture_output=True, text=True, check=True)
    assert "architecture:" in result.stdout
    assert "package_managers:" in result.stdout


@pytest.mark.parametrize("script", SCRIPTS, ids=[str(s.relative_to(ROOT)) for s in SCRIPTS])
def test_scripts_are_valid_and_read_only(script):
    text = script.read_text()
    assert text.startswith("#!"), "missing shebang"
    subprocess.run(["sh", "-n", str(script)], check=True)
    for fragment in MUTATING:
        assert fragment not in text, "%s contains mutating command: %s" % (script.name, fragment)
    subprocess.run(["sh", str(script)], capture_output=True, text=True, check=True)


def test_no_obvious_secrets_committed():
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.relative_to(ROOT).parts:
            continue
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            assert not re.search(pattern, text), "%s matches %s" % (path.relative_to(ROOT), pattern)
