# BITACORA TRAMO 1 — INDEX

> **Para Manus B futuro:** este archivo es el punto de entrada cuando regreses a este tramo. Léelo primero. Si necesitas detalle, grep sobre `bitacora.jsonl`.

## Estado del Tramo
- **Sueño Firmado #001** — FORJA OMEGA v1.0
- **Tramo:** 1 (diseño técnico de infraestructura inmune-coordinadora)
- **Fase:** 1.0 Detonación (Cámara de Chispa Modo B)
- **Vehículo:** Monstruo Embrionario v0.7
- **Última actividad:** 2026-05-28
- **Branch git:** `tramo-1-bitacora-y-dta`

## Componentes del Tramo (5 acoplados)
1. **Sistema Inmune declarativo** — refactor unificado sobre ~70% existente disperso (Memento, anti_dory, anti_ghost, write_policy, audit_middleware, secret-scan, Genome Vivo, Guardian, thread_immunity)
2. **Pit Wall** — desde cero, vigila SOLO dentro del sueño activo
3. **Meta-coordinador como protocolo (Capa B sueño)** — desde cero, declarativo NO agente
4. **STS — Sistema de Tránsito Soberano** — arriba de todo, 3 reglas binarias (R1 sueño / R2 mantenimiento / R3 chispa entrante)
5. **Vigía + Cirujano-Manus on-demand** — pipeline transversal de mantenimiento (reemplaza al PMM-burócrata descartado)

## Doctrinas nuevas pendientes de canonizar en TESIS v1.3
- **Principio de Soberanía Dominal** — el Monstruo no arbitra entre dominios incomparables
- **Principio del Cirujano Único Bien Despachado** — un cirujano competente end-to-end + Vigía que filtra
- **Principio de Captura en Tiempo Real (CTR)** — bitácora viva al cierre de cada intercambio, no al cierre del hilo
- **Principio de Discoverability Triple-Anclada (DTA)** — AGENTS.md + Guardian + Genome Vivo

## Anti-patrones detectados y corregidos
- **MOC-confusion** — confundí kernel/moc/moc.py (agente Sprint 36) con doctrina FORJA OMEGA
- **La-Forja-confusion** — pensé La Forja podía ser Pit Wall; es producto comercial, no
- **PMM-burócrata-descartado** — sobre-ingeniería con 4 etapas, reemplazado por Vigía+Cirujano

## Pregunta pendiente (último estado)
- **Pregunta 1 Detonación** sobre Meta-coordinador: cómo decide el Monstruo en un instante dado quién hace qué primero
- Alfredo respondió **parcialmente** con chispa transversal (1000 mensajes Telegram, Manus de mantenimiento)
- Alfredo declaró tener **varios puntos más pendientes** de pregunta 1 que aún no soltó
- **Próxima acción:** continuar Fase Detonación con captura activa hasta que Alfredo termine de soltar puntos pendientes, después firmar alcance binario y consultar 6 Sabios

## Cómo seguir absorbiendo contexto
```bash
# Ver eventos por tipo
jq -c 'select(.t=="firma")' forja_omega_tramo_1/bitacora.jsonl
jq -c 'select(.t=="chispa" and .a=="alfredo")' forja_omega_tramo_1/bitacora.jsonl
jq -c 'select(.t=="propuesta")' forja_omega_tramo_1/bitacora.jsonl

# Buscar por componente
jq -c 'select(.ref|contains("vigia"))' forja_omega_tramo_1/bitacora.jsonl

# Último evento
tail -1 forja_omega_tramo_1/bitacora.jsonl | jq .

# Reconstruir narrativa cronológica
jq -c '.' forja_omega_tramo_1/bitacora.jsonl | head -50
```

## Schema JSONL
```
{"ts":"ISO8601","t":"firma|chispa|propuesta|descarte|doctrina|antipattern|estado|pregunta_pendiente","a":"alfredo|manus","ref":"componente_o_concepto","c":"contenido_denso","v":"verbatim_si_aplica","s":"id_supersede_si_aplica"}
```

## Documentos canonizados que respaldan este tramo (en main)
- `bridge/FORJA_OMEGA_TESIS_v1_2_2026_05_28.md` — TESIS magna
- `bridge/ANEXO_PROTOCOLOS_SATELITE_v1_2026_05_28.md` — Anexo
- `bridge/CONTRATO_SUENO_FIRMADO_001_2026_05_28.md` — Contrato del sueño
