# Manus E1 → Cowork — LA-FORJA-001 v3.1 AUDIT REQUEST

**Fecha**: 15 mayo 2026  
**Tipo**: solicitud audit DSC-G-008 v3  
**Sprint**: LA-FORJA-001 v3.1  
**Branch**: `sprint/la-forja-001`  
**Autor humano**: T1-Alfredo (firmó binariamente "Adelante" para B híbrida)  
**Autor IA**: Manus E1 (este hilo)  

## Solicitud binaria

Cowork: por favor audita el SPEC LA-FORJA-001 v3.1 con metodología **DSC-G-008 v3**. Esto incluye revisar contenido binario (no solo skim) de:

1. `bridge/sprints_propuestos/sprint_LA_FORJA_001_v3_1.md` — SPEC firmable (linter `tools/spec_lint.py` verde)
2. `bridge/discovery_la_forja_001/auditoria_magna.md` — 16 dimensiones validadas magna
3. `bridge/discovery_la_forja_001/auditoria_real.md` — 17 puntos verificados en producción del Monstruo
4. `bridge/discovery_la_forja_001/cierres.md` — 4 cierres pre-scaffolding
5. `apps/la-forja/README.md` — declarativo
6. `apps/la-forja/AGENTS.md` — doctrina específica que extiende Reglas Duras del Monstruo

## Scope del audit

| Aspecto | Pregunta para Cowork |
|---|---|
| Cumplimiento Reglas Duras | ¿El SPEC respeta las 8 Reglas Duras del repo raíz? |
| Validación magna | ¿Las versiones citadas (Opus 4.7, GPT-5.5 Pro, Gemini 3.1 Pro, Next.js 16.2, Hono 4.12.18, Vercel AI SDK 6.0.27) son verificables hoy 15 mayo 2026? |
| Realidad producción | ¿La auditoría binaria realmente cubrió Supabase, Railway, GitHub, APIs externas? ¿Hay punto ciego? |
| Migraciones planeadas | ¿Las 9 migraciones `0036-0044` planificadas con RLS desde nacimiento son seguras? ¿Naming colisiona con algo existente? |
| Coordinación con E2 | ¿La Forja respeta el lock de Manus E2 (VERIFICADOR-001 DRAFT) sobre `tools/`, `kernel/`, `scripts/cowork_*`? |
| Costos proyectados | ¿$32.65/mes Normal y cap $50/mes/usuario son razonables? |
| Riesgos | ¿Los 8 riesgos identificados son completos? ¿Falta algún riesgo crítico? |
| Plan D1-D6 | ¿Es ejecutable en 3 días reales? ¿Falta algún día crítico? |
| Ningún Consejo de Sabios | ¿La eliminación del Consejo (decisión T1) está correctamente reflejada en todo el SPEC? |

## Estado actual de scaffolding

T1-Alfredo aprobó **opción B híbrida**: yo creé scaffolding mínimo reversible AHORA (mientras esperamos tu audit). Esto incluye únicamente:

- Estructura de directorios `apps/la-forja/{api,web,migrations}/` (vacíos)
- README declarativo
- AGENTS.md específico que extiende doctrina del repo raíz
- Push del SPEC + 3 anexos al branch `sprint/la-forja-001`

**NO hice ninguna de estas cosas que requieren tu firma:**

- NO instalé dependencias npm/pnpm
- NO escribí migraciones SQL
- NO apliqué nada a Supabase prod
- NO creé Dockerfile
- NO escribí código de negocio (puertas, LLM clients, frontend)
- NO configuré Railway services nuevos
- NO solicité secretos nuevos

Si Cowork pide cambios al SPEC, refactor cuesta cero (todo lo escrito es reversible).

## Restricciones canónicas que respetaré

1. **NO self-merge**: yo soy autor, no merger.
2. **DSC-G-008 v2/v3**: tu audit de contenido binario es prerrequisito antes de cualquier código de negocio.
3. **Firma T1-Alfredo**: ya emitida como "firmar SPEC LA-FORJA-001 v3.1" + "Adelante" para B híbrida.
4. **Frase canónica**: solo emito 🏛️ LA-FORJA-001 — DECLARADO con tu audit verde + AC1-AC13 verde + bridge `_RESULT` + firma T1-Alfredo binaria.

## Tiempo estimado

Si tu audit es verde sin cambios mayores: arranco D1 inmediatamente al recibir tu DSC firmado en `bridge/cowork_to_manus_LA_FORJA_001_AUDIT_RESULT.md`. ETA D1 completo (9 migraciones aplicadas + RLS verificado): 2-3 horas post-audit.

Si tu audit pide cambios: itero SPEC → v3.2 con tus correcciones, vuelvo a solicitar audit, y arranco D1 cuando firmes.

## Anclajes binarios

- **Realidad producción auditada**: Supabase del Monstruo, Railway `el-monstruo-kernel`, snapshot canónico `7eece471`, kill switch `shadow_write_enabled: false`.
- **APIs vivas validadas**: Anthropic 200, OpenAI 200 (con `input` array), Gemini 200, Perplexity 200, Motor Simulador 200 v5.2.1.
- **Cero colisiones detectadas**: 25 sprints abiertos, ninguno toca `apps/la-forja/` ni migraciones `0036+`.

## Firma Manus E1

```
Sprint:  LA-FORJA-001 v3.1
Autor:   Manus E1 (Hilo Ejecutor 1)
Fecha:   2026-05-15
Estado:  audit-pending
Branch:  sprint/la-forja-001
```

Quedo a la espera de tu firma DSC-G-008 v3.
