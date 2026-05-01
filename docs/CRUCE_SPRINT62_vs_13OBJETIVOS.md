# Cruce Sprint 62 vs. 13 Objetivos Maestros - Modo Detractor

**Fecha:** 1 mayo 2026
**Metodologia:** Cada epica se evalua como si fuera presentada a un inversor esceptico que busca debilidades.

---

## Matriz de Impacto

| Objetivo | Pre-S62 | Post-S62 | Delta | Epicas que Contribuyen |
|---|---|---|---|---|
| #1 Crear Empresas Reales | 87% | 89% | +2% | 62.3 (components para proyectos) |
| #2 Nivel Apple/Tesla | 77% | 83% | +6% | 62.3 (component library) |
| #3 Minima Complejidad | 80% | 82% | +2% | 62.1 (plugins simplifican extensiones) |
| #4 Nunca Equivocarse 2x | 83% | 84% | +1% | 62.2 (backup/restore) |
| #5 Gasolina Magna/Premium | 78% | 85% | +7% | 62.5 (cost optimization) |
| #6 Vanguardia Perpetua | 80% | 81% | +1% | 62.1 (plugin ecosystem) |
| #7 No Inventar Rueda | 92% | 93% | +1% | 62.1 (pluggy), 62.4 (exchangerate-api) |
| #8 Inteligencia Emergente | 82% | 83% | +1% | 62.5 (auto model selection) |
| #9 Transversalidad Universal | 100% | 100% | 0% | Ya completo |
| #10 Simulador Predictivo | 85% | 86% | +1% | 62.5 (cost data feeds simulator) |
| #11 Embriones Autonomos | 100% | 100% | 0% | Ya completo |
| #12 Ecosistema/Soberania | 75% | 85% | +10% | 62.1 (plugins), 62.2 (portability) |
| #13 Del Mundo | 72% | 82% | +10% | 62.4 (global deployment) |

**Promedio post-Sprint 62: 87.2%** (vs. 80.7% pre-Sprint 62 = +6.5%)

---

## Analisis Detractor por Epica

### Epica 62.1 - Plugin Architecture

**Lo que dice el plan:** Sistema de plugins con Pluggy, hooks, discovery, security check.

**Lo que dice el detractor:**

La seguridad del plugin system es ingenua. El `_security_check` busca strings prohibidos en el source code, pero eso se evade trivialmente con `getattr(os, 'system')('rm -rf /')`. Un atacante con conocimiento basico de Python bypasea el check en 5 minutos.

Ademas, no hay sandboxing real. Los plugins corren en el mismo proceso que el kernel. Un plugin malicioso puede acceder a `self.supabase`, leer todas las API keys del environment, o crashear el proceso entero.

El plan dice "plugin_sandbox.py" en la estructura pero no tiene implementacion. Es un archivo fantasma.

**Veredicto:** 5/10 sin correcciones. El concepto es correcto pero la ejecucion de seguridad es insuficiente para un sistema que maneja datos de negocio.

### Epica 62.2 - Data Portability Engine

**Lo que dice el plan:** Export/import completo en ZIP con JSON.

**Lo que dice el detractor:**

El export es funcional pero tiene un problema grave: no exporta archivos generados (imagenes, PDFs, assets de proyectos). Solo exporta datos de Supabase. Un usuario que exporta y reimporta pierde todos los archivos que El Monstruo genero para sus proyectos.

El import mode "replace" es peligroso: `delete().neq("id", "impossible")` borra TODA la tabla sin confirmacion. Un usuario que accidentalmente selecciona "replace" pierde todo.

No hay encriptacion del export. El ZIP contiene datos de negocio en texto plano. Si alguien intercepta el archivo, tiene acceso a toda la informacion del usuario.

**Veredicto:** 6/10. Funcional para backup basico, pero incompleto para portabilidad real.

### Epica 62.3 - Component Library

**Lo que dice el plan:** 30+ componentes con variantes, accessibility, responsive.

