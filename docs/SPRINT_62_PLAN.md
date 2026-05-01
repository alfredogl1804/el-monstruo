# Sprint 62 — "La Arquitectura Abierta"

**Fecha:** 1 mayo 2026
**Version:** 0.62.0
**Autor:** Manus AI
**Filosofia:** El Monstruo deja de ser una caja negra y se convierte en una plataforma extensible, portable, y economicamente optimizada.

---

## Contexto Estrategico

La serie 61-70 tiene como mision llevar todos los objetivos al 85%+. Post Sprint 61, los 4 objetivos mas rezagados son:

| Objetivo | Cobertura | Gap |
|---|---|---|
| #13 Del Mundo | 72% | 28% |
| #12 Ecosistema/Soberania | 75% | 25% |
| #2 Nivel Apple/Tesla | 77% | 23% |
| #5 Gasolina Magna/Premium | 78% | 22% |

Sprint 62 ataca los 4 simultaneamente con una arquitectura que los conecta: un sistema de plugins abierto (#12) que permite componentes visuales de calidad (#2), funciona globalmente (#13), y optimiza costos automaticamente (#5).

---

## Stack Validado en Tiempo Real

| Herramienta | Version | Fecha | Rol |
|---|---|---|---|
| Pluggy | ~1.5.0 | 2024 | Framework de hooks para plugin system [1] |
| Stripe | 15.1.0 | Apr 24, 2026 | Multi-currency (135+ currencies) [2] |
| shadcn/ui | latest | 2026 | Base para component library |
| Router Engine | Sprint 29 | Apr 25, 2026 | SDKs nativos (NO LiteLLM - CVE-2026-35030) |

**Decision critica:** LiteLLM esta PROHIBIDO en El Monstruo (CVE-2026-35030). El cost optimization engine se construye SOBRE el router nativo existente, no lo reemplaza.

---

## Epica 62.1 - Plugin Architecture

**Objetivo:** Obj #12 (Ecosistema/Soberania)
**Impacto:** +5% en Obj #12

### Vision

Transformar El Monstruo de un monolito cerrado a una plataforma extensible donde terceros (o el propio sistema) pueden agregar capacidades sin modificar el core. Patron Microkernel con hooks estilo Pluggy.

### Arquitectura

```
kernel/plugins/
  __init__.py
  plugin_spec.py          # Hook specifications (interfaz)
  plugin_manager.py       # Registry + lifecycle
  plugin_loader.py        # Discovery + validation
  plugin_sandbox.py       # Isolation + resource limits
  builtin/
    __init__.py
    webhook_plugin.py     # Migrar tools/webhook.py a plugin
    analytics_plugin.py   # Migrar observability hooks a plugin
```

### Componentes

#### 1. Plugin Specification (Hook Interface)

```python
"""kernel/plugins/plugin_spec.py"""
import pluggy

hookspec = pluggy.HookspecMarker("monstruo")
hookimpl = pluggy.HookimplMarker("monstruo")


class MonstruoPluginSpec:
    """Specification of all hooks available to plugins."""

    @hookspec
    def on_project_created(self, project_id: str, config: dict) -> None:
        """Called when a new project is created."""

    @hookspec
    def on_task_completed(self, task_id: str, result: dict) -> dict:
        """Called when an embrion completes a task. Can modify result."""

    @hookspec
    def on_model_selected(self, intent: str, model_name: str) -> str | None:
        """Called before model routing. Return alternative model or None."""

    @hookspec
    def on_content_generated(self, content: str, content_type: str) -> str:
        """Called after content generation. Can transform content."""

    @hookspec
    def on_error(self, error: Exception, context: dict) -> dict | None:
        """Called on error. Return recovery action or None."""

    @hookspec
    def on_deploy(self, project_id: str, artifacts: dict) -> dict:
        """Called before deployment. Can add/modify artifacts."""

    @hookspec
    def get_tools(self) -> list[dict]:
        """Return additional tools this plugin provides."""

    @hookspec
    def get_templates(self) -> list[dict]:
        """Return project templates this plugin provides."""
```

#### 2. Plugin Manager

```python
"""kernel/plugins/plugin_manager.py"""
import pluggy
import structlog
from typing import Any
from dataclasses import dataclass, field

logger = structlog.get_logger("plugins")

@dataclass
class PluginMetadata:
    name: str
    version: str
    author: str
    description: str
    hooks: list[str]
    enabled: bool = True
    config: dict = field(default_factory=dict)


class PluginManager:
    """Central registry and lifecycle manager for plugins."""

    def __init__(self):
        self.pm = pluggy.PluginManager("monstruo")
        self.pm.add_hookspecs(MonstruoPluginSpec)
        self._registry: dict[str, PluginMetadata] = {}
        self._load_order: list[str] = []

    async def register(self, plugin: Any, metadata: PluginMetadata) -> bool:
        """Register and validate a plugin."""
        if not self.pm.parse_hookimpl_opts(plugin, None):
            logger.warning("plugin_no_hooks", name=metadata.name)
            return False

        if not await self._security_check(plugin):
            logger.error("plugin_security_fail", name=metadata.name)
            return False

        self.pm.register(plugin, name=metadata.name)
        self._registry[metadata.name] = metadata
        self._load_order.append(metadata.name)
        logger.info("plugin_registered", name=metadata.name, version=metadata.version)
        return True

    async def unregister(self, name: str) -> bool:
        """Unregister a plugin by name."""
        if name not in self._registry:
            return False
        self.pm.unregister(name=name)
        del self._registry[name]
        self._load_order.remove(name)
        return True

    def call_hook(self, hook_name: str, **kwargs) -> list[Any]:
        """Call a hook and collect results from all plugins."""
        hook = getattr(self.pm.hook, hook_name, None)
        if hook is None:
            return []
        return hook(**kwargs)

    async def _security_check(self, plugin: Any) -> bool:
        """Validate plugin doesn't import dangerous modules."""
        import inspect
        source = inspect.getsource(type(plugin))
        forbidden = ["os.system", "subprocess", "eval(", "exec(", "__import__"]
        return not any(f in source for f in forbidden)

    def list_plugins(self) -> list[PluginMetadata]:
        return list(self._registry.values())
```

#### 3. Plugin Loader (Discovery)

```python
"""kernel/plugins/plugin_loader.py"""
import importlib
import importlib.util
from pathlib import Path
import structlog

logger = structlog.get_logger("plugins.loader")

PLUGINS_DIR = Path("plugins/")
BUILTIN_DIR = Path("kernel/plugins/builtin/")


class PluginLoader:
    """Discovers and loads plugins from filesystem."""

    def __init__(self, manager: PluginManager):
        self.manager = manager

    async def discover_and_load(self) -> int:
        """Discover all plugins and load them. Returns count loaded."""
        loaded = 0
        for path in BUILTIN_DIR.glob("*_plugin.py"):
            if await self._load_from_path(path, builtin=True):
                loaded += 1
        if PLUGINS_DIR.exists():
            for path in PLUGINS_DIR.glob("*/plugin.py"):
                if await self._load_from_path(path, builtin=False):
                    loaded += 1
        logger.info("plugins_loaded", count=loaded)
        return loaded

    async def _load_from_path(self, path: Path, builtin: bool) -> bool:
        try:
            spec = importlib.util.spec_from_file_location(f"plugin_{path.stem}", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            plugin = getattr(module, "plugin_instance", None)
            metadata = getattr(module, "plugin_metadata", None)
            if plugin is None or metadata is None:
                return False
            return await self.manager.register(plugin, metadata)
        except Exception as e:
            logger.error("plugin_load_error", path=str(path), error=str(e))
            return False
```

### API Publica

```
POST   /api/plugins              -> Install plugin (upload ZIP)
GET    /api/plugins              -> List installed plugins
DELETE /api/plugins/{name}       -> Uninstall plugin
PATCH  /api/plugins/{name}      -> Enable/disable plugin
GET    /api/plugins/{name}/config -> Get plugin config
PUT    /api/plugins/{name}/config -> Update plugin config
```

### Tabla Supabase

```sql
CREATE TABLE plugins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    version TEXT NOT NULL,
    author TEXT,
    description TEXT,
    hooks TEXT[] NOT NULL,
    enabled BOOLEAN DEFAULT true,
    config JSONB DEFAULT '{}',
    installed_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
```

---

## Epica 62.2 - Data Portability Engine

**Objetivo:** Obj #12 (Ecosistema/Soberania)
**Impacto:** +5% en Obj #12

### Vision

El usuario puede exportar TODOS sus datos en cualquier momento en formato estandar (JSON + ZIP). Tambien puede importar datos de un backup previo. Soberania real = portabilidad real.

### Arquitectura

```
kernel/portability/
  __init__.py
  exporter.py         # Full data export
  importer.py         # Data import with validation
  schema_validator.py # JSON Schema validation
  formats/
    __init__.py
    json_format.py    # JSON export/import
    zip_format.py     # ZIP bundle (JSON + assets)
```

### Export Schema

```python
"""kernel/portability/exporter.py"""
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
import structlog
from supabase import AsyncClient

logger = structlog.get_logger("portability.export")

EXPORT_VERSION = "1.0.0"

EXPORT_TABLES = [
    "projects", "project_configs", "causal_events", "causal_factors",
    "predictions", "error_lessons", "error_rules", "plugins",
    "embrion_tasks", "job_executions", "conversation_messages",
]


class DataExporter:
    """Export all user data to portable format."""

    def __init__(self, supabase: AsyncClient, user_id: str):
        self.supabase = supabase
        self.user_id = user_id

    async def export_full(self, output_dir: Path) -> Path:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        zip_path = output_dir / f"monstruo_export_{timestamp}.zip"

        manifest = {
            "version": EXPORT_VERSION,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "user_id": self.user_id,
            "tables": {},
        }

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for table in EXPORT_TABLES:
                data = await self._export_table(table)
                manifest["tables"][table] = {"count": len(data), "schema_version": "1.0"}
                zf.writestr(f"data/{table}.json", json.dumps(data, default=str, indent=2))
            zf.writestr("manifest.json", json.dumps(manifest, indent=2))
            zf.writestr("schema/tables.json", json.dumps(self._get_schema_definitions(), indent=2))

        logger.info("export_complete", path=str(zip_path), tables=len(EXPORT_TABLES))
        return zip_path

    async def _export_table(self, table: str) -> list[dict]:
        try:
            response = await self.supabase.table(table).select("*").execute()
            return response.data or []
        except Exception as e:
            logger.error("export_table_error", table=table, error=str(e))
            return []

    def _get_schema_definitions(self) -> dict:
        return {
            "version": EXPORT_VERSION,
            "tables": {table: {"type": "array", "items": {"type": "object"}} for table in EXPORT_TABLES}
        }
```

### Import with Validation

```python
"""kernel/portability/importer.py"""
import json
import zipfile
from pathlib import Path
import structlog
from supabase import AsyncClient

logger = structlog.get_logger("portability.import")


class DataImporter:
    """Import data from a portable export bundle."""

    def __init__(self, supabase: AsyncClient, user_id: str):
        self.supabase = supabase
        self.user_id = user_id

    async def import_from_zip(self, zip_path: Path, mode: str = "merge") -> dict:
        """Import data. Modes: merge, replace, dry_run."""
        results = {"imported": 0, "skipped": 0, "errors": 0, "tables": {}}

        with zipfile.ZipFile(zip_path, "r") as zf:
            manifest = json.loads(zf.read("manifest.json"))
            if not self._validate_manifest(manifest):
                raise ValueError("Invalid export manifest")

            for table in manifest["tables"]:
                records = json.loads(zf.read(f"data/{table}.json"))
                if mode == "dry_run":
                    results["tables"][table] = {"count": len(records), "status": "validated"}
                    continue
                table_result = await self._import_table(table, records, mode)
                results["tables"][table] = table_result
                results["imported"] += table_result.get("imported", 0)
                results["skipped"] += table_result.get("skipped", 0)
                results["errors"] += table_result.get("errors", 0)

        logger.info("import_complete", mode=mode, **results)
        return results

    async def _import_table(self, table: str, records: list[dict], mode: str) -> dict:
        imported, skipped, errors = 0, 0, 0
        if mode == "replace":
            await self.supabase.table(table).delete().neq("id", "impossible").execute()
        for record in records:
            try:
                if mode == "merge":
                    await self.supabase.table(table).upsert(record).execute()
                else:
                    await self.supabase.table(table).insert(record).execute()
                imported += 1
            except Exception as e:
                if "duplicate" in str(e).lower():
                    skipped += 1
                else:
                    errors += 1
        return {"imported": imported, "skipped": skipped, "errors": errors}

    def _validate_manifest(self, manifest: dict) -> bool:
        return all(k in manifest for k in ["version", "exported_at", "tables"])
```

### API Endpoints

```
POST /api/portability/export    -> Trigger full export (returns download URL)
POST /api/portability/import    -> Upload ZIP and import (mode: merge|replace|dry_run)
GET  /api/portability/status    -> Check export/import job status
GET  /api/portability/history   -> List previous exports
```

---

## Epica 62.3 - Component Library (Nivel Apple/Tesla)

**Objetivo:** Obj #2 (Nivel Apple/Tesla)
**Impacto:** +6% en Obj #2

### Vision

Biblioteca de 30+ componentes pre-built que El Monstruo usa al generar proyectos. Cada componente tiene variantes, es responsive, accesible, y sigue un design system coherente. Nivel de calidad: Apple Human Interface Guidelines + Tesla UI patterns.

### Arquitectura

```
kernel/components/
  __init__.py
  registry.py           # Component catalog
  renderer.py           # JSX/TSX generation
  validator.py          # Component quality check
  library/
    navigation/
      navbar.json, sidebar.json, breadcrumb.json
    hero/
      hero_split.json, hero_centered.json, hero_video.json, hero_parallax.json
    content/
      feature_grid.json, testimonial.json, pricing_table.json, timeline.json, faq.json
    forms/
      contact_form.json, checkout_form.json, search_bar.json, newsletter.json
    commerce/
      product_card.json, cart_drawer.json, order_summary.json, wishlist.json
    layout/
      footer.json, cta_section.json, stats_bar.json, divider.json, banner.json
```

### Component Schema

```python
"""kernel/components/registry.py"""
from dataclasses import dataclass, field
from typing import Optional
import json
from pathlib import Path
import structlog

logger = structlog.get_logger("components")

@dataclass
class ComponentVariant:
    name: str          # e.g., "minimal", "bold", "glassmorphism"
    description: str
    tailwind_classes: dict[str, str]  # element -> classes
    animations: list[str]             # framer-motion variants
    dark_mode: bool = True


@dataclass
class ComponentDefinition:
    id: str            # e.g., "hero_split"
    category: str      # e.g., "hero"
    name: str          # e.g., "Split Hero"
    description: str
    variants: list[ComponentVariant]
    props: dict[str, dict]           # prop_name -> {type, default, required}
    dependencies: list[str]          # npm packages needed
    accessibility: dict              # ARIA roles, keyboard nav
    responsive_breakpoints: dict[str, dict]  # sm/md/lg/xl overrides
    quality_score: float = 0.0       # Auto-calculated


class ComponentRegistry:
    """Central catalog of all available components."""

    def __init__(self, library_dir: Path = Path("kernel/components/library")):
        self.library_dir = library_dir
        self._components: dict[str, ComponentDefinition] = {}
        self._categories: dict[str, list[str]] = {}

    async def load_all(self) -> int:
        count = 0
        for json_file in self.library_dir.rglob("*.json"):
            try:
                data = json.loads(json_file.read_text())
                component = self._parse_component(data)
                self._components[component.id] = component
                category = component.category
                if category not in self._categories:
                    self._categories[category] = []
                self._categories[category].append(component.id)
                count += 1
            except Exception as e:
                logger.error("component_load_error", file=str(json_file), error=str(e))
        logger.info("components_loaded", count=count)
        return count

    def get_by_category(self, category: str) -> list[ComponentDefinition]:
        ids = self._categories.get(category, [])
        return [self._components[id] for id in ids]

    def get_by_id(self, component_id: str) -> Optional[ComponentDefinition]:
        return self._components.get(component_id)

    def search(self, query: str) -> list[ComponentDefinition]:
        query_lower = query.lower()
        return [
            c for c in self._components.values()
            if query_lower in c.name.lower() or query_lower in c.description.lower()
        ]

    def get_for_project_type(self, project_type: str) -> list[ComponentDefinition]:
        """Get recommended components for a project type."""
        recommendations = {
            "ecommerce": ["navbar", "hero_split", "product_card", "cart_drawer", "checkout_form", "footer"],
            "saas": ["navbar", "hero_centered", "feature_grid", "pricing_table", "testimonial", "cta_section", "footer"],
            "portfolio": ["navbar", "hero_video", "timeline", "stats_bar", "contact_form", "footer"],
            "blog": ["navbar", "hero_centered", "feature_grid", "search_bar", "footer"],
            "landing": ["navbar", "hero_split", "feature_grid", "testimonial", "pricing_table", "cta_section", "footer"],
        }
        ids = recommendations.get(project_type, recommendations["landing"])
        return [self._components[id] for id in ids if id in self._components]

    def _parse_component(self, data: dict) -> ComponentDefinition:
        variants = [ComponentVariant(**v) for v in data.get("variants", [])]
        return ComponentDefinition(
            id=data["id"], category=data["category"], name=data["name"],
            description=data["description"], variants=variants,
            props=data.get("props", {}), dependencies=data.get("dependencies", []),
            accessibility=data.get("accessibility", {}),
            responsive_breakpoints=data.get("responsive_breakpoints", {}),
        )
```

### Component Renderer

```python
"""kernel/components/renderer.py"""
import structlog

logger = structlog.get_logger("components.renderer")


class ComponentRenderer:
    """Generates JSX/TSX code from component definitions."""

    def __init__(self, registry: ComponentRegistry):
        self.registry = registry

    async def render(self, component_id: str, variant: str = "default",
                     props: dict = None, theme: str = "dark") -> str:
        component = self.registry.get_by_id(component_id)
        if not component:
            raise ValueError(f"Component not found: {component_id}")

        selected_variant = next(
            (v for v in component.variants if v.name == variant),
            component.variants[0] if component.variants else None
        )

        context = {"component": component, "variant": selected_variant,
                    "props": props or {}, "theme": theme}
        return await self._generate_jsx(context)

    async def render_page(self, component_ids: list[str],
                          project_type: str, theme: str = "dark") -> str:
        sections = []
        for cid in component_ids:
            jsx = await self.render(cid, theme=theme)
            sections.append(jsx)
        return "\n\n".join(sections)

    async def _generate_jsx(self, context: dict) -> str:
        """Use LLM to generate high-quality JSX from component spec."""
        component = context["component"]
        variant = context["variant"]

        prompt = f"""Generate a React component ({component.name}) with these specs:
- Category: {component.category}
- Variant: {variant.name if variant else 'default'}
- Props: {context['props']}
- Theme: {context['theme']}
- Accessibility: {component.accessibility}
- Tailwind classes: {variant.tailwind_classes if variant else {}}
- Must be responsive (sm/md/lg/xl breakpoints)
- Must include ARIA labels and keyboard navigation
- Must use Framer Motion for animations
- Quality level: Apple/Tesla (premium feel, micro-interactions)
"""
        from router.engine import route_completion
        response = await route_completion(
            messages=[{"role": "user", "content": prompt}],
            intent="execute",
        )
        return response.content
```

### Categorias de Componentes (30+)

| Categoria | Componentes | Variantes por Componente |
|---|---|---|
| Navigation | navbar, sidebar, breadcrumb, tabs | 4 (minimal, bold, glass, floating) |
| Hero | hero_split, hero_centered, hero_video, hero_parallax | 3 (light, dark, gradient) |
| Content | feature_grid, testimonial, pricing_table, timeline, FAQ | 3 (cards, list, minimal) |
| Forms | contact_form, checkout_form, search_bar, newsletter | 3 (inline, modal, floating) |
| Commerce | product_card, cart_drawer, order_summary, wishlist | 3 (grid, list, compact) |
| Layout | footer, cta_section, stats_bar, divider, banner | 3 (centered, split, full-width) |

---

## Epica 62.4 - Global Deployment Pipeline

**Objetivo:** Obj #13 (Del Mundo)
**Impacto:** +10% en Obj #13

### Vision

Llevar la internacionalizacion de "traduce texto" a "funciona globalmente." Multi-currency, timezone-aware scheduling, locale-specific legal compliance, y CDN geo-routing.

### Arquitectura

```
kernel/global/
  __init__.py
  currency_engine.py    # Multi-currency pricing
  timezone_engine.py    # Timezone-aware scheduling
  legal_compliance.py   # GDPR, CCPA, LGPD templates
  geo_router.py         # CDN config generation
  locale_registry.py    # Extended locale metadata
```

### Multi-Currency Engine

```python
"""kernel/global/currency_engine.py"""
from dataclasses import dataclass
from typing import Optional
import httpx
import structlog

logger = structlog.get_logger("global.currency")

@dataclass
class CurrencyConfig:
    code: str       # ISO 4217: USD, EUR, MXN
    symbol: str
    name: str
    decimal_places: int
    symbol_position: str    # "before" or "after"
    thousands_separator: str
    decimal_separator: str

# 20 most important currencies for global commerce
CURRENCIES: dict[str, CurrencyConfig] = {
    "USD": CurrencyConfig("USD", "$", "US Dollar", 2, "before", ",", "."),
    "EUR": CurrencyConfig("EUR", "E", "Euro", 2, "before", ".", ","),
    "GBP": CurrencyConfig("GBP", "L", "British Pound", 2, "before", ",", "."),
    "JPY": CurrencyConfig("JPY", "Y", "Japanese Yen", 0, "before", ",", "."),
    "MXN": CurrencyConfig("MXN", "$", "Mexican Peso", 2, "before", ",", "."),
    "BRL": CurrencyConfig("BRL", "R$", "Brazilian Real", 2, "before", ".", ","),
    "CAD": CurrencyConfig("CAD", "CA$", "Canadian Dollar", 2, "before", ",", "."),
    "AUD": CurrencyConfig("AUD", "A$", "Australian Dollar", 2, "before", ",", "."),
    "INR": CurrencyConfig("INR", "Rs", "Indian Rupee", 2, "before", ",", "."),
    "CNY": CurrencyConfig("CNY", "Y", "Chinese Yuan", 2, "before", ",", "."),
    "KRW": CurrencyConfig("KRW", "W", "Korean Won", 0, "before", ",", "."),
    "CHF": CurrencyConfig("CHF", "CHF", "Swiss Franc", 2, "before", "'", "."),
    "SEK": CurrencyConfig("SEK", "kr", "Swedish Krona", 2, "after", " ", ","),
    "NOK": CurrencyConfig("NOK", "kr", "Norwegian Krone", 2, "after", " ", ","),
    "ARS": CurrencyConfig("ARS", "$", "Argentine Peso", 2, "before", ".", ","),
    "COP": CurrencyConfig("COP", "$", "Colombian Peso", 0, "before", ".", ","),
    "CLP": CurrencyConfig("CLP", "$", "Chilean Peso", 0, "before", ".", ","),
    "AED": CurrencyConfig("AED", "AED", "UAE Dirham", 2, "before", ",", "."),
    "SAR": CurrencyConfig("SAR", "SAR", "Saudi Riyal", 2, "before", ",", "."),
    "TRY": CurrencyConfig("TRY", "TL", "Turkish Lira", 2, "before", ".", ","),
}

# Locale -> Default Currency mapping
LOCALE_CURRENCY: dict[str, str] = {
    "en-US": "USD", "en-GB": "GBP", "es-MX": "MXN", "es-ES": "EUR",
    "pt-BR": "BRL", "fr-FR": "EUR", "de-DE": "EUR", "ja-JP": "JPY",
    "ko-KR": "KRW", "zh-CN": "CNY", "ar-SA": "SAR", "hi-IN": "INR",
    "it-IT": "EUR", "nl-NL": "EUR", "sv-SE": "SEK", "no-NO": "NOK",
    "tr-TR": "TRY", "ar-AE": "AED", "es-AR": "ARS", "es-CO": "COP",
    "es-CL": "CLP", "en-CA": "CAD", "en-AU": "AUD",
}


class CurrencyEngine:
    """Multi-currency pricing and formatting."""

    def __init__(self):
        self._rates: dict[str, float] = {}
        self._rates_updated: Optional[str] = None

    async def refresh_rates(self) -> None:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10)
                data = resp.json()
                self._rates = data.get("rates", {})
                self._rates_updated = data.get("date")
        except Exception as e:
            logger.error("rates_refresh_error", error=str(e))

    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        if from_currency == to_currency:
            return amount
        usd_amount = amount / self._rates.get(from_currency, 1.0)
        return usd_amount * self._rates.get(to_currency, 1.0)

    def format_price(self, amount: float, currency_code: str) -> str:
        config = CURRENCIES.get(currency_code)
        if not config:
            return f"{amount:.2f} {currency_code}"
        rounded = round(amount, config.decimal_places)
        if config.decimal_places == 0:
            formatted = f"{int(rounded):,}".replace(",", config.thousands_separator)
        else:
            int_part = int(rounded)
            dec_part = round((rounded - int_part) * (10 ** config.decimal_places))
            int_str = f"{int_part:,}".replace(",", config.thousands_separator)
            dec_str = str(dec_part).zfill(config.decimal_places)
            formatted = f"{int_str}{config.decimal_separator}{dec_str}"
        if config.symbol_position == "before":
            return f"{config.symbol}{formatted}"
        return f"{formatted} {config.symbol}"

    def get_currency_for_locale(self, locale: str) -> str:
        return LOCALE_CURRENCY.get(locale, "USD")

    def generate_pricing_component(self, prices: dict[str, float], locale: str) -> dict:
        currency = self.get_currency_for_locale(locale)
        return {
            "currency": currency,
            "config": CURRENCIES[currency].__dict__,
            "prices": {
                plan: {
                    "amount": self.convert(usd_price, "USD", currency),
                    "formatted": self.format_price(self.convert(usd_price, "USD", currency), currency),
                }
                for plan, usd_price in prices.items()
            },
        }
```

### Timezone-Aware Scheduling

```python
"""kernel/global/timezone_engine.py"""
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from dataclasses import dataclass

@dataclass
class TimezoneConfig:
    iana_id: str
    display_name: str
    utc_offset: str
    locale: str

TIMEZONE_MAP: dict[str, TimezoneConfig] = {
    "America/New_York": TimezoneConfig("America/New_York", "Eastern Time", "UTC-5", "en-US"),
    "America/Los_Angeles": TimezoneConfig("America/Los_Angeles", "Pacific Time", "UTC-8", "en-US"),
    "America/Mexico_City": TimezoneConfig("America/Mexico_City", "Central Mexico", "UTC-6", "es-MX"),
    "America/Sao_Paulo": TimezoneConfig("America/Sao_Paulo", "Brasilia Time", "UTC-3", "pt-BR"),
    "Europe/London": TimezoneConfig("Europe/London", "GMT", "UTC+0", "en-GB"),
    "Europe/Paris": TimezoneConfig("Europe/Paris", "Central European", "UTC+1", "fr-FR"),
    "Europe/Berlin": TimezoneConfig("Europe/Berlin", "Central European", "UTC+1", "de-DE"),
    "Asia/Tokyo": TimezoneConfig("Asia/Tokyo", "Japan Standard", "UTC+9", "ja-JP"),
    "Asia/Shanghai": TimezoneConfig("Asia/Shanghai", "China Standard", "UTC+8", "zh-CN"),
    "Asia/Kolkata": TimezoneConfig("Asia/Kolkata", "India Standard", "UTC+5:30", "hi-IN"),
    "Asia/Dubai": TimezoneConfig("Asia/Dubai", "Gulf Standard", "UTC+4", "ar-AE"),
    "Asia/Riyadh": TimezoneConfig("Asia/Riyadh", "Arabia Standard", "UTC+3", "ar-SA"),
    "Australia/Sydney": TimezoneConfig("Australia/Sydney", "Australian Eastern", "UTC+11", "en-AU"),
}


class TimezoneEngine:
    def now_in_tz(self, tz_id: str) -> datetime:
        return datetime.now(ZoneInfo(tz_id))

    def convert(self, dt: datetime, from_tz: str, to_tz: str) -> datetime:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo(from_tz))
        return dt.astimezone(ZoneInfo(to_tz))

    def get_business_hours(self, tz_id: str) -> tuple[int, int]:
        exceptions = {"Asia/Tokyo": (9, 18), "Asia/Riyadh": (8, 16), "Asia/Dubai": (8, 17)}
        return exceptions.get(tz_id, (9, 18))

    def is_business_hours(self, tz_id: str) -> bool:
        now = self.now_in_tz(tz_id)
        start, end = self.get_business_hours(tz_id)
        return start <= now.hour < end and now.weekday() < 5

    def schedule_for_locale(self, locale: str, preferred_hour: int = 9) -> datetime:
        tz_id = self._locale_to_tz(locale)
        now = self.now_in_tz(tz_id)
        target = now.replace(hour=preferred_hour, minute=0, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return target

    def _locale_to_tz(self, locale: str) -> str:
        locale_tz = {
            "en-US": "America/New_York", "es-MX": "America/Mexico_City",
            "pt-BR": "America/Sao_Paulo", "en-GB": "Europe/London",
            "fr-FR": "Europe/Paris", "de-DE": "Europe/Berlin",
            "ja-JP": "Asia/Tokyo", "zh-CN": "Asia/Shanghai",
            "hi-IN": "Asia/Kolkata", "ar-SA": "Asia/Riyadh",
            "ar-AE": "Asia/Dubai", "ko-KR": "Asia/Shanghai",
        }
        return locale_tz.get(locale, "America/New_York")
```

### Legal Compliance Templates

```python
"""kernel/global/legal_compliance.py"""
from dataclasses import dataclass

@dataclass
class ComplianceTemplate:
    regulation: str
    regions: list[str]
    requirements: list[str]
    cookie_banner: bool
    data_deletion_required: bool
    consent_required: bool
    dpo_required: bool
    template_code: str

COMPLIANCE_TEMPLATES: dict[str, ComplianceTemplate] = {
    "GDPR": ComplianceTemplate(
        regulation="GDPR", regions=["EU", "EEA", "UK"],
        requirements=[
            "Cookie consent banner with granular options",
            "Right to erasure (data deletion endpoint)",
            "Data portability (export in machine-readable format)",
            "Privacy policy with specific disclosures",
            "Consent logging with timestamps",
            "DPO contact information",
        ],
        cookie_banner=True, data_deletion_required=True,
        consent_required=True, dpo_required=True, template_code="gdpr_consent_banner",
    ),
    "CCPA": ComplianceTemplate(
        regulation="CCPA", regions=["US-CA"],
        requirements=[
            "Do Not Sell My Personal Information link",
            "Right to know what data is collected",
            "Right to delete personal information",
            "Non-discrimination for exercising rights",
        ],
        cookie_banner=False, data_deletion_required=True,
        consent_required=False, dpo_required=False, template_code="ccpa_opt_out",
    ),
    "LGPD": ComplianceTemplate(
        regulation="LGPD", regions=["BR"],
        requirements=[
            "Consent banner (similar to GDPR)",
            "Data subject rights (access, correction, deletion)",
            "DPO (Encarregado) designation",
            "International transfer safeguards",
        ],
        cookie_banner=True, data_deletion_required=True,
        consent_required=True, dpo_required=True, template_code="lgpd_consent_banner",
    ),
}


class LegalComplianceEngine:
    def get_requirements_for_regions(self, regions: list[str]) -> list[ComplianceTemplate]:
        applicable = []
        for template in COMPLIANCE_TEMPLATES.values():
            if any(r in template.regions for r in regions):
                applicable.append(template)
        return applicable

    def generate_privacy_policy_sections(self, regions: list[str]) -> list[dict]:
        templates = self.get_requirements_for_regions(regions)
        return [{
            "regulation": t.regulation,
            "requirements": t.requirements,
            "needs_cookie_banner": t.cookie_banner,
            "needs_deletion_endpoint": t.data_deletion_required,
        } for t in templates]

    def get_consent_component(self, regions: list[str]) -> str:
        templates = self.get_requirements_for_regions(regions)
        for t in templates:
            if t.regulation == "GDPR":
                return t.template_code
        return templates[0].template_code if templates else "basic_consent"
```

---

## Epica 62.5 - Cost Optimization Engine

**Objetivo:** Obj #5 (Gasolina Magna/Premium)
**Impacto:** +7% en Obj #5

### Vision

Predecir el costo de cada tarea ANTES de ejecutarla, seleccionar automaticamente el modelo optimo basado en complejidad vs. presupuesto, y proveer un dashboard de unit economics en tiempo real.

### Arquitectura

```
kernel/cost/
  __init__.py
  predictor.py        # Token/cost prediction
  optimizer.py        # Model selection optimization
  budget_manager.py   # Budget allocation and tracking
  dashboard.py        # Cost analytics data
```

### Cost Predictor

```python
"""kernel/cost/predictor.py"""
from dataclasses import dataclass
from config.model_catalog import MODELS
import structlog

logger = structlog.get_logger("cost.predictor")

@dataclass
class CostPrediction:
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_cost_usd: float
    confidence: float
    recommended_model: str
    alternatives: list[dict]

TASK_TOKEN_PROFILES: dict[str, dict] = {
    "chat_simple": {"input": 200, "output": 300, "complexity": 0.2},
    "chat_complex": {"input": 500, "output": 1000, "complexity": 0.5},
    "code_generation": {"input": 800, "output": 2000, "complexity": 0.7},
    "code_review": {"input": 2000, "output": 1500, "complexity": 0.6},
    "deep_analysis": {"input": 1500, "output": 3000, "complexity": 0.9},
    "translation": {"input": 500, "output": 600, "complexity": 0.3},
    "summarization": {"input": 3000, "output": 500, "complexity": 0.4},
    "creative_writing": {"input": 300, "output": 2000, "complexity": 0.6},
    "planning": {"input": 1000, "output": 2000, "complexity": 0.8},
    "classification": {"input": 200, "output": 50, "complexity": 0.1},
}


class CostPredictor:
    def predict(self, task_type: str, context_length: int = 0,
                quality_requirement: float = 0.7) -> CostPrediction:
        profile = TASK_TOKEN_PROFILES.get(task_type, TASK_TOKEN_PROFILES["chat_complex"])
        input_tokens = profile["input"] + context_length
        output_tokens = profile["output"]

        model_costs = []
        for name, config in MODELS.items():
            if "pricing" not in config:
                continue
            pricing = config["pricing"]
            cost = (input_tokens / 1_000_000) * pricing["input"] + (output_tokens / 1_000_000) * pricing["output"]
            quality = self._estimate_quality(name, profile["complexity"])
            model_costs.append({
                "model": name, "cost": round(cost, 6),
                "quality_score": quality,
                "efficiency": quality / max(cost, 0.000001),
            })

        model_costs.sort(key=lambda x: x["efficiency"], reverse=True)
        viable = [m for m in model_costs if m["quality_score"] >= quality_requirement]
        if not viable:
            viable = model_costs[:3]

        recommended = min(viable, key=lambda x: x["cost"])
        return CostPrediction(
            estimated_input_tokens=input_tokens,
            estimated_output_tokens=output_tokens,
            estimated_cost_usd=recommended["cost"],
            confidence=0.75,
            recommended_model=recommended["model"],
            alternatives=viable[:5],
        )

    def _estimate_quality(self, model_name: str, complexity: float) -> float:
        tier_quality = {
            "gpt-5.5": 0.95, "claude-opus-4-7": 0.94, "claude-opus-4-6": 0.92,
            "gemini-3.1-pro": 0.91, "grok-4.20": 0.90,
            "claude-sonnet-4-6": 0.85, "deepseek-r1-0528": 0.84,
            "sonar-reasoning-pro": 0.83, "gpt-5.4": 0.82,
            "gemini-3.1-flash-lite": 0.70, "gpt-4.1-mini": 0.68, "kimi-k2.5": 0.65,
        }
        base_quality = tier_quality.get(model_name, 0.75)
        if complexity > 0.7 and base_quality < 0.8:
            base_quality *= 0.85
        return round(base_quality, 2)
```

### Budget Manager

```python
"""kernel/cost/budget_manager.py"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger("cost.budget")

@dataclass
class BudgetAllocation:
    daily_limit_usd: float = 5.0
    monthly_limit_usd: float = 100.0
    spent_today_usd: float = 0.0
    spent_this_month_usd: float = 0.0
    last_reset: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    alerts_sent: list[str] = field(default_factory=list)


class BudgetManager:
    def __init__(self):
        self.allocation = BudgetAllocation()
        self._history: list[dict] = []

    def can_spend(self, estimated_cost: float) -> tuple[bool, str]:
        self._maybe_reset()
        if self.allocation.spent_today_usd + estimated_cost > self.allocation.daily_limit_usd:
            return False, f"Daily limit exceeded ({self.allocation.daily_limit_usd} USD)"
        if self.allocation.spent_this_month_usd + estimated_cost > self.allocation.monthly_limit_usd:
            return False, f"Monthly limit exceeded ({self.allocation.monthly_limit_usd} USD)"
        return True, "OK"

    def record_spend(self, amount: float, model: str, task_type: str) -> None:
        self.allocation.spent_today_usd += amount
        self.allocation.spent_this_month_usd += amount
        self._history.append({
            "amount": amount, "model": model, "task_type": task_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        self._check_alerts()

    def get_remaining(self) -> dict:
        return {
            "daily_remaining": self.allocation.daily_limit_usd - self.allocation.spent_today_usd,
            "monthly_remaining": self.allocation.monthly_limit_usd - self.allocation.spent_this_month_usd,
            "daily_pct_used": (self.allocation.spent_today_usd / self.allocation.daily_limit_usd) * 100,
            "monthly_pct_used": (self.allocation.spent_this_month_usd / self.allocation.monthly_limit_usd) * 100,
        }

    def get_analytics(self) -> dict:
        if not self._history:
            return {"total_spent": 0, "by_model": {}, "by_task": {}}
        by_model: dict[str, float] = {}
        by_task: dict[str, float] = {}
        for entry in self._history:
            by_model[entry["model"]] = by_model.get(entry["model"], 0) + entry["amount"]
            by_task[entry["task_type"]] = by_task.get(entry["task_type"], 0) + entry["amount"]
        return {
            "total_spent": sum(e["amount"] for e in self._history),
            "by_model": dict(sorted(by_model.items(), key=lambda x: x[1], reverse=True)),
            "by_task": dict(sorted(by_task.items(), key=lambda x: x[1], reverse=True)),
            "avg_cost_per_task": sum(e["amount"] for e in self._history) / len(self._history),
        }

    def _maybe_reset(self) -> None:
        now = datetime.now(timezone.utc)
        if now.date() > self.allocation.last_reset.date():
            self.allocation.spent_today_usd = 0.0
            self.allocation.last_reset = now
            self.allocation.alerts_sent = []
        if now.month != self.allocation.last_reset.month:
            self.allocation.spent_this_month_usd = 0.0

    def _check_alerts(self) -> None:
        pct = (self.allocation.spent_today_usd / self.allocation.daily_limit_usd) * 100
        for t in [50, 75, 90, 100]:
            if pct >= t and f"daily_{t}" not in self.allocation.alerts_sent:
                logger.warning("budget_alert", threshold=t, spent=self.allocation.spent_today_usd)
                self.allocation.alerts_sent.append(f"daily_{t}")
```

### Optimizer (Model Selection)

```python
"""kernel/cost/optimizer.py"""
import structlog
from kernel.cost.predictor import CostPredictor, CostPrediction
from kernel.cost.budget_manager import BudgetManager

logger = structlog.get_logger("cost.optimizer")


class CostOptimizer:
    def __init__(self, predictor: CostPredictor, budget: BudgetManager):
        self.predictor = predictor
        self.budget = budget

    async def select_model(self, task_type: str, context_length: int = 0,
                           quality_floor: float = 0.7, prefer_speed: bool = False) -> dict:
        prediction = self.predictor.predict(task_type, context_length, quality_floor)
        can_spend, reason = self.budget.can_spend(prediction.estimated_cost_usd)

        if can_spend:
            return {
                "model": prediction.recommended_model,
                "estimated_cost": prediction.estimated_cost_usd,
                "quality_score": next(
                    (a["quality_score"] for a in prediction.alternatives
                     if a["model"] == prediction.recommended_model), 0.8),
                "budget_status": "ok",
            }

        for alt in sorted(prediction.alternatives, key=lambda x: x["cost"]):
            can_alt, _ = self.budget.can_spend(alt["cost"])
            if can_alt and alt["quality_score"] >= quality_floor * 0.9:
                logger.info("model_downgraded", original=prediction.recommended_model,
                            selected=alt["model"], reason=reason)
                return {
                    "model": alt["model"], "estimated_cost": alt["cost"],
                    "quality_score": alt["quality_score"],
                    "budget_status": "downgraded", "reason": reason,
                }

        cheapest = min(prediction.alternatives, key=lambda x: x["cost"])
        logger.warning("budget_exhausted", cheapest=cheapest["model"])
        return {
            "model": cheapest["model"], "estimated_cost": cheapest["cost"],
            "quality_score": cheapest["quality_score"],
            "budget_status": "exhausted",
            "reason": "All budgets exceeded, using cheapest model",
        }
```

---

## Integracion con el Sistema Existente

### Punto de Integracion: Router Engine

El Cost Optimizer se integra en `router/engine.py` como un paso previo al model selection:

```python
# En router/engine.py, antes de seleccionar modelo:
from kernel.cost.optimizer import CostOptimizer

async def route_completion(messages, intent, **kwargs):
    # 1. Cost optimization (nuevo)
    optimization = await cost_optimizer.select_model(
        task_type=intent.value,
        context_length=sum(len(m["content"]) for m in messages),
        quality_floor=kwargs.get("quality_floor", 0.7),
    )
    # 2. Use optimized model instead of default
    model_name = optimization["model"]
    # 3. Record spend after completion
    # ... existing routing logic ...
```

### Punto de Integracion: Plugin System

Los plugins se cargan al startup en `main.py`:

```python
# En main.py, despues de inicializar el kernel:
from kernel.plugins.plugin_manager import PluginManager
from kernel.plugins.plugin_loader import PluginLoader

plugin_manager = PluginManager()
loader = PluginLoader(plugin_manager)
await loader.discover_and_load()
```

---

## Tabla de Dependencias Nuevas

| Paquete | Version | Proposito | Costo |
|---|---|---|---|
| pluggy | ~1.5.0 | Plugin hooks framework | $0 (MIT) |
| exchangerate-api | API free | Exchange rates | $0 (1500 req/month free) |
| zoneinfo | stdlib | Timezone handling | $0 (Python 3.9+) |

**Costo total adicional:** ~$0-2/mes (solo exchange rate API si excede free tier)

---

## Criterios de Exito

| Metrica | Target | Medicion |
|---|---|---|
| Plugins cargados al startup | >=2 builtin | `GET /api/plugins` |
| Export completo funcional | <30s para 1000 records | Benchmark |
| Import con validacion | 0 data loss en merge mode | Test suite |
| Componentes en registry | >=30 | `ComponentRegistry.load_all()` |
| Cost prediction accuracy | +/-30% del costo real | Comparar prediccion vs. real |
| Budget enforcement | 100% de stops cuando excede | Test con budget=0 |
| Currencies soportadas | 20 | `len(CURRENCIES)` |
| Legal templates | 3 (GDPR, CCPA, LGPD) | `len(COMPLIANCE_TEMPLATES)` |

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| Plugin malicioso ejecuta codigo peligroso | MEDIA | ALTO | Security check + sandbox + whitelist |
| Exchange rate API down | BAJA | BAJO | Cache rates 24h + hardcoded fallback |
| Cost prediction inaccurate | MEDIA | MEDIO | Feedback loop: real vs predicted -> adjust |
| Component library crece sin control | BAJA | MEDIO | Quality gate: score minimo 0.8 |

---

## Referencias

[1]: https://pluggy.readthedocs.io/ "Pluggy - Plugin management and hook calling"
[2]: https://docs.stripe.com/connect/currencies "Stripe - Multi-currency support (135+ currencies)"
[3]: https://ui.shadcn.com/ "shadcn/ui - The Foundation for your Design System"
[4]: https://pypi.org/project/litellm/ "LiteLLM 1.83.14 - AI Gateway (NOT USED due to CVE)"
[5]: https://www.mindstudio.ai/blog/ai-agent-token-cost-optimization-multi-model-routing/ "Token Cost Optimization with Multi-Model Routing"
