import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sync_hosts  # noqa: E402

MANIFEST = json.loads((ROOT / "manifest.json").read_text())
NAMES = [s["name"] for s in MANIFEST["skills"]]
INSTALL = ROOT / "scripts" / "install.sh"
MARKER = ".termux-elite-managed"

# host -> (user destination under HOME, project destination under the project dir)
HOSTS = {
    "claude": (".claude/skills", ".claude/skills"),
    "opencode": (".config/opencode/skills", ".opencode/skills"),
    "gemini": (".gemini/skills", ".gemini/skills"),
    "agy": (".gemini/config/skills", ".agents/skills"),
    "agents": (".agents/skills", ".agents/skills"),
    "kiro": (".kiro/skills", ".kiro/skills"),
}
MATRIX = [(h, s) for h in HOSTS for s in ("user", "project")]
MATRIX_IDS = ["%s-%s" % m for m in MATRIX]


@pytest.fixture
def sandbox(tmp_path):
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    env = dict(os.environ, HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"))
    return home, project, env


def run_install(sandbox, *args):
    home, project, env = sandbox
    return subprocess.run(
        ["sh", str(INSTALL)] + list(args),
        cwd=str(project), env=env, capture_output=True, text=True, timeout=60,
    )


def dest_for(sandbox, host, scope):
    home, project, _ = sandbox
    user_rel, project_rel = HOSTS[host]
    return (home / user_rel) if scope == "user" else (project / project_rel)


def scope_args(scope):
    return ["--project"] if scope == "project" else []


def tree_files(path):
    return sorted(str(p) for p in Path(path).rglob("*"))


# --- generated files --------------------------------------------------------

def test_generated_files_match_render():
    for rel, text in sync_hosts.render().items():
        assert (ROOT / rel).read_text() == text, "stale generated file: " + rel


def test_sync_check_passes_on_clean_repo():
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_hosts.py"), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_sync_check_detects_drift(tmp_path):
    copy = tmp_path / "repo"
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
    (copy / "AGENTS.md").write_text("tampered\n")
    r = subprocess.run([sys.executable, str(copy / "scripts" / "sync_hosts.py"), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 1
    assert "stale: AGENTS.md" in r.stdout


def test_sync_writes_files_when_missing(tmp_path):
    copy = tmp_path / "repo"
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
    (copy / "gemini-extension.json").unlink()
    script = str(copy / "scripts" / "sync_hosts.py")
    assert subprocess.run([sys.executable, script, "--check"], capture_output=True).returncode == 1
    assert subprocess.run([sys.executable, script], capture_output=True).returncode == 0
    assert subprocess.run([sys.executable, script, "--check"], capture_output=True).returncode == 0


JSON_FILES = [p for p in sync_hosts.render() if p.endswith(".json")]


@pytest.mark.parametrize("rel", JSON_FILES)
def test_manifest_has_name_and_version(rel):
    data = json.loads((ROOT / rel).read_text())
    entry = data["plugins"][0] if "plugins" in data else data
    assert entry["name"] == MANIFEST["name"]
    assert entry["version"] == MANIFEST["version"]


def test_agents_md_lists_every_skill():
    text = (ROOT / "AGENTS.md").read_text()
    for name in NAMES:
        assert "`%s`" % name in text, name + " missing from AGENTS.md"


# --- installer --------------------------------------------------------------

@pytest.mark.parametrize("host,scope", MATRIX, ids=MATRIX_IDS)
def test_install_creates_every_skill_with_marker(sandbox, host, scope):
    r = run_install(sandbox, host, *scope_args(scope))
    assert r.returncode == 0, r.stderr
    dest = dest_for(sandbox, host, scope)
    for name in NAMES:
        assert (dest / name / "SKILL.md").is_file(), name
        assert (dest / name / MARKER).is_file(), name
    assert "%d skill(s) install" % len(NAMES) in r.stdout


def test_install_does_not_pollute_repo(sandbox):
    run_install(sandbox, "claude")
    for name in NAMES:
        assert not (ROOT / "skills" / name / MARKER).exists()


@pytest.mark.parametrize("host,scope", MATRIX, ids=MATRIX_IDS)
def test_dry_run_changes_nothing(sandbox, host, scope):
    home, project, _ = sandbox
    r = run_install(sandbox, host, "--dry-run", *scope_args(scope))
    assert r.returncode == 0, r.stderr
    assert tree_files(home) == [] and tree_files(project) == []
    assert "would:" in r.stdout


def test_link_creates_symlinks_to_repo(sandbox):
    r = run_install(sandbox, "claude", "--link")
    assert r.returncode == 0, r.stderr
    dest = dest_for(sandbox, "claude", "user")
    for name in NAMES:
        target = dest / name
        assert target.is_symlink(), name
        assert Path(os.readlink(str(target))).resolve() == (ROOT / "skills" / name).resolve()
        assert (target / "SKILL.md").is_file()
        assert not (ROOT / "skills" / name / MARKER).exists()


def test_reinstall_is_idempotent(sandbox):
    assert run_install(sandbox, "agents").returncode == 0
    r = run_install(sandbox, "agents")
    assert r.returncode == 0, r.stderr
    assert "0 skipped" in r.stdout
    dest = dest_for(sandbox, "agents", "user")
    for name in NAMES:
        assert (dest / name / MARKER).is_file()


def test_reinstall_refreshes_managed_copy(sandbox):
    run_install(sandbox, "agents")
    dest = dest_for(sandbox, "agents", "user")
    stale = dest / NAMES[0] / "stale.txt"
    stale.write_text("old")
    assert run_install(sandbox, "agents").returncode == 0
    assert not stale.exists()


def test_copy_to_link_switch_on_managed_install(sandbox):
    run_install(sandbox, "agents")
    r = run_install(sandbox, "agents", "--link")
    assert r.returncode == 0, r.stderr
    dest = dest_for(sandbox, "agents", "user")
    assert all((dest / n).is_symlink() for n in NAMES)


def test_foreign_skill_is_never_overwritten(sandbox):
    dest = dest_for(sandbox, "claude", "user")
    foreign = dest / NAMES[0]
    foreign.mkdir(parents=True)
    (foreign / "SKILL.md").write_text("mine")
    r = run_install(sandbox, "claude")
    assert r.returncode == 0, r.stderr
    assert (foreign / "SKILL.md").read_text() == "mine"
    assert not (foreign / MARKER).exists()
    assert "skip %s" % NAMES[0] in r.stdout
    assert "1 skipped" in r.stdout
    for name in NAMES[1:]:
        assert (dest / name / MARKER).is_file()


def test_foreign_symlink_is_never_replaced(sandbox, tmp_path):
    dest = dest_for(sandbox, "claude", "user")
    dest.mkdir(parents=True)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (dest / NAMES[0]).symlink_to(elsewhere)
    r = run_install(sandbox, "claude", "--link")
    assert r.returncode == 0, r.stderr
    assert os.readlink(str(dest / NAMES[0])) == str(elsewhere)
    assert elsewhere.is_dir()


@pytest.mark.parametrize("mode", [[], ["--link"]], ids=["copy", "link"])
def test_uninstall_removes_only_managed_skills(sandbox, mode):
    dest = dest_for(sandbox, "opencode", "user")
    foreign = dest / NAMES[0]
    foreign.mkdir(parents=True)
    (foreign / "SKILL.md").write_text("mine")
    run_install(sandbox, "opencode", *mode)
    r = run_install(sandbox, "opencode", "--uninstall")
    assert r.returncode == 0, r.stderr
    assert (foreign / "SKILL.md").read_text() == "mine"
    for name in NAMES[1:]:
        assert not (dest / name).exists() and not (dest / name).is_symlink()
    for name in NAMES:
        assert (ROOT / "skills" / name / "SKILL.md").is_file()


def test_uninstall_dry_run_changes_nothing(sandbox):
    run_install(sandbox, "kiro")
    dest = dest_for(sandbox, "kiro", "user")
    before = tree_files(dest)
    r = run_install(sandbox, "kiro", "--uninstall", "--dry-run")
    assert r.returncode == 0, r.stderr
    assert tree_files(dest) == before


def test_uninstall_with_nothing_installed_is_clean(sandbox):
    r = run_install(sandbox, "gemini", "--uninstall")
    assert r.returncode == 0, r.stderr
    assert "0 skill(s) uninstall" in r.stdout


def test_skill_filter_installs_only_named_skills(sandbox):
    picked = NAMES[:2]
    args = ["claude"]
    for name in picked:
        args += ["--skill", name]
    r = run_install(sandbox, *args)
    assert r.returncode == 0, r.stderr
    dest = dest_for(sandbox, "claude", "user")
    assert sorted(p.name for p in dest.iterdir()) == sorted(picked)


def test_skill_filter_limits_uninstall(sandbox):
    run_install(sandbox, "claude")
    run_install(sandbox, "claude", "--uninstall", "--skill", NAMES[0])
    dest = dest_for(sandbox, "claude", "user")
    assert not (dest / NAMES[0]).exists()
    assert all((dest / n).exists() for n in NAMES[1:])


def test_unknown_skill_exits_2_and_writes_nothing(sandbox):
    home, project, _ = sandbox
    r = run_install(sandbox, "claude", "--skill", "no-such-skill")
    assert r.returncode == 2
    assert "unknown skill" in r.stderr
    assert tree_files(home) == [] and tree_files(project) == []


def test_unknown_host_exits_2(sandbox):
    r = run_install(sandbox, "emacs")
    assert r.returncode == 2
    assert "unknown host" in r.stderr


def test_missing_host_exits_2(sandbox):
    assert run_install(sandbox).returncode == 2


def test_unknown_option_exits_2(sandbox):
    assert run_install(sandbox, "claude", "--bogus").returncode == 2


def test_extra_argument_exits_2(sandbox):
    assert run_install(sandbox, "claude", "kiro").returncode == 2


def test_skill_option_without_name_exits_2(sandbox):
    assert run_install(sandbox, "claude", "--skill").returncode == 2


def test_help_exits_0(sandbox):
    r = run_install(sandbox, "--help")
    assert r.returncode == 0
    assert "Usage:" in r.stdout


# --- repository hygiene -----------------------------------------------------

def test_no_legacy_wording_outside_tests():
    pattern = re.compile(r"\bARIA\b|Guardian")
    skip = {".git", "tests", "__pycache__", ".pytest_cache"}
    hits = []
    for base, dirs, files in os.walk(str(ROOT)):
        dirs[:] = [d for d in dirs if d not in skip]
        for f in files:
            if not f.endswith((".md", ".py", ".sh", ".json", ".yml", ".yaml", ".txt")):
                continue
            p = Path(base) / f
            if pattern.search(p.read_text(errors="ignore")):
                hits.append(str(p.relative_to(ROOT)))
    assert hits == []


ADAPTERS = {
    "adapters/claude-code/README.md": ["/plugin marketplace add Alex72-py/termux-elite", "sh scripts/install.sh claude"],
    "adapters/gemini-cli/README.md": ["gemini skills install", "gemini extensions install", "sh scripts/install.sh gemini"],
    "adapters/antigravity/README.md": ["agy plugin install", "sh scripts/install.sh agy"],
    "adapters/opencode/README.md": ["sh scripts/install.sh opencode"],
    "adapters/generic/README.md": ["codex plugin", "/add-plugin", "sh scripts/install.sh kiro", "sh scripts/install.sh agents"],
}


@pytest.mark.parametrize("rel", sorted(ADAPTERS))
def test_adapter_readme_has_install_commands(rel):
    path = ROOT / rel
    assert path.is_file(), rel
    text = path.read_text()
    for command in ADAPTERS[rel]:
        assert command in text, "%s missing %r" % (rel, command)


def test_documented_installer_hosts_exist():
    docs = [ROOT / "README.md"] + [ROOT / rel for rel in ADAPTERS]
    for path in docs:
        for host in re.findall(r"scripts/install\.sh ([a-z]+)", path.read_text()):
            assert host in HOSTS, "%s documents unknown host %s" % (path.name, host)


def test_every_installer_host_is_documented():
    text = "\n".join((ROOT / rel).read_text() for rel in ADAPTERS)
    for host in HOSTS:
        assert "scripts/install.sh %s" % host in text, host
