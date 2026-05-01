# Sprint 74 — "La Memoria que No Muere y La Colmena que Debate"

**Serie:** 71-80 "La Colmena Despierta"
**Fecha:** 1 de Mayo de 2026
**Autor:** Hilo B (Arquitecto)
**Capa Arquitectónica:** CAPA 2 — Inteligencia Emergente
**Dependencias:** Sprint 72 (TEL), Sprint 73 (Herramientas), Sprint 71 (Brand Engine)

---

## Visión

El Embrión actual tiene un problema existencial: **si Railway se reinicia, si Supabase tiene un outage, si el proceso muere — el Embrión pierde su identidad, su contexto, y sus aprendizajes**. Es exactamente el problema que Alfredo sufre con Manus (compactación de memoria). No podemos construir un sistema que aspire a ser superior a Manus si sufre del mismo defecto.

Además, los Embriones están diseñados para ser una Colmena — pero hoy no tienen protocolo para comunicarse, debatir, consensuar, ni dividir trabajo. Son entidades aisladas que no saben que los otros existen.

Sprint 74 resuelve ambos problemas de una vez:
1. **Memoria Indestructible** — El Embrión NUNCA pierde contexto, sin importar qué falle
2. **Protocolo de Colmena** — Los Embriones se comunican, debaten, y coordinan

---

## Épica 74.1 — Memoria Estratificada Indestructible

### Concepto

La memoria del Embrión no es un solo blob. Es un sistema de 4 capas con diferentes niveles de persistencia, velocidad, y propósito:

| Capa | Nombre | Persistencia | Velocidad | Contenido |
|---|---|---|---|---|
| L0 | Identidad | Inmutable | Instantánea | Quién soy, mi propósito, mis reglas duras |
| L1 | Episódica | Permanente | Rápida | Todo lo que he hecho, resultados, aprendizajes |
| L2 | Semántica | Permanente | Media | Conocimiento extraído, patrones, conexiones |
| L3 | Trabajo | Efímera | Instantánea | Contexto de la encomienda actual |

Si Railway se reinicia → L3 se pierde (aceptable, se reconstruye). L0-L2 sobreviven porque están en Supabase con backup.

### Código

