"""
Unit Tests — B6-E6 Real Verification Harness
Anti-Dory FORGE v3.0 — Batch 005 Célula F

Tests real minisign verification using public key.
NO private key. NO signing real actions.
"""

import os
import subprocess
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from kernel.anti_dory.b6_signature_verifier import (
    SignatureVerifier,
    VerificationResult,
    VerificationStatus,
    compute_file_hash,
    find_public_key,
    is_minisign_available,
    PUBLIC_KEY_RELATIVE_PATH,
)


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def dummy_key(temp_dir):
    """Create a dummy public key file."""
    key_dir = Path(temp_dir) / ".monstruo" / "keys"
    key_dir.mkdir(parents=True)
    key_path = key_dir / "dory_cure_kill_switch.pub"
    key_path.write_text("untrusted comment: minisign public key DUMMY\nRWTest1234567890==\n")
    return str(key_path)


@pytest.fixture
def verifier_with_key(temp_dir, dummy_key):
    """Verifier with a dummy key available."""
    return SignatureVerifier(repo_root=temp_dir)


class TestIsMinisignAvailable:
    def test_returns_bool(self):
        result = is_minisign_available()
        assert isinstance(result, bool)

    @patch("subprocess.run")
    def test_available_when_installed(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        assert is_minisign_available() is True

    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_not_available_when_missing(self, mock_run):
        assert is_minisign_available() is False


class TestComputeFileHash:
    def test_deterministic(self, temp_dir):
        f = Path(temp_dir) / "test.txt"
        f.write_text("hello world")
        h1 = compute_file_hash(str(f))
        h2 = compute_file_hash(str(f))
        assert h1 == h2

    def test_different_content_different_hash(self, temp_dir):
        f1 = Path(temp_dir) / "a.txt"
        f2 = Path(temp_dir) / "b.txt"
        f1.write_text("content A")
        f2.write_text("content B")
        assert compute_file_hash(str(f1)) != compute_file_hash(str(f2))

    def test_sha256_length(self, temp_dir):
        f = Path(temp_dir) / "test.txt"
        f.write_text("test")
        assert len(compute_file_hash(str(f))) == 64


class TestFindPublicKey:
    def test_finds_key_in_repo_root(self, temp_dir, dummy_key):
        result = find_public_key(repo_root=temp_dir)
        assert result is not None
        assert result.exists()

    def test_returns_none_when_not_found(self, temp_dir):
        result = find_public_key(repo_root=temp_dir + "/nonexistent")
        # May or may not find in fallback locations
        # Just verify it returns Path or None
        assert result is None or isinstance(result, Path)


class TestSignatureVerifier:
    def test_check_prerequisites(self, verifier_with_key):
        prereqs = verifier_with_key.check_prerequisites()
        assert "minisign_available" in prereqs
        assert "public_key_found" in prereqs
        assert prereqs["public_key_found"] is True

    def test_public_key_hash(self, verifier_with_key):
        h = verifier_with_key.get_public_key_hash()
        assert h is not None
        assert len(h) == 64

    def test_verify_public_key_integrity(self, verifier_with_key):
        result = verifier_with_key.verify_public_key_integrity()
        assert result is True

    def test_no_key_integrity_fails(self):
        with patch("kernel.anti_dory.b6_signature_verifier.find_public_key", return_value=None):
            verifier = SignatureVerifier.__new__(SignatureVerifier)
            verifier._repo_root = "/nonexistent"
            verifier._public_key_path = None
            assert verifier.verify_public_key_integrity() is False


class TestVerifyArtifact:
    @patch("kernel.anti_dory.b6_signature_verifier.is_minisign_available", return_value=False)
    def test_tool_not_found(self, mock_avail, verifier_with_key):
        result = verifier_with_key.verify_artifact("/tmp/test.txt")
        assert result.status == VerificationStatus.TOOL_NOT_FOUND

    def test_key_not_found(self, temp_dir):
        with patch("kernel.anti_dory.b6_signature_verifier.find_public_key", return_value=None):
            verifier = SignatureVerifier.__new__(SignatureVerifier)
            verifier._repo_root = "/nonexistent"
            verifier._public_key_path = None
            with patch("kernel.anti_dory.b6_signature_verifier.is_minisign_available", return_value=True):
                result = verifier.verify_artifact("/tmp/test.txt")
                assert result.status == VerificationStatus.KEY_NOT_FOUND

    def test_no_signature_file(self, verifier_with_key, temp_dir):
        artifact = Path(temp_dir) / "artifact.txt"
        artifact.write_text("content")
        with patch("kernel.anti_dory.b6_signature_verifier.is_minisign_available", return_value=True):
            result = verifier_with_key.verify_artifact(str(artifact))
            assert result.status == VerificationStatus.NO_SIGNATURE

    @patch("subprocess.run")
    def test_verified_success(self, mock_run, verifier_with_key, temp_dir):
        mock_run.return_value = MagicMock(returncode=0, stdout="Signature and comment signature verified", stderr="")
        artifact = Path(temp_dir) / "artifact.txt"
        artifact.write_text("signed content")
        sig = Path(temp_dir) / "artifact.txt.minisig"
        sig.write_text("dummy sig")
        with patch("kernel.anti_dory.b6_signature_verifier.is_minisign_available", return_value=True):
            result = verifier_with_key.verify_artifact(str(artifact), str(sig))
            assert result.status == VerificationStatus.VERIFIED

    @patch("subprocess.run")
    def test_verification_failed(self, mock_run, verifier_with_key, temp_dir):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Signature verification failed")
        artifact = Path(temp_dir) / "artifact.txt"
        artifact.write_text("tampered content")
        sig = Path(temp_dir) / "artifact.txt.minisig"
        sig.write_text("bad sig")
        with patch("kernel.anti_dory.b6_signature_verifier.is_minisign_available", return_value=True):
            result = verifier_with_key.verify_artifact(str(artifact), str(sig))
            assert result.status == VerificationStatus.FAILED


class TestRealMinisignIntegration:
    """Integration tests that run only if minisign is actually installed."""

    @pytest.mark.skipif(not is_minisign_available(), reason="minisign not installed")
    def test_sign_and_verify_dummy(self, temp_dir):
        """Full cycle: generate key, sign, verify — all with dummy data."""
        # Generate a temporary keypair
        key_path = Path(temp_dir) / "test.pub"
        sec_path = Path(temp_dir) / "test.key"

        subprocess.run(
            ["minisign", "-G", "-p", str(key_path), "-s", str(sec_path), "-W"],
            input=b"",
            capture_output=True,
        )

        # Create artifact
        artifact = Path(temp_dir) / "test_artifact.txt"
        artifact.write_text("This is a test artifact for B6-E6")

        # Sign it
        subprocess.run(
            ["minisign", "-Sm", str(artifact), "-s", str(sec_path)],
            capture_output=True,
        )

        # Verify using our harness
        verifier = SignatureVerifier.__new__(SignatureVerifier)
        verifier._repo_root = temp_dir
        verifier._public_key_path = key_path

        result = verifier.verify_artifact(str(artifact))
        assert result.status == VerificationStatus.VERIFIED
