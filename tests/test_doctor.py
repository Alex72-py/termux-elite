import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
DOCTOR = ROOT / "scripts" / "doctor.sh"
SCRIPTS = sorted((ROOT / "skills").glob("*/scripts/*.sh"))
FIRST = "skills/termux-environment/scripts/detect-environment.sh"


def run_doctor(*args, home=None, root=None):
    script = (root or ROOT) / "scripts" / "doctor.sh"
    env = dict(os.environ)
    if home is not None:
        env["HOME"] = str(home)
    return subprocess.run(["sh", str(script)] + list(args), cwd=str(home or ROOT),
                          env=env, capture_output=True, text=True, timeout=120)


def headers(stdout):
    return [l[3:-3] for l in stdout.splitlines() if l.startswith("== ") and l.endswith(" ==")]


def test_runs_every_helper_with_environment_first(tmp_path):
    r = run_doctor(home=tmp_path)
    assert r.returncode == 0, r.stderr
    found = headers(r.stdout)
    assert found[0] == FIRST
    assert sorted(found) == sorted(str(s.relative_to(ROOT)) for s in SCRIPTS)
    assert "platform:" in r.stdout
    assert "Done." in r.stdout


def test_list_names_helpers_without_running_them(tmp_path):
    r = run_doctor("--list", home=tmp_path)
    assert r.returncode == 0, r.stderr
    lines = r.stdout.split()
    assert lines[0] == FIRST
    assert len(lines) == len(SCRIPTS)
    assert "platform:" not in r.stdout


def test_skill_filter(tmp_path):
    r = run_doctor("--skill", "termux-network", home=tmp_path)
    assert r.returncode == 0, r.stderr
    assert headers(r.stdout) == ["skills/termux-network/scripts/check-network.sh"]


def test_skill_without_helper_prints_nothing_to_run(tmp_path):
    r = run_doctor("--skill", "github-actions", home=tmp_path)
    assert r.returncode == 0, r.stderr
    assert headers(r.stdout) == []


@pytest.mark.parametrize("args", [["--skill", "nope"], ["--skill", "../etc"], ["--skill", ".hidden"],
                                  ["--skill", ""], ["--skill"], ["--bogus"]])
def test_bad_arguments_exit_2(args, tmp_path):
    assert run_doctor(*args, home=tmp_path).returncode == 2


def test_help_exits_0(tmp_path):
    r = run_doctor("--help", home=tmp_path)
    assert r.returncode == 0 and "Usage:" in r.stdout


def test_doctor_does_not_change_the_filesystem(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    before = sorted(str(p) for p in home.rglob("*"))
    assert run_doctor(home=home).returncode == 0
    assert sorted(str(p) for p in home.rglob("*")) == before


def test_failing_helper_is_reported_and_does_not_stop_the_run(tmp_path):
    copy = tmp_path / "repo"
    shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
    (copy / "skills" / "termux-network" / "scripts" / "check-network.sh").write_text("#!/usr/bin/env sh\nexit 3\n")
    home = tmp_path / "home"
    home.mkdir()
    r = run_doctor(home=home, root=copy)
    assert r.returncode == 0, r.stderr
    assert "helper exited with status 3" in r.stdout
    assert "Done." in r.stdout
    assert len(headers(r.stdout)) == len(SCRIPTS)


@pytest.mark.parametrize("script", SCRIPTS, ids=[str(s.relative_to(ROOT)) for s in SCRIPTS])
def test_each_helper_leaves_home_untouched(script, tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    env = dict(os.environ, HOME=str(home))
    subprocess.run(["sh", str(script)], cwd=str(tmp_path), env=env,
                   capture_output=True, text=True, timeout=60)
    assert sorted(str(p) for p in home.rglob("*")) == [], "%s wrote under HOME" % script.name