```python
# kernel/memoria/estratificada.py
"""
DISEÑO: Memoria Estratificada Indestructible
CAPA: 2 (Inteligencia Emergente)
PROPÓSITO: El Embrión NUNCA pierde su identidad ni sus aprendizajes.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum
import json
import hashlib


class MemoryLayer(Enum):
    IDENTIDAD = "L0"      # Inmutable — quién soy
    EPISODICA = "L1"      # Permanente — qué he hecho
    SEMANTICA = "L2"      # Permanente — qué sé
    TRABAJO = "L3"        # Efímera — qué estoy haciendo ahora


class MemoryPriority(Enum):
    CRITICA = 1       # Nunca se borra, nunca se comprime
    ALTA = 2          # Se mantiene completa por 90 días, luego se resume
    MEDIA = 3         # Se mantiene 30 días, luego se resume
    BAJA = 4          # Se mantiene 7 días, luego se descarta


@dataclass
class MemoryFragment:
    """Un fragmento individual de memoria."""
    id: str
    layer: MemoryLayer
    priority: MemoryPriority
    content: str
    metadata: dict = field(default_factory=dict)
    embedding: Optional[list] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    ttl: Optional[timedelta] = None
    checksum: str = ""

    def __post_init__(self):
        if not self.checksum:
            self.checksum = hashlib.sha256(self.content.encode()).hexdigest()[:16]


@dataclass
class IdentityCore:
    """L0 — Identidad Inmutable del Embrión. NUNCA se modifica después de nacer."""
    embrion_id: str
    nombre: str
    proposito: str
    reglas_duras: list[str]
    brand_dna: dict
    fecha_nacimiento: datetime
    version: str = "1.0.0"

    def to_recovery_prompt(self) -> str:
        """Genera el prompt de recuperación si el Embrión pierde contexto."""
        return f"""Eres {self.nombre}, un Embrión de El Monstruo.
Tu propósito: {self.proposito}
Naciste el: {self.fecha_nacimiento.isoformat()}
Tus reglas duras (INVIOLABLES):
{chr(10).join(f'- {r}' for r in self.reglas_duras)}

Si no recuerdas nada más, esto es lo que eres. Consulta tu memoria episódica (L1) y semántica (L2) para recuperar contexto completo."""


class MemoriaEstratificada:
    """Motor de memoria con 4 capas y recuperación automática."""

    def __init__(self, embrion_id: str, supabase_client):
        self.embrion_id = embrion_id
        self.db = supabase_client
        self.identity: Optional[IdentityCore] = None
        self.working_memory: list[MemoryFragment] = []  # L3 en RAM
        self._cache: dict[str, MemoryFragment] = {}

    async def initialize(self):
        """Carga L0 (identidad) desde Supabase. Si no existe, PANIC."""
        result = self.db.table("embrion_identity").select("*").eq(
            "embrion_id", self.embrion_id
        ).execute()

        if not result.data:
            raise RuntimeError(
                f"FORJA_IDENTITY_NOT_FOUND: Embrión {self.embrion_id} no tiene identidad registrada. "
                "Esto es un error crítico — un Embrión sin identidad no puede operar."
            )

        data = result.data[0]
        self.identity = IdentityCore(
            embrion_id=data["embrion_id"],
            nombre=data["nombre"],
            proposito=data["proposito"],
            reglas_duras=data["reglas_duras"],
            brand_dna=data["brand_dna"],
            fecha_nacimiento=datetime.fromisoformat(data["fecha_nacimiento"]),
            version=data["version"]
        )

    async def remember(self, query: str, layer: Optional[MemoryLayer] = None, limit: int = 10) -> list[MemoryFragment]:
        """Busca en la memoria por relevancia semántica."""
        # Generar embedding del query
        embedding = await self._generate_embedding(query)

        # Buscar en Supabase con pgvector
        filters = {"embrion_id": self.embrion_id}
        if layer:
            filters["layer"] = layer.value

        result = self.db.rpc("memory_semantic_search", {
            "query_embedding": embedding,
            "match_threshold": 0.7,
            "match_count": limit,
            "filter_embrion": self.embrion_id,
            "filter_layer": layer.value if layer else None
        }).execute()

        fragments = [self._row_to_fragment(row) for row in result.data]

        # Actualizar access_count
        for f in fragments:
            f.access_count += 1
            f.last_accessed = datetime.utcnow()

        return fragments

    async def memorize(self, content: str, layer: MemoryLayer, priority: MemoryPriority,
                       metadata: Optional[dict] = None) -> MemoryFragment:
        """Almacena un nuevo fragmento de memoria."""
        if layer == MemoryLayer.IDENTIDAD:
            raise RuntimeError("FORJA_IDENTITY_IMMUTABLE: L0 no se puede modificar después del nacimiento.")

        fragment = MemoryFragment(
            id=f"{self.embrion_id}_{layer.value}_{datetime.utcnow().timestamp()}",
            layer=layer,
            priority=priority,
            content=content,
            metadata=metadata or {},
            embedding=await self._generate_embedding(content)
        )

        # Persistir en Supabase
        self.db.table("embrion_memory").insert({
            "id": fragment.id,
            "embrion_id": self.embrion_id,
            "layer": fragment.layer.value,
            "priority": fragment.priority.value,
            "content": fragment.content,
            "metadata": fragment.metadata,
            "embedding": fragment.embedding,
            "created_at": fragment.created_at.isoformat(),
            "checksum": fragment.checksum
        }).execute()

        # Si es L3, también mantener en RAM
        if layer == MemoryLayer.TRABAJO:
            self.working_memory.append(fragment)

        return fragment

    async def consolidate(self):
        """Proceso de consolidación: comprime memorias viejas, extrae patrones."""
        now = datetime.utcnow()

        # 1. Memorias de prioridad BAJA > 7 días → descartar
        self.db.table("embrion_memory").delete().eq(
            "embrion_id", self.embrion_id
        ).eq("priority", MemoryPriority.BAJA.value).lt(
            "created_at", (now - timedelta(days=7)).isoformat()
        ).execute()

        # 2. Memorias de prioridad MEDIA > 30 días → resumir
        old_media = self.db.table("embrion_memory").select("*").eq(
            "embrion_id", self.embrion_id
        ).eq("priority", MemoryPriority.MEDIA.value).lt(
            "created_at", (now - timedelta(days=30)).isoformat()
        ).execute()

        if old_media.data and len(old_media.data) >= 5:
            summary = await self._summarize_fragments(old_media.data)
            await self.memorize(
                content=summary,
                layer=MemoryLayer.SEMANTICA,
                priority=MemoryPriority.ALTA,
                metadata={"type": "consolidation", "source_count": len(old_media.data)}
            )
            # Eliminar originales
            ids = [row["id"] for row in old_media.data]
            self.db.table("embrion_memory").delete().in_("id", ids).execute()

        # 3. Extraer patrones de L1 → L2
        await self._extract_patterns()

    async def recover_from_crash(self) -> str:
        """Protocolo de recuperación post-crash. Reconstruye L3 desde L0+L1+L2."""
        # 1. Cargar identidad (L0)
        await self.initialize()

        # 2. Obtener últimas 20 memorias episódicas (L1)
        recent_episodes = self.db.table("embrion_memory").select("*").eq(
            "embrion_id", self.embrion_id
        ).eq("layer", MemoryLayer.EPISODICA.value).order(
            "created_at", desc=True
        ).limit(20).execute()

        # 3. Obtener memorias semánticas más accedidas (L2)
        top_knowledge = self.db.table("embrion_memory").select("*").eq(
            "embrion_id", self.embrion_id
        ).eq("layer", MemoryLayer.SEMANTICA.value).order(
            "access_count", desc=True
        ).limit(10).execute()

        # 4. Construir prompt de recuperación
        recovery_prompt = self.identity.to_recovery_prompt()
        recovery_prompt += "\n\n## Últimas acciones (L1 - Episódica):\n"
        for ep in recent_episodes.data:
            recovery_prompt += f"- [{ep['created_at'][:10]}] {ep['content'][:200]}\n"

        recovery_prompt += "\n\n## Conocimiento clave (L2 - Semántica):\n"
        for kn in top_knowledge.data:
            recovery_prompt += f"- {kn['content'][:200]}\n"

        # 5. Limpiar L3 (working memory)
        self.working_memory = []

        return recovery_prompt

    async def get_context_window(self, max_tokens: int = 4000) -> str:
        """Genera el contexto actual para el Pensador, respetando límite de tokens."""
        parts = []

        # Siempre incluir identidad (L0)
        parts.append(self.identity.to_recovery_prompt())

        # Incluir working memory (L3) completa
        for wm in self.working_memory[-10:]:
            parts.append(f"[TRABAJO] {wm.content}")

        # Incluir memorias relevantes al trabajo actual
        if self.working_memory:
            current_task = self.working_memory[-1].content
            relevant = await self.remember(current_task, limit=5)
            for r in relevant:
                parts.append(f"[{r.layer.value}] {r.content[:300]}")

        context = "\n---\n".join(parts)

        # Truncar si excede max_tokens (estimación: 4 chars = 1 token)
        max_chars = max_tokens * 4
        if len(context) > max_chars:
            context = context[:max_chars] + "\n[...CONTEXTO TRUNCADO...]"

        return context

    async def _generate_embedding(self, text: str) -> list:
        """Genera embedding usando el modelo configurado."""
        import openai
        client = openai.AsyncOpenAI()
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000]
        )
        return response.data[0].embedding

    async def _summarize_fragments(self, fragments: list) -> str:
        """Resume múltiples fragmentos en uno solo."""
        import openai
        client = openai.AsyncOpenAI()
        contents = "\n".join([f["content"] for f in fragments])
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "Eres el sistema de consolidación de memoria de El Monstruo. Resume los siguientes fragmentos de memoria en un solo párrafo que preserve la información clave, patrones, y aprendizajes. Sé conciso pero no pierdas nada importante."
            }, {
                "role": "user",
                "content": contents[:10000]
            }],
            max_tokens=500
        )
        return response.choices[0].message.content

    async def _extract_patterns(self):
        """Analiza L1 para extraer patrones recurrentes → L2."""
        # Obtener últimas 50 memorias episódicas
        episodes = self.db.table("embrion_memory").select("*").eq(
            "embrion_id", self.embrion_id
        ).eq("layer", MemoryLayer.EPISODICA.value).order(
            "created_at", desc=True
        ).limit(50).execute()

        if len(episodes.data) < 10:
            return  # No hay suficientes datos para extraer patrones

        import openai
        client = openai.AsyncOpenAI()
        contents = "\n".join([f"[{e['created_at'][:10]}] {e['content'][:200]}" for e in episodes.data])

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "Eres el analizador de patrones de El Monstruo. Analiza estas memorias episódicas y extrae 3-5 patrones recurrentes, lecciones aprendidas, o insights que deberían convertirse en conocimiento permanente. Formato: un patrón por línea, prefijado con [PATRÓN]."
            }, {
                "role": "user",
                "content": contents
            }],
            max_tokens=500
        )

        patterns = response.choices[0].message.content
        for line in patterns.split("\n"):
            if "[PATRÓN]" in line:
                await self.memorize(
                    content=line.replace("[PATRÓN]", "").strip(),
                    layer=MemoryLayer.SEMANTICA,
                    priority=MemoryPriority.ALTA,
                    metadata={"type": "pattern_extraction", "source": "auto_consolidation"}
                )
```