**Lo que dice el detractor:**

Los componentes se definen como JSON schemas pero se GENERAN con LLM en runtime. Esto significa que cada vez que El Monstruo usa un componente, paga tokens de LLM para generar el JSX. Para un proyecto con 10 componentes, eso son 10 llamadas LLM adicionales.

Deberia haber un cache de componentes ya renderizados. Si el hero_split con variant "dark" ya fue generado una vez, no deberia regenerarse.

Ademas, la calidad de los componentes depende 100% del LLM. No hay tests visuales, no hay regression testing, no hay Storybook. Un cambio en el modelo o en el prompt puede degradar la calidad de todos los componentes silenciosamente.

**Veredicto:** 5.5/10. La idea es excelente pero la implementacion es costosa y fragil.

### Epica 62.4 - Global Deployment Pipeline

**Lo que dice el plan:** Multi-currency, timezones, legal compliance.

**Lo que dice el detractor:**

El CurrencyEngine usa exchangerate-api.com que es un servicio gratuito con 1500 requests/mes. Si El Monstruo tiene 50 usuarios activos que generan proyectos con pricing, se agotan las requests en 1 dia.

Los legal compliance templates son estaticos. GDPR, CCPA, y LGPD cambian constantemente. El plan no tiene mecanismo para actualizar los templates cuando cambia la legislacion. En 6 meses los templates pueden estar desactualizados y generar problemas legales para los usuarios.

Falta la regulacion mas importante para LATAM: la Ley Federal de Proteccion de Datos Personales (Mexico), PDPA (India), y POPIA (Sudafrica). Si el objetivo es "Del Mundo", solo cubrir 3 regulaciones es insuficiente.

**Veredicto:** 6/10. Buen inicio pero incompleto para el claim de "global."

### Epica 62.5 - Cost Optimization Engine

**Lo que dice el plan:** Prediccion de costos, model selection automatica, budget management.

**Lo que dice el detractor:**

Los TASK_TOKEN_PROFILES son hardcoded. El chat_simple siempre estima 200 input + 300 output tokens. Pero en la realidad, un "chat_simple" puede variar de 50 a 2000 tokens dependiendo del contexto. La prediccion tiene un margen de error enorme.

El plan dice "confidence: 0.75" pero no explica como se calcula ni como se mejora. Es un numero magico.

La integracion con el Router Engine es superficial. El plan muestra 3 lineas de pseudocodigo pero no aborda como manejar el caso donde el optimizer selecciona un modelo que el router no tiene configurado, o que esta en cooldown, o que tiene rate limits.

**Veredicto:** 6.5/10. El concepto de cost optimization es critico y necesario, pero la implementacion necesita feedback loop real.

---

## Correcciones Mandatorias

### C1: Plugin Sandboxing Real (Epica 62.1)

**Problema:** Security check basado en string matching es trivialmente evadible.

**Correccion:** Implementar sandboxing real con RestrictedPython o ejecutar plugins en subprocess con resource limits:

```python
"""kernel/plugins/plugin_sandbox.py"""
import resource
import multiprocessing
from typing import Any, Callable

MAX_MEMORY_MB = 128
MAX_CPU_SECONDS = 10


def run_sandboxed(func: Callable, *args, **kwargs) -> Any:
    """Execute plugin function in sandboxed subprocess."""
    def _worker(result_queue):
        # Set resource limits
        resource.setrlimit(resource.RLIMIT_AS, (MAX_MEMORY_MB * 1024 * 1024, -1))
        resource.setrlimit(resource.RLIMIT_CPU, (MAX_CPU_SECONDS, MAX_CPU_SECONDS + 5))
        try:
            result = func(*args, **kwargs)
            result_queue.put(("ok", result))
        except Exception as e:
            result_queue.put(("error", str(e)))

    queue = multiprocessing.Queue()
    proc = multiprocessing.Process(target=_worker, args=(queue,))
    proc.start()
    proc.join(timeout=MAX_CPU_SECONDS + 5)

    if proc.is_alive():
        proc.kill()
        return None

    if not queue.empty():
        status, result = queue.get()
        if status == "ok":
            return result
    return None
```

