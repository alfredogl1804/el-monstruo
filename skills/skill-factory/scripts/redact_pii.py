#!/usr/bin/env python3.11
"""
redact_pii.py — Detección y redacción de PII en skills generadas.

Escanea todos los archivos de una skill buscando información personal
identificable (PII) y la redacta o marca para revisión.

Uso:
    python3.11 redact_pii.py --skill-dir /path/to/skill --output pii_report.yaml
    python3.11 redact_pii.py --skill-dir /path/to/skill --output pii_report.yaml --redact
"""

import argparse, re, yaml, sys
from pathlib import Path


# Patrones de PII
PII_PATTERNS = {
    "email": {
        "regex": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "severity": "HIGH",
        "replacement": "[EMAIL_REDACTED]"
    },
    "phone_mx": {
        "regex": r'\b(?:\+52|52)?[\s-]?(?:\d{2,3})[\s-]?\d{3,4}[\s-]?\d{4}\b',
        "severity": "HIGH",
        "replacement": "[PHONE_REDACTED]"
    },
    "phone_us": {
        "regex": r'\b(?:\+1)?[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}\b',
        "severity": "HIGH",
        "replacement": "[PHONE_REDACTED]"
    },
    "curp": {
        "regex": r'\b[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d\b',
        "severity": "CRITICAL",
        "replacement": "[CURP_REDACTED]"
    },
    "rfc": {
        "regex": r'\b[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}\b',
        "severity": "CRITICAL",
        "replacement": "[RFC_REDACTED]"
    },
    "ssn": {
        "regex": r'\b\d{3}-\d{2}-\d{4}\b',
        "severity": "CRITICAL",
        "replacement": "[SSN_REDACTED]"
    },
    "credit_card": {
        "regex": r'\b(?:\d{4}[\s-]?){3}\d{4}\b',
        "severity": "CRITICAL",
        "replacement": "[CC_REDACTED]"
    },
    "ip_address": {
        "regex": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        "severity": "MEDIUM",
        "replacement": "[IP_REDACTED]"
    },
    "api_key_pattern": {
        "regex": r'\b(?:sk-|pk-|api_|key_)[a-zA-Z0-9]{20,}\b',
        "severity": "CRITICAL",
        "replacement": "[API_KEY_REDACTED]"
    },
    "hardcoded_secret": {
        "regex": r'(?:password|secret|token|api_key)\s*=\s*["\'][^"\']{8,}["\']',
        "severity": "CRITICAL",
        "replacement": "[SECRET_REDACTED]"
    }
}

# Archivos a escanear
SCANNABLE_EXTENSIONS = {".py", ".md", ".yaml", ".yml", ".json", ".txt", ".toml", ".cfg", ".ini"}

# Archivos a ignorar
IGNORE_PATTERNS = {"__pycache__", ".git", "node_modules", ".env.example"}


def scan_file(filepath: Path) -> list:
    """Escanea un archivo buscando PII."""
    findings = []
    
    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return findings
    
    lines = content.split("\n")
    
    for pattern_name, config in PII_PATTERNS.items():
        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(config["regex"], line, re.IGNORECASE)
            for match in matches:
                # Filtrar falsos positivos comunes
                matched_text = match.group()
                
                # Ignorar IPs de localhost/ejemplo
                if pattern_name == "ip_address" and matched_text in ("127.0.0.1", "0.0.0.0", "192.168.1.1"):
                    continue
                
                # Ignorar emails de ejemplo
                if pattern_name == "email" and any(x in matched_text for x in ["example.com", "test.com", "placeholder"]):
                    continue
                
                findings.append({
                    "file": str(filepath),
                    "line": line_num,
                    "pattern": pattern_name,
                    "severity": config["severity"],
                    "matched": matched_text[:50],  # Truncar para no exponer PII en reporte
                    "context": line.strip()[:100]
                })
    
    return findings


def scan_skill(skill_dir: Path) -> list:
    """Escanea toda la skill buscando PII."""
    all_findings = []
    
    for filepath in skill_dir.rglob("*"):
        if filepath.is_file() and filepath.suffix in SCANNABLE_EXTENSIONS:
            # Verificar que no está en directorio ignorado
            if any(ignore in str(filepath) for ignore in IGNORE_PATTERNS):
                continue
            
            findings = scan_file(filepath)
            all_findings.extend(findings)
    
    return all_findings


def redact_findings(findings: list) -> dict:
    """Redacta PII encontrado en los archivos."""
    files_modified = {}
    
    # Agrupar por archivo
    by_file = {}
    for f in findings:
        filepath = f["file"]
        if filepath not in by_file:
            by_file[filepath] = []
        by_file[filepath].append(f)
    
    for filepath, file_findings in by_file.items():
        path = Path(filepath)
        content = path.read_text(encoding="utf-8")
        original = content
        
        for finding in file_findings:
            pattern_config = PII_PATTERNS.get(finding["pattern"], {})
            replacement = pattern_config.get("replacement", "[REDACTED]")
            content = re.sub(pattern_config["regex"], replacement, content, flags=re.IGNORECASE)
        
        if content != original:
            path.write_text(content, encoding="utf-8")
            files_modified[filepath] = len(file_findings)
    
    return files_modified


def main():
    parser = argparse.ArgumentParser(description="Detecta y redacta PII en skills")
    parser.add_argument("--skill-dir", required=True, help="Directorio de la skill")
    parser.add_argument("--output", required=True, help="Path de salida para pii_report.yaml")
    parser.add_argument("--redact", action="store_true", help="Redactar PII encontrado")
    args = parser.parse_args()
    
    skill_dir = Path(args.skill_dir)
    
    if not skill_dir.exists():
        print(f"❌ Directorio no existe: {skill_dir}")
        sys.exit(1)
    
    print(f"🔍 Escaneando PII en: {skill_dir.name}")
    
    findings = scan_skill(skill_dir)
    
    # Clasificar por severidad
    critical = [f for f in findings if f["severity"] == "CRITICAL"]
    high = [f for f in findings if f["severity"] == "HIGH"]
    medium = [f for f in findings if f["severity"] == "MEDIUM"]
    
    report = {
        "skill_dir": str(skill_dir),
        "total_findings": len(findings),
        "critical": len(critical),
        "high": len(high),
        "medium": len(medium),
        "findings": findings,
        "redacted": False
    }
    
    print(f"\n  Resultados:")
    print(f"    Total: {len(findings)}")
    print(f"    Critical: {len(critical)}")
    print(f"    High: {len(high)}")
    print(f"    Medium: {len(medium)}")
    
    if args.redact and findings:
        print(f"\n  🔒 Redactando PII...")
        modified = redact_findings(findings)
        report["redacted"] = True
        report["files_modified"] = modified
        print(f"    Archivos modificados: {len(modified)}")
    
    # Guardar reporte
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(report, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"\n📁 Reporte PII guardado en: {args.output}")
    
    # Exit code basado en severidad
    if critical:
        sys.exit(2)  # Critical PII found
    elif high:
        sys.exit(1)  # High PII found
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
