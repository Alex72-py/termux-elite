import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "skills" / "termux-environment" / "scripts" / "detect-environment.sh"
TERMUX_PREFIX = "/data/data/com.termux/files/usr"

pytestmark = pytest.mark.skipif(sys.platform != "linux", reason="classification tests simulate Linux hosts")


def run(tmp_path, env=None, status="TracerPid:\t0\n", os_release=None, shim=None):
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    status_file = tmp_path / "status"
    status_file.write_text(status)
    release_file = tmp_path / "os-release"
    release_file.write_text(os_release or "")
    path = "/usr/bin:/bin"
    if shim:
        bindir = tmp_path / "shim"
        bindir.mkdir(exist_ok=True)
        for name, body in shim.items():
            f = bindir / name
            f.write_text("#!/bin/sh\n" + body + "\n")
            f.chmod(0o755)
        path = "%s:%s" % (bindir, path)
    full = {"PATH": path, "HOME": str(home), "TERMUX_ELITE_PROC_STATUS": str(status_file),
            "TERMUX_ELITE_OS_RELEASE": str(release_file)}
    full.update(env or {})
    out = subprocess.run(["sh", str(SCRIPT)], env=full, capture_output=True, text=True, check=True).stdout
    facts = {}
    for line in out.splitlines():
        key, sep, value = line.partition(": ")
        if sep and not line.startswith(" "):
            facts[key] = value
    return facts


def test_native_termux(tmp_path):
    facts = run(tmp_path, env={"PREFIX": TERMUX_PREFIX, "TERMUX_VERSION": "0.118.3"})
    assert facts["environment_class"] == "termux-native"
    assert facts["libc"] == "bionic"
    assert facts["system_package_manager"] == "pkg"
    assert facts["tur_repo"] == "not-enabled"
    assert "tur-repo" in facts["hint"]


def test_proot_distro(tmp_path):
    facts = run(tmp_path, status="TracerPid:\t4242\n", os_release="ID=debian\n")
    assert facts["environment_class"] == "proot"
    assert facts["system_package_manager"] == "apt"
    assert "tur_repo" not in facts
    assert "termux-*" in facts["hint"]


def test_inherited_termux_prefix_inside_proot_is_not_native(tmp_path):
    facts = run(tmp_path, env={"PREFIX": TERMUX_PREFIX}, status="TracerPid:\t4242\n", os_release="ID=ubuntu\n")
    assert facts["environment_class"] == "proot"


def test_other_android_shell(tmp_path):
    facts = run(tmp_path, shim={"getprop": 'echo 14'})
    assert facts["environment_class"] == "android-other"
    assert facts["libc"] == "bionic"
    assert "ask" in facts["hint"]


def test_macos(tmp_path):
    facts = run(tmp_path, shim={"uname": 'case "$1" in -s) echo Darwin;; -m) echo arm64;; *) echo x;; esac'})
    assert facts["environment_class"] == "macos"
    assert facts["system_package_manager"] == "brew"
    assert "do not apply" in facts["hint"]


def test_plain_linux_is_never_termux_or_proot(tmp_path):
    facts = run(tmp_path, os_release="ID=debian\n")
    assert facts["environment_class"] in {"linux", "container", "wsl"}
    assert facts["system_package_manager"] == "apt"
    assert "tur_repo" not in facts


def test_enabled_termux_repositories_are_reported(tmp_path):
    prefix = tmp_path / "prefix"
    sources = prefix / "etc" / "apt" / "sources.list.d"
    sources.mkdir(parents=True)
    (sources / "tur.list").write_text("deb https://example.invalid tur main\n")
    facts = run(tmp_path, env={"PREFIX": str(prefix)})
    assert facts["tur_repo"] == "enabled"
    assert facts["x11_repo"] == "not-enabled"
    assert facts["root_repo"] == "not-enabled"
    assert "example.invalid" not in "".join(facts.values())


def test_externally_managed_marker_is_detected(tmp_path):
    prefix = tmp_path / "prefix"
    (prefix / "lib" / "python3.12").mkdir(parents=True)
    (prefix / "lib" / "python3.12" / "EXTERNALLY-MANAGED").write_text("[externally-managed]\n")
    facts = run(tmp_path, env={"PREFIX": str(prefix)})
    assert facts["python_externally_managed"] == "yes"


def test_helper_leaves_home_untouched(tmp_path):
    run(tmp_path, env={"PREFIX": TERMUX_PREFIX})
    assert list((tmp_path / "home").iterdir()) == []


def skill_text(name):
    return (ROOT / "skills" / name / "SKILL.md").read_text()


def test_python_skill_encodes_the_install_ladder():
    text = skill_text("python-native-build")
    for needle in ("environment_class", "python-cryptography", "tur-repo", "--system-site-packages",
                   "externally-managed-environment", "PEP 668", "pkg search python-<name>"):
        assert needle in text, needle
    ladder = text.index("Native Termux install ladder")
    assert ladder < text.index("Compile from source")
    assert "never the default" in text


def test_python_skill_does_not_recommend_breaking_system_packages():
    for line in skill_text("python-native-build").splitlines():
        if line.startswith("- With the skill:"):
            assert "--break-system-packages" not in line


def test_environment_skill_lists_every_class():
    text = skill_text("termux-environment")
    for name in ("termux-native", "proot", "android-other", "linux", "wsl", "container", "macos", "unknown"):
        assert "`%s`" % name in text, name


def test_agents_md_tells_agents_to_classify_first():
    text = (ROOT / "AGENTS.md").read_text()
    assert "environment_class" in text and "tur-repo" in text
