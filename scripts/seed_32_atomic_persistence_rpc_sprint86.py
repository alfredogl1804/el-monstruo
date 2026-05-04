"""
Semilla #32 — Persistencia atómica via RPC PL/pgSQL (Sprint 86 Bloque 3)

Lección a sembrar en la base error_memory:

  Cuando un cliente HTTP REST stateless (PostgREST / supabase-py) necesita
  ejecutar varias mutaciones que DEBEN ser atómicas (todas o ninguna), la
  única forma correcta es delegar a una función PL/pgSQL del lado servidor
  y llamarla via RPC. Operaciones secuenciales en el cliente NO son
  transaccionales aunque se vean atómicas — un fallo intermedio deja
  estado parcial.

Patrón ganador:
  1. Escribir migración SQL con función `domain_apply_outcome(...)` que
     hace todas las mutaciones bajo BEGIN/COMMIT implícito.
  2. Llamarla via supabase-py: `client.rpc(name, params).execute()`.
  3. La función devuelve jsonb con resumen para el cliente.
  4. REVOKE PUBLIC + GRANT service_role solo.

Anti-patrón:
  - Hacer `client.table().upsert().execute()` seguido de `client.table().insert()`
    seguido de `client.table().update()`. NO es atómico.

Origen del aprendizaje:
  Sprint 86 Bloque 3 del Catastro — directiva de Cowork explícita
  ("transacción atómica para que se hagan en bloque o se rollbackeen
  en bloque"). supabase-py 2.29.0 (2026-04-24) confirmado sin soporte
  de transacciones HTTP nativas.

Uso:
  Este archivo describe el payload que el Hilo Ejecutor debe POST-ear
  a https://el-monstruo-mvp.up.railway.app/v1/error-memory/seed con el
  schema oficial. Ver scripts/seed_28_*.py como referencia del schema.

[Hilo Manus Catastro] · Sprint 86 Bloque 3 · 2026-05-04
"""
from __future__ import annotations

SEED_PAYLOAD = {
    "id": "seed-32-atomic-persistence-rpc-sprint86",
    "sprint": "86",
    "bloque": "3",
    "fecha": "2026-05-04",
    "hilo": "manus_catastro",
    "categoria": "patron_arquitectonico",
    "titulo": "Atomicidad real con PostgREST/supabase-py = RPC PL/pgSQL",
    "contexto": (
        "El Catastro necesita persistir 3 mutaciones atómicamente: "
        "UPSERT catastro_modelos + INSERT catastro_eventos + UPDATE "
        "catastro_curadores (deltas de trust score). supabase-py 2.29.0 "
        "(PostgREST stateless) NO soporta transacciones HTTP nativas. "
        "Operaciones secuenciales del cliente NO son transaccionales — "
        "un fallo intermedio deja estado parcial inconsistente."
    ),
    "patron_recomendado": (
        "Crear función PL/pgSQL `domain_apply_outcome(p_a jsonb, "
        "p_b jsonb, p_c jsonb)` que ejecuta las mutaciones del lado "
        "servidor bajo transacción implícita. Llamarla desde Python "
        "con `client.rpc(name, params).execute()`. La función devuelve "
        "jsonb con resumen. REVOKE PUBLIC + GRANT service_role."
    ),
    "antipatron_evitado": (
        "client.table('a').upsert(x).execute() seguido de "
        "client.table('b').insert(y).execute() — NO atómico, sin rollback "
        "automático."
    ),
    "evidencia_archivos": [
        "scripts/018_sprint86_catastro_rpc.sql",
        "kernel/catastro/persistence.py",
        "tests/test_sprint86_bloque3.py",
    ],
    "validado_con_tests": 32,
    "validado_smoke": True,
}


def main() -> None:
    import json
    print(json.dumps(SEED_PAYLOAD, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