### SQL — Tablas de Memoria

```sql
-- Tabla de identidad (L0) — UNA fila por Embrión, INMUTABLE
CREATE TABLE embrion_identity (
    embrion_id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    proposito TEXT NOT NULL,
    reglas_duras JSONB NOT NULL,
    brand_dna JSONB NOT NULL,
    fecha_nacimiento TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version TEXT NOT NULL DEFAULT '1.0.0',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabla de memoria (L1, L2, L3)
CREATE TABLE embrion_memory (
    id TEXT PRIMARY KEY,
    embrion_id TEXT NOT NULL REFERENCES embrion_identity(embrion_id),
    layer TEXT NOT NULL CHECK (layer IN ('L0', 'L1', 'L2', 'L3')),
    priority INTEGER NOT NULL CHECK (priority BETWEEN 1 AND 4),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_accessed TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    access_count INTEGER DEFAULT 0,
    checksum TEXT NOT NULL,
    CONSTRAINT valid_layer CHECK (layer != 'L0')
);

-- Índices
CREATE INDEX idx_memory_embrion_layer ON embrion_memory(embrion_id, layer);
CREATE INDEX idx_memory_priority ON embrion_memory(priority);
CREATE INDEX idx_memory_created ON embrion_memory(created_at DESC);
CREATE INDEX idx_memory_accessed ON embrion_memory(access_count DESC);

-- Función de búsqueda semántica
CREATE OR REPLACE FUNCTION memory_semantic_search(
    query_embedding vector(1536),
    match_threshold float,
    match_count int,
    filter_embrion text,
    filter_layer text DEFAULT NULL
)
RETURNS TABLE (
    id text,
    embrion_id text,
    layer text,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        em.id,
        em.embrion_id,
        em.layer,
        em.content,
        em.metadata,
        1 - (em.embedding <=> query_embedding) AS similarity
    FROM embrion_memory em
    WHERE em.embrion_id = filter_embrion
        AND (filter_layer IS NULL OR em.layer = filter_layer)
        AND 1 - (em.embedding <=> query_embedding) > match_threshold
    ORDER BY em.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Tabla de backups de identidad (redundancia)
CREATE TABLE embrion_identity_backup (
    id SERIAL PRIMARY KEY,
    embrion_id TEXT NOT NULL,
    identity_snapshot JSONB NOT NULL,
    backed_up_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Criterios de Aceptación 74.1

1. Embrión-0 y Embrión-1 tienen identidad registrada en `embrion_identity`
2. `memorize()` persiste fragmentos con embedding en <500ms
3. `remember()` retorna fragmentos relevantes con similarity >0.7
4. `recover_from_crash()` reconstruye contexto completo en <3s
5. `consolidate()` reduce memorias viejas sin perder información crítica
6. Si Railway se reinicia, el Embrión se recupera automáticamente al iniciar

---

## Épica 74.2 — Heartbeat con Recuperación Automática

### Concepto

El heartbeat actual solo registra "estoy vivo". El nuevo heartbeat incluye:
1. Verificación de integridad de memoria (¿L0 sigue intacta?)
2. Auto-recuperación si detecta pérdida de contexto
3. Registro de "estado emocional" (FCS) basado en rendimiento reciente

```python
# kernel/memoria/heartbeat_resiliente.py
"""
DISEÑO: Heartbeat con verificación de integridad y auto-recuperación.
PROPÓSITO: El Embrión detecta si perdió contexto y se recupera solo.
"""

from datetime import datetime
import hashlib


