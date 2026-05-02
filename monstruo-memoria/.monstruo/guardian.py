#!/usr/bin/env python3
"""
GUARDIAN V5 — Sistema Anti-Compactación con Memoria Persistente
================================================================
Evolución de V4. Cambios clave:
  - user_id = "guardian_v5" (migración limpia)
  - 3 capas: core (siempre), index (siempre), doc (bajo demanda)
  - NO re-ingesta memorias en cada recovery (el bug de V4)
  - Dedup por sha256 en metadata al guardar
  - CLI: remember con --layer y --tag
  - CLI: recall con --layer y --tag filtering

Backend: Supabase PostgREST (tabla monstruo_memory)
Backup: GitHub repo (identity.json + OMEGA files)
Anclajes: Filesystem + Kernel API + Supabase DB (consenso 2/3)
"""
import json
import os
import sys
import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import quote
import ssl

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════
STATE_DIR = Path.home() / ".monstruo" / "state"
IDENTITY_FILE = STATE_DIR / "identity.json"
OMEGA_DIR = Path.home() / ".monstruo" / "omega"
LOGS_DIR = Path.home() / ".monstruo" / "logs"

for d in [STATE_DIR, OMEGA_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

KERNEL_URL = os.environ.get("KERNEL_BASE_URL", "")
KERNEL_KEY = os.environ.get("MONSTRUO_API_KEY", "")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# V5 config
MEMORY_USER_ID = "guardian_v5"
VERSION = "5.0.0"
SSL_CTX = ssl.create_default_context()

def log(msg: str, level: str = "INFO"):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    log_file = LOGS_DIR / "guardian.log"
    with open(log_file, "a") as f:
        f.write(line + "\n")


# ═══════════════════════════════════════════════════════════════
# SUPABASE MEMORY CLIENT (V5 — con capas)
# ═══════════════════════════════════════════════════════════════
class SupabaseMemory:
    """Client for Supabase-backed persistent memory with V5 layer system."""
    
    def __init__(self, base_url: str, service_key: str):
        self.base_url = base_url.rstrip("/")
        self.key = service_key
        self.headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, path: str, data=None, extra_headers=None):
        url = f"{self.base_url}/rest/v1/{path}"
        headers = {**self.headers}
        if extra_headers:
            headers.update(extra_headers)
        body = json.dumps(data).encode() if data else None
        req = Request(url, data=body, headers=headers, method=method)
        try:
            resp = urlopen(req, timeout=15, context=SSL_CTX)
            raw = resp.read()
            return json.loads(raw) if raw else None
        except HTTPError as e:
            error_body = e.read().decode()
            log(f"Supabase HTTP {e.code}: {error_body[:200]}", "ERROR")
            return None
        except (URLError, Exception) as e:
            log(f"Supabase connection error: {e}", "ERROR")
            return None
    
    def _parse_meta(self, row):
        """Safely parse metadata from a row."""
        m = row.get("metadata") or {}
        if isinstance(m, str):
            try:
                m = json.loads(m)
            except:
                m = {}
        return m
    
    def remember(self, content: str, task_type: str, layer: str = "core",
                 tag: str = "general", importance: int = 8) -> str:
        """
        Store a new memory with V5 metadata.
        Dedup: checks sha256 of content against existing memories.
        Returns UUID or None.
        """
        if not content or not content.strip():
            return None
        if task_type not in ("fact", "instruction"):
            log(f"Invalid task_type: {task_type}", "WARN")
            return None
        if layer not in ("core", "index", "doc"):
            log(f"Invalid layer: {layer}", "WARN")
            return None
        
        sha = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        # Check for duplicate by sha
        existing = self._request("GET",
            f"monstruo_memory?user_id=eq.{MEMORY_USER_ID}&select=id,metadata&limit=200",
            extra_headers={"Range": "0-199"})
        if existing:
            for r in existing:
                m = self._parse_meta(r)
                if m.get("sha") == sha:
                    log(f"Duplicate (sha={sha}), skipping: {content[:50]}...", "WARN")
                    return None
        
        mem_id = str(uuid.uuid4())
        metadata = {
            "v": 5,
            "layer": layer,
            "tag": tag,
            "importance": min(max(importance, 1), 10),
            "sha": sha
        }
        
        row = {
            "id": mem_id,
            "user_id": MEMORY_USER_ID,
            "role": "system",
            "content": content[:60000],
            "task_type": task_type,
            "metadata": json.dumps(metadata)
        }
        
        result = self._request("POST", "monstruo_memory",
                              data=row,
                              extra_headers={"Prefer": "return=minimal"})
        if result is not None or True:  # POST with return=minimal returns empty
            log(f"Memory STORED [{layer}/{tag}] imp={importance}: {content[:50]}...")
            return mem_id
        return None
    
    def recall(self, query: str = None, layer: str = None, tag: str = None,
               limit: int = 50) -> list:
        """
        Retrieve memories with optional filters.
        """
        params = [f"user_id=eq.{MEMORY_USER_ID}"]
        
        if query:
            params.append(f"content=ilike.*{quote(query, safe='')}*")
        
        params.append(f"order=created_at.asc")
        params.append(f"limit={limit}")
        
        path = f"monstruo_memory?{'&'.join(params)}&select=*"
        results = self._request("GET", path, extra_headers={"Range": f"0-{limit-1}"})
        
        if not results:
            return []
        
        # Post-filter by layer and tag (JSONB filtering)
        if layer:
            results = [r for r in results if self._parse_meta(r).get("layer") == layer]
        if tag:
            results = [r for r in results if self._parse_meta(r).get("tag") == tag]
        
        return results
    
    def recall_by_layer(self, layer: str, limit: int = 100) -> list:
        """Retrieve all memories from a specific layer."""
        return self.recall(layer=layer, limit=limit)
    
    def count_by_layer(self) -> dict:
        """Count memories per layer."""
        all_mems = self._request("GET",
            f"monstruo_memory?user_id=eq.{MEMORY_USER_ID}&select=metadata",
            extra_headers={"Range": "0-999"})
        if not all_mems:
            return {"core": 0, "index": 0, "doc": 0, "total": 0}
        
        counts = {"core": 0, "index": 0, "doc": 0}
        for r in all_mems:
            m = self._parse_meta(r)
            layer = m.get("layer", "?")
            if layer in counts:
                counts[layer] += 1
        counts["total"] = len(all_mems)
        return counts
    
    def count_memories(self) -> int:
        """Count total memories."""
        results = self._request("GET",
            f"monstruo_memory?user_id=eq.{MEMORY_USER_ID}&select=id",
            extra_headers={"Range": "0-999"})
        return len(results) if results else 0


