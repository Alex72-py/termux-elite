import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "evals"))
import route  # noqa: E402

MANIFEST = json.loads((ROOT / "manifest.json").read_text())
NAMES = [s["name"] for s in MANIFEST["skills"]]
SCENARIOS = json.loads((ROOT / "evals" / "scenarios.json").read_text())
MIN_DIRECT_HITS = 28
MIN_PARAPHRASE_HITS = 12


def test_scenarios_are_well_formed():
    ids = [s["id"] for s in SCENARIOS]
    assert len(ids) == len(set(ids))
    for s in SCENARIOS:
        assert s["kind"] in {"direct", "paraphrase"}
        assert s["expected_skill"] in NAMES
        assert s["user_says"].strip() and s["first_action"].strip()
        assert s["must_not"] and all(isinstance(x, str) and x for x in s["must_not"])


@pytest.mark.parametrize("name", NAMES)
def test_every_skill_has_direct_and_paraphrase_scenarios(name):
    kinds = {s["kind"] for s in SCENARIOS if s["expected_skill"] == name}
    assert kinds == {"direct", "paraphrase"}


def hits(kind):
    chosen = [s for s in SCENARIOS if s["kind"] == kind]
    good = [s for s in chosen if route.rank(s["user_says"], MANIFEST)[0][0] == s["expected_skill"]]
    return len(good), [s["id"] for s in chosen if s not in good]


def test_direct_scenarios_route_correctly():
    count, missed = hits("direct")
    assert count >= MIN_DIRECT_HITS, missed


def test_paraphrased_scenarios_route_correctly():
    count, missed = hits("paraphrase")
    assert count >= MIN_PARAPHRASE_HITS, missed


def test_route_cli_prints_ranking(capsys):
    assert route.main(["route.py", "termux", "battery", "status", "hangs"]) == 0
    assert capsys.readouterr().out.splitlines()
    assert route.main(["route.py"]) == 2


def test_scenarios_contain_no_secret_like_strings():
    blob = json.dumps(SCENARIOS)
    for marker in ("ghp_", "BEGIN PRIVATE KEY", "AKIA", "xoxb-"):
        assert marker not in blob