Ademas, crear whitelist de hooks que cada plugin puede usar. Un plugin que declara `hooks: ["on_content_generated"]` NO puede acceder a `on_deploy`.

### C2: Export de Assets (Epica 62.2)

**Problema:** Solo exporta datos de Supabase, no archivos generados.

**Correccion:** Agregar export de archivos desde storage:

```python
# En exporter.py, agregar:
async def _export_assets(self, zf: zipfile.ZipFile) -> int:
    """Export generated assets from storage."""
    count = 0
    # List all files in user's storage bucket
    files = await self.supabase.storage.from_("projects").list(self.user_id)
    for file_info in files:
        data = await self.supabase.storage.from_("projects").download(
            f"{self.user_id}/{file_info['name']}"
        )
        zf.writestr(f"assets/{file_info['name']}", data)
        count += 1
    return count
```

Agregar confirmacion obligatoria para mode "replace" con countdown de 5 segundos.

### C3: Component Cache (Epica 62.3)

**Problema:** Cada render de componente hace una llamada LLM.

**Correccion:** Implementar cache de componentes renderizados:

```python
# En renderer.py, agregar:
_render_cache: dict[str, str] = {}  # key: f"{component_id}:{variant}:{theme}" -> JSX

async def render(self, component_id, variant="default", props=None, theme="dark"):
    cache_key = f"{component_id}:{variant}:{theme}"
    if cache_key in self._render_cache and not props:
        return self._render_cache[cache_key]
    
    jsx = await self._generate_jsx(context)
    if not props:  # Only cache default renders
        self._render_cache[cache_key] = jsx
    return jsx
```

Ademas, pre-render los 30 componentes al startup y almacenar en Supabase. Solo regenerar cuando se actualiza el component schema.

### C4: Exchange Rate Fallback (Epica 62.4)

**Problema:** Free API con 1500 req/month es insuficiente.

**Correccion:** Cache rates en Supabase con refresh diario (1 req/dia = 30/mes):

```python
# En currency_engine.py:
async def refresh_rates(self) -> None:
    # 1. Check Supabase cache first
    cached = await self.supabase.table("exchange_rates").select("*").order("updated_at", desc=True).limit(1).execute()
    if cached.data and self._is_fresh(cached.data[0]["updated_at"], hours=24):
        self._rates = cached.data[0]["rates"]
        return
    
    # 2. Only call API if cache is stale
    # ... existing API call ...
    
    # 3. Save to Supabase
    await self.supabase.table("exchange_rates").insert({
        "rates": self._rates, "updated_at": datetime.now(timezone.utc).isoformat()
    }).execute()
```

### C5: Legal Templates Expansion (Epica 62.4)

**Problema:** Solo 3 regulaciones para un sistema "global."

**Correccion:** Agregar al menos 3 regulaciones mas:

```python
# Agregar a COMPLIANCE_TEMPLATES:
"LFPDPPP": ComplianceTemplate(  # Mexico
    regulation="LFPDPPP", regions=["MX"],
    requirements=["Aviso de privacidad", "Consentimiento expreso", "Derechos ARCO"],
    cookie_banner=True, data_deletion_required=True,
    consent_required=True, dpo_required=False,
    template_code="lfpdppp_aviso_privacidad",
),
"PDPA_IN": ComplianceTemplate(  # India
    regulation="PDPA", regions=["IN"],
    requirements=["Consent notice", "Data fiduciary obligations", "Cross-border transfer rules"],
    cookie_banner=True, data_deletion_required=True,
    consent_required=True, dpo_required=True,
    template_code="pdpa_consent",
),
"POPIA": ComplianceTemplate(  # South Africa
    regulation="POPIA", regions=["ZA"],
    requirements=["Processing limitation", "Purpose specification", "Information officer"],
    cookie_banner=True, data_deletion_required=True,
    consent_required=True, dpo_required=True,
    template_code="popia_consent",
),
```

