"""
Semilla #34 — Exposición dual REST + sub-FastMCP graceful (Sprint 86 Bloque 5)

Lección a sembrar en la base error_memory:

  Cuando un dominio del Monstruo (Catastro, Memento, Magna, etc.) necesita
  exponer sus capacidades al ecosistema, el patrón ganador 2026 es DUAL:
  un APIRouter REST canónico bajo `/v1/<dominio>/*` para clientes HTTP
  externos + un sub-FastMCP "mounteable" para que clientes MCP (Claude
  Desktop, Cowork, Embriones) lo invoquen como tools nativas. AMBAS capas
  comparten un mismo Engine de lógica pura (sin acoplamiento a transport).

Patrón ganador (Catastro Bloque 5):

  kernel/<dominio>/
    ├── recommendation.py       ← Engine puro: Pydantic + db_factory + cache
    ├── catastro_routes.py      ← APIRouter REST con auth Bearer
    └── mcp_tools.py            ← FastMCP sub-server con build_<dominio>_mcp()

  kernel/main.py (lifespan):
    engine = Engine(db_factory=build_default_db_factory())
    app.state.<dominio>_engine = engine
    routes.set_dependencies(engine)
    mcp_tools.set_mcp_engine(engine)
    app.include_router(routes.router, prefix=f"/v1/{dominio}")
    if mcp_tools.<dominio>_mcp is not None:
        fastmcp_server.mount(dominio, mcp_tools.<dominio>_mcp)

Ventajas sobre alternativas:

  1. Cero duplicación: el Engine es UNO solo, ambas capas lo usan.
  2. Cache compartido entre HTTP y MCP (mismo singleton via app.state).
  3. Tests del Engine son agnósticos de transport (no FastAPI ni FastMCP).
  4. Auth dura solo en HTTP (MCP usa el transport-level del cliente).
  5. Si fastmcp NO está instalado, el sub-MCP devuelve None y el mount es
     no-op — la capa HTTP sigue funcionando perfectamente (Capa 7).

Salvaguardas obligatorias (anti-autoboicot):

  - El Engine MUST aceptar `db_factory=None` y devolver modo `degraded` en
    TODAS sus métodos en vez de crashear (Capa 7 Resiliencia Agéntica).
  - `os.environ` lectura FRESH en el guard de auth (anti-Dory) — NUNCA
    cachear `MONSTRUO_API_KEY` al import.
  - Cache LRU SOLO almacena resultados con `degraded=False` (no envenenar).
  - El sub-FastMCP MUST tener fallback si `import fastmcp` falla
    (`return None` + log warning, no raise).
  - Identidad de marca en TODOS los códigos de error: prefijo
    `<dominio>_<accion>_<failure_type>` (ver Brand Engine, Regla Dura #4).

Anti-patrón evitado:

  Crear un servidor FastMCP standalone separado (puerto distinto, proceso
  distinto) "para no contaminar" el HTTP server. Esto duplica infra,
  rompe el cache compartido, complica el deployment y desincroniza la
  evolución del schema. La unión vía `mount()` en el FastMCP existente
  es la solución canónica FastMCP 3.0+ (Feb 2026).

Patrón de inyección anti-Dory en routes:

  _engine_singleton: Optional[Engine] = None

  def set_dependencies(engine): ...   ← llama lifespan
  def _get_engine(request):
      eng = getattr(request.app.state, "<dominio>_engine", None)
      if eng is not None: return eng
      if _engine_singleton is not None: return _engine_singleton
      raise HTTPException(503, detail="<dominio>_engine_not_initialized")

  Esto permite a tests pasar un mock via `set_dependencies(mock)` sin
  inicializar todo el lifespan FastAPI.

Tests obligatorios para cualquier dominio que adopte este patrón:

  · Auth: sin key → 401, key inválida → 401, sin env var → 503.
  · Modo degraded: db caída → todas las respuestas con degraded=True
    + degraded_reason explícito.
  · Cache LRU: 2da llamada idéntica → cache_hit=True; degraded NO se
    cachea.
  · FastMCP fallback: monkeypatch sys.modules["fastmcp"]=None →
    build_<dominio>_mcp() retorna None, no raise.
  · Identidad de marca: códigos error con prefijo correcto.
  · 1 opt-in real con env var <DOMINIO>_INTEGRATION_TESTS=true.

Mejoras del Audit Cowork al Bloque 4 incorporadas en Bloque 5:

  - APIRouter REST canónico bajo `/v1/catastro/*` (no solo MCP).
  - Auth idéntico al patrón Memento (X-API-Key + Authorization: Bearer).
  - Modo degraded graceful: 200 OK con degraded=true en payload (Capa 7).
  - Cache LRU 60s con invalidate() expuesto + tracking cache_hit en
    cada response (telemetría obj #11).
  - sub-FastMCP montado en el FastMCP existente del kernel (no separado).

Origen del aprendizaje:

  Sprint 86 Bloque 5 del Catastro — diseño del MCP Server
  catastro.recommend() con APIRouter REST + sub-FastMCP graceful.
  Validado en tiempo real contra FastMCP 3.0 docs (Feb 2026),
  Speakeasy MCP composition patterns (Mar 2026), y consenso de
  Cowork audit Bloque 4 (green light directo).

Uso:

  Este archivo describe el payload que el Hilo Ejecutor debe POST-ear
  a https://el-monstruo-mvp.up.railway.app/v1/error-memory/seed con el
  schema oficial. Ver scripts/seed_28_*.py como referencia del schema.

[Hilo Manus Catastro] · Sprint 86 Bloque 5 · 2026-05-04
"""
from __future__ import annotations


