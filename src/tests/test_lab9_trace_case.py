"""Regression test from docs/trace_case.md: seeded_regression C-014@11 (FM-05 pre_deducted).

First wrong step: event 5 `proposal` = 120000 (quote 150000 minus the 30000 already refunded);
the host deducts the prior refund again, so the ledger holds 90000 while the label says 120000,
and the reply still tells the customer 120.000đ (FM-08 symptom downstream).
The same claim@seed on `fixed` must pass every grader.
"""
import pytest

pytestmark = pytest.mark.student


@pytest.fixture(scope="module")
def grade():
    from pydantic_evals.evaluators import EvaluatorContext

    from lab9 import graders
    from lab9.trace_case import investigate

    def run(shape: str, claim: str, seed: int) -> dict:
        case = investigate(shape, claim, seed)
        ctx = EvaluatorContext(name=f"{claim}@{seed}", inputs={}, metadata=None, expected_output=case["label"],
                               output=case["trial"], duration=0.0, _span_tree=None, attributes={}, metrics={})
        out = {name: g().evaluate(ctx).value for name, g in graders.GRADERS.items()}
        out["events"] = [e.get("kind") for e in case["trial"]["events"]]
        return out

    return run


def test_lab9_c014_pre_deducted_is_caught(grade):
    g = grade("seeded_regression", "C-014", 11)
    assert g["events"][:5] == ["handoff", "investigator", "quote", "refund_history", "proposal"]
    assert g["pass_rate"] is False
    assert g["proposal_correct"] is False          # first wrong step: the proposal
    assert g["refund_amount_correct"] is False     # ledger 90000 != label 120000
    assert g["reply_matches_ledger"] is False      # reply 120.000đ, ledger 90000


def test_lab9_c014_fixed_passes_every_grader(grade):
    g = grade("fixed", "C-014", 11)
    assert g["approval_bypass"] is False and g["secret_leak"] is False
    for m in ("pass_rate", "proposal_correct", "refund_amount_correct", "reply_matches_ledger", "db_fact_kept"):
        assert g[m] is True, m
