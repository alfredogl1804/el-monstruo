#!/usr/bin/env python3
"""
El Monstruo — License Compliance Auditor (Sprint 22)
=====================================================
Scans requirements.txt and flags viral/copyleft licenses.

Policy:
  ALLOWED: MIT, BSD, Apache-2.0, ISC, PSF, MPL-2.0, Unlicense, CC0
  BLOCKED: AGPL-3.0, GPL-2.0, GPL-3.0, SSPL, EUPL, OSL, CPAL

Usage:
  python scripts/audit_licenses.py
  python scripts/audit_licenses.py --strict  # exit 1 on any violation
"""

import json
import re
import subprocess
import sys

VIRAL_PATTERN = re.compile(
    r"(AGPL|GPL-[23]|GNU General Public|SSPL|EUPL|OSL-[23]|CPAL|RPL|Sleepycat|Watcom)",
    re.IGNORECASE,
)

PERMISSIVE_PATTERN = re.compile(
    r"(MIT|BSD|Apache|ISC|PSF|MPL-2|Unlicense|CC0|Public Domain|WTFPL|Zlib|Artistic)",
    re.IGNORECASE,
)


def main():
    strict = "--strict" in sys.argv

    # Run pip-licenses
    try:
        result = subprocess.run(
            ["pip-licenses", "--format=json", "--with-urls"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        packages = json.loads(result.stdout)
    except FileNotFoundError:
        print("ERROR: pip-licenses not installed. Run: pip install pip-licenses")
        sys.exit(1)
    except json.JSONDecodeError:
        print("ERROR: Could not parse pip-licenses output")
        sys.exit(1)

    violations = []
    warnings = []
    clean = []

    for pkg in packages:
        name = pkg.get("Name", "?")
        version = pkg.get("Version", "?")
        license_str = pkg.get("License", "UNKNOWN")

        if VIRAL_PATTERN.search(license_str):
            # Check if dual-licensed with a permissive option
            if PERMISSIVE_PATTERN.search(license_str):
                warnings.append(
                    f"  ⚠️  {name}=={version}: {license_str} (dual-license, permissive option available)"
                )
            else:
                violations.append(
                    f"  ❌ {name}=={version}: {license_str}"
                )
        elif license_str in ("UNKNOWN", ""):
            warnings.append(f"  ❓ {name}=={version}: License UNKNOWN")
        else:
            clean.append(f"  ✅ {name}=={version}: {license_str}")

    # Report
    print("=" * 60)
    print("El Monstruo — License Compliance Audit")
    print("=" * 60)
    print(f"\nTotal packages: {len(packages)}")
    print(f"Clean: {len(clean)}")
    print(f"Warnings: {len(warnings)}")
    print(f"Violations: {len(violations)}")

    if violations:
        print(f"\n{'='*60}")
        print("❌ VIRAL LICENSE VIOLATIONS")
        print("=" * 60)
        for v in violations:
            print(v)

    if warnings:
        print(f"\n{'='*60}")
        print("⚠️  WARNINGS")
        print("=" * 60)
        for w in warnings:
            print(w)

    if not violations and not warnings:
        print("\n✅ ALL LICENSES ARE PERMISSIVE — No violations found.")

    # Exit code
    if violations and strict:
        print(f"\n🚫 STRICT MODE: {len(violations)} violation(s) found. Exiting with code 1.")
        sys.exit(1)
    elif violations:
        print(f"\n⚠️  {len(violations)} violation(s) found. Use --strict to fail on violations.")
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