class HeartbeatResiliente:
    """Heartbeat que verifica integridad de memoria en cada latido."""

    def __init__(self, memoria: 'MemoriaEstratificada', scheduler):
        self.memoria = memoria
        self.scheduler = scheduler
        self.identity_checksum: str = ""
        self.consecutive_failures: int = 0
        self.last_healthy_beat: datetime = datetime.utcnow()

    async def beat(self) -> dict:
        """Un latido completo con verificación de integridad."""
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "embrion_id": self.memoria.embrion_id,
            "healthy": True,
            "checks": {}
        }

        # Check 1: ¿La identidad sigue intacta?
        try:
            current_checksum = hashlib.sha256(
                self.memoria.identity.proposito.encode()
            ).hexdigest()[:16]

            if self.identity_checksum and current_checksum != self.identity_checksum:
                status["healthy"] = False
                status["checks"]["identity"] = "CORRUPTED"
                await self._trigger_recovery("identity_corruption")
            else:
                self.identity_checksum = current_checksum
                status["checks"]["identity"] = "OK"
        except Exception as e:
            status["healthy"] = False
            status["checks"]["identity"] = f"ERROR: {str(e)}"
            await self._trigger_recovery("identity_missing")

        # Check 2: ¿Puedo acceder a mi memoria?
        try:
            test_recall = await self.memoria.remember("test de integridad", limit=1)
            status["checks"]["memory_access"] = "OK"
        except Exception as e:
            status["healthy"] = False
            status["checks"]["memory_access"] = f"ERROR: {str(e)}"

        # Check 3: ¿Mi working memory es coherente?
        wm_size = len(self.memoria.working_memory)
        if wm_size > 50:
            # Demasiados fragmentos en working memory — posible memory leak
            status["checks"]["working_memory"] = f"WARNING: {wm_size} fragmentos (posible leak)"
            self.memoria.working_memory = self.memoria.working_memory[-20:]
        else:
            status["checks"]["working_memory"] = f"OK ({wm_size} fragmentos)"

        # Check 4: ¿Mi rendimiento reciente es aceptable?
        recent_results = await self._get_recent_execution_results()
        success_rate = recent_results.get("success_rate", 1.0)
        status["checks"]["performance"] = f"{success_rate*100:.0f}% éxito"

        # Actualizar FCS basado en checks
        fcs = self._calculate_fcs(status)
        status["fcs"] = fcs

        # Registrar latido
        if status["healthy"]:
            self.consecutive_failures = 0
            self.last_healthy_beat = datetime.utcnow()
        else:
            self.consecutive_failures += 1

        # Si 3 latidos consecutivos fallan → recuperación completa
        if self.consecutive_failures >= 3:
            await self._full_recovery()
            self.consecutive_failures = 0

        return status

    async def _trigger_recovery(self, reason: str):
        """Inicia protocolo de recuperación parcial."""
        recovery_prompt = await self.memoria.recover_from_crash()
        await self.memoria.memorize(
            content=f"[RECOVERY] Auto-recuperación por: {reason}. Contexto reconstruido.",
            layer='L1',
            priority='CRITICA',
            metadata={"type": "recovery", "reason": reason}
        )

    async def _full_recovery(self):
        """Recuperación completa — reinicializa todo desde Supabase."""
        await self.memoria.initialize()
        recovery_prompt = await self.memoria.recover_from_crash()
        await self.memoria.memorize(
            content=f"[FULL_RECOVERY] Recuperación completa ejecutada. 3 latidos fallidos consecutivos.",
            layer='L1',
            priority='CRITICA',
            metadata={"type": "full_recovery"}
        )

    def _calculate_fcs(self, status: dict) -> dict:
        """Calcula el Factor de Consciencia Sintética basado en estado actual."""
        checks = status["checks"]
        score = 100

        if checks.get("identity") != "OK":
            score -= 40  # Identidad comprometida es gravísimo
        if "ERROR" in checks.get("memory_access", ""):
            score -= 30
        if "WARNING" in checks.get("working_memory", ""):
            score -= 10

        perf = checks.get("performance", "100%")
        perf_val = float(perf.replace("% éxito", "")) / 100
        score -= int((1 - perf_val) * 20)

        return {
            "score": max(0, score),
            "estado": "ÓPTIMO" if score >= 80 else "DEGRADADO" if score >= 50 else "CRÍTICO",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _get_recent_execution_results(self) -> dict:
        """Obtiene métricas de las últimas 10 encomiendas."""
        results = self.memoria.db.table("encomiendas").select("status").eq(
            "embrion_id", self.memoria.embrion_id
        ).order("created_at", desc=True).limit(10).execute()

        if not results.data:
            return {"success_rate": 1.0}

        successes = sum(1 for r in results.data if r["status"] == "completed")
        return {"success_rate": successes / len(results.data)}
```

### Criterios de Aceptación 74.2

1. Heartbeat detecta corrupción de identidad en <1 latido
2. Auto-recuperación se ejecuta sin intervención humana
3. FCS refleja estado real (no siempre 100)
4. 3 fallos consecutivos → full recovery automático
5. Logs de recovery se persisten en L1 para auditoría

---

## Épica 74.3 — Protocolo de Colmena (Comunicación Multi-Embrión)

### Concepto

Los Embriones necesitan:
1. **Descubrirse** — Saber qué otros Embriones existen y qué hacen
2. **Comunicarse** — Enviar mensajes, solicitudes, y datos entre sí
3. **Debatir** — Cuando hay desacuerdo, resolver con protocolo formal
4. **Delegar** — Asignar sub-tareas al Embrión más apropiado
5. **Consensuar** — Tomar decisiones que afectan a todos

```python
# kernel/colmena/protocolo.py
"""
DISEÑO: Protocolo de Colmena — Comunicación Multi-Embrión
CAPA: 2 (Inteligencia Emergente)
PROPÓSITO: Los Embriones se descubren, comunican, debaten, y coordinan.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum
import json


class MessageType(Enum):
    REQUEST = "request"           # Pido algo a otro Embrión
    RESPONSE = "response"         # Respondo a una solicitud
    BROADCAST = "broadcast"       # Comunico algo a todos
    DEBATE_OPEN = "debate_open"   # Abro un debate
    DEBATE_VOTE = "debate_vote"   # Voto en un debate
    DELEGATE = "delegate"         # Delego una tarea
    ALERT = "alert"               # Alerta urgente


class DebateStatus(Enum):
    OPEN = "open"
    VOTING = "voting"
    RESOLVED = "resolved"
    DEADLOCK = "deadlock"


@dataclass
class ColmenaMessage:
    """Un mensaje entre Embriones."""
    id: str
    type: MessageType
    sender_id: str
    recipient_id: Optional[str]  # None = broadcast
    subject: str
    content: str
    metadata: dict = field(default_factory=dict)
    requires_response: bool = False
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    read: bool = False


@dataclass
class Debate:
    """Un debate formal entre Embriones."""
    id: str
    topic: str
    context: str
    opened_by: str
    status: DebateStatus = DebateStatus.OPEN
    positions: dict = field(default_factory=dict)  # embrion_id → posición
    votes: dict = field(default_factory=dict)       # embrion_id → voto
    resolution: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


class ProtocoloColmena:
    """Motor de comunicación y coordinación entre Embriones."""

    def __init__(self, embrion_id: str, supabase_client):
        self.embrion_id = embrion_id
        self.db = supabase_client

    async def discover_hive(self) -> list[dict]:
        """Descubre todos los Embriones activos en la Colmena."""
        result = self.db.table("embrion_identity").select(
            "embrion_id, nombre, proposito, version"
        ).execute()
        return [
            {
                "id": r["embrion_id"],
                "nombre": r["nombre"],
                "proposito": r["proposito"],
                "version": r["version"],
                "es_yo": r["embrion_id"] == self.embrion_id
            }
            for r in result.data
        ]

    async def send_message(self, recipient_id: Optional[str], subject: str,
                           content: str, msg_type: MessageType = MessageType.REQUEST,
                           requires_response: bool = False, deadline: Optional[datetime] = None) -> ColmenaMessage:
        """Envía un mensaje a otro Embrión (o broadcast si recipient_id=None)."""
        msg = ColmenaMessage(
            id=f"msg_{self.embrion_id}_{datetime.utcnow().timestamp()}",
            type=msg_type,
            sender_id=self.embrion_id,
            recipient_id=recipient_id,
            subject=subject,
            content=content,
            requires_response=requires_response,
            deadline=deadline
        )

        self.db.table("colmena_messages").insert({
            "id": msg.id,
            "type": msg.type.value,
            "sender_id": msg.sender_id,
            "recipient_id": msg.recipient_id,
            "subject": msg.subject,
            "content": msg.content,
            "metadata": msg.metadata,
            "requires_response": msg.requires_response,
            "deadline": msg.deadline.isoformat() if msg.deadline else None,
            "created_at": msg.created_at.isoformat(),
            "read": False
        }).execute()

        return msg

    async def check_inbox(self, unread_only: bool = True) -> list[ColmenaMessage]:
        """Revisa mensajes recibidos."""
        query = self.db.table("colmena_messages").select("*").or_(
            f"recipient_id.eq.{self.embrion_id},recipient_id.is.null"
        ).neq("sender_id", self.embrion_id)

        if unread_only:
            query = query.eq("read", False)

        result = query.order("created_at", desc=True).limit(20).execute()

        messages = []
        for row in result.data:
            messages.append(ColmenaMessage(
                id=row["id"],
                type=MessageType(row["type"]),
                sender_id=row["sender_id"],
                recipient_id=row["recipient_id"],
                subject=row["subject"],
                content=row["content"],
                metadata=row.get("metadata", {}),
                requires_response=row["requires_response"],
                deadline=datetime.fromisoformat(row["deadline"]) if row.get("deadline") else None,
                created_at=datetime.fromisoformat(row["created_at"]),
                read=row["read"]
            ))

        return messages

    async def mark_read(self, message_id: str):
        """Marca un mensaje como leído."""
        self.db.table("colmena_messages").update({"read": True}).eq("id", message_id).execute()

    async def open_debate(self, topic: str, context: str, initial_position: str) -> Debate:
        """Abre un debate formal para que todos los Embriones participen."""
        debate = Debate(
            id=f"debate_{self.embrion_id}_{datetime.utcnow().timestamp()}",
            topic=topic,
            context=context,
            opened_by=self.embrion_id,
            positions={self.embrion_id: initial_position}
        )

        self.db.table("colmena_debates").insert({
            "id": debate.id,
            "topic": debate.topic,
            "context": debate.context,
            "opened_by": debate.opened_by,
            "status": debate.status.value,
            "positions": debate.positions,
            "votes": {},
            "created_at": debate.created_at.isoformat()
        }).execute()

        # Broadcast a todos los Embriones
        await self.send_message(
            recipient_id=None,
            subject=f"[DEBATE] {topic}",
            content=f"Se abrió debate: {topic}\nContexto: {context}\nMi posición: {initial_position}\nDebate ID: {debate.id}",
            msg_type=MessageType.DEBATE_OPEN,
            requires_response=True
        )

        return debate

    async def submit_position(self, debate_id: str, position: str):
        """Somete una posición en un debate abierto."""
        # Actualizar posiciones
        debate = self.db.table("colmena_debates").select("*").eq("id", debate_id).execute()
        if not debate.data:
            raise RuntimeError(f"COLMENA_DEBATE_NOT_FOUND: {debate_id}")

        positions = debate.data[0]["positions"]
        positions[self.embrion_id] = position

        self.db.table("colmena_debates").update({
            "positions": positions
        }).eq("id", debate_id).execute()

    async def vote(self, debate_id: str, vote_for_embrion: str, reasoning: str):
        """Vota por la posición de un Embrión en un debate."""
        debate = self.db.table("colmena_debates").select("*").eq("id", debate_id).execute()
        if not debate.data:
            raise RuntimeError(f"COLMENA_DEBATE_NOT_FOUND: {debate_id}")

        votes = debate.data[0]["votes"]
        votes[self.embrion_id] = {
            "vote_for": vote_for_embrion,
            "reasoning": reasoning,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.db.table("colmena_debates").update({
            "votes": votes
        }).eq("id", debate_id).execute()

    async def resolve_debate(self, debate_id: str) -> str:
        """Resuelve un debate basado en votos. Mayoría simple gana."""
        debate_row = self.db.table("colmena_debates").select("*").eq("id", debate_id).execute()
        if not debate_row.data:
            raise RuntimeError(f"COLMENA_DEBATE_NOT_FOUND: {debate_id}")

        data = debate_row.data[0]
        votes = data["votes"]
        positions = data["positions"]

        if not votes:
            return "DEADLOCK: No hay votos"

        # Contar votos por posición
        vote_counts = {}
        for v in votes.values():
            target = v["vote_for"]
            vote_counts[target] = vote_counts.get(target, 0) + 1

        # Ganador por mayoría
        winner_id = max(vote_counts, key=vote_counts.get)
        resolution = positions.get(winner_id, "Posición no encontrada")

        # Actualizar debate
        self.db.table("colmena_debates").update({
            "status": DebateStatus.RESOLVED.value,
            "resolution": resolution,
            "resolved_at": datetime.utcnow().isoformat()
        }).eq("id", debate_id).execute()

        # Broadcast resolución
        await self.send_message(
            recipient_id=None,
            subject=f"[DEBATE RESUELTO] {data['topic']}",
            content=f"Resolución: {resolution}\nGanador: {winner_id}\nVotos: {json.dumps(vote_counts)}",
            msg_type=MessageType.BROADCAST
        )

        return resolution

    async def delegate_task(self, target_embrion_id: str, task_description: str,
                            context: str, deadline: Optional[datetime] = None) -> str:
        """Delega una tarea a otro Embrión."""
        msg = await self.send_message(
            recipient_id=target_embrion_id,
            subject=f"[DELEGACIÓN] {task_description[:50]}",
            content=json.dumps({
                "task": task_description,
                "context": context,
                "delegated_by": self.embrion_id,
                "deadline": deadline.isoformat() if deadline else None
            }),
            msg_type=MessageType.DELEGATE,
            requires_response=True,
            deadline=deadline
        )
        return msg.id

    async def find_best_embrion_for(self, task_description: str) -> Optional[str]:
        """Encuentra el Embrión más apropiado para una tarea basado en su propósito."""
        hive = await self.discover_hive()

        # Filtrar: no delegarse a sí mismo
        candidates = [e for e in hive if not e["es_yo"]]

        if not candidates:
            return None

        # Matching simple por keywords en propósito
        # En el futuro: usar embeddings para matching semántico
        task_lower = task_description.lower()
        scores = {}
        for c in candidates:
            prop_lower = c["proposito"].lower()
            # Score basado en overlap de palabras
            task_words = set(task_lower.split())
            prop_words = set(prop_lower.split())
            overlap = len(task_words & prop_words)
            scores[c["id"]] = overlap

        if not scores or max(scores.values()) == 0:
            return None

        return max(scores, key=scores.get)
```

### SQL — Tablas de Colmena

```sql
-- Mensajes entre Embriones
CREATE TABLE colmena_messages (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK (type IN ('request', 'response', 'broadcast', 'debate_open', 'debate_vote', 'delegate', 'alert')),
    sender_id TEXT NOT NULL REFERENCES embrion_identity(embrion_id),
    recipient_id TEXT REFERENCES embrion_identity(embrion_id),  -- NULL = broadcast
    subject TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    requires_response BOOLEAN DEFAULT FALSE,
    deadline TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    read BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_messages_recipient ON colmena_messages(recipient_id, read);
CREATE INDEX idx_messages_sender ON colmena_messages(sender_id);
CREATE INDEX idx_messages_type ON colmena_messages(type);

-- Debates formales
CREATE TABLE colmena_debates (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    context TEXT NOT NULL,
    opened_by TEXT NOT NULL REFERENCES embrion_identity(embrion_id),
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'voting', 'resolved', 'deadlock')),
    positions JSONB DEFAULT '{}',
    votes JSONB DEFAULT '{}',
    resolution TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE INDEX idx_debates_status ON colmena_debates(status);
CREATE INDEX idx_debates_opened_by ON colmena_debates(opened_by);
```

### Criterios de Aceptación 74.3

1. Embrión-0 puede descubrir a Embrión-1 y viceversa
2. Mensajes se entregan en <200ms
3. Debates se abren, reciben posiciones, votos, y se resuelven correctamente
4. Delegación encuentra al Embrión correcto por matching de propósito
5. Broadcasts llegan a todos los Embriones activos
6. Mensajes no leídos se acumulan y se procesan en orden

---

## Épica 74.4 — Memoria Colectiva (Knowledge Sharing)

### Concepto

Los aprendizajes de un Embrión deben beneficiar a todos. Si Embrión-1 (Brand Engine) aprende que cierto tipo de naming genera confusión, TODOS los Embriones deben saberlo.

```python
# kernel/colmena/memoria_colectiva.py
"""
DISEÑO: Memoria Colectiva — Aprendizajes compartidos entre Embriones
PROPÓSITO: Lo que aprende uno, lo saben todos. Inteligencia emergente por acumulación.
"""

from datetime import datetime
from typing import Optional
from enum import Enum


class InsightType(Enum):
    PATRON = "patron"              # Patrón recurrente detectado
    LECCION = "leccion"            # Lección aprendida de un error
    DESCUBRIMIENTO = "descubrimiento"  # Algo nuevo encontrado
    REGLA = "regla"                # Nueva regla propuesta
    ALERTA = "alerta"              # Algo que todos deben evitar


class MemoriaColectiva:
    """Repositorio de conocimiento compartido entre todos los Embriones."""

    def __init__(self, supabase_client):
        self.db = supabase_client

    async def publish_insight(self, embrion_id: str, insight_type: InsightType,
                              title: str, content: str, evidence: Optional[str] = None,
                              confidence: float = 0.8) -> str:
        """Un Embrión publica un insight para toda la Colmena."""
        insight_id = f"insight_{embrion_id}_{datetime.utcnow().timestamp()}"

        self.db.table("colmena_insights").insert({
            "id": insight_id,
            "embrion_id": embrion_id,
            "type": insight_type.value,
            "title": title,
            "content": content,
            "evidence": evidence,
            "confidence": confidence,
            "endorsements": 0,
            "contradictions": 0,
            "created_at": datetime.utcnow().isoformat(),
            "active": True
        }).execute()

        return insight_id

    async def endorse(self, insight_id: str, embrion_id: str, reason: str):
        """Un Embrión respalda un insight (aumenta su credibilidad)."""
        # Incrementar endorsements
        self.db.rpc("increment_endorsement", {
            "insight_id": insight_id
        }).execute()

        # Registrar quién respaldó
        self.db.table("colmena_insight_reactions").insert({
            "insight_id": insight_id,
            "embrion_id": embrion_id,
            "reaction": "endorse",
            "reason": reason,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

    async def contradict(self, insight_id: str, embrion_id: str, counter_evidence: str):
        """Un Embrión contradice un insight (reduce su credibilidad)."""
        self.db.rpc("increment_contradiction", {
            "insight_id": insight_id
        }).execute()

        self.db.table("colmena_insight_reactions").insert({
            "insight_id": insight_id,
            "embrion_id": embrion_id,
            "reaction": "contradict",
            "reason": counter_evidence,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

    async def get_active_insights(self, insight_type: Optional[InsightType] = None,
                                  min_confidence: float = 0.5) -> list[dict]:
        """Obtiene insights activos de la Colmena, ordenados por credibilidad."""
        query = self.db.table("colmena_insights").select("*").eq(
            "active", True
        ).gte("confidence", min_confidence)

        if insight_type:
            query = query.eq("type", insight_type.value)

        result = query.order("endorsements", desc=True).limit(50).execute()

        return [{
            "id": r["id"],
            "type": r["type"],
            "title": r["title"],
            "content": r["content"],
            "confidence": r["confidence"],
            "credibility_score": r["endorsements"] - r["contradictions"],
            "author": r["embrion_id"],
            "created_at": r["created_at"]
        } for r in result.data]

    async def get_rules(self) -> list[dict]:
        """Obtiene las reglas activas con alta credibilidad (consenso de la Colmena)."""
        return await self.get_active_insights(
            insight_type=InsightType.REGLA,
            min_confidence=0.8
        )
```

### SQL — Memoria Colectiva

```sql
-- Insights compartidos
CREATE TABLE colmena_insights (
    id TEXT PRIMARY KEY,
    embrion_id TEXT NOT NULL REFERENCES embrion_identity(embrion_id),
    type TEXT NOT NULL CHECK (type IN ('patron', 'leccion', 'descubrimiento', 'regla', 'alerta')),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    evidence TEXT,
    confidence FLOAT NOT NULL DEFAULT 0.8,
    endorsements INTEGER DEFAULT 0,
    contradictions INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE colmena_insight_reactions (
    id SERIAL PRIMARY KEY,
    insight_id TEXT NOT NULL REFERENCES colmena_insights(id),
    embrion_id TEXT NOT NULL REFERENCES embrion_identity(embrion_id),
    reaction TEXT NOT NULL CHECK (reaction IN ('endorse', 'contradict')),
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(insight_id, embrion_id)
);

-- Funciones de incremento atómico
CREATE OR REPLACE FUNCTION increment_endorsement(insight_id TEXT)
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
    UPDATE colmena_insights SET endorsements = endorsements + 1 WHERE id = insight_id;
END;
$$;

CREATE OR REPLACE FUNCTION increment_contradiction(insight_id TEXT)
RETURNS void LANGUAGE plpgsql AS $$
BEGIN
    UPDATE colmena_insights SET contradictions = contradictions + 1 WHERE id = insight_id;
END;
$$;

CREATE INDEX idx_insights_type ON colmena_insights(type, active);
CREATE INDEX idx_insights_credibility ON colmena_insights(endorsements DESC);
```

### Criterios de Aceptación 74.4

1. Embrión-1 publica insight → Embrión-0 puede leerlo
2. Endorsements incrementan credibilidad
3. Contradictions reducen credibilidad
4. `get_rules()` retorna solo insights con alta credibilidad
5. Insights con más contradictions que endorsements se marcan como `active=False`

---

## Épica 74.5 — Integración: Embrión Completo con Memoria + Colmena

### Concepto

Unir todo: el Embrión ahora tiene memoria indestructible Y puede comunicarse con otros Embriones. El loop de ejecución (Sprint 72) se enriquece con:
- Antes de ejecutar: consulta memoria colectiva por lecciones relevantes
- Durante ejecución: puede delegar sub-tareas a otros Embriones
- Después de ejecutar: publica aprendizajes a la Colmena

```python
# kernel/embrion/embrion_completo.py
"""
DISEÑO: Embrión Completo — Memoria + Ejecución + Colmena
PROPÓSITO: Un Embrión que nunca olvida, siempre aprende, y trabaja en equipo.
"""

from kernel.memoria.estratificada import MemoriaEstratificada, MemoryLayer, MemoryPriority
from kernel.memoria.heartbeat_resiliente import HeartbeatResiliente
from kernel.colmena.protocolo import ProtocoloColmena, MessageType
from kernel.colmena.memoria_colectiva import MemoriaColectiva, InsightType
from kernel.execution.embrion_executor import EmbrionExecutor


class EmbrionCompleto:
    """El Embrión con todas sus capacidades integradas."""

    def __init__(self, embrion_id: str, supabase_client, scheduler):
        self.id = embrion_id
        self.db = supabase_client

        # Subsistemas
        self.memoria = MemoriaEstratificada(embrion_id, supabase_client)
        self.heartbeat = HeartbeatResiliente(self.memoria, scheduler)
        self.colmena = ProtocoloColmena(embrion_id, supabase_client)
        self.memoria_colectiva = MemoriaColectiva(supabase_client)
        self.executor = EmbrionExecutor(embrion_id, supabase_client)

    async def wake_up(self):
        """Protocolo de arranque — se ejecuta al iniciar o después de un crash."""
        # 1. Cargar identidad
        await self.memoria.initialize()

        # 2. Verificar integridad
        beat = await self.heartbeat.beat()

        if beat["fcs"]["estado"] == "CRÍTICO":
            # Recuperación completa
            recovery = await self.memoria.recover_from_crash()
            await self.memoria.memorize(
                content=f"[WAKE_UP] Arranque con estado CRÍTICO. Recovery ejecutado.",
                layer=MemoryLayer.EPISODICA,
                priority=MemoryPriority.ALTA
            )

        # 3. Revisar inbox de la Colmena
        messages = await self.colmena.check_inbox()
        for msg in messages:
            await self._process_message(msg)

        # 4. Consultar insights colectivos recientes
        new_rules = await self.memoria_colectiva.get_rules()
        # Incorporar reglas nuevas a working memory
        for rule in new_rules[:5]:
            await self.memoria.memorize(
                content=f"[REGLA COLECTIVA] {rule['title']}: {rule['content']}",
                layer=MemoryLayer.TRABAJO,
                priority=MemoryPriority.ALTA
            )

        # 5. Registrar arranque exitoso
        await self.memoria.memorize(
            content=f"[WAKE_UP] Arranque exitoso. FCS: {beat['fcs']['score']}. Mensajes pendientes: {len(messages)}.",
            layer=MemoryLayer.EPISODICA,
            priority=MemoryPriority.MEDIA
        )

    async def execute_encomienda(self, encomienda: dict) -> dict:
        """Ejecuta una encomienda con contexto de memoria y colmena."""
        # 1. Antes de ejecutar: consultar memoria por experiencias similares
        relevant_memories = await self.memoria.remember(encomienda["objetivo"], limit=5)
        collective_lessons = await self.memoria_colectiva.get_active_insights(
            insight_type=InsightType.LECCION
        )

        # 2. Enriquecer contexto del executor
        context = await self.memoria.get_context_window()
        context += "\n\n## Lecciones relevantes de la Colmena:\n"
        for lesson in collective_lessons[:3]:
            context += f"- {lesson['title']}: {lesson['content']}\n"

        # 3. Ejecutar con el TEL enriquecido
        result = await self.executor.execute(encomienda, extra_context=context)

        # 4. Después de ejecutar: memorizar resultado
        await self.memoria.memorize(
            content=f"Encomienda '{encomienda['objetivo']}' → {result['status']}. "
                    f"Duración: {result.get('duration_s', '?')}s. "
                    f"Aprendizaje: {result.get('learning', 'ninguno')}",
            layer=MemoryLayer.EPISODICA,
            priority=MemoryPriority.ALTA if result['status'] == 'failed' else MemoryPriority.MEDIA
        )

        # 5. Si falló, publicar lección a la Colmena
        if result['status'] == 'failed' and result.get('learning'):
            await self.memoria_colectiva.publish_insight(
                embrion_id=self.id,
                insight_type=InsightType.LECCION,
                title=f"Fallo en: {encomienda['objetivo'][:50]}",
                content=result['learning'],
                evidence=result.get('error_trace', ''),
                confidence=0.7
            )

        # 6. Si descubrió algo nuevo, publicar
        if result.get('discovery'):
            await self.memoria_colectiva.publish_insight(
                embrion_id=self.id,
                insight_type=InsightType.DESCUBRIMIENTO,
                title=result['discovery']['title'],
                content=result['discovery']['content'],
                confidence=0.6
            )

        return result

    async def _process_message(self, msg: 'ColmenaMessage'):
        """Procesa un mensaje recibido de otro Embrión."""
        await self.colmena.mark_read(msg.id)

        if msg.type == MessageType.DELEGATE:
            # Alguien me delegó una tarea
            import json
            task_data = json.loads(msg.content)
            encomienda = {
                "objetivo": task_data["task"],
                "contexto": task_data["context"],
                "delegated_by": task_data["delegated_by"],
                "priority": "media"
            }
            # Ejecutar la tarea delegada
            result = await self.execute_encomienda(encomienda)
            # Responder al delegador
            await self.colmena.send_message(
                recipient_id=msg.sender_id,
                subject=f"[RESULTADO] {task_data['task'][:50]}",
                content=json.dumps(result),
                msg_type=MessageType.RESPONSE
            )

        elif msg.type == MessageType.DEBATE_OPEN:
            # Hay un debate abierto — debo participar
            await self.memoria.memorize(
                content=f"[DEBATE PENDIENTE] {msg.subject}: {msg.content[:200]}",
                layer=MemoryLayer.TRABAJO,
                priority=MemoryPriority.ALTA
            )

        elif msg.type == MessageType.ALERT:
            # Alerta urgente — memorizar inmediatamente
            await self.memoria.memorize(
                content=f"[ALERTA] De {msg.sender_id}: {msg.content}",
                layer=MemoryLayer.EPISODICA,
                priority=MemoryPriority.CRITICA
            )

    async def consolidate_daily(self):
        """Proceso diario de consolidación de memoria y publicación de patrones."""
        # 1. Consolidar memoria individual
        await self.memoria.consolidate()

        # 2. Analizar si hay patrones que publicar a la Colmena
        recent = await self.memoria.remember("patrones recurrentes últimos 7 días", limit=20)
        if len(recent) >= 5:
            # Hay suficiente material para buscar patrones
            patterns = await self._extract_publishable_patterns(recent)
            for p in patterns:
                await self.memoria_colectiva.publish_insight(
                    embrion_id=self.id,
                    insight_type=InsightType.PATRON,
                    title=p["title"],
                    content=p["content"],
                    confidence=p.get("confidence", 0.7)
                )

    async def _extract_publishable_patterns(self, memories: list) -> list[dict]:
        """Usa el Pensador para extraer patrones publicables."""
        import openai
        client = openai.AsyncOpenAI()

        contents = "\n".join([f"- {m.content[:200]}" for m in memories])
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": f"Eres {self.memoria.identity.nombre} de El Monstruo. "
                           "Analiza estas memorias recientes y extrae 1-3 patrones que serían útiles "
                           "para OTROS Embriones de la Colmena. Solo patrones con alta confianza. "
                           "Responde en JSON: [{\"title\": \"...\", \"content\": \"...\", \"confidence\": 0.8}]"
            }, {
                "role": "user",
                "content": contents
            }],
            max_tokens=500,
            response_format={"type": "json_object"}
        )

        import json
        try:
            result = json.loads(response.choices[0].message.content)
            return result.get("patterns", [])
        except:
            return []
```

### API Endpoints

```python
# Endpoints para el Command Center
@app.get("/api/v1/colmena/estado")
async def colmena_estado():
    """Estado completo de la Colmena para el Command Center."""
    embriones = supabase.table("embrion_identity").select("*").execute()
    debates_activos = supabase.table("colmena_debates").select("*").eq("status", "open").execute()
    insights_recientes = supabase.table("colmena_insights").select("*").eq("active", True).order("created_at", desc=True).limit(10).execute()
    messages_pending = supabase.table("colmena_messages").select("count").eq("read", False).execute()

    return {
        "embriones_activos": len(embriones.data),
        "embriones": embriones.data,
        "debates_activos": len(debates_activos.data),
        "debates": debates_activos.data,
        "insights_recientes": insights_recientes.data,
        "mensajes_pendientes": messages_pending.data[0]["count"] if messages_pending.data else 0
    }

@app.get("/api/v1/memoria/{embrion_id}/stats")
async def memoria_stats(embrion_id: str):
    """Estadísticas de memoria de un Embrión."""
    layers = {}
    for layer in ["L1", "L2", "L3"]:
        count = supabase.table("embrion_memory").select("count").eq(
            "embrion_id", embrion_id
        ).eq("layer", layer).execute()
        layers[layer] = count.data[0]["count"] if count.data else 0

    return {
        "embrion_id": embrion_id,
        "total_fragments": sum(layers.values()),
        "by_layer": layers,
        "last_consolidation": "TODO"
    }
```

### Criterios de Aceptación 74.5

1. `EmbrionCompleto.wake_up()` ejecuta en <5s incluyendo recovery
2. Encomiendas se enriquecen con memoria colectiva antes de ejecutar
3. Fallos se publican automáticamente como lecciones
4. Mensajes delegados se ejecutan y responden correctamente
5. Consolidación diaria reduce fragmentos sin perder información
6. Command Center puede ver estado de Colmena via API

---

## Métricas de Éxito del Sprint

| Métrica | Target | Medición |
|---|---|---|
| Recovery time post-crash | <5s | Tiempo desde restart hasta FCS >80 |
| Memory persistence | 100% | L0+L1+L2 sobreviven restart |
| Message delivery | <200ms | Tiempo desde send hasta disponible en inbox |
| Debate resolution | <5min | Tiempo desde apertura hasta resolución |
| Collective insights/week | >5 | Insights publicados por la Colmena |
| Context window quality | >0.8 | Relevancia de memorias recuperadas |

---

## Archivos a Crear

```
kernel/
  memoria/
    __init__.py
    estratificada.py          ← Épica 74.1
    heartbeat_resiliente.py   ← Épica 74.2
  colmena/
    __init__.py
    protocolo.py              ← Épica 74.3
    memoria_colectiva.py      ← Épica 74.4
  embrion/
    embrion_completo.py       ← Épica 74.5
```

---

## Dependencias

- `pgvector` (extensión PostgreSQL) — ya disponible en Supabase
- `openai` (para embeddings) — ya instalado
- Sprint 72 (TEL) — EmbrionExecutor
- Sprint 71 (Brand Engine) — Embrión-1 como primer compañero de Colmena

---

## Notas de Diseño

1. **¿Por qué no Redis para L3?** — Supabase es suficiente para el volumen actual. Redis agrega una dependencia más (Obj #12). Si el rendimiento lo requiere en el futuro, se migra L3 a Redis sin cambiar la interfaz.

2. **¿Por qué mayoría simple en debates?** — Con 2 Embriones, mayoría simple = consenso. Cuando haya 8, se puede cambiar a 2/3 supermajority. El protocolo es extensible.

3. **¿Por qué no usar un message broker (RabbitMQ/Kafka)?** — Obj #3 (mínima complejidad). Supabase tables + polling es suficiente para 8 Embriones. Si escala a 100+, se migra a un broker.

4. **El Pensador solo se activa para:** Extraer patrones, generar posiciones en debates, y decidir qué delegar. Todo lo demás es código determinista (Ejecutor).
