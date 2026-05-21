"""
B6-E6 Dummy Signature Verification Dry-Run
Anti-Dory FORGE v3.0 — Batch 004 Célula C

Verifica que el flujo de firma/verificación con minisign funciona
usando un archivo DUMMY y la clave PÚBLICA real del kill switch.

NO usa la clave privada real.
NO usa Fase 1.
NO escribe en producción.

Flujo:
1. Genera un archivo dummy con contenido conocido.
2. Genera un par de claves DUMMY (efímeras, solo para este test).
3. Firma el archivo dummy con la clave dummy.
4. Verifica la firma con la clave dummy.
5. Verifica que la clave pública real existe y tiene el formato correcto.
"""

import hashlib
import os
import subprocess
import tempfile

import pytest


# SHA-256 conocido de la clave pública real
REAL_PUBLIC_KEY_SHA256 = "cbdc2cd7f687d27dc450762676f0cc0bf2629d76265daafcf47af941fcb406b3"
REAL_PUBLIC_KEY_PATH = ".monstruo/keys/dory_cure_kill_switch.pub"


def minisign_available() -> bool:
    """Check if minisign is installed."""
    try:
        result = subprocess.run(["minisign", "-v"], capture_output=True, text=True)
        return result.returncode == 0 or "minisign" in result.stdout.lower() or "minisign" in result.stderr.lower()
    except FileNotFoundError:
        return False


@pytest.fixture
def dummy_file():
    """Create a temporary dummy file to sign."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("ANTI-DORY KILL SWITCH DRY RUN — THIS IS A DUMMY FILE\n")
        f.write("If you see this in production, something went wrong.\n")
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def dummy_keypair():
    """Generate an ephemeral keypair for testing (NOT the real one)."""
    tmpdir = tempfile.mkdtemp()
    secret_key = os.path.join(tmpdir, "dummy_test.key")
    public_key = os.path.join(tmpdir, "dummy_test.pub")

    # Generate keypair with empty password for test automation
    result = subprocess.run(
        ["minisign", "-G", "-s", secret_key, "-p", public_key, "-W"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        pytest.skip(f"minisign -G failed: {result.stderr}")

    yield {"secret": secret_key, "public": public_key, "dir": tmpdir}

    # Cleanup
    for f in [secret_key, public_key]:
        if os.path.exists(f):
            os.unlink(f)
    os.rmdir(tmpdir)


@pytest.mark.skipif(not minisign_available(), reason="minisign not installed")
class TestB6E6DryRun:
    """Dry-run del flujo de firma con claves dummy."""

    def test_sign_dummy_file(self, dummy_file, dummy_keypair):
        """Firma un archivo dummy con clave dummy."""
        sig_file = dummy_file + ".minisig"
        result = subprocess.run(
            ["minisign", "-S", "-s", dummy_keypair["secret"], "-m", dummy_file],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Sign failed: {result.stderr}"
        assert os.path.exists(sig_file)
        # Cleanup sig
        os.unlink(sig_file)

    def test_verify_dummy_signature(self, dummy_file, dummy_keypair):
        """Firma y verifica un archivo dummy."""
        sig_file = dummy_file + ".minisig"
        # Sign
        subprocess.run(
            ["minisign", "-S", "-s", dummy_keypair["secret"], "-m", dummy_file],
            capture_output=True,
            text=True,
        )
        # Verify
        result = subprocess.run(
            ["minisign", "-V", "-p", dummy_keypair["public"], "-m", dummy_file],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Verify failed: {result.stderr}"
        assert "Signature and comment signature verified" in (result.stdout + result.stderr)
        # Cleanup sig
        if os.path.exists(sig_file):
            os.unlink(sig_file)

    def test_tampered_file_fails_verification(self, dummy_file, dummy_keypair):
        """Un archivo modificado post-firma debe fallar verificación."""
        sig_file = dummy_file + ".minisig"
        # Sign
        subprocess.run(
            ["minisign", "-S", "-s", dummy_keypair["secret"], "-m", dummy_file],
            capture_output=True,
            text=True,
        )
        # Tamper
        with open(dummy_file, "a") as f:
            f.write("TAMPERED CONTENT\n")
        # Verify should fail
        result = subprocess.run(
            ["minisign", "-V", "-p", dummy_keypair["public"], "-m", dummy_file],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0, "Tampered file should fail verification"
        # Cleanup sig
        if os.path.exists(sig_file):
            os.unlink(sig_file)


class TestRealPublicKeyIntegrity:
    """Verifica la integridad de la clave pública real (sin usar la privada)."""

    def test_real_public_key_exists(self):
        """La clave pública real debe existir en el repo."""
        # Buscar relativo al directorio del repo
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        key_path = os.path.join(repo_root, REAL_PUBLIC_KEY_PATH)
        assert os.path.exists(key_path), f"Public key not found at {key_path}"

    def test_real_public_key_sha256(self):
        """La clave pública real debe tener el SHA-256 esperado."""
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        key_path = os.path.join(repo_root, REAL_PUBLIC_KEY_PATH)
        if not os.path.exists(key_path):
            pytest.skip("Public key file not found")
        with open(key_path, "rb") as f:
            content = f.read()
        sha256 = hashlib.sha256(content).hexdigest()
        assert sha256 == REAL_PUBLIC_KEY_SHA256, (
            f"SHA-256 mismatch! Expected {REAL_PUBLIC_KEY_SHA256}, got {sha256}"
        )

    def test_real_public_key_format(self):
        """La clave pública real debe tener formato minisign válido."""
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        key_path = os.path.join(repo_root, REAL_PUBLIC_KEY_PATH)
        if not os.path.exists(key_path):
            pytest.skip("Public key file not found")
        with open(key_path, "r") as f:
            lines = f.readlines()
        # minisign public keys have 2 lines: comment + base64 key
        assert len(lines) == 2, f"Expected 2 lines, got {len(lines)}"
        assert lines[0].startswith("untrusted comment:"), "First line must be untrusted comment"
        # Second line is base64 encoded key (typically 56 chars)
        key_b64 = lines[1].strip()
        assert len(key_b64) > 20, f"Key too short: {len(key_b64)} chars"