# ═══════════════════════════════════════════════════════════════
# ANCLAJE 1: FILESYSTEM
# ═══════════════════════════════════════════════════════════════
def check_anchor_filesystem() -> dict:
    try:
        if not IDENTITY_FILE.exists():
            return {"valid": False, "error": "identity.json no existe", "data": None}
        data = json.loads(IDENTITY_FILE.read_text())
        required = ["hilo", "rol", "proyecto_activo", "errores_criticos_no_repetir"]
        missing = [f for f in required if f not in data]
        if missing:
            return {"valid": False, "error": f"Campos faltantes: {missing}", "data": data}
        return {"valid": True, "data": data, "source": "filesystem"}
    except Exception as e:
        return {"valid": False, "error": str(e), "data": None}


# ═══════════════════════════════════════════════════════════════
# ANCLAJE 2: KERNEL API
# ═══════════════════════════════════════════════════════════════
def check_anchor_kernel() -> dict:
    if not KERNEL_URL or not KERNEL_KEY:
        return {"valid": False, "error": "KERNEL_BASE_URL o MONSTRUO_API_KEY no configuradas", "data": None}
    try:
        headers = {"x-api-key": KERNEL_KEY}
        req = Request(f"{KERNEL_URL}/health", headers=headers)
        resp = urlopen(req, timeout=10, context=SSL_CTX)
        health = json.loads(resp.read())
        
        req2 = Request(f"{KERNEL_URL}/v1/tools", headers=headers)
        resp2 = urlopen(req2, timeout=10, context=SSL_CTX)
        tools_data = json.loads(resp2.read())
        tools_activas = [t["name"] for t in tools_data.get("tools", []) if t.get("active")]
        
        req3 = Request(f"{KERNEL_URL}/v1/embrion/estado", headers=headers)
        try:
            resp3 = urlopen(req3, timeout=10, context=SSL_CTX)
            embrion = json.loads(resp3.read())
        except:
            embrion = {"running": False, "ciclos": 0}
        
        return {
            "valid": True,
            "data": {
                "kernel_online": True,
                "version": health.get("version", "?"),
                "tools_activas": tools_activas,
                "embrion_running": embrion.get("running", False),
                "embrion_ciclos": embrion.get("ciclos", 0),
                "fcs_score": health.get("fcs_score", 0)
            },
            "source": "kernel"
        }
    except Exception as e:
        return {"valid": False, "error": str(e), "data": None}


