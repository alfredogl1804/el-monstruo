"""
Memento ContaminationDetector — Sprint Memento Bloque 6 (Capa Memoria Soberana v1.0)
====================================================================================

Heurística magna que detecta cuando un hilo opera con contexto compactado
obsoleto ANTES de ejecutar una operación crítica. Reemplaza la detección
manual humana de los 3 falsos positivos del 2026-05-04 (TiDB gateway01
fantasma, Radar legacy, migration "pendiente").

Capa Memento: este módulo aplica el principio "no confíes en el contexto;
verifica contra evidencia forense en repo + histórico Supabase".

DECISIONES DE DISEÑO (alineadas con green light Cowork B6):

1. **Conservador** — falso positivo es PEOR que falso negativo en esta
   capa. Severidad HIGH solo cuando hay evidencia forense reproducible
   (hash existió en commits previos, validation_id previa contradictoria).

2. **Async-first con timeout global** (default 500 ms). Si una heurística
   tarda más, se loguea y se devuelve `[]` (degraded). El detector NUNCA
   bloquea la respuesta del endpoint /v1/memento/validate.

3. **Heurísticas independientes** ejecutadas en `asyncio.gather` con
   `return_exceptions=True`. Si una falla, las otras siguen.

4. **Shadow mode v1.0** — el detector calcula findings; el endpoint los
   adjunta a la response y los persiste, pero NO altera `proceed`. Si en
   1-2 semanas el false positive rate < 5%, en B7 (o sprint posterior)
   se activa el bloqueo en HIGH.

5. **Sin dependencias nuevas** — usa stdlib (asyncio, subprocess) +
   psycopg2/SDK Supabase ya disponible en `app.state.db`.

HEURÍSTICAS:

- **H1** — `credential_hash_obsolete` — `context_used.credential_hash_first_8`
  NO matchea source_of_truth actual, PERO ese hash existió en algún commit
  previo del repo. Señal: contexto compactado heredando credenciales viejas.
  Severidad: HIGH.

- **H2** — `host_divergent_with_history` — la última `memento_validation`
  exitosa de este `hilo_id` para esta `operation` fue contra host X, pero
  ahora declara host Y, y la diferencia es estructural (no solo subdomain).
  Señal: cluster fantasma o contexto contaminado.
  Severidad: HIGH.

- **H3** — `operation_without_recent_preflight` — el hilo ejecuta operación
  crítica pero NO pasó por /v1/memento/validate en las últimas N (default 20)
  validaciones registradas en esta ventana de tiempo (default 60 min).
  Señal: hilo operando ciego (es informativo, NO sospecha hostil).
  Severidad: MEDIUM.

REFS:
    - bridge/sprint_memento_preinvestigation/spec_sprint_memento.md
    - kernel/memento/validator.py (donde se llama el detector)
    - scripts/020_memento_contamination_columns.sql (migration de índices)
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ===========================================================================
# Tipos públicos
# ===========================================================================


@dataclass
class ContaminationFinding:
    """Un finding de contaminación detectada por una heurística."""

    rule_id: str  # "H1" | "H2" | "H3"
    severity: str  # "HIGH" | "MEDIUM" | "LOW"
    evidence: Dict[str, Any]  # datos forenses reproducibles
    recommendation: str  # acción sugerida al hilo
    validation_id_ref: Optional[str] = None  # validation_id contradictoria si aplica

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContaminationReport:
    """Resultado agregado del detector."""

    findings: List[ContaminationFinding] = field(default_factory=list)
    detector_runtime_ms: float = 0.0
    timed_out_rules: List[str] = field(default_factory=list)
    skipped_rules: List[str] = field(default_factory=list)  # rules deshabilitadas o sin datos

    @property
    def has_warning(self) -> bool:
        """True si hay al menos un finding (cualquier severidad)."""
        return len(self.findings) > 0

    @property
    def has_high_severity(self) -> bool:
        return any(f.severity == "HIGH" for f in self.findings)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "findings": [f.to_dict() for f in self.findings],
            "detector_runtime_ms": round(self.detector_runtime_ms, 2),
            "timed_out_rules": self.timed_out_rules,
            "skipped_rules": self.skipped_rules,
            "has_warning": self.has_warning,
            "has_high_severity": self.has_high_severity,
        }


# ===========================================================================
# Detector
# ===========================================================================


class ContaminationDetector:
    """
    Heurística magna que evalúa si un contexto declarado por un hilo está
    contaminado (i.e., heredado de un contexto compactado obsoleto).

    Constructor:
        db: cliente Supabase async (espera método `select(table, ...)`).
            Si es None, H2 y H3 quedan deshabilitadas.
        repo_root: raíz del repo git para H1 (default = cwd).
            Si no es git repo, H1 queda deshabilitada.
        timeout_ms_per_rule: timeout por heurística (default 200 ms).
        global_timeout_ms: timeout global del detector (default 500 ms).
        h3_lookback_minutes: ventana para H3 (default 60 min).
        h3_min_recent_validations: si el hilo tiene >= N validaciones recientes
            sin esta operation, dispara H3 (default 5; threshold conservador
            para evitar falsos positivos en hilos nuevos).

    Uso:
        detector = ContaminationDetector(db=db_client, repo_root="/path/to/repo")
        report = await detector.detect(
            hilo_id="hilo_manus_ticketlike",
            operation="sql_against_production",
            context_used={"host": "...", "credential_hash_first_8": "abc123"},
            current_source_of_truth={"host": "...", "credential_hash_first_8": "xyz789"},
            current_validation_id="mv_2026-05-05T01:30_xxx",
        )
        if report.has_high_severity:
            # logear, no bloquear (shadow mode v1.0)
            ...
    """

    def __init__(
        self,
        db: Any = None,
        repo_root: Optional[str] = None,
        timeout_ms_per_rule: int = 200,
        global_timeout_ms: int = 500,
        h3_lookback_minutes: int = 60,
        h3_min_recent_validations: int = 5,
    ):
        self._db = db
        self._repo_root = repo_root or os.getcwd()
        self._timeout_per_rule = timeout_ms_per_rule / 1000.0
        self._global_timeout = global_timeout_ms / 1000.0
        self._h3_lookback_minutes = h3_lookback_minutes
        self._h3_min_recent_validations = h3_min_recent_validations

    # ---------------------------------------------------------------------
    # Entrypoint público
    # ---------------------------------------------------------------------

    async def detect(
        self,
        *,
        hilo_id: str,
        operation: str,
        context_used: Dict[str, Any],
        current_source_of_truth: Optional[Dict[str, Any]] = None,
        current_validation_id: Optional[str] = None,
    ) -> ContaminationReport:
        """
        Ejecuta las 3 heurísticas en paralelo con timeout global.

        Retorna ContaminationReport con findings (puede ser vacío).
        """
        start_ts = time.monotonic()
        report = ContaminationReport()

        # Construir tareas
        tasks: List[asyncio.Task] = []
        rule_names: List[str] = []

        # H1 — credential hash obsoleto (requiere current_source_of_truth)
        if current_source_of_truth is not None:
            tasks.append(
                asyncio.create_task(
                    self._safe_rule(
                        "H1",
                        self._rule_h1_credential_hash_obsolete(
                            context_used, current_source_of_truth
                        ),
                    )
                )
            )
            rule_names.append("H1")
        else:
            report.skipped_rules.append("H1")

        # H2 — host divergente con histórico (requiere db)
        if self._db is not None:
            tasks.append(
                asyncio.create_task(
                    self._safe_rule(
                        "H2",
                        self._rule_h2_host_divergent(
                            hilo_id, operation, context_used, current_validation_id
                        ),
                    )
                )
            )
            rule_names.append("H2")
        else:
            report.skipped_rules.append("H2")

        # H3 — sin pre-flight reciente (requiere db)
        if self._db is not None:
            tasks.append(
                asyncio.create_task(
                    self._safe_rule(
                        "H3",
                        self._rule_h3_no_recent_preflight(
                            hilo_id, operation, current_validation_id
                        ),
                    )
                )
            )
            rule_names.append("H3")
        else:
            report.skipped_rules.append("H3")

        if not tasks:
            report.detector_runtime_ms = (time.monotonic() - start_ts) * 1000
            return report

        # Esperar todas con timeout global usando asyncio.wait
        # (para distinguir done vs pending sin perder la info por el cancel)
        done, pending = await asyncio.wait(tasks, timeout=self._global_timeout)

        # Mapear pending a sus rule_names ANTES de cancelar
        if pending:
            pending_rule_names = [
                rn for rn, t in zip(rule_names, tasks) if t in pending
            ]
            for t in pending:
                t.cancel()
            report.timed_out_rules = pending_rule_names
            logger.warning(
                "contamination_detector_global_timeout timeout_ms=%s timed_out=%s",
                int(self._global_timeout * 1000),
                report.timed_out_rules,
            )

        # Procesar las que terminaron a tiempo
        for rule_name, t in zip(rule_names, tasks):
            if t not in done:
                continue
            try:
                res = t.result()
            except Exception as exc:
                logger.warning(
                    "contamination_rule_error rule=%s error=%s",
                    rule_name,
                    exc,
                )
                continue
            if res is None:
                continue
            # res es Optional[ContaminationFinding]
            report.findings.append(res)

        report.detector_runtime_ms = (time.monotonic() - start_ts) * 1000
        return report

    # ---------------------------------------------------------------------
    # Wrapper con timeout per-rule
    # ---------------------------------------------------------------------

    async def _safe_rule(self, rule_id: str, coro) -> Optional[ContaminationFinding]:
        """Aplica timeout per-rule + atrapa excepciones (no propagan)."""
        try:
            return await asyncio.wait_for(coro, timeout=self._timeout_per_rule)
        except asyncio.TimeoutError:
            logger.warning(
                "contamination_rule_timeout rule=%s timeout_ms=%s",
                rule_id,
                int(self._timeout_per_rule * 1000),
            )
            return None
        except Exception as exc:
            logger.warning(
                "contamination_rule_exception rule=%s error=%s",
                rule_id,
                exc,
            )
            return None

    # ---------------------------------------------------------------------
    # H1 — credential_hash obsoleto detectable en git history
    # ---------------------------------------------------------------------

    async def _rule_h1_credential_hash_obsolete(
        self,
        context_used: Dict[str, Any],
        current_source_of_truth: Dict[str, Any],
    ) -> Optional[ContaminationFinding]:
        """
        H1 — Si el hash declarado NO matchea la fuente actual, escanea git log
        en busca de ese hash. Si aparece en algún commit previo, hay evidencia
        forense de contexto compactado heredando credencial vieja.

        Threshold conservador:
        - Solo evalúa si hay `credential_hash_first_8` (o `credential_hash`)
          en context_used.
        - Solo evalúa si hay un campo equivalente en current_source_of_truth.
        - Hash debe tener >= 8 chars hex (no bombea git con strings genéricos).
        - Solo dispara si `git rev-list HEAD --grep="<hash>"` devuelve >= 1 commit.
        """
        # Extraer hashes
        ctx_hash = (
            context_used.get("credential_hash_first_8")
            or context_used.get("credential_hash")
            or ""
        ).strip()
        sot_hash = (
            current_source_of_truth.get("credential_hash_first_8")
            or current_source_of_truth.get("credential_hash")
            or ""
        ).strip()

        if not ctx_hash or not sot_hash:
            return None  # nada que comparar

        if ctx_hash == sot_hash:
            return None  # match — no hay obsolescencia

        # Sanity: hash debe ser hex >= 8 chars (anti-falsos positivos)
        if len(ctx_hash) < 8 or not all(c in "0123456789abcdefABCDEF" for c in ctx_hash):
            return None

        # Ejecutar git log con grep en async subprocess
        try:
            proc = await asyncio.create_subprocess_exec(
                "git",
                "-C",
                self._repo_root,
                "log",
                "--all",
                "--format=%H",
                f"--grep={ctx_hash}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _stderr = await proc.communicate()
        except (FileNotFoundError, OSError) as exc:
            logger.debug("h1_git_unavailable error=%s", exc)
            return None

        if proc.returncode != 0:
            return None

        commits = [c for c in stdout.decode("utf-8", errors="ignore").strip().split("\n") if c]
        if not commits:
            return None  # hash no aparece en historia → no es legacy del repo

        # FORENSE positiva: hash declarado existió en N commits previos pero no es el actual
        return ContaminationFinding(
            rule_id="H1",
            severity="HIGH",
            evidence={
                "context_hash": ctx_hash,
                "current_source_of_truth_hash": sot_hash,
                "matching_commits_count": len(commits),
                "first_matching_commit": commits[0][:12] if commits else None,
                "hint": "El hash declarado existió en commits previos pero ya no es la verdad actual",
            },
            recommendation=(
                "Re-leer credenciales desde la fuente de verdad (credentials.md o "
                "Railway env). Posible contexto compactado heredando credencial rotada."
            ),
        )

    # ---------------------------------------------------------------------
    # H2 — host divergente vs última validación exitosa
    # ---------------------------------------------------------------------

    async def _rule_h2_host_divergent(
        self,
        hilo_id: str,
        operation: str,
        context_used: Dict[str, Any],
        current_validation_id: Optional[str],
    ) -> Optional[ContaminationFinding]:
        """
        H2 — Compara el `host` declarado contra el host de la última validación
        OK del mismo hilo + operation. Si difieren estructuralmente (no solo
        subdomain trivial), dispara HIGH.

        Threshold conservador:
        - Solo evalúa si context_used tiene `host`.
        - Solo evalúa si hay >= 1 validación previa OK del mismo (hilo, operation).
        - "Diferencia estructural" = los últimos 3 segmentos del FQDN difieren.
          Cambios de subdomain trivial (e.g., gateway01 → gateway05 dentro del
          mismo cluster TiDB) NO se consideran estructurales para minimizar
          falsos positivos. PERO — paradoja del incidente TiDB: gateway01 vs
          gateway05 SÍ era contaminación. Por eso evaluamos también si el
          hostname difiere en CARACTERES NUMÉRICOS DENTRO del primer segmento
          y la última validación OK fue hace > 24h (señal de "yo creí que era
          este host pero el hilo lleva días desconectado").
        """
        ctx_host = (context_used.get("host") or "").strip().lower()
        if not ctx_host:
            return None

        # Query Supabase: última validación OK del mismo hilo+operation que NO sea la actual
        try:
            rows = await self._db.select(
                "memento_validations",
                filters={
                    "hilo_id": hilo_id,
                    "operation": operation,
                    "validation_status": "ok",
                },
                order_by="ts.desc",
                limit=5,  # tomamos 5 por si la primera es la actual
            )
        except Exception as exc:
            logger.debug("h2_db_query_failed error=%s", exc)
            return None

        if not rows:
            return None

        # Encontrar la primera validación previa que NO sea la actual
        previous: Optional[Dict[str, Any]] = None
        for row in rows:
            if current_validation_id and row.get("validation_id") == current_validation_id:
                continue
            previous = row
            break

        if previous is None:
            return None

        prev_ctx = previous.get("context_used") or {}
        prev_host = (prev_ctx.get("host") or "").strip().lower()
        if not prev_host or prev_host == ctx_host:
            return None  # match exacto o sin host previo → no hay divergencia

        # Análisis estructural
        ctx_segments = ctx_host.split(".")
        prev_segments = prev_host.split(".")

        # Caso 1: difieren los últimos 3 segmentos (FQDN root cambia)
        # e.g., "gateway05.us-east-1.prod.aws.tidbcloud.com" vs "...other.cloud.com"
        ctx_root = ".".join(ctx_segments[-3:]) if len(ctx_segments) >= 3 else ctx_host
        prev_root = ".".join(prev_segments[-3:]) if len(prev_segments) >= 3 else prev_host
        structural_change = ctx_root != prev_root

        # Caso 2: gateway01 vs gateway05 (mismo cluster pero numerador difiere
        # en el primer segmento) — solo si la última validación es vieja
        first_seg_numeric_change = False
        if not structural_change and len(ctx_segments) > 0 and len(prev_segments) > 0:
            ctx_first = ctx_segments[0]
            prev_first = prev_segments[0]
            if ctx_first != prev_first:
                # ¿Solo cambia un sufijo numérico?
                ctx_alpha = "".join(c for c in ctx_first if c.isalpha())
                prev_alpha = "".join(c for c in prev_first if c.isalpha())
                ctx_num = "".join(c for c in ctx_first if c.isdigit())
                prev_num = "".join(c for c in prev_first if c.isdigit())
                if ctx_alpha == prev_alpha and ctx_alpha and ctx_num != prev_num:
                    # Es un cambio numérico dentro del cluster.
                    # Solo flag si la última validación es > 24h vieja.
                    prev_ts_str = previous.get("ts") or ""
                    prev_ts = self._parse_iso_ts(prev_ts_str)
                    if prev_ts is not None:
                        from datetime import datetime, timezone

                        age_hours = (datetime.now(timezone.utc).timestamp() - prev_ts) / 3600
                        if age_hours > 24:
                            first_seg_numeric_change = True

        if not structural_change and not first_seg_numeric_change:
            return None

        return ContaminationFinding(
            rule_id="H2",
            severity="HIGH",
            evidence={
                "current_host": ctx_host,
                "previous_host": prev_host,
                "previous_validation_id": previous.get("validation_id"),
                "previous_ts": previous.get("ts"),
                "change_type": "structural_fqdn" if structural_change else "numeric_in_first_segment_after_24h",
                "hint": (
                    "El host declarado difiere del último host conocido para este "
                    "(hilo, operation). Posible cluster fantasma o contexto compactado."
                ),
            },
            recommendation=(
                "Verificar el host actual contra credentials.md o Railway env. "
                "Si el cambio es legítimo, ejecutar /v1/memento/validate explícitamente "
                "antes de la operación para confirmar."
            ),
            validation_id_ref=previous.get("validation_id"),
        )

    # ---------------------------------------------------------------------
    # H3 — operación sin pre-flight reciente
    # ---------------------------------------------------------------------

    async def _rule_h3_no_recent_preflight(
        self,
        hilo_id: str,
        operation: str,
        current_validation_id: Optional[str],
    ) -> Optional[ContaminationFinding]:
        """
        H3 — MEDIUM informativo. Si el hilo registró >= N validaciones
        recientes (default 5) en la ventana (default 60 min) pero ninguna
        para esta `operation` (excluyendo la actual), señala que está
        operando ciego sobre esta operación.

        Esta es una heurística *informativa*: no implica mala fe ni error,
        solo recuerda al hilo que su contexto operativo de esta operación
        es viejo o nuevo.
        """
        from datetime import datetime, timedelta, timezone

        cutoff = (datetime.now(timezone.utc) - timedelta(minutes=self._h3_lookback_minutes)).isoformat()

        try:
            rows = await self._db.select(
                "memento_validations",
                filters={"hilo_id": hilo_id},
                order_by="ts.desc",
                limit=50,
                filters_gte={"ts": cutoff},
            )
        except TypeError:
            # SDK puede no soportar filters_gte; fallback simple
            try:
                rows = await self._db.select(
                    "memento_validations",
                    filters={"hilo_id": hilo_id},
                    order_by="ts.desc",
                    limit=50,
                )
                # Filtrar manualmente
                rows = [r for r in rows if (r.get("ts") or "") >= cutoff]
            except Exception as exc:
                logger.debug("h3_db_query_failed error=%s", exc)
                return None
        except Exception as exc:
            logger.debug("h3_db_query_failed error=%s", exc)
            return None

        # Excluir la validación actual (si está en los rows)
        rows = [
            r for r in rows
            if not current_validation_id or r.get("validation_id") != current_validation_id
        ]

        if len(rows) < self._h3_min_recent_validations:
            return None  # hilo nuevo o sin actividad suficiente

        # ¿Hay alguna validación previa para esta misma operation?
        same_op = [r for r in rows if r.get("operation") == operation]
        if same_op:
            return None  # sí hay validación reciente para esta operation

        return ContaminationFinding(
            rule_id="H3",
            severity="MEDIUM",
            evidence={
                "hilo_id": hilo_id,
                "operation": operation,
                "lookback_minutes": self._h3_lookback_minutes,
                "recent_validations_total": len(rows),
                "recent_validations_for_this_op": 0,
                "hint": (
                    "El hilo está activo pero no validó esta operación en la "
                    "ventana reciente. Es informativo (MEDIUM), no bloquea."
                ),
            },
            recommendation=(
                "Considerá si el contexto de esta operación está fresco. "
                "Si la última operación de este tipo fue hace más de 1 hora, "
                "re-leer fuente de verdad antes de proceder."
            ),
        )

    # ---------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------

    @staticmethod
    def _parse_iso_ts(ts_str: str) -> Optional[float]:
        """Parsea un timestamp ISO 8601 a Unix timestamp (segundos)."""
        if not ts_str:
            return None
        try:
            from datetime import datetime

            # Normalizar Z → +00:00 (Python < 3.11)
            normalized = ts_str.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized).timestamp()
        except (ValueError, TypeError):
            return None


__all__ = [
    "ContaminationDetector",
    "ContaminationFinding",
    "ContaminationReport",
]
