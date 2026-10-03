import os
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
DOCTOR = ROOT / "scripts" / "doctor.sh"
HELPERS = sorted((ROOT / "skills").glob("*/scripts/*.sh"))


@pytest.fixture
def sandbox(tmp_path):
    home = tmp_path / "home"
    work = tmp_path / "work"
    home.mkdir()
    work.mkdir()
    return home, work, dict(os.environ, HOME=str(home))


def doctor(sandbox, *args):
    home, work, env = sandbox
    return subprocess.run(["sh", str(DOCTOR)] + list(args), cwd=str(work), env=env,
                          capture_output=True, text=True, timeout=120)


def listing(path):
    return sorted(str(p) for p in Path(path).rglob("*"))


def test_runs_every_helper_and_exits_zero(sandbox):
    r = doctor(sandbox)
    assert r.returncode == 0, r.stderr
    headers = re.findall(r"^== (\S+): (\S+) ==$", r.stdout, re.M)
    assert sorted(h[1] for h in headers) == sorted(str(p.relative_to(ROOT)) for p in HELPERS)
    assert "(helper exited" not in r.stdout
    assert "Nothing was changed" in r.stdout


def test_environment_snapshot_comes_first(sandbox):
    r = doctor(sandbox)
    first = re.search(r"^== (\S+): ", r.stdout, re.M).group(1)
    assert first == "termux-environment"
    assert "termux_apk_release:" in r.stdout


def test_doctor_is_read_only(sandbox):
    home, work, _ = sandbox
    before = (listing(home), listing(work))
    assert doctor(sandbox).returncode == 0
    assert (listing(home), listing(work)) == before


def test_list_does_not_run_helpers(sandbox):
    r = doctor(sandbox, "--list")
    assert r.returncode == 0, r.stderr
    lines = [l for l in r.stdout.splitlines() if l]
    assert len(lines) == len(HELPERS)
    assert "platform:" not in r.stdout and "==" not in r.stdout


def test_skill_filter_limits_output(sandbox):
    r = doctor(sandbox, "--skill", "termux-network", "--skill", "termux-sshd")
    assert r.returncode == 0, r.stderr
    names = set(re.findall(r"^== (\S+): ", r.stdout, re.M))
    assert names == {"termux-network", "termux-sshd"}


@pytest.mark.parametrize("args", [["--skill", "nope"], ["--skill", "../x"], ["--skill"], ["--bogus"]])
def test_bad_input_exits_2(sandbox, args):
    assert doctor(sandbox, *args).returncode == 2


def test_help_exits_zero(sandbox):
    r = doctor(sandbox, "--help")
    assert r.returncode == 0 and "Usage:" in r.stdout


def test_doctor_is_executable():
    assert os.access(str(DOCTOR), os.X_OK)
