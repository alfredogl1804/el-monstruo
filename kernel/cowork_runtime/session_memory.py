"""
kernel/cowork_runtime/session_memory.py — T3 MAGNA Sprint COWORK-RUNTIME-001

Memoria persistente entre sesiones Cowork. Cliente Supabase para tabla
`cowork_sesiones` (migracion 0009).

Funciones:
- `start_session()`: crea fila al inicio de sesion Cowork
- `update_session()`: actualiza estado en curso (turnos, commits, violaciones)
- `close_session()`: cierra fila con resumen y deudas pendientes
- `read_last_session()`: para Pre-flight Memento extendido (T3 corazon)
- `build_pre_flight_block()`: bloque listo para inyectar al system prompt

Anti-Dory:
- Cada llamada lee env frescas (no cachea SUPABASE_URL ni SUPABASE_SERVICE_KEY)
- Si Supabase no esta configurado, fallback a archivo local JSON

Uso CLI:

    # Leer ultima sesion (lo que va al Pre-flight)
    python -m kernel.cowork_runtime.session_memory pre-flight

    # Crear sesion nueva
    python -m kernel.cowork_runtime.session_memory start

    # Cerrar sesion actual con resumen
    python -m kernel.cowork_runtime.session_memory close \\
        --session-id <uuid> --resumen "..." --deudas '["X","Y"]'
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

_REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_FALLBACK_PATH = _REPO_ROOT / ".cowork_sesiones_local.json"


# =============================================================================
# Errores tipados
# =============================================================================


class SessionMemoryError(Exception):
    pass


class SupabaseUnavailableError(SessionMemoryError):
    pass


# =============================================================================
# Cliente Supabase REST minimal (sin dependencias)
# =============================================================================


@dataclass
class SupabaseConfig:
    url: str
    service_key: str

    @classmethod
    def from_env(cls) -> Optional["SupabaseConfig"]:
        """Lectura fresca anti-Dory. None si no esta configurado."""
        url = os.environ.get("SUPABASE_URL")
        # Aceptamos ambos nombres por compat con doctrina DSC-S-007
        key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            return None
        return cls(url=url.rstrip("/"), service_key=key)


def _supabase_request(
    config: SupabaseConfig,
    method: str,
    path: str,
    body: Optional[dict | list] = None,
    extra_headers: Optional[dict] = None,
    timeout: int = 10,
) -> Any:
    """Llamada REST minima sin dependencias externas."""
    url = f"{config.url}/rest/v1{path}"
    headers = {
        "apikey": config.service_key,
        "Authorization": f"Bearer {config.service_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if extra_headers:
        headers.update(extra_headers)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode("utf-8")
            if not payload:
                return None
            return json.loads(payload)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise SupabaseUnavailableError(f"HTTP {e.code} en {method} {url}: {body[:200]}") from e
    except urllib.error.URLError as e:
        raise SupabaseUnavailableError(f"URLError {method} {url}: {e}") from e


# =============================================================================
# Modelo de fila
# =============================================================================


@dataclass
class CoworkSesion:
    id: Optional[str] = None
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    duracion_minutos: Optional[int] = None
    turnos_totales: int = 0
    pre_flight_ejecutado: bool = False
    commits_productivos: int = 0
    violaciones_detectadas: list = field(default_factory=list)
    palabras_clave_alfredo: list = field(default_factory=list)
    correctivos_recibidos: list = field(default_factory=list)
    deudas_pendientes_proxima_sesion: list = field(default_factory=list)
    resumen_lecciones: Optional[str] = None
    sprint_activo: Optional[str] = None
    kernel_version: Optional[str] = None
    embrion_ultimo_latido: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "CoworkSesion":
        kwargs = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**kwargs)

    def to_dict(self) -> dict:
        out = {}
        for k in self.__dataclass_fields__:
            v = getattr(self, k)
            if v is not None:
                out[k] = v
        return out


# =============================================================================
# Storage layer (Supabase con fallback local JSON)
# =============================================================================


class SessionMemoryStore:
    """Wrapper sobre Supabase con fallback a JSON local."""

    def __init__(
        self,
        config: Optional[SupabaseConfig] = None,
        local_fallback_path: Optional[Path] = None,
    ) -> None:
        # Lectura fresca de env (NO cachear)
        self.config = config if config is not None else SupabaseConfig.from_env()
        self.local_path = local_fallback_path or LOCAL_FALLBACK_PATH
        self.use_supabase = self.config is not None

    # ---- Operaciones ----

    def insert(self, sesion: CoworkSesion) -> CoworkSesion:
        if self.use_supabase:
            try:
                rows = _supabase_request(
                    self.config,  # type: ignore[arg-type]
                    "POST",
                    "/cowork_sesiones",
                    body=sesion.to_dict(),
                    extra_headers={"Prefer": "return=representation"},
                )
                if rows:
                    return CoworkSesion.from_dict(rows[0])
                return sesion
            except SupabaseUnavailableError:
                # Fallback a local
                pass
        return self._local_insert(sesion)

    def update(self, sesion_id: str, patch: dict) -> Optional[CoworkSesion]:
        if self.use_supabase:
            try:
                rows = _supabase_request(
                    self.config,  # type: ignore[arg-type]
                    "PATCH",
                    f"/cowork_sesiones?id=eq.{sesion_id}",
                    body=patch,
                    extra_headers={"Prefer": "return=representation"},
                )
                if rows:
                    return CoworkSesion.from_dict(rows[0])
                return None
            except SupabaseUnavailableError:
                pass
        return self._local_update(sesion_id, patch)

    def get_last(self) -> Optional[CoworkSesion]:
        if self.use_supabase:
            try:
                rows = _supabase_request(
                    self.config,  # type: ignore[arg-type]
                    "GET",
                    "/cowork_sesiones?order=fecha_inicio.desc&limit=1",
                )
                if rows:
                    return CoworkSesion.from_dict(rows[0])
                return None
            except SupabaseUnavailableError:
                pass
        return self._local_get_last()

    # ---- Local fallback ----

    def _local_load(self) -> list[dict]:
        if self.local_path.exists():
            try:
                return json.loads(self.local_path.read_text())
            except Exception:
                return []
        return []

    def _local_save(self, rows: list[dict]) -> None:
        self.local_path.parent.mkdir(parents=True, exist_ok=True)
        self.local_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False))

    def _local_insert(self, sesion: CoworkSesion) -> CoworkSesion:
        import uuid

        rows = self._local_load()
        if not sesion.id:
            sesion.id = str(uuid.uuid4())
        if not sesion.fecha_inicio:
            sesion.fecha_inicio = datetime.now(timezone.utc).isoformat()
        rows.append(sesion.to_dict())
        self._local_save(rows)
        return sesion

    def _local_update(self, sesion_id: str, patch: dict) -> Optional[CoworkSesion]:
        rows = self._local_load()
        for r in rows:
            if r.get("id") == sesion_id:
                r.update(patch)
                self._local_save(rows)
                return CoworkSesion.from_dict(r)
        return None

    def _local_get_last(self) -> Optional[CoworkSesion]:
        rows = self._local_load()
        if not rows:
            return None
        rows_sorted = sorted(rows, key=lambda r: r.get("fecha_inicio") or "", reverse=True)
        return CoworkSesion.from_dict(rows_sorted[0])

    def read_recent(self, limit: int = 50) -> list[dict]:
        """
        Lee las ultimas N sesiones (dicts crudos para flexibilidad).
        Usado por dashboard T6. Supabase con fallback local.
        """
        if self.use_supabase:
            try:
                rows = _supabase_request(
                    self.config,  # type: ignore[arg-type]
                    "GET",
                    f"/cowork_sesiones?order=fecha_inicio.desc&limit={int(limit)}",
                )
                return rows or []
            except SupabaseUnavailableError:
                pass
        rows = self._local_load()
        return sorted(rows, key=lambda r: r.get("fecha_inicio") or "", reverse=True)[:limit]


# =============================================================================
# Operaciones de alto nivel (lo que llama Cowork)
# =============================================================================


def start_session(
    sprint_activo: Optional[str] = None,
    kernel_version: Optional[str] = None,
    store: Optional[SessionMemoryStore] = None,
) -> CoworkSesion:
    """Crea fila al inicio de una sesion Cowork."""
    store = store or SessionMemoryStore()
    sesion = CoworkSesion(
        fecha_inicio=datetime.now(timezone.utc).isoformat(),
        sprint_activo=sprint_activo,
        kernel_version=kernel_version,
    )
    return store.insert(sesion)


def update_session(
    sesion_id: str,
    patch: dict,
    store: Optional[SessionMemoryStore] = None,
) -> Optional[CoworkSesion]:
    """Actualiza la sesion en curso."""
    store = store or SessionMemoryStore()
    return store.update(sesion_id, patch)


def close_session(
    sesion_id: str,
    resumen_lecciones: str,
    deudas_pendientes: Optional[list] = None,
    store: Optional[SessionMemoryStore] = None,
) -> Optional[CoworkSesion]:
    """Cierra la sesion con resumen y deudas para la proxima."""
    store = store or SessionMemoryStore()
    fecha_fin = datetime.now(timezone.utc).isoformat()
    last = store.get_last()
    duracion = None
    if last and last.fecha_inicio:
        try:
            inicio = datetime.fromisoformat(last.fecha_inicio.replace("Z", "+00:00"))
            duracion = int((datetime.now(timezone.utc) - inicio).total_seconds() // 60)
        except Exception:
            duracion = None
    patch = {
        "fecha_fin": fecha_fin,
        "duracion_minutos": duracion,
        "resumen_lecciones": resumen_lecciones,
        "deudas_pendientes_proxima_sesion": deudas_pendientes or [],
    }
    return store.update(sesion_id, patch)


def read_last_session(
    store: Optional[SessionMemoryStore] = None,
) -> Optional[CoworkSesion]:
    """Lee la ultima sesion para Pre-flight Memento extendido."""
    store = store or SessionMemoryStore()
    return store.get_last()


def build_pre_flight_block(
    last: Optional[CoworkSesion] = None,
    store: Optional[SessionMemoryStore] = None,
) -> str:
    """
    Bloque listo para inyectar al system prompt al inicio de cada sesion Cowork.

    Pre-flight Memento extendido (T3): Cowork arranca cada sesion sabiendo
    que paso en la anterior, que deudas quedaron pendientes, y que correctivos
    recibio.
    """
    if last is None:
        last = read_last_session(store)
    if last is None:
        return (
            "[COWORK_PRE_FLIGHT — primera sesion registrada]\n"
            "  No hay sesion previa en cowork_sesiones.\n"
            "  Operar con CLAUDE.md + COWORK_OPERATING_SYSTEM_v0_1 como base.\n"
        )

    lines = [
        "==========================================",
        "[COWORK_PRE_FLIGHT — ultima sesion]",
        f"  id: {last.id}",
        f"  fecha_inicio: {last.fecha_inicio}",
        f"  fecha_fin: {last.fecha_fin or '(no cerrada — sesion previa interrumpida)'}",
        f"  duracion_min: {last.duracion_minutos if last.duracion_minutos is not None else 'N/A'}",
        f"  turnos: {last.turnos_totales}",
        f"  pre_flight_ejecutado: {last.pre_flight_ejecutado}",
        f"  commits_productivos: {last.commits_productivos}",
        f"  sprint: {last.sprint_activo or 'N/A'}",
        f"  kernel_version: {last.kernel_version or 'N/A'}",
    ]
    if last.violaciones_detectadas:
        lines.extend(
            [
                "",
                f"## Violaciones detectadas en la sesion previa ({len(last.violaciones_detectadas)})",
            ]
        )
        for v in last.violaciones_detectadas[:5]:
            v_str = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
            lines.append(f"  - {v_str[:200]}")
    if last.correctivos_recibidos:
        lines.extend(
            [
                "",
                f"## Correctivos recibidos de Alfredo en la sesion previa ({len(last.correctivos_recibidos)})",
            ]
        )
        for c in last.correctivos_recibidos[:5]:
            c_str = c if isinstance(c, str) else json.dumps(c, ensure_ascii=False)
            lines.append(f"  - {c_str[:200]}")
    if last.deudas_pendientes_proxima_sesion:
        lines.extend(
            [
                "",
                f"## DEUDAS PENDIENTES (atender en esta sesion — {len(last.deudas_pendientes_proxima_sesion)})",
            ]
        )
        for d in last.deudas_pendientes_proxima_sesion:
            d_str = d if isinstance(d, str) else json.dumps(d, ensure_ascii=False)
            lines.append(f"  - {d_str[:200]}")
    if last.resumen_lecciones:
        lines.extend(
            [
                "",
                "## Resumen de lecciones",
                f"  {last.resumen_lecciones[:500]}",
            ]
        )
    lines.append("==========================================")
    return "\n".join(lines)


# =============================================================================
# CLI
# =============================================================================


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Memoria persistente Cowork (T3 Sprint COWORK-RUNTIME-001).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_start = sub.add_parser("start", help="Crea sesion nueva.")
    p_start.add_argument("--sprint", default=None)
    p_start.add_argument("--kernel-version", default=None)

    p_close = sub.add_parser("close", help="Cierra sesion existente.")
    p_close.add_argument("--session-id", required=True)
    p_close.add_argument("--resumen", required=True)
    p_close.add_argument("--deudas", default="[]", help="JSON array de deudas.")

    sub.add_parser("pre-flight", help="Imprime bloque Pre-flight Memento extendido.")

    sub.add_parser("last", help="Imprime ultima sesion en JSON.")

    args = parser.parse_args(argv)

    if args.cmd == "start":
        sesion = start_session(
            sprint_activo=args.sprint,
            kernel_version=args.kernel_version,
        )
        print(json.dumps(sesion.to_dict(), indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "close":
        try:
            deudas = json.loads(args.deudas)
        except json.JSONDecodeError:
            print(f"error: --deudas debe ser JSON valido, recibido: {args.deudas!r}", file=sys.stderr)
            return 2
        result = close_session(args.session_id, args.resumen, deudas)
        if result is None:
            print(f"sesion {args.session_id} no encontrada", file=sys.stderr)
            return 1
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        return 0

    if args.cmd == "pre-flight":
        print(build_pre_flight_block())
        return 0

    if args.cmd == "last":
        last = read_last_session()
        if last is None:
            print("null")
            return 0
        print(json.dumps(last.to_dict(), indent=2, ensure_ascii=False))
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
