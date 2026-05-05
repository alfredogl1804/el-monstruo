"""
Semilla #36 — Dashboard de Salud como visibilidad obligatoria
              (Sprint 86 Bloque 7 — Catastro)

Lección a sembrar en la base error_memory:
  Cualquier dominio del Monstruo (Catastro, Memento, Magna+, Vanguardia,
  etc.) que persista estado y se expone vía REST/MCP DEBE entregar un
  Dashboard de Salud antes de cerrar su sprint. Sin dashboard, el sistema
  funciona pero es ciego: humanos (Alfredo) y agentes externos (Cowork)
  no pueden inspeccionar trust_level, drift, timeline ni curators sin
  meterse al código o al SQL. Esto rompe Obj #9 (Transversalidad: el
  módulo expone sus datos para otros) y la Capa 7 Resiliencia Agéntica
  (observabilidad semántica + learning loop). El dashboard es la
  contraparte humana del MCP/REST: lo mismo, en HTML legible.

Patrón ganador (Catastro Bloque 7):

  kernel/<dominio>/dashboard.py — DashboardEngine puro
    - 3 endpoints JSON: summary, timeline, curators (si aplica)
    - 1 endpoint HTML: render vanilla con Chart.js sin build step
    - Cache LRU 60s reutilizado del módulo recommendation
    - Modo degraded en TODAS las respuestas (degraded:true cuando DB
      caída, devuelve estructura vacía, NO crashea)
    - Identidad de marca: errores `<dominio>_dashboard_*`, colores
      Brand DNA (#F97316 forja + #1C1917 graphite + #A8A29E acero)

  kernel/<dominio>/<dominio>_routes.py — Modificación quirúrgica
    - 4 nuevos endpoints bajo /dashboard/* en el router existente
    - Auth condicional: PÚBLICA por defecto (read-only es seguro),
      endurecible con `<DOMINIO>_DASHBOARD_REQUIRE_AUTH=true` SIN
      redeploy de código (env var leída fresh en cada request)
    - DashboardEngine inyectable via app.state o singleton fallback
    - HTML render con `include_in_schema=False` para no contaminar
      OpenAPI

  bridge/<DOMINIO>_OPERATIONAL_GUIDE.md — Guía operativa para humanos
    - Qué es el dominio, cómo consultar, cómo leer cada panel
    - Tabla de troubleshooting síntoma → diagnóstico → solución
    - Variables de entorno relevantes
    - Quién hace qué (RACI por hilo)

  scripts/_smoke_dashboard_<dominio>_sprint*.py — Smoke E2E
    - Cliente HTTP urllib stdlib (cero deps externas)
    - Valida 4 endpoints contra Railway o localhost
    - Acepta KERNEL_URL del env o argv[1]
    - Auth opcional via MONSTRUO_API_KEY
    - Exit codes: 0 ok, 1 assertion_failure, 2 config_error

Disciplina de visibilidad (Capa 7 Resiliencia Agéntica):

  1. Trust Level único campo top-level: healthy / degraded / down
     - healthy: cron diario corriendo, fuentes ok, drift bajo
     - degraded: alguna fuente caída pero hay datos válidos cacheados
     - down: sin datos, infra rota, intervención humana requerida

  2. Timeline siempre lookback configurable (default 14 días, max 90):
     runs/eventos/avg_failure_rate por día. Línea de runs estable en 1
     es la señal de cron sano.

  3. Trust Scores de curadores con delta_7d obligatorio. Si un curador
     pierde >0.05 en 7 días, alertar (drift de modelo backend).

  4. Bandas de confianza visibles en TODA métrica derivada (trono_low,
     trono_high). Banda ancha = pocos datos = decisión arriesgada.

  5. degraded_reason categorizada: no_db_factory_configured,
     supabase_down, no_runs_yet, cache_miss_only. Cada categoría tiene
     una acción específica documentada en la guía operativa.

Salvaguardas obligatorias (anti-autoboicot):

  - Dashboard PÚBLICO read-only por defecto: bloquear con auth solo si
    el dominio expone PII o datos sensibles. Para meta-datos de
    sistema (Catastro, Memento), público es correcto y permite a
    Cowork inspeccionar sin pasar credenciales.
  - HTML render con `include_in_schema=False`: no contamina /docs
    OpenAPI ni rompe clientes generados con typed-fetch.
  - Auth condicional con env var (no constante en código): permite
    endurecer en producción sin tocar el repo.
  - Cache compartido con recommendation: misma TTL, misma estrategia
    de invalidate. NO duplicar infra de cache.
  - Tests con DB sintética (FakeClient + FakeQuery): nunca tocar
    Supabase real en CI. 1 test opt-in marcado para integración.

Anti-patrón que ESTA semilla previene:

  Construir dashboards como SPA separada (Next.js, React, Vue) cuando
  el dominio es read-only y los datos caben en 3 endpoints JSON. La SPA
  agrega: build pipeline, deploy independiente, auth duplicada, costo
  de mantenimiento, divergencia con el backend. El HTML vanilla con
  Chart.js (CDN, sin build) cumple el 95% de los casos en MVP. Si en
  el futuro hace falta interactividad rica, REEMPLAZAR el endpoint
  /dashboard/ por la SPA y mantener los 3 JSON intactos. Backwards
  compatible.

Tests obligatorios al adoptar este patrón:

  - DashboardEngine con 3 modos degraded: sin db_factory, db crash,
    sin datos.
  - Happy path con DB sintética: assertions sobre trust_level,
    counts, drift_detected.
  - Cache LRU: hit, miss, invalidate, separación por método.
  - Auth condicional: default false, true via env, explicit false
    via env.
  - HTML render: <!DOCTYPE html>, identidad de marca presente,
    Chart.js CDN, consume los 3 endpoints.
  - APIRouter integration con TestClient: 200 público, 401 con auth
    activada, 422 con args inválidos, degraded en endpoint cuando
    db_factory=None.
  - E2E secuencial: recommend → dashboard summary → timeline →
    curators todos en mismo TestClient (validar inyección de engine
    es correcta).

Complementa semillas:
  - #19 (eventos_publish: contrato observabilidad)
  - #28 (memento_search: contrato cache TTL)
  - #29 (gateway resilience: fallback graceful)
  - #30 (audit traceability)
  - #31 (degraded mode contract)
  - #32 (atomic persistence RPC)
  - #33 (z-scores intra-dominio)
  - #34 (dual REST + sub-FastMCP)
  - #35 (orquestación de runs productivos)

Objetivos Maestros que satisface:
  Obj #2 (Apple/Tesla): dashboard premium con identidad inmutable.
  Obj #3 (Mínima Complejidad): vanilla HTML + CDN, sin build.
  Obj #5 (Magna/Premium): documentación exhaustiva en guía operativa.
  Obj #7 (No Inventar Rueda): reuso de cache LRU, validación reuso de
    auth helper, Chart.js (no rebuild).
  Obj #9 (Transversalidad): expone datos para humanos+agentes externos.
  Obj #12 (Soberanía): observabilidad sin dependencia de Grafana,
    Datadog, ni servicios SaaS.

[Hilo Manus Catastro] · Sprint 86 Bloque 7 · 2026-05-04 · v0.86.7
"""
from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request
import json


