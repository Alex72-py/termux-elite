import json
import os
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
MANIFEST = json.loads((ROOT / "manifest.json").read_text())
SKILLS = MANIFEST["skills"]
NAMES = {s["name"] for s in SKILLS}
IDS = [s["name"] for s in SKILLS]
RISKS = {"low", "medium", "high"}
REQUIRED_KEYS = {
    "name", "path", "description", "triggers", "required_capabilities",
    "platform", "risk_level", "related", "scripts",
}
REQUIRED_SECTIONS = [
    "## Purpose", "## When to use", "## When NOT to use", "## Decision tree",
    "## Safety", "## Verification", "## Handoffs", "## Report",
]
SCRIPTS = sorted((ROOT / "skills").glob("*/scripts/*.sh"))
SECRET_PATTERNS = [
    r"ghp_[A-Za-z0-9]{36}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"AKIA[0-9A-Z]{16}",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
]
MUTATING_PHRASES = (
    "pkg install", "apt install", "apt-get install", "pip install", "termux-setup-storage",
)
MUTATING_COMMANDS = re.compile(r"(?<![\w./-])(rm|mv|chmod|chown|sudo|pkill|kill)\s")
HOST_SPECIFIC = ("Guardian", "ARIA")
MAX_BODY_LINES = 150


def parse_frontmatter(text):
    assert text.startswith("---\n"), "missing frontmatter"
    end = text.index("\n---\n", 4)
    fields = {}
    for line in text[4:end].splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields, text[end + 5:]


def read(item):
    return parse_frontmatter((ROOT / item["path"]).read_text())


def section(body, title):
    return body.split(title, 1)[1].split("\n## ", 1)[0]


def test_manifest_basics():
    assert MANIFEST["schema_version"] == 1
    assert re.fullmatch(r"\d+\.\d+\.\d+", MANIFEST["version"])
    assert SKILLS
    assert len(NAMES) == len(SKILLS), "duplicate skill names"


@pytest.mark.parametrize("item", SKILLS, ids=IDS)
def test_manifest_entry_shape(item):
    assert REQUIRED_KEYS <= set(item), sorted(REQUIRED_KEYS - set(item))
    assert item["risk_level"] in RISKS
    assert item["triggers"] and all(isinstance(t, str) and t for t in item["triggers"])
    assert item["required_capabilities"]
    assert item["path"] == "skills/%s/SKILL.md" % item["name"]
    assert (ROOT / item["path"]).exists()


def test_every_skill_directory_is_listed():
    on_disk = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
    assert on_disk == NAMES


@pytest.mark.parametrize("item", SKILLS, ids=IDS)
def test_frontmatter_matches_manifest(item):
    fields, _ = read(item)
    assert fields["name"] == item["name"]
    assert fields["description"] == item["description"]
    assert [t.strip() for t in fields["triggers"].split(",")] == item["triggers"]
    assert fields["risk"] == item["risk_level"]


@pytest.mark.parametrize("item", SKILLS, ids=IDS)
def test_description_is_discoverable(item):
    fields, _ = read(item)
    desc = fields["description"]
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", fields["name"]) and len(fields["name"]) <= 64
    assert 150 <= len(desc) <= 1024, len(desc)
    assert "Use when" in desc or "Use for" in desc, "description must say when to use the skill"
    assert "Do NOT use" in desc, "description must say when not to use the skill"
    assert ": " not in desc and " #" not in desc, "would break YAML plain scalars"


@pytest.mark.parametrize("item", SKILLS, ids=IDS)
def test_frontmatter_is_valid_yaml(item):
    yaml = pytest.importorskip("yaml")
    text = (ROOT / item["path"]).read_text()
    end = text.index("\n---\n", 4)
    data = yaml.safe_load(text[4:end])
    assert data["name"] == item["name"]
    assert isinstance(data["description"], str)


