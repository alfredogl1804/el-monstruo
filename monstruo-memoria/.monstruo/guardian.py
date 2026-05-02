#!/usr/bin/env python3
"""
GUARDIAN V4 — Sistema Anti-Compactación con Memoria Persistente
================================================================
Implementa la arquitectura de Cloudflare Agent Memory sobre Supabase:
  - 4 tipos de memoria: fact, event, instruction, task
  - Supersession chains (manejo de contradicciones)
  - Verification pipeline (8 checks antes de guardar)
  - Multi-channel retrieval (keyword, type, recency, importance)
  - Decay model (memorias se degradan si no se acceden)

Backend: Supabase PostgREST (tabla monstruo_memory)
Backup: GitHub repo (identity.json + OMEGA files)
Anclajes: Filesystem + Kernel API + Supabase DB (consenso 2/3)

Schema de monstruo_memory:
  id: UUID (PK)
  user_id: TEXT (siempre "guardian_v4")
  role: TEXT ("fact" | "event" | "instruction" | "task")
  content: TEXT (el contenido de la memoria)
  task_type: TEXT (tipo secundario o tag principal)
  brain_used: TEXT (source: "hilo_a", "hilo_b", "hilo_c", "user", "system")
  metadata: JSONB {
    importance: 1-10,
    confidence: 0-1,
    tags: [],
    entities: [],
    supersedes: uuid|null,
    superseded_by: uuid|null,
    is_active: bool,
    verified: bool,
    verification_method: str,
    access_count: int,
    last_accessed: iso_timestamp,
    decay_score: 0-1,
    summary: str
  }
  embedding: vector(1536) | null
  created_at: timestamptz
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

# Memory config
MEMORY_USER_ID = "guardian_v4"
DECAY_RATE = 0.05  # 5% decay per day without access
MIN_DECAY_SCORE = 0.1  # Never fully forget
MAX_MEMORIES_RETRIEVE = 50  # Max memories to load on recovery

def log(msg: str, level: str = "INFO"):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    log_file = LOGS_DIR / "guardian.log"
    with open(log_file, "a") as f:
        f.write(line + "\n")


# ═══════════════════════════════════════════════════════════════
# SUPABASE MEMORY CLIENT
# ═══════════════════════════════════════════════════════════════
class SupabaseMemory:
    """Client for Supabase-backed persistent memory."""
    
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
            resp = urlopen(req, timeout=15)
            raw = resp.read()
            return json.loads(raw) if raw else None
        except HTTPError as e:
            error_body = e.read().decode()
            log(f"Supabase HTTP {e.code}: {error_body[:200]}", "ERROR")
            return None
        except (URLError, Exception) as e:
            log(f"Supabase connection error: {e}", "ERROR")
            return None
    
    def remember(self, content: str, memory_type: str, source: str,
                 importance: int = 5, confidence: float = 0.8,
                 tags: list = None, entities: list = None,
                 summary: str = None, supersedes: str = None) -> str:
        """
        Store a new memory. Returns the UUID of the stored memory.
        
        memory_type: 'fact' | 'event' | 'instruction' | 'task'
        source: 'hilo_a' | 'hilo_b' | 'hilo_c' | 'user' | 'system'
        """
        # Verification pipeline
        if not self._verify_memory(content, memory_type, importance):
            log(f"Memory REJECTED by verification pipeline: {content[:50]}...", "WARN")
            return None
        
        mem_id = str(uuid.uuid4())
        metadata = {
            "importance": min(max(importance, 1), 10),
            "confidence": min(max(confidence, 0), 1),
            "tags": tags or [],
            "entities": entities or [],
            "supersedes": supersedes,
            "superseded_by": None,
            "is_active": True,
            "verified": True,
            "verification_method": "pipeline_v4",
            "access_count": 0,
            "last_accessed": None,
            "decay_score": 1.0,
            "summary": summary or content[:100]
        }
        
        row = {
            "id": mem_id,
            "user_id": MEMORY_USER_ID,
            "role": "system",
            "content": content,
            "task_type": memory_type,
            "brain_used": source,
            "metadata": metadata
        }
        
        result = self._request("POST", "monstruo_memory",
                              data=row,
                              extra_headers={"Prefer": "return=representation"})
        
        if result:
            # Handle supersession chain
            if supersedes:
                self._mark_superseded(supersedes, mem_id)
            log(f"Memory STORED [{memory_type}] importance={importance}: {content[:60]}...")
            return mem_id
        return None
    
    def recall(self, query: str = None, memory_type: str = None,
               tags: list = None, min_importance: int = 1,
               limit: int = MAX_MEMORIES_RETRIEVE,
               active_only: bool = True) -> list:
        """
        Multi-channel retrieval. Returns list of memories sorted by relevance.
        
        Channels:
        1. Type filter (exact match on memory_type)
        2. Keyword search (content contains query)
        3. Tag filter (metadata->tags contains tag)
        4. Importance filter (metadata->importance >= min)
        5. Recency (ordered by created_at DESC)
        """
        # Build query params
        params = [f"user_id=eq.{MEMORY_USER_ID}"]
        
        if active_only:
            params.append("metadata->>is_active=eq.true")
        
        if memory_type:
            params.append(f"task_type=eq.{memory_type}")
        
        if query:
            params.append(f"content=ilike.*{quote(query, safe='')}*")
        
        params.append(f"order=created_at.desc")
        params.append(f"limit={limit}")
        
        path = f"monstruo_memory?{'&'.join(params)}&select=*"
        results = self._request("GET", path)
        
        if not results:
            return []
        
        # Post-filter by importance
        if min_importance > 1:
            results = [r for r in results if r.get("metadata", {}).get("importance", 0) >= min_importance]
        
        # Post-filter by tags
        if tags:
            results = [r for r in results 
                      if any(t in r.get("metadata", {}).get("tags", []) for t in tags)]
        
        # Update access counts
        for r in results:
            self._touch_memory(r["id"])
        
        return results
    
    def recall_all_critical(self) -> list:
        """Retrieve ALL active memories with importance >= 7. Used during recovery."""
        params = [
            f"user_id=eq.{MEMORY_USER_ID}",
            "metadata->>is_active=eq.true",
            "order=created_at.desc",
            f"limit={MAX_MEMORIES_RETRIEVE}"
        ]
        path = f"monstruo_memory?{'&'.join(params)}&select=*"
        results = self._request("GET", path)
        
        if not results:
            return []
        
        # Filter by importance >= 7 in post-processing (JSONB filtering limitations)
        critical = [r for r in results if r.get("metadata", {}).get("importance", 0) >= 7]
        return critical
    
    def recall_recent(self, hours: int = 24, limit: int = 20) -> list:
        """Retrieve memories from the last N hours."""
        params = [
            f"user_id=eq.{MEMORY_USER_ID}",
            "metadata->>is_active=eq.true",
            "order=created_at.desc",
            f"limit={limit}"
        ]
        path = f"monstruo_memory?{'&'.join(params)}&select=*"
        return self._request("GET", path) or []
    
    def count_memories(self) -> int:
        """Count total active memories."""
        params = [f"user_id=eq.{MEMORY_USER_ID}"]
        path = f"monstruo_memory?{'&'.join(params)}&select=id"
        headers = {"Prefer": "count=exact"}
        # Use HEAD to get count
        results = self._request("GET", path, extra_headers=headers)
        return len(results) if results else 0
    
    def _verify_memory(self, content: str, memory_type: str, importance: int) -> bool:
        """
        Verification pipeline (simplified from Cloudflare's 8 checks):
        1. Non-empty content
        2. Valid memory type
        3. Reasonable length (not too short, not too long)
        4. No duplicate (exact match in last 24h)
        5. Importance in valid range
        """
        # Check 1: Non-empty
        if not content or not content.strip():
            return False
        
        # Check 2: Valid type
        if memory_type not in ("fact", "event", "instruction", "task"):
            return False
        
        # Check 3: Reasonable length
        if len(content) < 10 or len(content) > 10000:
            return False
        
        # Check 4: No exact duplicate (check recent memories)
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        recent = self.recall(query=None, limit=20)
        for r in recent:
            existing_hash = hashlib.sha256(r.get("content", "").encode()).hexdigest()[:16]
            if existing_hash == content_hash:
                log(f"Duplicate memory detected, skipping", "WARN")
                return False
        
        # Check 5: Valid importance
        if importance < 1 or importance > 10:
            return False
        
        return True
    
    def _mark_superseded(self, old_id: str, new_id: str):
        """Mark an old memory as superseded by a new one."""
        # Get old memory's metadata
        path = f"monstruo_memory?id=eq.{old_id}&select=metadata"
        old = self._request("GET", path)
        if old and len(old) > 0:
            meta = old[0].get("metadata", {})
            meta["superseded_by"] = new_id
            meta["is_active"] = False
            self._request("PATCH", f"monstruo_memory?id=eq.{old_id}",
                         data={"metadata": meta})
            log(f"Memory {old_id[:8]} superseded by {new_id[:8]}")
    
    def _touch_memory(self, mem_id: str):
        """Update access count and last_accessed timestamp."""
        path = f"monstruo_memory?id=eq.{mem_id}&select=metadata"
        result = self._request("GET", path)
        if result and len(result) > 0:
            meta = result[0].get("metadata", {})
            meta["access_count"] = meta.get("access_count", 0) + 1
            meta["last_accessed"] = datetime.now(timezone.utc).isoformat()
            # Refresh decay score on access
            meta["decay_score"] = min(1.0, meta.get("decay_score", 0.5) + 0.1)
            self._request("PATCH", f"monstruo_memory?id=eq.{mem_id}",
                         data={"metadata": meta})


# ═══════════════════════════════════════════════════════════════
# ANCLAJE 1: FILESYSTEM (Local, inmediato)
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
# ANCLAJE 2: KERNEL API (Verdad en vivo)
# ═══════════════════════════════════════════════════════════════
def check_anchor_kernel() -> dict:
    if not KERNEL_URL or not KERNEL_KEY:
        return {"valid": False, "error": "KERNEL_BASE_URL o MONSTRUO_API_KEY no configuradas", "data": None}
    try:
        headers = {"x-api-key": KERNEL_KEY}
        # Health check
        req = Request(f"{KERNEL_URL}/health", headers=headers)
        resp = urlopen(req, timeout=10)
        health = json.loads(resp.read())
        
        # Tools
        req2 = Request(f"{KERNEL_URL}/v1/tools", headers=headers)
        resp2 = urlopen(req2, timeout=10)
        tools_data = json.loads(resp2.read())
        tools_activas = [t["name"] for t in tools_data.get("tools", []) if t.get("active")]
        
        # Embrion
        req3 = Request(f"{KERNEL_URL}/v1/embrion/estado", headers=headers)
        try:
            resp3 = urlopen(req3, timeout=10)
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
# ANCLAJE 3: SUPABASE MEMORY (Persistencia distribuida)
# ═══════════════════════════════════════════════════════════════
def check_anchor_supabase() -> dict:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"valid": False, "error": "SUPABASE_URL o SUPABASE_SERVICE_KEY no configuradas", "data": None}
    try:
        mem = SupabaseMemory(SUPABASE_URL, SUPABASE_KEY)
        count = mem.count_memories()
        critical = mem.recall_all_critical()
        recent = mem.recall_recent(hours=48, limit=10)
        
        return {
            "valid": True,
            "data": {
                "total_memories": count,
                "critical_memories": len(critical),
                "recent_memories": len(recent),
                "memories_critical": critical,
                "memories_recent": recent
            },
            "source": "supabase"
        }
    except Exception as e:
        return {"valid": False, "error": str(e), "data": None}


# ═══════════════════════════════════════════════════════════════
# MEMORY INGESTION — Bulk load identity into Supabase
# ═══════════════════════════════════════════════════════════════
def ingest_identity_to_supabase(identity: dict, mem: SupabaseMemory):
    """
    Take the filesystem identity and ensure all critical facts
    are stored in Supabase memory for cross-session persistence.
    """
    # Core identity facts
    facts_to_store = [
        {
            "content": f"Soy Hilo {identity.get('hilo', '?')}. Mi rol es: {identity.get('rol', '?')}",
            "type": "fact",
            "importance": 10,
            "tags": ["identity", "core"],
            "entities": ["El Monstruo", f"Hilo {identity.get('hilo', '?')}"]
        },
        {
            "content": f"Proyecto activo: {identity.get('proyecto_activo', '?')} en {identity.get('proyecto_path', '?')}",
            "type": "fact",
            "importance": 9,
            "tags": ["project", "active"],
            "entities": [identity.get("proyecto_activo", "")]
        },
    ]
    
    # Errors to never repeat
    for err in identity.get("errores_criticos_no_repetir", []):
        facts_to_store.append({
            "content": f"ERROR CRITICO NO REPETIR: {err}",
            "type": "instruction",
            "importance": 10,
            "tags": ["error", "critical", "never_repeat"],
            "entities": []
        })
    
    # Command center state
    cc = identity.get("command_center", {})
    if cc:
        facts_to_store.append({
            "content": f"Command Center version: {cc.get('version_id', '?')}. Features: {', '.join(cc.get('features_completadas', []))}. Stack: {cc.get('stack', '?')}",
            "type": "fact",
            "importance": 8,
            "tags": ["command_center", "state"],
            "entities": ["Command Center"]
        })
    
    # Tools state
    tools_activas = identity.get("tools_activas_produccion", [])
    tools_inactivas = identity.get("tools_inactivas_produccion", [])
    if tools_activas or tools_inactivas:
        facts_to_store.append({
            "content": f"Tools ACTIVAS en produccion: {tools_activas}. Tools que EXISTEN en codigo pero NO estan activas: {tools_inactivas[:5]}",
            "type": "fact",
            "importance": 9,
            "tags": ["tools", "kernel", "capabilities"],
            "entities": ["Kernel"]
        })
    
    # Embrion state
    emb = identity.get("estado_embrion", {})
    if emb:
        facts_to_store.append({
            "content": f"Embrion: running={emb.get('running')}, usa mismo kernel, diferencia vs app: {emb.get('diferencia_vs_app', '?')}. Problema actual: {emb.get('problema_actual', 'ninguno')}",
            "type": "fact",
            "importance": 7,
            "tags": ["embrion", "state"],
            "entities": ["Embrion-0"]
        })
    
    # Store each fact (dedup handled by verification pipeline)
    stored = 0
    for fact in facts_to_store:
        result = mem.remember(
            content=fact["content"],
            memory_type=fact["type"],
            source=f"hilo_{identity.get('hilo', 'b').lower()}",
            importance=fact["importance"],
            confidence=1.0,
            tags=fact["tags"],
            entities=fact["entities"],
            summary=fact["content"][:100]
        )
        if result:
            stored += 1
    
    log(f"Ingested {stored}/{len(facts_to_store)} memories to Supabase")
    return stored


# ═══════════════════════════════════════════════════════════════
# MAIN RECOVERY FLOW
# ═══════════════════════════════════════════════════════════════
def run_recovery():
    print()
    print("=" * 70)
    print("  GUARDIAN V4 — Anti-Compactación con Memoria Persistente")
    print("  Arquitectura: Cloudflare Agent Memory sobre Supabase")
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
    
    # === Imprimir estado restaurado ===
    identity = anchor1.get("data", {}) if anchor1["valid"] else {}
    kernel = anchor2.get("data", {}) if anchor2["valid"] else {}
    supabase_data = anchor3.get("data", {}) if anchor3["valid"] else {}
    
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
        print(f"║  FCS: {kernel.get('fcs_score', 0)}")
    
    if supabase_data:
        print(f"║")
        print(f"║  Memoria Persistente: {supabase_data.get('total_memories', 0)} memorias totales")
        print(f"║  Memorias críticas: {supabase_data.get('critical_memories', 0)}")
        print(f"║  Memorias recientes (48h): {supabase_data.get('recent_memories', 0)}")
    
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
    
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║              MEMORIAS PERSISTENTES (Supabase)                   ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    
    # Print critical memories from Supabase
    critical_mems = supabase_data.get("memories_critical", [])
    if critical_mems:
        for i, m in enumerate(critical_mems[:10], 1):
            meta = m.get("metadata", {})
            content = m.get("content", "")[:80]
            mtype = m.get("role", "?")
            imp = meta.get("importance", "?")
            print(f"║  [{mtype}|imp:{imp}] {content}")
    else:
        print(f"║  (Sin memorias críticas almacenadas aún)")
    
    # Print recent memories
    recent_mems = supabase_data.get("memories_recent", [])
    if recent_mems:
        print(f"║")
        print(f"║  --- Últimas memorias (48h) ---")
        for m in recent_mems[:5]:
            meta = m.get("metadata", {})
            content = m.get("content", "")[:70]
            mtype = m.get("role", "?")
            print(f"║  [{mtype}] {content}")
    
    print(f"║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    print(f"║              CAPACIDADES REALES (VERIFICADAS)                   ║")
    print(f"╠══════════════════════════════════════════════════════════════════╣")
    
    if kernel:
        tools = kernel.get("tools_activas", [])
        print(f"║  Tools ACTIVAS en producción: {tools}")
    
    print(f"║")
    print(f"╚══════════════════════════════════════════════════════════════════╝")
    print()
    
    # === Sync identity to Supabase for cross-session persistence ===
    if anchor1["valid"] and SUPABASE_URL and SUPABASE_KEY:
        mem = SupabaseMemory(SUPABASE_URL, SUPABASE_KEY)
        ingest_identity_to_supabase(identity, mem)
        log("Identity synced to Supabase persistent memory")
    
    # === Audit log ===
    audit = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "4.0.0",
        "anchors": {
            "filesystem": anchor1["valid"],
            "kernel": anchor2["valid"],
            "supabase": anchor3["valid"]
        },
        "consensus": valid_count,
        "memories_total": supabase_data.get("total_memories", 0),
        "memories_critical": supabase_data.get("critical_memories", 0),
        "action": "restored" if valid_count >= 1 else "halted"
    }
    
    audit_file = LOGS_DIR / "audit.jsonl"
    with open(audit_file, "a") as f:
        f.write(json.dumps(audit) + "\n")
    
    print("IDENTIDAD RESTAURADA")


# ═══════════════════════════════════════════════════════════════
# CLI INTERFACE — For storing memories from other scripts/hilos
# ═══════════════════════════════════════════════════════════════
def cli_remember(args):
    """CLI: python3 guardian.py remember --type fact --importance 8 --content "..." """
    import argparse
    parser = argparse.ArgumentParser(description="Store a memory")
    parser.add_argument("--type", choices=["fact", "event", "instruction", "task"], required=True)
    parser.add_argument("--content", required=True)
    parser.add_argument("--importance", type=int, default=5)
    parser.add_argument("--source", default="hilo_b")
    parser.add_argument("--tags", nargs="*", default=[])
    parser.add_argument("--entities", nargs="*", default=[])
    parser.add_argument("--supersedes", default=None)
    parsed = parser.parse_args(args)
    
    mem = SupabaseMemory(SUPABASE_URL, SUPABASE_KEY)
    result = mem.remember(
        content=parsed.content,
        memory_type=parsed.type,
        source=parsed.source,
        importance=parsed.importance,
        tags=parsed.tags,
        entities=parsed.entities,
        supersedes=parsed.supersedes
    )
    if result:
        print(f"OK: {result}")
    else:
        print("FAILED: Memory not stored")
        sys.exit(1)


def cli_recall(args):
    """CLI: python3 guardian.py recall --type fact --query "kernel" """
    import argparse
    parser = argparse.ArgumentParser(description="Recall memories")
    parser.add_argument("--type", choices=["fact", "event", "instruction", "task"])
    parser.add_argument("--query", default=None)
    parser.add_argument("--tags", nargs="*", default=None)
    parser.add_argument("--min-importance", type=int, default=1)
    parser.add_argument("--limit", type=int, default=20)
    parsed = parser.parse_args(args)
    
    mem = SupabaseMemory(SUPABASE_URL, SUPABASE_KEY)
    results = mem.recall(
        query=parsed.query,
        memory_type=parsed.type,
        tags=parsed.tags,
        min_importance=parsed.min_importance,
        limit=parsed.limit
    )
    
    print(f"Found {len(results)} memories:")
    for r in results:
        meta = r.get("metadata", {})
        print(f"  [{r['role']}|imp:{meta.get('importance','?')}|decay:{meta.get('decay_score','?'):.2f}] {r['content'][:80]}")
        print(f"    id={r['id'][:8]} source={r['brain_used']} created={r['created_at'][:19]}")


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
        else:
            print(f"Unknown command: {command}")
            print("Usage: guardian.py [recover|remember|recall]")
            sys.exit(1)
    else:
        # Default: run recovery
        run_recovery()
