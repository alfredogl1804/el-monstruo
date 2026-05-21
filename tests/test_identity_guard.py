"""
OPP-NB-023 R1 — Tests for kernel/identity_guard.py

Minimal tests to demonstrate the guard works correctly.
Does NOT modify existing tests or CI.
"""

import sys
from pathlib import Path

# Add project root to path for import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from kernel.identity_guard import (
    ANONYMOUS_SENTINEL,
    UNRESOLVED_USER_CONTEXT,
    BLOCKED_USER_IDS,
    UserIdStatus,
    resolve_user_id,
    is_anonymous_blocked,
    require_resolved_user,
    annotate_user_id,
)
import unittest


class TestResolveUserId(unittest.TestCase):
    """Test resolve_user_id() classification logic."""

    def test_anonymous_is_blocked(self):
        """anonymous → BLOCKED, returns UNRESOLVED_USER_CONTEXT"""
        resolved, status = resolve_user_id("anonymous")
        self.assertEqual(resolved, UNRESOLVED_USER_CONTEXT)
        self.assertEqual(status, UserIdStatus.BLOCKED)

    def test_empty_string_is_blocked(self):
        """'' → BLOCKED"""
        resolved, status = resolve_user_id("")
        self.assertEqual(resolved, UNRESOLVED_USER_CONTEXT)
        self.assertEqual(status, UserIdStatus.BLOCKED)

    def test_none_is_unresolved(self):
        """None → UNRESOLVED"""
        resolved, status = resolve_user_id(None)
        self.assertEqual(resolved, UNRESOLVED_USER_CONTEXT)
        self.assertEqual(status, UserIdStatus.UNRESOLVED)

    def test_null_string_is_blocked(self):
        """'null' → BLOCKED"""
        resolved, status = resolve_user_id("null")
        self.assertEqual(resolved, UNRESOLVED_USER_CONTEXT)
        self.assertEqual(status, UserIdStatus.BLOCKED)

    def test_undefined_is_blocked(self):
        """'undefined' → BLOCKED"""
        resolved, status = resolve_user_id("undefined")
        self.assertEqual(resolved, UNRESOLVED_USER_CONTEXT)
        self.assertEqual(status, UserIdStatus.BLOCKED)

    def test_valid_user_is_resolved(self):
        """'alfredo' → RESOLVED, preserves original"""
        resolved, status = resolve_user_id("alfredo")
        self.assertEqual(resolved, "alfredo")
        self.assertEqual(status, UserIdStatus.RESOLVED)

    def test_case_insensitive_blocking(self):
        """'Anonymous' (capitalized) → BLOCKED"""
        resolved, status = resolve_user_id("Anonymous")
        self.assertEqual(resolved, UNRESOLVED_USER_CONTEXT)
        self.assertEqual(status, UserIdStatus.BLOCKED)

    def test_whitespace_trimmed(self):
        """' anonymous ' (padded) → BLOCKED"""
        resolved, status = resolve_user_id(" anonymous ")
        self.assertEqual(resolved, UNRESOLVED_USER_CONTEXT)
        self.assertEqual(status, UserIdStatus.BLOCKED)

    def test_real_uuid_is_resolved(self):
        """UUID-style user_id → RESOLVED"""
        resolved, status = resolve_user_id("usr_abc123def456")
        self.assertEqual(resolved, "usr_abc123def456")
        self.assertEqual(status, UserIdStatus.RESOLVED)


class TestIsAnonymousBlocked(unittest.TestCase):
    """Test is_anonymous_blocked() quick check."""

    def test_anonymous_blocked(self):
        self.assertTrue(is_anonymous_blocked("anonymous"))

    def test_none_blocked(self):
        self.assertTrue(is_anonymous_blocked(None))

    def test_valid_not_blocked(self):
        self.assertFalse(is_anonymous_blocked("alfredo"))

    def test_empty_blocked(self):
        self.assertTrue(is_anonymous_blocked(""))


class TestRequireResolvedUser(unittest.TestCase):
    """Test require_resolved_user() enforcement."""

    def test_raises_on_anonymous(self):
        """anonymous raises ValueError"""
        with self.assertRaises(ValueError) as ctx:
            require_resolved_user("anonymous", context="test_path")
        self.assertIn("BLOCKED", str(ctx.exception))
        self.assertIn("test_path", str(ctx.exception))

    def test_raises_on_none(self):
        """None raises ValueError"""
        with self.assertRaises(ValueError):
            require_resolved_user(None)

    def test_passes_valid_user(self):
        """Valid user_id passes through"""
        result = require_resolved_user("alfredo", context="test")
        self.assertEqual(result, "alfredo")


class TestAnnotateUserId(unittest.TestCase):
    """Test annotate_user_id() structured output."""

    def test_blocked_annotation(self):
        ann = annotate_user_id("anonymous")
        self.assertEqual(ann["user_id_original"], "anonymous")
        self.assertEqual(ann["user_id_resolved"], UNRESOLVED_USER_CONTEXT)
        self.assertEqual(ann["user_id_status"], "BLOCKED")
        self.assertTrue(ann["is_blocked"])
        self.assertEqual(ann["guard_version"], "OPP-NB-023-R1")

    def test_resolved_annotation(self):
        ann = annotate_user_id("alfredo")
        self.assertEqual(ann["user_id_original"], "alfredo")
        self.assertEqual(ann["user_id_resolved"], "alfredo")
        self.assertEqual(ann["user_id_status"], "RESOLVED")
        self.assertFalse(ann["is_blocked"])


if __name__ == "__main__":
    unittest.main()