def main() -> int:
    """POST de la semilla al endpoint /v1/error-memory/seed del Monstruo."""
    base_url = os.environ.get("KERNEL_URL", "")
    api_key = os.environ.get("MONSTRUO_API_KEY", "")

    if not base_url or not api_key:
        print(
            "ERROR: KERNEL_URL y MONSTRUO_API_KEY son obligatorios.\n"
            "Uso:\n"
            "  KERNEL_URL=https://el-monstruo-mvp.up.railway.app \\\n"
            "  MONSTRUO_API_KEY=<key> \\\n"
            "  python3 scripts/seed_36_dashboard_visibilidad_obligatoria_sprint86.py"
        )
        return 2

    payload = {
        "id": "seed_36_dashboard_visibilidad_obligatoria_sprint86",
        "categoria": "patron_arquitectonico",
        "severidad": "critica",
        "titulo": (
            "Dashboard de Salud como visibilidad obligatoria de cualquier "
            "dominio del Monstruo (Catastro Bloque 7)"
        ),
        "leccion": __doc__,
        "fuente": "hilo_manus_catastro",
        "sprint": "86",
        "bloque": "7",
        "validado_por": "tests/test_sprint86_bloque7.py (29 PASS) + smoke E2E",
        "fecha": "2026-05-04",
    }

    url = base_url.rstrip("/") + "/v1/error-memory/seed"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            print(f"OK status={resp.status}")
            print(body)
            return 0
    except urllib.error.HTTPError as exc:
        print(f"FAIL status={exc.code}")
        print(exc.read().decode("utf-8") if exc.fp else "")
        return 1
    except urllib.error.URLError as exc:
        print(f"FAIL network: {exc.reason}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
