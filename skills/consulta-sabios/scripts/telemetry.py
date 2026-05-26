#!/usr/bin/env python3.11
"""
telemetry.py — Capa de Telemetría para Mejora Perpetua
=======================================================
Captura métricas de cada consulta para alimentar el ciclo de mejora.

Funciones públicas:
    - generate_run_id()        → ID único para cada ejecución
    - create_run_dir(run_id)   → Crea estructura de carpetas del run
    - estimate_tokens(text)    → Estimación rápida de tokens (~4 chars/token)
    - fingerprint(text)        → SHA-256 del texto para deduplicación/caché
    - append_jsonl(path, row)  → Append atómico a archivo JSONL
    - write_run_artifact(...)  → Guarda artefacto en carpeta del run
    - record_step_metric(...)  → Registra métrica de una etapa
    - finalize_run(...)        → Cierra el run con métricas finales

Almacenamiento:
    Fase 1: JSONL + artefactos por run en filesystem
    data/
    ├── runs/YYYY-MM-DD/run_<id>/
    │   ├── input/
    │   ├── output/
    │   ├── manifest.json
    │   ├── telemetry.json
    │   └── scores.json
    └── history/
        ├── consultas.jsonl
        └── sabios_metrics.jsonl

Creado: 2026-04-08 (P0 auditoría sabios)
"""

import hashlib
import json
import os
import shutil
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

# Directorio base de datos
DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent / "data"
HISTORY_DIR = DATA_DIR / "history"
RUNS_DIR = DATA_DIR / "runs"


def generate_run_id() -> str:
    """Genera un ID único para cada ejecución del flujo."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:8]
    return f"run_{ts}_{short_uuid}"


def create_run_dir(run_id: str) -> Path:
    """Crea la estructura de carpetas para un run."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    run_dir = RUNS_DIR / date_str / run_id
    (run_dir / "input").mkdir(parents=True, exist_ok=True)
    (run_dir / "output").mkdir(parents=True, exist_ok=True)
    return run_dir


def estimate_tokens(text: str) -> int:
    """
    Estimación rápida de tokens.
    Regla: ~4 caracteres por token en inglés, ~3.5 en español.
    Usamos 3.75 como promedio para contenido mixto.
    """
    if not text:
        return 0
    return max(1, int(len(text) / 3.75))


def fingerprint(text: str) -> str:
    """SHA-256 del texto para deduplicación y caché."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def append_jsonl(path: str | Path, row: dict):
    """
    Append atómico a archivo JSONL.
    Crea el archivo y directorios si no existen.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(row, ensure_ascii=False, default=str) + "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def write_run_artifact(run_dir: str | Path, filename: str, content: Any):
    """
    Guarda un artefacto en la carpeta del run.
    Si content es dict/list, lo guarda como JSON.
    Si es str, lo guarda como texto.
    """
    run_dir = Path(run_dir)
    filepath = run_dir / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(content, (dict, list)):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2, default=str)
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(str(content))

    return filepath


def copy_input_artifact(run_dir: str | Path, source_path: str, dest_name: str = None):
    """Copia un archivo de entrada al directorio input/ del run."""
    run_dir = Path(run_dir)
    source = Path(source_path)
    if not source.exists():
        return None
    dest = run_dir / "input" / (dest_name or source.name)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    return dest