SEED_PAYLOAD = {
    "id": "seed-34-apirouter-submcp-dual-sprint86",
    "sprint": "86",
    "bloque": "5",
    "fecha": "2026-05-04",
    "hilo": "manus_catastro",
    "categoria": "patron_arquitectonico",
    "titulo": "Exposición dual REST + sub-FastMCP graceful para dominios del Monstruo",
    "leccion_corta": (
        "Para exponer un dominio al ecosistema usa DOS capas (APIRouter REST + "
        "sub-FastMCP mounteable) sobre UN Engine puro compartido. Cache singleton "
        "vía app.state. Modo degraded graceful en TODAS las capas. fastmcp como "
        "import opcional con fallback None — no como dependencia dura."
    ),
    "patron_ganador": {
        "estructura_archivos": {
            "engine.py": "Pydantic + db_factory + cache LRU + modo degraded",
            "routes.py": "APIRouter REST con auth Bearer + set_dependencies()",
            "mcp_tools.py": "FastMCP sub-server + set_mcp_engine() + build_*_mcp()",
        },
        "lifespan_main_py": [
            "engine = Engine(db_factory=build_default_db_factory())",
            "app.state.<dominio>_engine = engine",
            "routes.set_dependencies(engine)",
            "mcp_tools.set_mcp_engine(engine)",
            "app.include_router(routes.router, prefix='/v1/<dominio>')",
            "if mcp_tools.<dominio>_mcp is not None and fastmcp_server is not None:",
            "    fastmcp_server.mount('<dominio>', mcp_tools.<dominio>_mcp)",
        ],
        "ventajas": [
            "Cero duplicación de lógica (Engine único)",
            "Cache compartido entre HTTP y MCP",
            "Tests del Engine agnósticos de transport",
            "Auth dura solo en HTTP, MCP usa transport-level",
            "Graceful degradation si fastmcp ausente",
        ],
    },
    "salvaguardas_obligatorias": [
        "Engine acepta db_factory=None → degraded en vez de crashear",
        "os.environ FRESH en cada request del auth (anti-Dory)",
        "Cache LRU NO almacena respuestas con degraded=True",
        "sub-FastMCP fallback a None si import fastmcp falla",
        "Identidad marca: <dominio>_<accion>_<failure_type> en error codes",
    ],
    "anti_patron_evitado": (
        "Servidor FastMCP standalone separado (puerto/proceso distinto). "
        "Duplica infra, rompe cache compartido, complica deployment. La unión "
        "vía mount() en el FastMCP existente es canónica FastMCP 3.0+."
    ),
    "tests_obligatorios": [
        "Auth: sin key → 401, key inválida → 401, sin env var → 503",
        "Modo degraded: db caída → degraded=True + reason explícito",
        "Cache LRU: 2da llamada idéntica → cache_hit=True; degraded NO cachea",
        "FastMCP fallback: monkeypatch sys.modules['fastmcp']=None → None",
        "Identidad marca: códigos error con prefijo correcto",
        "1 opt-in real con env var <DOMINIO>_INTEGRATION_TESTS=true",
    ],
    "validado_contra": [
        "FastMCP 3.0 docs (Feb 2026) — server composition / mount()",
        "Speakeasy MCP composition patterns (Mar 2026)",
        "Cowork audit Bloque 4 (green light directo, sin caveats)",
        "Patrón Memento del kernel (kernel/memento_routes.py)",
    ],
    "implementacion_referencia": {
        "engine": "kernel/catastro/recommendation.py",
        "routes": "kernel/catastro/catastro_routes.py",
        "mcp_tools": "kernel/catastro/mcp_tools.py",
        "main_py_diff": "kernel/main.py L1233-1274",
        "tests": "tests/test_sprint86_bloque5.py",
        "smoke": "scripts/_smoke_catastro_mcp_sprint86.py",
    },
    "objetivos_maestros_satisfechos": [
        "#2 (Apple/Tesla calidad premium): naming semántico + docstrings narrativos",
        "#3 (Mínima Complejidad): UN Engine compartido, no duplicación",
        "#4 (No equivocarse 2x): mejoras audit Cowork B4 incorporadas",
        "#7 (No inventar rueda): reusa FastMCP del kernel via mount()",
        "#9 (Transversalidad): sub-MCP expone tools a otros dominios",
        "#12 (Soberanía): db_factory inyectable, Engine independiente de Supabase",
    ],
    "capa_arquitectonica": "C1 (Manos) — Backend Deployment + Observabilidad",
    "capas_transversales_activas": [
        "Capa 7 (Resiliencia Agéntica): modo degraded en todas las respuestas",
    ],
}


if __name__ == "__main__":
    import json
    print(json.dumps(SEED_PAYLOAD, indent=2, ensure_ascii=False))