@pytest.mark.parametrize("item", SKILLS, ids=IDS)
def test_skill_has_required_sections(item):
    _, body = read(item)
    for heading in REQUIRED_SECTIONS:
        assert heading in body, "%s missing %s" % (item["name"], heading)
    if item["risk_level"] in ("medium", "high"):
        assert "## Rollback" in body, "%s is %s risk but has no Rollback" % (item["name"], item["risk_level"])
    assert len(body.splitlines()) <= MAX_BODY_LINES


@pytest.mark.parametrize("item", SKILLS, ids=IDS)
def test_handoffs_are_real_and_match_manifest(item):
    _, body = read(item)
    found = re.findall(r"^- `([a-z0-9-]+)`", section(body, "## Handoffs"), re.M)
    assert found, "no handoffs"
    assert item["name"] not in found
    assert set(found) <= NAMES, sorted(set(found) - NAMES)
    assert sorted(found) == sorted(item["related"])


@pytest.mark.parametrize("item", SKILLS, ids=IDS)
def test_cross_references_name_real_skills(item):
    _, body = read(item)
    for ref in re.findall(r"\(see ([a-z0-9-]+)\)", body):
        assert ref in NAMES, ref


@pytest.mark.parametrize("item", SKILLS, ids=IDS)
def test_scripts_are_referenced_and_listed(item):
    _, body = read(item)
    skill_dir = (ROOT / item["path"]).parent
    on_disk = sorted(str(p.relative_to(ROOT)) for p in skill_dir.glob("scripts/*.sh"))
    assert on_disk == sorted(item["scripts"])
    referenced = set(re.findall(r"scripts/([A-Za-z0-9_.-]+\.sh)", body))
    assert referenced == {Path(p).name for p in on_disk}, "SKILL.md and scripts/ disagree"


@pytest.mark.parametrize("script", SCRIPTS, ids=[str(s.relative_to(ROOT)) for s in SCRIPTS])
def test_scripts_are_valid_read_only_and_run(script):
    text = script.read_text()
    assert text.startswith("#!"), "missing shebang"
    assert os.access(script, os.X_OK), "not executable"
    assert "set -eu" in text
    subprocess.run(["sh", "-n", str(script)], check=True)
    code = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
    for phrase in MUTATING_PHRASES:
        assert phrase not in code, "%s contains mutating phrase %r" % (script.name, phrase)
    hit = MUTATING_COMMANDS.search(code)
    assert not hit, "%s contains mutating command %r" % (script.name, hit.group(1))
    result = subprocess.run(["sh", str(script)], capture_output=True, text=True, timeout=120, cwd=str(ROOT))
    assert result.returncode == 0, result.stderr
    assert re.search(r"^\s*[a-z_]+:", result.stdout, re.M), "script printed no key: value facts"


def test_environment_script_reports_core_facts():
    out = subprocess.run(
        ["sh", str(ROOT / "skills/termux-environment/scripts/detect-environment.sh")],
        capture_output=True, text=True, check=True,
    ).stdout
    assert "architecture:" in out and "package_managers:" in out


def test_git_auth_script_redacts_credentials(tmp_path):
    script = ROOT / "skills/git-credentials/scripts/check-git-auth.sh"
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "remote", "add", "origin", "https://user:s3cr3t@example.com/x.git"], cwd=tmp_path, check=True)
    out = subprocess.run(["sh", str(script)], capture_output=True, text=True, cwd=tmp_path, check=True).stdout
    assert "s3cr3t" not in out and "<redacted>" in out


def test_network_script_rejects_odd_hostnames():
    script = ROOT / "skills/termux-network/scripts/check-network.sh"
    result = subprocess.run(["sh", str(script), "a;b"], capture_output=True, text=True)
    assert result.returncode == 2


@pytest.mark.parametrize("item", SKILLS, ids=IDS)
def test_skills_do_not_leak_host_specific_terms(item):
    text = (ROOT / item["path"]).read_text()
    for term in HOST_SPECIFIC:
        assert term not in text, term


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