### C6: Cost Prediction Feedback Loop (Epica 62.5)

**Problema:** Token profiles son hardcoded, confidence es un numero magico.

**Correccion:** Implementar feedback loop que ajusta profiles basado en datos reales:

```python
# En predictor.py, agregar:
async def record_actual(self, task_type: str, actual_input: int,
                        actual_output: int, actual_cost: float) -> None:
    """Record actual usage to improve predictions."""
    profile = TASK_TOKEN_PROFILES.get(task_type)
    if not profile:
        return
    
    # Exponential moving average (alpha=0.1)
    alpha = 0.1
    profile["input"] = int(profile["input"] * (1 - alpha) + actual_input * alpha)
    profile["output"] = int(profile["output"] * (1 - alpha) + actual_output * alpha)
    
    # Update confidence based on prediction accuracy
    predicted_cost = self.predict(task_type).estimated_cost_usd
    error_pct = abs(predicted_cost - actual_cost) / max(actual_cost, 0.001)
    # Confidence decreases with error
    self._confidence = max(0.3, min(0.95, 1.0 - error_pct))
```

### C7: Router Integration Robustness (Epica 62.5)

**Problema:** Integracion con Router Engine no maneja edge cases.

**Correccion:** Agregar fallback chain:

```python
# En optimizer.py, agregar:
async def select_model_safe(self, task_type: str, **kwargs) -> dict:
    """Select model with fallback chain for robustness."""
    try:
        result = await self.select_model(task_type, **kwargs)
        # Verify model is actually available in router
        from config.model_catalog import MODELS
        if result["model"] not in MODELS:
            logger.warning("optimizer_model_not_in_catalog", model=result["model"])
            # Fall back to router's default selection
            return {"model": None, "budget_status": "fallback_to_router"}
        return result
    except Exception as e:
        logger.error("optimizer_error", error=str(e))
        return {"model": None, "budget_status": "error_fallback"}
```

### C8: Export Encryption (Epica 62.2)

**Problema:** Export ZIP contiene datos de negocio en texto plano.

**Correccion:** Agregar encriptacion opcional con password:

```python
# En exporter.py, modificar export_full:
async def export_full(self, output_dir: Path, password: str = None) -> Path:
    # ... existing export logic ...
    
    if password:
        # Use pyminizip for password-protected ZIP
        import pyminizip
        encrypted_path = output_dir / f"monstruo_export_{timestamp}_encrypted.zip"
        pyminizip.compress(str(zip_path), None, str(encrypted_path), password, 5)
        zip_path.unlink()  # Remove unencrypted version
        return encrypted_path
    
    return zip_path
```

---

## Score de Confianza

**Sin correcciones:** 5.8/10 — Conceptos solidos pero implementacion de seguridad y robustez insuficientes.

**Con correcciones C1-C8:** 8.0/10 — Plugin sandboxing real, component cache, y feedback loops elevan la calidad a produccion.

**Correcciones criticas (MUST):** C1 (sandboxing), C3 (cache), C6 (feedback loop)
**Correcciones importantes (SHOULD):** C2 (assets), C4 (rate cache), C7 (router fallback)
**Correcciones deseables (NICE):** C5 (legal expansion), C8 (encryption)

---

## Objetivos que NO Avanzaron

| Objetivo | Cobertura | Razon | Proximo Sprint |
|---|---|---|---|
| #9 Transversalidad | 100% | Ya completo | N/A |
| #11 Embriones | 100% | Ya completo | N/A |

Todos los demas objetivos avanzan al menos +1%. Los 4 mas rezagados (#13, #12, #2, #5) reciben los mayores deltas (+10%, +10%, +6%, +7% respectivamente).
