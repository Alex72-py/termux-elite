import json
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parents[1]
MANIFEST = json.loads((ROOT / "manifest.json").read_text())
NAMES = [s["name"] for s in MANIFEST["skills"]]
README = (ROOT / "README.md").read_text()
FORMS = sorted((ROOT / ".github" / "ISSUE_TEMPLATE").glob("*.yml"))
FORM_IDS = [f.name for f in FORMS]


def test_readme_has_one_line_install():
    assert "npx skills add Alex72-py/termux-elite" in README


@pytest.mark.parametrize("name", NAMES)
def test_readme_links_every_skill(name):
    assert "[`%s`](skills/%s/SKILL.md)" % (name, name) in README


def test_readme_skill_count_matches_manifest():
    badge = re.search(r"badge/skills-(\d+)-", README)
    prose = re.search(r"(\d+) short, tested playbooks", README)
    assert badge and prose
    assert int(badge.group(1)) == len(NAMES)
    assert int(prose.group(1)) == len(NAMES)


def test_readme_relative_links_resolve():
    for target in re.findall(r"\]\(([^)]+)\)", README):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        path = target.split("#")[0]
        assert (ROOT / path).exists(), "broken README link: " + target


def test_readme_does_not_document_removed_hosts():
    for host in re.findall(r"scripts/install\.sh ([a-z]+)", README):
        assert host in {"claude", "opencode", "gemini", "agy", "agents", "kiro"}, host


@pytest.mark.parametrize("form", FORMS, ids=FORM_IDS)
def test_issue_forms_are_valid_yaml(form):
    data = yaml.safe_load(form.read_text())
    if form.name == "config.yml":
        assert isinstance(data["blank_issues_enabled"], bool)
        assert data["contact_links"] and all("url" in c for c in data["contact_links"])
        return
    assert data["name"] and data["description"]
    ids = []
    for item in data["body"]:
        assert item["type"] in {"markdown", "textarea", "input", "dropdown", "checkboxes"}
        if item["type"] != "markdown":
            assert item["attributes"]["label"]
            ids.append(item["id"])
    assert len(ids) == len(set(ids))
    if item["type"] == "dropdown":
        assert len(item["attributes"]["options"]) >= 2


def test_failure_report_requires_environment_and_error():
    data = yaml.safe_load((ROOT / ".github" / "ISSUE_TEMPLATE" / "failure-report.yml").read_text())
    required = {i["id"] for i in data["body"] if i.get("validations", {}).get("required")}
    assert {"kind", "environment", "error"} <= required


def test_community_files_exist():
    assert (ROOT / ".github" / "pull_request_template.md").is_file()
    security = (ROOT / "SECURITY.md").read_text()
    assert "Report a vulnerability" in security


def test_changelog_top_entry_is_current():
    heading = re.search(r"^## (.+)$", (ROOT / "CHANGELOG.md").read_text(), re.M).group(1)
    assert heading == "Unreleased" or heading.startswith(MANIFEST["version"])
