"""Decorator + storage para validacion magna de claims (DSC-V-001)."""
from __future__ import annotations

import functools
import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional, Protocol


class StaleClaimError(Exception):
    """Claim sin validacion vigente. Bloquea retorno hasta record_validation()."""


@dataclass
class ClaimRecord:
    claim_type: str
    claim_fingerprint: str
    claim_value: str
    validator: str
    evidence_url: str | None
    timestamp_unix: float
    ttl_seconds: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_valid_at(self, now_unix: float) -> bool:
        return now_unix < (self.timestamp_unix + self.ttl_seconds)


class ValidationLogStorage(Protocol):
    def find_latest(self, claim_type: str) -> Optional[ClaimRecord]: ...
    def find_latest_by_fingerprint(self, fingerprint: str) -> Optional[ClaimRecord]: ...
    def insert(self, record: ClaimRecord) -> None: ...


class LocalFileStorage:
    """JSONL append-only file. Default cuando no hay Supabase configurado."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path("reports/validation_log.jsonl")

    def _read_all(self) -> list[ClaimRecord]:
        if not self.path.exists():
            return []
        records = []
        for line in self.path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                records.append(ClaimRecord(**d))
            except (json.JSONDecodeError, TypeError):
                continue
        return records

    def find_latest(self, claim_type: str) -> Optional[ClaimRecord]:
        candidates = [r for r in self._read_all() if r.claim_type == claim_type]
        return max(candidates, key=lambda r: r.timestamp_unix) if candidates else None

    def find_latest_by_fingerprint(self, fingerprint: str) -> Optional[ClaimRecord]:
        candidates = [
            r for r in self._read_all() if r.claim_fingerprint == fingerprint
        ]
        return max(candidates, key=lambda r: r.timestamp_unix) if candidates else None

    def insert(self, record: ClaimRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")


_DEFAULT_STORAGE: ValidationLogStorage | None = None


def set_default_storage(storage: ValidationLogStorage) -> None:
    global _DEFAULT_STORAGE
    _DEFAULT_STORAGE = storage


def _get_storage() -> ValidationLogStorage:
    global _DEFAULT_STORAGE
    if _DEFAULT_STORAGE is None:
        _DEFAULT_STORAGE = LocalFileStorage()
    return _DEFAULT_STORAGE


def _claim_fingerprint(claim_type: str, claim_value: Any) -> str:
    payload = json.dumps(
        {"type": claim_type, "value": claim_value},
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def record_validation(
    claim_type: str,
    claim_value: Any,
    validator: str,
    evidence_url: str | None = None,
    ttl_hours: int = 24,
    metadata: dict[str, Any] | None = None,
    storage: ValidationLogStorage | None = None,
) -> ClaimRecord:
    """Persiste un registro de validacion magna en el log."""
    record = ClaimRecord(
        claim_type=claim_type,
        claim_fingerprint=_claim_fingerprint(claim_type, claim_value),
        claim_value=str(claim_value)[:1000],
        validator=validator,
        evidence_url=evidence_url,
        timestamp_unix=time.time(),
        ttl_seconds=int(ttl_hours * 3600),
        metadata=metadata or {},
    )
    target = storage or _get_storage()
    target.insert(record)
    return record


def requires_perplexity_validation(
    claim_type: str,
    ttl_hours: int = 24,
    storage: ValidationLogStorage | None = None,
) -> Callable:
    """Decorator: levanta StaleClaimError si no hay validacion vigente."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            target = storage or _get_storage()
            latest = target.find_latest(claim_type)
            now = time.time()
            if latest is None:
                raise StaleClaimError(
                    f"DSC-V-001: claim_type '{claim_type}' SIN validacion en "
                    f"el log. Llamar record_validation('{claim_type}', value, "
                    f"validator='perplexity', evidence_url=...) antes de invocar "
                    f"{func.__name__}()."
                )
            if not latest.is_valid_at(now):
                age_hours = (now - latest.timestamp_unix) / 3600
                ttl_h = latest.ttl_seconds / 3600
                raise StaleClaimError(
                    f"DSC-V-001: claim_type '{claim_type}' VENCIDO. Ultima "
                    f"validacion hace {age_hours:.1f}h (TTL fue {ttl_h:.1f}h). "
                    f"Re-validar via Perplexity y re-llamar record_validation()."
                )
            return func(*args, **kwargs)
        wrapper.__perplexity_validation__ = {  # type: ignore[attr-defined]
            "claim_type": claim_type,
            "ttl_hours": ttl_hours,
        }
        return wrapper
    return decorator


__all__ = [
    "ClaimRecord",
    "LocalFileStorage",
    "StaleClaimError",
    "ValidationLogStorage",
    "record_validation",
    "requires_perplexity_validation",
    "set_default_storage",
]