class RunTelemetry:
    """
    Colector de telemetría para un run completo.
    Uso:
        tel = RunTelemetry(run_id, run_dir)
        tel.start_step("pre_vuelo")
        ... ejecutar paso ...
        tel.end_step("pre_vuelo", success=True, extra={"sabios_ok": 6})
        tel.finalize(status="success")
    """

    def __init__(
        self,
        run_id: str,
        run_dir: str | Path,
        modo: str = "enjambre",
        profundidad_pre: str = "normal",
        profundidad_post: str = "normal",
        skill_version: str = "1.1.0",
    ):
        self.run_id = run_id
        self.run_dir = Path(run_dir)
        self.modo = modo
        self.profundidad_pre = profundidad_pre
        self.profundidad_post = profundidad_post
        self.skill_version = skill_version
        self.timestamp_start = datetime.now().isoformat()
        self.time_start = time.time()
        self.steps = {}
        self.sabios_metrics = []
        self.prompt_fingerprint = None

    def set_prompt_fingerprint(self, text: str):
        """Registra el fingerprint del prompt principal."""
        self.prompt_fingerprint = fingerprint(text)

    def start_step(self, step_name: str):
        """Marca el inicio de un paso."""
        self.steps[step_name] = {
            "step_name": step_name,
            "time_start": time.time(),
            "duration_ms": 0,
            "success": None,
            "retry_count": 0,
            "input_chars": 0,
            "output_chars": 0,
            "input_tokens_est": 0,
            "output_tokens_est": 0,
            "error_type": None,
            "extra": {},
        }

    def end_step(
        self,
        step_name: str,
        success: bool = True,
        input_chars: int = 0,
        output_chars: int = 0,
        error_type: str = None,
        extra: dict = None,
    ):
        """Marca el fin de un paso con sus métricas."""
        if step_name not in self.steps:
            self.start_step(step_name)

        step = self.steps[step_name]
        step["duration_ms"] = int((time.time() - step["time_start"]) * 1000)
        step["success"] = success
        step["input_chars"] = input_chars
        step["output_chars"] = output_chars
        step["input_tokens_est"] = estimate_tokens("x" * input_chars) if input_chars else 0
        step["output_tokens_est"] = estimate_tokens("x" * output_chars) if output_chars else 0
        step["error_type"] = error_type
        if extra:
            step["extra"].update(extra)
        # Remove internal time_start
        del step["time_start"]

    def record_sabio_metric(self, resultado: dict):
        """Registra la métrica de un sabio individual."""
        metric = {
            "run_id": self.run_id,
            "sabio_id": resultado.get("sabio_id", "unknown"),
            "sabio": resultado.get("sabio", "unknown"),
            "modelo": resultado.get("modelo", "unknown"),
            "duration_ms": int(resultado.get("tiempo_seg", 0) * 1000),
            "success": resultado.get("exito", False),
            "retry_count": resultado.get("intento", 1) - 1,
            "output_chars": len(resultado.get("respuesta", "")),
            "output_tokens_est": estimate_tokens(resultado.get("respuesta", "")),
            "error_type": _classify_error(resultado.get("error")) if resultado.get("error") else None,
            "timestamp": resultado.get("timestamp", datetime.now().isoformat()),
        }
        self.sabios_metrics.append(metric)

    def finalize(self, status: str = "success", extra: dict = None) -> dict:
        """
        Cierra el run, persiste telemetría y retorna el registro completo.
        """
        duration_total_ms = int((time.time() - self.time_start) * 1000)

        sabios_exitosos = sum(1 for m in self.sabios_metrics if m["success"])

        run_record = {
            "run_id": self.run_id,
            "timestamp_start": self.timestamp_start,
            "timestamp_end": datetime.now().isoformat(),
            "skill_version": self.skill_version,
            "modo": self.modo,
            "profundidad_pre": self.profundidad_pre,
            "profundidad_post": self.profundidad_post,
            "prompt_fingerprint": self.prompt_fingerprint,
            "duration_ms_total": duration_total_ms,
            "status": status,
            "sabios_requested": len(self.sabios_metrics),
            "sabios_successful": sabios_exitosos,
            "steps": list(self.steps.values()),
        }

        if extra:
            run_record.update(extra)

        # Persistir artefactos del run
        write_run_artifact(self.run_dir, "telemetry.json", run_record)

        # Persistir al historial JSONL
        append_jsonl(HISTORY_DIR / "consultas.jsonl", run_record)

        for metric in self.sabios_metrics:
            append_jsonl(HISTORY_DIR / "sabios_metrics.jsonl", metric)

        return run_record


def _classify_error(error_str: str) -> str:
    """Clasifica un error en categorías normalizadas."""
    if not error_str:
        return None
    error_lower = error_str.lower()
    if "timeout" in error_lower or "timed out" in error_lower:
        return "timeout"
    if "429" in error_str or "rate limit" in error_lower:
        return "rate_limit"
    if "401" in error_str or "unauthorized" in error_lower:
        return "auth_error"
    if "403" in error_str or "forbidden" in error_lower:
        return "forbidden"
    if "500" in error_str or "502" in error_str or "503" in error_str:
        return "server_error"
    if "json" in error_lower or "parse" in error_lower:
        return "parse_error"
    if "context" in error_lower or "token" in error_lower or "length" in error_lower:
        return "context_overflow"
    return "unknown"


# ═══════════════════════════════════════════════════════════════════
# UTILIDADES DE LECTURA DEL HISTORIAL
# ═══════════════════════════════════════════════════════════════════


def read_jsonl(path: str | Path) -> list:
    """Lee un archivo JSONL y retorna lista de dicts."""
    path = Path(path)
    if not path.exists():
        return []
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def get_run_count() -> int:
    """Retorna el número total de runs registrados."""
    return len(read_jsonl(HISTORY_DIR / "consultas.jsonl"))


def get_recent_runs(n: int = 10) -> list:
    """Retorna los últimos N runs."""
    runs = read_jsonl(HISTORY_DIR / "consultas.jsonl")
    return runs[-n:]


if __name__ == "__main__":
    # Test rápido
    print("📊 Telemetría consulta-sabios")
    print(f"   Data dir: {DATA_DIR}")
    print(f"   Runs registrados: {get_run_count()}")
    print(f"   estimate_tokens('Hola mundo'): {estimate_tokens('Hola mundo')}")
    print(f"   fingerprint('test'): {fingerprint('test')[:16]}...")
    print(f"   generate_run_id(): {generate_run_id()}")
    print("✅ Telemetría operativa")