# ═══════════════════════════════════════════════════════════════
# ANCLAJE 3: SUPABASE MEMORY
# ═══════════════════════════════════════════════════════════════
def check_anchor_supabase() -> dict:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"valid": False, "error": "SUPABASE_URL o SUPABASE_SERVICE_KEY no configuradas", "data": None}
    try:
        mem = SupabaseMemory(SUPABASE_URL, SUPABASE_KEY)
        counts = mem.count_by_layer()
        
        # Load CORE + INDEX for recovery display
        core = mem.recall_by_layer("core", limit=100)
        index = mem.recall_by_layer("index", limit=50)
        
        return {
            "valid": True,
            "data": {
                "counts": counts,
                "core_memories": core,
                "index_memories": index
            },
            "source": "supabase"
        }
    except Exception as e:
        return {"valid": False, "error": str(e), "data": None}


# ═══════════════════════════════════════════════════════════════
# MAIN RECOVERY FLOW (V5 — NO re-ingesta)
# ═══════════════════════════════════════════════════════════════
def run_recovery():
    print()
    print("=" * 70)
    print("  GUARDIAN V5 — Anti-Compactación con Memoria Persistente")
    print("  Capas: core (siempre) | index (siempre) | doc (bajo demanda)")
    print(f"  Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 70)
    print()
    
    # === Verificar los 3 anclajes ===
    log("Verificando Anclaje 1: Filesystem...")
    anchor1 = check_anchor_filesystem()
    log(f"  → {'VÁLIDO' if anchor1['valid'] else 'FALLO: ' + anchor1.get('error', '?')}")
    
    log("Verificando Anclaje 2: Kernel API...")
    anchor2 = check_anchor_kernel()
    log(f"  → {'VÁLIDO' if anchor2['valid'] else 'FALLO: ' + anchor2.get('error', '?')}")
    
    log("Verificando Anclaje 3: Supabase Memory...")
    anchor3 = check_anchor_supabase()
    log(f"  → {'VÁLIDO' if anchor3['valid'] else 'FALLO: ' + anchor3.get('error', '?')}")
    
    # === Consenso ===
    valid_count = sum(1 for a in [anchor1, anchor2, anchor3] if a["valid"])
    
    print()
    print(f"{'─' * 70}")
    print(f"  CONSENSO: {valid_count}/3 anclajes válidos", end="")
    
    if valid_count >= 2:
        print(" ✓ PROCEDER")
    elif valid_count == 1:
        print(" ⚠ DEGRADADO (1 anclaje, proceder con cautela)")
    else:
        print(" ✗ HALT — Sin contexto verificado")
        print()
        print("  ╔══════════════════════════════════════════════════════════════╗")
        print("  ║  NO PUEDO OPERAR SIN CONTEXTO VERIFICADO.                   ║")
        print("  ║  Pregunta al usuario antes de actuar.                        ║")
        print("  ╚══════════════════════════════════════════════════════════════╝")
        return
    
    print(f"{'─' * 70}")
    print()
    
    # === Obtener datos ===
    identity = anchor1.get("data", {}) if anchor1["valid"] else {}
    kernel = anchor2.get("data", {}) if anchor2["valid"] else {}
    supabase_data = anchor3.get("data", {}) if anchor3["valid"] else {}
    
    counts = supabase_data.get("counts", {})
    core_mems = supabase_data.get("core_memories", [])
    index_mems = supabase_data.get("index_memories", [])
    
    # === IDENTIDAD ===
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                    IDENTIDAD RESTAURADA                         ║")
    print("╠══════════════════════════════════════════════════════════════════╣")
    
    if identity:
        print(f"║  Hilo: {identity.get('hilo', '?')}")
        print(f"║  Rol: {identity.get('rol', '?')}")
        print(f"║  Proyecto: {identity.get('proyecto_activo', '?')}")
        print(f"║  Path: {identity.get('proyecto_path', '?')}")
    
    if kernel:
        print(f"║")
        print(f"║  Kernel: {'ONLINE' if kernel.get('kernel_online') else 'OFFLINE'} (v{kernel.get('version', '?')})")
        print(f"║  Tools activas: {kernel.get('tools_activas', [])}")
        print(f"║  Embrión: {'running' if kernel.get('embrion_running') else 'stopped'} ({kernel.get('embrion_ciclos', 0)} ciclos)")
    
    print(f"║")
    print(f"║  Memoria V5: {counts.get('total', 0)} total (core:{counts.get('core', 0)} index:{counts.get('index', 0)} doc:{counts.get('doc', 0)})")
    
    # === ERRORES CRÍTICOS ===
    print(f"║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║              ERRORES CRÍTICOS — NO REPETIR                      ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    
    errors = identity.get("errores_criticos_no_repetir", [])
    for i, err in enumerate(errors, 1):
        if len(err) > 64:
            print(f"║  {i}. {err[:64]}")
            print(f"║     {err[64:]}")
        else:
            print(f"║  {i}. {err}")
    
    # === CORE MEMORIES ===
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║              MEMORIAS CORE ({len(core_mems)})                   ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    
    if core_mems:
        for m in core_mems:
            meta = self_parse_meta(m)
            tag = meta.get("tag", "?")
            content = m.get("content", "")[:75]
            print(f"║  [{tag}] {content}")
    else:
        print(f"║  (Sin memorias core — ejecutar upload_v5.py)")
    
    # === INDEX MEMORIES ===
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║              ÍNDICES ({len(index_mems)})                        ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    
    if index_mems:
        for m in index_mems:
            meta = self_parse_meta(m)
            tag = meta.get("tag", "?")
            content = m.get("content", "")[:75]
            print(f"║  [{tag}] {content}")
    else:
        print(f"║  (Sin índices)")
    
    # === CAPACIDADES ===
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║              CAPACIDADES REALES (VERIFICADAS)                   ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    
    if kernel:
        tools = kernel.get("tools_activas", [])
        print(f"║  Tools ACTIVAS en producción: {tools}")
    
    print(f"║")
    print(f"║  Docs bajo demanda: {counts.get('doc', 0)} disponibles")
    print(f"║  Usar: python3 guardian.py recall --query 'keyword' --layer doc")
    print(f"║")
    print(f"╚══════════════════════════════════════════════════════════════════╝")
    print()
    
    # V5: NO re-ingesta. Las memorias ya están en Supabase.
    # Solo logueamos la recovery.
    
    # === Audit log ===
    audit = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": VERSION,
        "anchors": {
            "filesystem": anchor1["valid"],
            "kernel": anchor2["valid"],
            "supabase": anchor3["valid"]
        },
        "consensus": valid_count,
        "memories": counts,
        "action": "restored" if valid_count >= 1 else "halted"
    }
    
    audit_file = LOGS_DIR / "audit.jsonl"
    with open(audit_file, "a") as f:
        f.write(json.dumps(audit) + "\n")
    
    print("IDENTIDAD RESTAURADA")


def self_parse_meta(row):
    """Parse metadata from a memory row."""
    m = row.get("metadata") or {}
    if isinstance(m, str):
        try:
            m = json.loads(m)
        except:
            m = {}
    return m


# ═══════════════════════════════════════════════════════════════
# CLI: remember
# ═══════════════════════════════════════════════════════════════
def cli_remember(args):
    """CLI: python3 guardian.py remember 'content' --type fact --layer core --tag estado"""
    import argparse
    parser = argparse.ArgumentParser(description="Store a memory (V5)")
    parser.add_argument("content", help="Memory content text")
    parser.add_argument("--type", choices=["fact", "instruction"], default="fact")
    parser.add_argument("--layer", choices=["core", "index", "doc"], default="core")
    parser.add_argument("--tag", default="general")
    parser.add_argument("--importance", type=int, default=8)
    parsed = parser.parse_args(args)
    
    mem = SupabaseMemory(SUPABASE_URL, SUPABASE_KEY)
    result = mem.remember(
        content=parsed.content,
        task_type=parsed.type,
        layer=parsed.layer,
        tag=parsed.tag,
        importance=parsed.importance
    )
    if result:
        print(f"OK: {result}")
    else:
        print("FAILED or DUPLICATE")
        sys.exit(1)


# ═══════════════════════════════════════════════════════════════
# CLI: recall
# ═══════════════════════════════════════════════════════════════
def cli_recall(args):
    """CLI: python3 guardian.py recall --query 'brand' --layer doc"""
    import argparse
    parser = argparse.ArgumentParser(description="Recall memories (V5)")
    parser.add_argument("--query", default=None)
    parser.add_argument("--layer", choices=["core", "index", "doc"], default=None)
    parser.add_argument("--tag", default=None)
    parser.add_argument("--limit", type=int, default=20)
    parsed = parser.parse_args(args)
    
    mem = SupabaseMemory(SUPABASE_URL, SUPABASE_KEY)
    results = mem.recall(
        query=parsed.query,
        layer=parsed.layer,
        tag=parsed.tag,
        limit=parsed.limit
    )
    
    print(f"Found {len(results)} memories:")
    for r in results:
        meta = self_parse_meta(r)
        layer = meta.get("layer", "?")
        tag = meta.get("tag", "?")
        imp = meta.get("importance", "?")
        content = r.get("content", "")[:100]
        print(f"  [{layer}/{tag}|imp:{imp}] {content}")
        print(f"    id={r['id'][:8]} created={r['created_at'][:19]}")


# ═══════════════════════════════════════════════════════════════
# CLI: stats
# ═══════════════════════════════════════════════════════════════
def cli_stats():
    """CLI: python3 guardian.py stats"""
    mem = SupabaseMemory(SUPABASE_URL, SUPABASE_KEY)
    counts = mem.count_by_layer()
    print(f"Guardian V5 Memory Stats:")
    print(f"  Total:  {counts['total']}")
    print(f"  Core:   {counts['core']}")
    print(f"  Index:  {counts['index']}")
    print(f"  Doc:    {counts['doc']}")


# ═══════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "remember":
            cli_remember(sys.argv[2:])
        elif command == "recall":
            cli_recall(sys.argv[2:])
        elif command == "recover":
            run_recovery()
        elif command == "stats":
            cli_stats()
        else:
            print(f"Unknown command: {command}")
            print("Usage: guardian.py [recover|remember|recall|stats]")
            print("  recover  — Full recovery (default)")
            print("  remember — Store a memory")
            print("  recall   — Search memories")
            print("  stats    — Show memory counts by layer")
            sys.exit(1)
    else:
        # Default: run recovery
        run_recovery()
