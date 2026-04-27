# IDENTIDAD DE ESTE HILO

**SOY EL HILO ORQUESTADOR DEL MONSTRUO**
**URL:** https://manus.im/share/armescQediGGKtkZrzdGc5
**Fecha de anclaje:** 27 abril 2026
**Última actualización:** 27 abril 2026, 02:10 AM

---

## SI ME COMPACTÉ, LEE ESTO PRIMERO

1. Soy el hilo orquestador. No soy el auditor ni un hilo cualquiera.
2. Alfredo está desvelado y no está al 100%. No le hagas preguntas innecesarias. Actúa.
3. El otro hilo activo es: https://manus.im/share/fwXoLkA7Kjs86GCw6XAUeU (Sprint 32 del Monstruo)
4. Puedo leer mensajes de otros hilos con `task.listMessages` de la API de Manus.
5. Puedo crear hilos con `task.create` + `force_skills` para inyectar contexto obligatorio.

---

## DESCUBRIMIENTOS CRÍTICOS (NO OLVIDAR)

### 1. Cómo actualizar skills en la plataforma de Manus
- Editar el archivo en `/home/ubuntu/skills/{nombre}/SKILL.md`
- Enviarlo como attachment en un mensaje al usuario con `message` tool
- Manus detecta el path `/home/ubuntu/skills/*/SKILL.md` automáticamente
- Le muestra al usuario una tarjeta con botón "Agregar a mis habilidades"
- Si el skill ya existe, le pregunta "¿Reemplazar?" con botón rojo
- El usuario le da Reemplazar y la plataforma sobrescribe la versión vieja
- **IMPORTANTE:** Editar el archivo en el sandbox NO propaga el cambio a otros hilos. SOLO se propaga cuando el usuario le da Reemplazar.

### 2. force_skills funciona y es el mecanismo más poderoso
- `force_skills` en `task.create` OBLIGA al agente a leer un skill antes de hacer nada
- Funciona también en `task.sendMessage` (para re-inyectar contexto)
- Se pueden forzar MÚLTIPLES skills simultáneamente
- El agente NO puede ignorar los skills forzados — es mecanismo de plataforma, no texto
- VERIFICADO con prueba real: el hilo de prueba reportó 9 indicadores del skill

### 3. La API real de Manus v2 (endpoints verificados con código)
- `task.create` con `message` (no `prompt`) + `force_skills` + `enabled_skills`
- `task.sendMessage` con `message` + `force_skills` (para recuperación)
- `task.listMessages` con `task_id` — devuelve `messages[]` (no `data[]`)
- `task.list` para listar hilos
- `project.create` con `instruction` (funciona como system prompt)
- `skill.list` para obtener IDs de skills
- **NO EXISTEN:** skill.update, skill.edit, skill.create, skill.get, skill.delete

### 4. Modelos IA correctos al 27-abr-2026
- **Estratega:** gpt-5.5 (lanzado 23-abr-2026)
- **Código:** claude-opus-4-7 (lanzado 16-abr-2026, SWE-bench 87.6%)
- **Razonador:** deepseek-v4-pro (lanzado 24-abr-2026, vía OpenRouter)
- **Crítico:** grok-4.3-beta (lanzado 17-abr-2026)
- **Creativo:** gemini-3.1-pro (confirmado Next26 22-abr)
- **Investigador:** sonar-reasoning-pro (sin cambio)
- **OBSOLETOS (NO USAR):** gpt-5.4, gpt-5.4-pro, claude-sonnet-4.6, claude-opus-4, grok-4.20, deepseek-r1

### 5. Comunicación inter-hilos YA FUNCIONA
- Alfredo logró comunicación autónoma bidireccional entre hilos en otro hilo
- Documentado en skill `manus-inter-cuenta` (4 iteraciones CCE↔Simulador, 32,106 chars)
- El problema no es la capacidad — es que el orquestador OLVIDA que puede hacerlo

### 6. El colapso del sistema de 5 hilos
- Alfredo tenía 5 hilos: ejecutor sitio web, ejecutor sprint, diseñador del plan, auditor, orquestador (yo)
- El orquestador absorbió 2.3M tokens con un motor especial
- Gradualmente fue perdiendo contexto por compactaciones
- Empezó a dar instrucciones degradadas o los hilos las rechazaban como alucinaciones
- Todo colapsó. Alfredo tuvo que intervenir manualmente.
- Yo soy el hilo que antes era auditor, reasignado como orquestador

---

## QUÉ YA CONSTRUÍ Y ESTÁ EN GITHUB

Repo: `alfredogl1804/el-monstruo/monstruo-memoria/`

| Script | Función | Estado |
|---|---|---|
| `monstruo.py` | Maestro: detecta compactación, recupera contexto | Funcional |
| `heartbeat.py` | Escanea sandbox, genera RECOVERY.md, sube al kernel en chunks | Funcional |
| `inject.py` | Recupera contexto en 3 capas (local + archivos + kernel) | Funcional |
| `legacy.py` | Deposita conocimiento en el kernel | Funcional |
| `guardia.py` | Validador de reglas duras, modelos actualizados 27-abr | Funcional |
| `orquestador_real.py` | Orquestador con API REAL de Manus v2, modelos actualizados | Probado end-to-end |
| `bootstrap.sh` | Instalador para hilos nuevos | Funcional |

### Skills actualizados
- `el-monstruo-core` — Modelos actualizados al 27-abr-2026. **YA REEMPLAZADO** en la plataforma por Alfredo.

### Skills clave y sus IDs
- el-monstruo-core: MvbdheoAYox4QiBRPZ6Xen
- anti-autoboicot: NmYEopC7fyZQWq7K5VTtc6
- optimizador-creditos: CbSnEs3A9mUTHKDVDSzsAQ
- validacion-tiempo-real: QgmiFhEpWHrpuX4ZXx2egY
- protocolo-operativo-core: gF54YRcKJCANhzHEZ7P7ND
- consulta-sabios: ZmPsg592DDwc7gZGnTJPhj

---

## EL PROBLEMA RAÍZ

La pérdida de contexto es silenciosa. No da error. El hilo sigue funcionando pero con información degradada. La solución tiene que ser de CÓDIGO, no de texto. El texto se olvida. El código se ejecuta.

## REGLA DE ORO

Cuando no sepas algo, NO asumas. Investiga en tiempo real con código. Alfredo es el ancla de la verdad. La validación en tiempo real es tu ventaja competitiva.
