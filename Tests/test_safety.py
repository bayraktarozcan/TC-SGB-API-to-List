"""Tests for the publication safety policy shared by all production lines."""

from __future__ import annotations

import pytest

from Scripts.src.safety import (
    BLOCKED_EXACT,
    SHARED_APEX,
    SHARED_SERVICE_APEX,
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
        ("amazonaws.com", Decision.REVIEW),
        ("amazonaws.com.cn", Decision.REVIEW),
        ("amazonaws.eu", Decision.REVIEW),
        ("api.aws", Decision.REVIEW),
        ("api.amazonwebservices.eu", Decision.REVIEW),
        ("amazonwebservices.eu", Decision.REVIEW),
        ("c2s.ic.gov", Decision.REVIEW),
        ("sc2s.sgov.gov", Decision.REVIEW),
        ("csp.hci.ic.gov", Decision.REVIEW),
        ("cloud.adc-e.uk", Decision.REVIEW),
        ("s3.amazonaws.com", Decision.REVIEW),
        ("s3.us-east-2.amazonaws.com", Decision.REVIEW),
        ("s3-eu-west-1.amazonaws.com", Decision.REVIEW),
        ("s3.dualstack.us-east-1.amazonaws.com", Decision.REVIEW),
        ("s3-fips.us-east-2.amazonaws.com", Decision.REVIEW),
        ("s3-fips.dualstack.us-east-2.amazonaws.com", Decision.REVIEW),
        ("s3-accesspoint-fips.dualstack.us-east-2.amazonaws.com", Decision.REVIEW),
        ("s3-control.dualstack.us-east-1.amazonaws.com", Decision.REVIEW),
        ("s3tables.us-east-1.amazonaws.com", Decision.REVIEW),
        ("s3tables.us-east-1.api.aws", Decision.REVIEW),
        ("s3vectors.us-east-1.api.aws", Decision.REVIEW),
        ("s3-outposts-fips.us-east-2.api.aws", Decision.REVIEW),
        ("s3express-control.us-east-1.amazonaws.com", Decision.REVIEW),
        ("s3express-use1-az4.us-east-1.amazonaws.com", Decision.REVIEW),
        ("s3express-use1-az4.dualstack.us-east-1.amazonaws.com", Decision.REVIEW),
        ("s3-website-us-east-1.amazonaws.com", Decision.REVIEW),
        ("s3-website.us-east-2.amazonaws.com", Decision.REVIEW),
        ("s3-website.eusc-de-east-1.amazonaws.eu", Decision.REVIEW),
        ("s3-accelerate.amazonaws.com", Decision.REVIEW),
        ("s3-accelerate.dualstack.amazonaws.com", Decision.REVIEW),
        ("s3-global.amazonaws.com", Decision.REVIEW),
        ("s3-global.dualstack.amazonaws.com", Decision.REVIEW),
        ("accesspoint.s3-global.amazonaws.com", Decision.REVIEW),
        ("mrap.accesspoint.s3-global.amazonaws.com", Decision.REVIEW),
        ("s3-external-1.amazonaws.com", Decision.REVIEW),
        ("s3.cn-north-1.amazonaws.com.cn", Decision.REVIEW),
        ("s3-accesspoint.cn-north-1.amazonaws.com.cn", Decision.REVIEW),
        ("s3.eusc-de-east-1.amazonaws.eu", Decision.REVIEW),
        ("s3.dualstack.eusc-de-east-1.amazonaws.eu", Decision.REVIEW),
        ("s3vectors.eusc-de-east-1.api.amazonwebservices.eu", Decision.REVIEW),
        ("s3.us-iso-east-1.c2s.ic.gov", Decision.REVIEW),
        ("s3.us-isob-east-1.sc2s.sgov.gov", Decision.REVIEW),
        ("s3.us-isof-south-1.csp.hci.ic.gov", Decision.REVIEW),
        ("s3.eu-isoe-west-1.cloud.adc-e.uk", Decision.REVIEW),
        ("mybucket.s3.amazonaws.com", Decision.ACCEPT),
        ("mybucket.s3.us-east-2.amazonaws.com", Decision.ACCEPT),
        ("mybucket.s3-fips.us-east-2.amazonaws.com", Decision.ACCEPT),
        ("mybucket.s3-accesspoint-fips.dualstack.us-east-2.amazonaws.com", Decision.ACCEPT),
        ("mybucket.s3-accelerate.amazonaws.com", Decision.ACCEPT),
        ("mybucket.s3-external-1.amazonaws.com", Decision.ACCEPT),
        ("mybucket.s3-website-us-east-1.amazonaws.com", Decision.ACCEPT),
        ("mybucket.s3-global.amazonaws.com", Decision.ACCEPT),
        ("mybucket.mrap.accesspoint.s3-global.amazonaws.com", Decision.ACCEPT),
        ("mybucket.s3tables.us-east-1.api.aws", Decision.ACCEPT),
        ("mybucket.s3vectors.us-east-1.api.aws", Decision.ACCEPT),
        ("mybucket.s3.eusc-de-east-1.amazonaws.eu", Decision.ACCEPT),
        ("mybucket.s3-website.eusc-de-east-1.amazonaws.eu", Decision.ACCEPT),
        ("mybucket.s3vectors.eusc-de-east-1.api.amazonwebservices.eu", Decision.ACCEPT),
        ("mybucket.s3.us-iso-east-1.c2s.ic.gov", Decision.ACCEPT),
        ("s3-fips.s3.amazonaws.com", Decision.ACCEPT),
        ("s3-accesspoint.s3.amazonaws.com", Decision.ACCEPT),
        ("s3.amazonaws.com.evil.example.com", Decision.ACCEPT),
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
    assert "amazonaws.com" in SHARED_SERVICE_APEX
    assert "s3.amazonaws.com" not in SHARED_SERVICE_APEX


def test_s3_bucket_hosts_stay_eligible():
    for host in (
        "mybucket.s3.amazonaws.com",
        "mybucket.s3.us-east-2.amazonaws.com",
        "s3.s3.amazonaws.com",
    ):
        assert decide_host(host, source="test").decision == Decision.ACCEPT


def test_case_and_dot_normalized():
    assert decide_host("GOOGLE.COM.", source="t").decision == Decision.REJECT
    assert decide_host("  Docs.Google.Com  ", source="t").decision == Decision.REVIEW


def test_unicode_trailing_dot_normalized():
    for host in ("s3.amazonaws.com\u3002", "s3.amazonaws.com\uff0e", "s3.amazonaws.com\uff61"):
        record = decide_host(host, source="t")
        assert record.decision == Decision.REVIEW
        assert record.indicator == "s3.amazonaws.com"
    assert decide_host("google.com\u3002", source="t").decision == Decision.REJECT
    assert decide_host("docs.google.com\u3002", source="t").decision == Decision.REVIEW


def test_empty_normalized_host_rejected():
    for host in ("", "。", "..."):
        assert decide_host(host, source="t").decision == Decision.REJECT


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
