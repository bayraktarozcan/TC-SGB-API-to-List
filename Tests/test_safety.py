"""Tests for the publication safety policy shared by all production lines."""

from __future__ import annotations

import pytest

from Scripts.src.safety import (
    BLOCKED_EXACT,
    SHARED_APEX,
    Decision,
    SafetyRecord,
    SafetySummary,
    decide_host,
)


@pytest.mark.parametrize(
    ("host", "decision"),
    [
        ("google.com", Decision.REJECT),
        ("www.google.com", Decision.REJECT),
        ("www.linkedin.com", Decision.REJECT),
        ("gemini.google.com", Decision.REJECT),
        ("accounts.google.com", Decision.REJECT),
        ("ogs.google.com", Decision.REJECT),
        ("youtube.com", Decision.REJECT),
        ("docs.google.com", Decision.REVIEW),
        ("sites.google.com", Decision.REVIEW),
        ("drive.usercontent.google.com", Decision.REVIEW),
        ("storage.googleapis.com", Decision.REVIEW),
        ("firebasestorage.googleapis.com", Decision.REVIEW),
        ("evil-phish.com", Decision.ACCEPT),
        ("google.js.cn", Decision.ACCEPT),
        ("evil-google.com", Decision.ACCEPT),
        ("google.com.evil.example.com", Decision.ACCEPT),
        ("accounts.google.com.evil.example.com", Decision.ACCEPT),
        ("youtube.security-notifications-google.com", Decision.ACCEPT),
        ("evil.sites.google.com", Decision.ACCEPT),
        ("evil.storage.googleapis.com", Decision.ACCEPT),
        ("1.2.3.4", Decision.ACCEPT),
    ],
)
def test_policy_verdicts(host: str, decision: Decision):
    record = decide_host(host, source="test")
    assert record.decision == decision
    assert record.indicator == host
    assert record.source == "test"
    assert record.reason


def test_matching_is_exact_host_only():
    assert "google.com" in BLOCKED_EXACT
    assert "google.js.cn" not in BLOCKED_EXACT
    assert "evil-google.com" not in BLOCKED_EXACT
    assert "google.com.evil.example.com" not in BLOCKED_EXACT
    assert "docs.google.com" in SHARED_APEX
    assert "evil.sites.google.com" not in SHARED_APEX


def test_case_and_dot_normalized():
    assert decide_host("GOOGLE.COM.", source="t").decision == Decision.REJECT
    assert decide_host("  Docs.Google.Com  ", source="t").decision == Decision.REVIEW


def test_unencodable_hostname_rejected():
    record = decide_host("a" * 300, source="t")
    assert record.decision == Decision.REJECT


def test_safety_record_defaults():
    record = SafetyRecord(source="s", indicator="h", decision=Decision.ACCEPT, reason="r")
    assert record.rule is None


def test_safety_summary_defaults():
    summary = SafetySummary()
    assert (summary.accepted, summary.rejected, summary.review) == (0, 0, 0)
    assert summary.records == []
