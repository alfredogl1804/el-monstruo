"""
El Monstruo — La Memoria de Errores (Sprint 51, Capa 0.1)
==========================================================
Sistema persistente que registra cada fallo del kernel, detecta patrones,
y alimenta consultas pre-action para que el Monstruo no repita errores.

Filosofía:
    Obj #4 — No equivocarse dos veces. Cada fallo es lección. Cada lección
    es regla. Cada regla baja la probabilidad del siguiente fallo.

Arquitectura:
    nodes.execute → except → ErrorMemory.record(error, ctx)
                                    ↓
                              signature dedupe + embedding
                                    ↓
                              error_memory (Supabase + pgvector)
                                    ↑
    nodes.enrich → ErrorMemory.consult(intent, ctx) → reglas → system_prompt

Soberanía (Obj #12):
    Sin OPENAI_API_KEY (embeddings) → degrada a búsqueda exacta por module/action.
    Sin extensión pgvector → degrada a fila simple sin embedding.
    En ambos casos el sistema sigue funcionando con menos cobertura semántica.

Endpoints expuestos al Command Center:
    GET /v1/error-memory/recent?limit=20
    GET /v1/error-memory/patterns?min_confidence=0.7
    POST /v1/error-memory/{signature}/resolve  {resolution: "..."}

Sprint 51 — 2026-05-03
Autor: Hilo B (Cowork)
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

import structlog

logger = structlog.get_logger("kernel.error_memory")


# ── Configuración ──────────────────────────────────────────────────────

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"  # 1536 dims
DEFAULT_EMBEDDING_DIMS = 1536
DEFAULT_SIMILARITY_THRESHOLD = 0.78
DEFAULT_MIN_CONFIDENCE_TO_APPLY = 0.7
DEFAULT_PATTERN_MIN_CLUSTER_SIZE = 3
DEFAULT_RECENT_LIMIT = 20
DEFAULT_TOP_K_RULES = 3

# Sanitización de mensajes — quita ruido determinístico para que
# errores equivalentes hashen al mismo signature
RE_TIMESTAMP = re.compile(
    r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?'
)
RE_UUID = re.compile(
    r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',
    re.IGNORECASE,
)
RE_HEX_HASH = re.compile(r'\b[0-9a-f]{16,}\b', re.IGNORECASE)
RE_PATH_LINE = re.compile(r'(/[\w/.\-]+):(\d+)')
RE_INTEGER_ID = re.compile(r'\bid=\d+\b')
RE_PORT = re.compile(r':\d{4,5}\b')
RE_MULTI_SPACE = re.compile(r'\s+')
# Identificadores cortos comunes que cambian entre ejecuciones equivalentes:
# "run abc-123", "thread xyz_456", "job foo-bar", "req-789", "tx_abc"
RE_RUN_THREAD_ID = re.compile(
    r'\b(run|thread|job|tx|req|task|step|trace|session|plan)[\s_=:-]+[\w\-]{2,}\b',
    re.IGNORECASE,
)


# ── Excepciones con identidad ──────────────────────────────────────────

class ErrorMemoryDbNoDisponible(RuntimeError):
    """No se pudo conectar a Supabase para escribir/leer la memoria de errores.

    Causa: SUPABASE conexión rechazada o tabla error_memory no existe.
    Sugerencia: verificar migración 013 aplicada y SUPABASE_SERVICE_KEY en env.
    """


class ErrorMemoryEmbeddingFallido(RuntimeError):
    """Generación de embedding falló — modo degradado activo.

    Causa: OPENAI_API_KEY ausente o API rechazó la petición.
    Sugerencia: el sistema sigue operando con búsqueda por module/action
    exacto. Configurar OPENAI_API_KEY si quieres búsqueda semántica.
    """


class ErrorMemoryPgvectorFaltante(RuntimeError):
    """La extensión pgvector no está activa en Supabase.

    Causa: la migración 013 no se aplicó completa o el plan de Supabase
    no incluye pgvector.
    Sugerencia: ejecutar `CREATE EXTENSION vector;` o usar modo degradado.
    """


# ── Tipos ──────────────────────────────────────────────────────────────

@dataclass
class ErrorRule:
    """Regla aprendida desde un error registrado, lista para inyectar al prompt."""
    error_signature: str
    sanitized_message: str
    resolution: Optional[str]
    confidence: float
    similarity: float = 0.0
    occurrences: int = 1
    module: str = ""

    def to_prompt_hint(self) -> str:
        """Renderiza la regla como sugerencia para el system prompt."""
        confianza_pct = int(self.confidence * 100)
        prefix = (
            f"⚠ Error similar previo (confianza {confianza_pct}%, "
            f"visto {self.occurrences}x"
        )
        if self.module:
            prefix += f", módulo {self.module}"
        prefix += f"): {self.sanitized_message[:200]}"
        if self.resolution:
            prefix += f"\n  → Resolución conocida: {self.resolution}"
        return prefix


@dataclass
class ErrorPattern:
    """Patrón agregado detectado por el cron de aggregate_patterns()."""
    pattern_name: str
    description: str
    signature_cluster: list[str]
    confidence: float
    suggested_rule: Optional[str]
    detected_at: str


# ── Implementación ────────────────────────────────────────────────────

class ErrorMemory:
    """Registro persistente de errores + consulta semántica pre-action.

    Métodos principales:
        record(error, context)      → registra fallo (post-error hook)
        consult(intent, context)    → busca reglas (pre-action hook)
        aggregate_patterns()        → cron 24h
        get_recent(limit)           → endpoint /v1/error-memory/recent
        get_patterns()              → endpoint /v1/error-memory/patterns
        resolve(signature, text)    → marca como resuelto
        adjust_confidence(sig, dx)  → tuning de confianza

    Ejemplo:
        em = ErrorMemory(db=supabase, embedding_client=openai_async)
        await em.initialize()
        await em.record(exc, {"module": "kernel.task_planner", "action": "execute_step"})
        rules = await em.consult("ejecutar tool github", {"module": "kernel.tool_dispatch"})
        for r in rules:
            system_prompt += "\\n" + r.to_prompt_hint()
    """

    TABLE = "error_memory"
    TABLE_PATTERNS = "error_memory_patterns"

    def __init__(
        self,
        db: Any = None,
        embedding_client: Any = None,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        min_confidence_to_apply: float = DEFAULT_MIN_CONFIDENCE_TO_APPLY,
    ):
        self._db = db
        self._embedding_client = embedding_client
        self._similarity_threshold = similarity_threshold
        self._min_confidence = min_confidence_to_apply
        self._initialized = False
        self._has_pgvector = False

    async def initialize(self) -> bool:
        """Verifica conexión DB y disponibilidad de pgvector. Idempotente."""
        if not self._db or not getattr(self._db, "connected", False):
            logger.warning(
                "error_memory_no_db",
                hint="DB no disponible, ErrorMemory deshabilitada",
            )
            return False
        try:
            # Probe: ¿la tabla existe?
            _ = await self._db.select(self.TABLE, columns="id", limit=1)
            self._initialized = True
            self._has_pgvector = await self._probe_pgvector()
            logger.info(
                "error_memory_initialized",
                pgvector=self._has_pgvector,
                embedding_active=self._embedding_client is not None,
                threshold=self._similarity_threshold,
                min_confidence=self._min_confidence,
            )
            return True
        except Exception as e:
            logger.error("error_memory_init_failed", error=str(e))
            return False

    @property
    def initialized(self) -> bool:
        return self._initialized

    @property
    def has_pgvector(self) -> bool:
        return self._has_pgvector

    # ── API pública: record / consult / aggregate ──────────────────

    async def record(
        self,
        error: Exception,
        context: dict[str, Any],
    ) -> Optional[str]:
        """Registra un error. Devuelve error_signature.

        Si el signature ya existe: incrementa occurrences, actualiza last_seen_at.
        Si no: crea fila nueva con embedding (best-effort).

        Args:
            error: la excepción capturada
            context: dict con al menos `module`. Idealmente también `action`,
                `run_id`, `thread_id`, `tool_calls`.

        Returns:
            error_signature (32 chars hex) o None si falló el registro.
        """
        if not self._initialized:
            return None

        error_type = type(error).__name__
        module = context.get("module", "desconocido")
        action = context.get("action", "")
        raw_message = str(error)[:2000]
        sanitized = self._sanitize_message(raw_message)
        signature = self._compute_signature(error_type, module, sanitized)
        now = datetime.now(timezone.utc).isoformat()

        try:
            existing = await self._db.select(
                self.TABLE,
                columns="id, occurrences",
                filters={"error_signature": signature},
                limit=1,
            )

            if existing:
                row = existing[0]
                new_count = int(row.get("occurrences", 1)) + 1
                await self._db.update(
                    self.TABLE,
                    data={
                        "occurrences": new_count,
                        "last_seen_at": now,
                    },
                    filters={"error_signature": signature},
                )
                logger.info(
                    "error_memory_recorded",
                    signature=signature[:12],
                    occurrences=new_count,
                    duplicate=True,
                )
                return signature

            embedding = await self._embed_safe(sanitized)
            data = {
                "error_signature": signature,
                "error_type": error_type,
                "module": module,
                "action": action,
                "message": raw_message,
                "sanitized_message": sanitized,
                "context": self._truncate_context(context),
                "occurrences": 1,
                "first_seen_at": now,
                "last_seen_at": now,
                "confidence": 0.5,
                "status": "open",
            }
            if embedding is not None:
                data["embedding"] = embedding

            await self._db.insert(self.TABLE, data=data)
            logger.info(
                "error_memory_recorded",
                signature=signature[:12],
                module=module,
                action=action,
                error_type=error_type,
                duplicate=False,
                has_embedding=embedding is not None,
            )
            return signature
        except Exception as e:
            logger.error(
                "error_memory_record_failed",
                error=str(e),
                signature=signature[:12],
            )
            return None

    async def consult(
        self,
        intent: str,
        context: dict[str, Any],
        top_k: int = DEFAULT_TOP_K_RULES,
    ) -> list[ErrorRule]:
        """Busca errores similares al intent actual. Devuelve reglas aplicables.

        Modo semántico (pgvector + embeddings activos):
            cosine similarity sobre el embedding del intent+context.
        Modo degradado (sin pgvector o sin embeddings):
            filtro por module exacto, opcionalmente priorizado por action.

        Solo retorna reglas con confidence ≥ self._min_confidence.

        Args:
            intent: descripción de lo que el sistema va a intentar.
            context: dict con al menos `module`. Idealmente también `action`.
            top_k: cuántas reglas retornar como máximo.

        Returns:
            lista de ErrorRule ordenada por relevancia descendente.
        """
        if not self._initialized:
            return []

        try:
            # Modo semántico
            if self._has_pgvector and self._embedding_client:
                rules = await self._consult_semantic(intent, context, top_k)
                if rules is not None:
                    return rules
                # Fallback a degradado si embedding falló

            # Modo degradado
            return await self._consult_exact(context, top_k)
        except Exception as e:
            logger.warning("error_memory_consult_failed", error=str(e))
            return []

    async def aggregate_patterns(self) -> list[ErrorPattern]:
        """Cron 24h: detecta clusters semánticos y propone reglas.

        Estrategia v1 (Sprint 51):
            - Agrupa errores abiertos por (error_type, module).
            - Cluster con ≥ DEFAULT_PATTERN_MIN_CLUSTER_SIZE → patrón candidato.
            - Confidence inicial 0.5; sube por trigger update_error_pattern_validated.

        v2 (post-Sprint 51):
            clustering semántico por embedding (DBSCAN sobre vectores).
        """
        if not self._initialized:
            return []
        try:
            rows = await self._db.select(
                self.TABLE,
                columns="error_signature, error_type, module, occurrences",
                filters={"status": "open"},
                limit=1000,
            )
            if not rows:
                return []

            clusters: dict[tuple[str, str], list[dict]] = {}
            for r in rows:
                key = (r.get("error_type", ""), r.get("module", ""))
                clusters.setdefault(key, []).append(r)

            patterns: list[ErrorPattern] = []
            now_iso = datetime.now(timezone.utc).isoformat()

            for (etype, mod), members in clusters.items():
                if len(members) < DEFAULT_PATTERN_MIN_CLUSTER_SIZE:
                    continue
                pattern_name = f"{etype}_{mod}_recurrente".replace(".", "_")
                total_occurrences = sum(
                    int(m.get("occurrences", 1)) for m in members
                )
                description = (
                    f"{len(members)} errores únicos del tipo {etype} "
                    f"en módulo {mod}. Total ocurrencias: {total_occurrences}."
                )
                pattern = ErrorPattern(
                    pattern_name=pattern_name,
                    description=description,
                    signature_cluster=[
                        m["error_signature"] for m in members
                    ],
                    confidence=0.5,
                    suggested_rule=None,
                    detected_at=now_iso,
                )
                patterns.append(pattern)

                await self._db.upsert(
                    self.TABLE_PATTERNS,
                    data={
                        "pattern_name": pattern_name,
                        "description": description,
                        "signature_cluster": pattern.signature_cluster,
                        "confidence": pattern.confidence,
                        "suggested_rule": pattern.suggested_rule,
                    },
                    on_conflict="pattern_name",
                )

            logger.info(
                "error_memory_patterns_aggregated",
                clusters_evaluated=len(clusters),
                patterns_promoted=len(patterns),
            )
            return patterns
        except Exception as e:
            logger.error("error_memory_aggregate_failed", error=str(e))
            return []

    # ── API para endpoints ─────────────────────────────────────────

    async def get_recent(self, limit: int = DEFAULT_RECENT_LIMIT) -> list[dict]:
        """Últimos errores para `/v1/error-memory/recent`."""
        if not self._initialized:
            return []
        rows = await self._db.select(
            self.TABLE,
            columns=(
                "error_signature, error_type, module, action, "
                "sanitized_message, occurrences, first_seen_at, "
                "last_seen_at, confidence, status, resolution"
            ),
            order_by="last_seen_at",
            order_desc=True,
            limit=max(1, min(limit, 100)),
        )
        return rows or []

    async def get_patterns(
        self,
        min_confidence: float = 0.7,
        limit: int = 50,
    ) -> list[dict]:
        """Patrones detectados para `/v1/error-memory/patterns`.

        Filtra por confidence en Python (el cliente Supabase del proyecto
        no soporta operadores como `gte` directamente en filters).
        """
        if not self._initialized:
            return []
        rows = await self._db.select(
            self.TABLE_PATTERNS,
            columns="*",
            order_by="detected_at",
            order_desc=True,
            limit=max(1, min(limit * 2, 200)),
        )
        if not rows:
            return []
        filtrados = [
            r for r in rows
            if float(r.get("confidence", 0)) >= min_confidence
        ]
        return filtrados[:limit]

    async def resolve(self, signature: str, resolution: str) -> bool:
        """Marca un error como resuelto con una resolución conocida.

        Sube confidence a 0.8 (presumiendo que el operador validó la regla).
        """
        if not self._initialized:
            return False
        try:
            await self._db.update(
                self.TABLE,
                data={
                    "status": "resolved",
                    "resolution": resolution[:2000],
                    "confidence": 0.8,
                },
                filters={"error_signature": signature},
            )
            logger.info(
                "error_memory_resolved",
                signature=signature[:12],
                resolution_chars=len(resolution),
            )
            return True
        except Exception as e:
            logger.error(
                "error_memory_resolve_failed",
                error=str(e),
                signature=signature[:12],
            )
            return False

    async def adjust_confidence(
        self,
        signature: str,
        delta: float,
    ) -> Optional[float]:
        """Ajusta confidence acotado a [0.1, 1.0]. Devuelve nuevo valor."""
        if not self._initialized:
            return None
        try:
            row = await self._db.select(
                self.TABLE,
                columns="confidence",
                filters={"error_signature": signature},
                limit=1,
            )
            if not row:
                return None
            current = float(row[0].get("confidence", 0.5))
            new_value = max(0.1, min(1.0, current + delta))
            await self._db.update(
                self.TABLE,
                data={"confidence": round(new_value, 2)},
                filters={"error_signature": signature},
            )
            logger.info(
                "error_memory_confidence_adjusted",
                signature=signature[:12],
                old=current,
                new=new_value,
                delta=delta,
            )
            return new_value
        except Exception as e:
            logger.warning("error_memory_adjust_failed", error=str(e))
            return None

    # ── Helpers internos ───────────────────────────────────────────

    async def _consult_semantic(
        self,
        intent: str,
        context: dict[str, Any],
        top_k: int,
    ) -> Optional[list[ErrorRule]]:
        """Consulta vía pgvector. Retorna None si falla embedding."""
        query_text = " ".join([
            intent,
            context.get("module", ""),
            context.get("action", ""),
        ]).strip()
        embedding = await self._embed_safe(query_text)
        if embedding is None:
            return None
        try:
            rows = await self._db.rpc(
                "search_similar_errors",
                params={
                    "query_embedding": embedding,
                    "match_threshold": self._similarity_threshold,
                    "match_count": top_k,
                },
            )
        except Exception as e:
            logger.warning(
                "error_memory_rpc_failed",
                error=str(e),
                fallback="modo_degradado",
            )
            return None
        rules = [
            self._row_to_rule(r) for r in (rows or [])
            if float(r.get("confidence", 0)) >= self._min_confidence
        ]
        return rules

    async def _consult_exact(
        self,
        context: dict[str, Any],
        top_k: int,
    ) -> list[ErrorRule]:
        """Consulta degradada: filtro exacto por module."""
        module = context.get("module", "")
        action = context.get("action", "")
        if not module:
            return []
        rows = await self._db.select(
            self.TABLE,
            columns=(
                "error_signature, sanitized_message, resolution, "
                "confidence, occurrences, module, action"
            ),
            filters={"module": module, "status": "open"},
            limit=top_k * 3,
        )
        if not rows:
            return []
        rules = [
            self._row_to_rule(r) for r in rows
            if float(r.get("confidence", 0)) >= self._min_confidence
        ]
        # Priorizar matches exactos de action
        if action:
            rules.sort(key=lambda r: 0 if action in r.sanitized_message else 1)
        return rules[:top_k]

    async def _probe_pgvector(self) -> bool:
        """Verifica si pgvector está activo. Best-effort sin fallar."""
        try:
            # Intento directo: una RPC simple
            test_vec = [0.0] * DEFAULT_EMBEDDING_DIMS
            result = await self._db.rpc(
                "search_similar_errors",
                params={
                    "query_embedding": test_vec,
                    "match_threshold": 0.99,
                    "match_count": 1,
                },
            )
            # Si llegamos aquí sin excepción, la función existe
            _ = result
            return True
        except Exception as e:
            logger.info(
                "error_memory_pgvector_no_disponible",
                error=str(e)[:100],
                hint="modo degradado activo (búsqueda exacta)",
            )
            return False

    def _sanitize_message(self, message: str) -> str:
        """Quita IDs/timestamps/paths para que mensajes equivalentes hashen igual."""
        s = message
        s = RE_TIMESTAMP.sub("<TS>", s)
        s = RE_UUID.sub("<UUID>", s)
        s = RE_HEX_HASH.sub("<HASH>", s)
        s = RE_PATH_LINE.sub(r"\1:<LINE>", s)
        s = RE_INTEGER_ID.sub("id=<N>", s)
        s = RE_RUN_THREAD_ID.sub(lambda m: f"{m.group(1).lower()} <ID>", s)
        s = RE_PORT.sub(":<PORT>", s)
        s = RE_MULTI_SPACE.sub(" ", s).strip()
        return s[:1000]

    def _compute_signature(
        self,
        error_type: str,
        module: str,
        sanitized: str,
    ) -> str:
        """SHA-256 truncado de los tres componentes."""
        h = hashlib.sha256()
        h.update(error_type.encode())
        h.update(b"|")
        h.update(module.encode())
        h.update(b"|")
        h.update(sanitized.encode())
        return h.hexdigest()[:32]

    def _truncate_context(self, context: dict) -> dict:
        """Trunca el context para no almacenar payloads gigantes en JSONB."""
        out: dict[str, Any] = {}
        for k, v in context.items():
            if k in ("module", "action"):
                # Ya están como columnas dedicadas
                continue
            if isinstance(v, str):
                out[k] = (v[:500] + "…[truncado]") if len(v) > 500 else v
            elif isinstance(v, (list, dict)):
                s = str(v)
                out[k] = (
                    {"_truncated": True, "preview": s[:500]}
                    if len(s) > 500 else v
                )
            elif isinstance(v, (int, float, bool)) or v is None:
                out[k] = v
            else:
                out[k] = str(v)[:200]
        return out

    async def _embed_safe(self, text: str) -> Optional[list[float]]:
        """Genera embedding. Si falla, retorna None — modo degradado."""
        if not self._embedding_client:
            return None
        try:
            resp = await self._embedding_client.embeddings.create(
                model=DEFAULT_EMBEDDING_MODEL,
                input=text[:8000],
            )
            return list(resp.data[0].embedding)
        except Exception as e:
            logger.warning(
                "error_memory_embedding_failed",
                error=str(e),
                text_chars=len(text),
            )
            return None

    def _row_to_rule(self, row: dict) -> ErrorRule:
        return ErrorRule(
            error_signature=row.get("error_signature", ""),
            sanitized_message=row.get("sanitized_message", ""),
            resolution=row.get("resolution"),
            confidence=float(row.get("confidence", 0.5)),
            similarity=float(row.get("similarity", 0.0)),
            occurrences=int(row.get("occurrences", 1)),
            module=row.get("module", ""),
        )


# ── Helpers de bootstrap ───────────────────────────────────────────────

def build_embedding_client():
    """Crea cliente de embeddings si OPENAI_API_KEY está disponible.

    Soberanía: si falta la key, devuelve None y ErrorMemory degrada
    a búsqueda por module/action exacto. El sistema sigue operando.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.info(
            "error_memory_embeddings_disabled",
            hint="OPENAI_API_KEY no presente, modo degradado activo",
        )
        return None
    try:
        from openai import AsyncOpenAI
        return AsyncOpenAI(api_key=api_key)
    except ImportError:
        logger.warning(
            "error_memory_openai_missing",
            hint="paquete openai no instalado, modo degradado activo",
        )
        return None
