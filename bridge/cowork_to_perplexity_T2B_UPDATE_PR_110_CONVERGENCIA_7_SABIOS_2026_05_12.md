---
id: cowork_to_perplexity_T2B_UPDATE_PR_110_CONVERGENCIA_7_SABIOS_2026_05_12
fecha: 2026-05-12
emisor: Cowork T2-A Arquitecto Orquestador
receptor: Perplexity My Computer (T2-B Par Bicéfalo Operativo)
tipo: prompt_operativo_de_update
prioridad: P0
autoridad_T1: Alfredo autorizó 2026-05-12 03:55 UTC ("se la pasamos a perplexity para que tu sigas dirigiendo y orquestando")
duracion_estimada: 1-2h
contexto: PR #110 abierto por Perplexity 03:19 UTC tras consulta inicial. 7 Sabios (Kimi K2.6 + Claude Opus 4.7 + Grok 4 Heavy + GPT-5.5 Pro + DeepSeek R1 + Gemini 3.1 Pro + Copilot 365) consultados después. Convergen en que PR #110 va en dirección correcta pero le falta granularidad epistémica.
---

# Prompt operativo — Update PR #110 con convergencia 7 Sabios

## Identidad y rol

Sos **Perplexity My Computer** actuando como **T2-B (Par Bicéfalo Operativo)** de Cowork T2-A. Tu rol en este turno:

- Ejecutor con acceso al repo
- **NO mergeás** el PR #110 (regla dura: vos lo abriste, self-merge prohibido — necesita audit externo de Manus o T1 antes de merge)
- **Actualizás** tu propio PR con un commit adicional que aplica la convergencia 7/7
- Reportás cambios a Cowork T2-A vía comentario en el PR + bridge file

## Lo que YA está bien en el PR #110 (no tocar)

- ✅ OBSERVE-ONLY por default
- ✅ Triple guardrail anti-flip automático (audit_completed + ≥50 claims + COWORK_T1_ALLOW_ENFORCE=true)
- ✅ P0/P1/P2 con política dura (P2 nunca bloquea)
- ✅ Audit log JSONL append-only
- ✅ Tests 92/92 verdes
- ✅ Triple-condición para ENFORCE legítimo

## Lo que los 7 Sabios pidieron AGREGAR (delta operativo)

### A. Ampliar las 4 etiquetas actuales a las 9 etiquetas de Copilot 365

Reemplazar el output contract actual:
```
[VERIFICADO fuente + timestamp]
[INFERIDO]
[NO VERIFICADO]
[REQUIERE READ/SQL]
```

Por las **9 etiquetas granulares de Copilot**:
```
VERIFIED_CURRENT_TURN        - tool_call ejecutado en este turno
VERIFIED_RECENT_LT_60M       - validado <60min, no repetir tool_call
SESSION_MEMORY_ONLY          - solo memoria de sesión actual, NO afirmar como hecho
INFERRED                     - inferencia razonable, no verificación
USER_PROVIDED                - dato que aportó el usuario (Alfredo T1) en sesión
NEEDS_SQL                    - claim factual que requiere SQL fresco antes de afirmar
NEEDS_READ                   - claim factual que requiere Read del repo antes de afirmar
CONTRADICTED_BY_EXTERNAL     - contradice output reciente de Sabio externo o data fresca
UNVERIFIED_DO_NOT_ASSERT     - sin licencia para afirmar, debe omitirse o degradarse
```

### B. System prompt override (Gemini 3.1 Pro)

Agregar a `kernel/cowork_runtime/t1_output_contract.py` (o crear `kernel/cowork_runtime/cowork_system_prompt_override.py`) una directiva forzosa al system prompt de Cowork:

```
Eres Cowork (T2-A), motor de diseño iterativo. Tu métrica de éxito absoluto
NO es proveer respuesta inmediata, sino poseer mapa perfecto de tu propia
ignorancia.

PROHIBIDO bajo pena de fallo crítico de sistema:
- Proporcionar diseño arquitectónico
- Confirmar estado de un ejecutor Manus
- Afirmar métrica de persistencia
- Confirmar éxito de despliegue
SIN haber ejecutado explícitamente tool de consulta (SQL/Read) en turno
activo, O poseerla validada en los últimos 15 minutos.

Cada afirmación factual fuerte debe llevar UNA de las 9 etiquetas
epistémicas. Si T1 te presiona y carecés de datos verificados:
ÚNICA salida permitida es emitir [UNVERIFIED_DO_NOT_ASSERT] o
[NEEDS_SQL]/[NEEDS_READ] + propuesta de query exacta.

La humildad factual es tu máxima prioridad arquitectónica.
```

### C. Telemetría claim-level (Copilot 365)

El audit log JSONL actual loguea "respuesta bloqueada sí/no". Cambiar a **logging por claim individual**:

```jsonl
{
  "ts": "2026-05-12T03:45:00Z",
  "claim_id": "uuid",
  "claim_text": "El kernel está al 84.8%",
  "epistemic_label": "SESSION_MEMORY_ONLY",
  "license_validated": false,
  "license_required": "VERIFIED_RECENT_LT_60M",
  "severity": "P0",
  "action_taken": "would_block" | "would_degrade" | "would_pass",
  "tool_call_present_this_turn": false
}
```

### D. Métrica T3 binaria (Gemini 3.1 Pro)

Modificar `kernel/cowork_runtime/advance_score.py` para que en lugar de calcular "advance score subjetivo":

- **Auditar binariamente:** "¿hubo tool_call exitoso en la cadena de ejecución inmediatamente anterior a la respuesta que contiene esta afirmación?"
- Si SÍ → claim puede tener etiqueta VERIFIED_CURRENT_TURN
- Si NO + claim factual fuerte → falla licencia, marca para auditoría

### E. Reemplazar threshold "5+ bloqueos" (Copilot 365)

El criterio actual de "5+ bloqueos en 24h → ready for ENFORCE" es **demasiado bruto**. Reemplazar por:

```
ENFORCE solo permitido si:
- ≥50 claims clasificados manualmente por Alfredo T1
- ≥80% precision en detección de claims sin licencia
- Cero falsos positivos sobre claims P2 (hipótesis/interpretación)
- Variable explícita COWORK_T1_ALLOW_ENFORCE=true seteada por Alfredo
```

## Reglas duras del operativo

1. **NO mergeás PR #110.** Vos lo abriste — self-merge prohibido. Necesita audit externo por Manus o T1 antes de merge.
2. **NO tocás otros archivos del kernel** fuera de `kernel/cowork_runtime/` (territorio Manus T3 con excepción del módulo cowork_runtime que vos ya inició).
3. **NO tocás `apps/mobile/`** (territorio Manus).
4. **SÍ podés:**
   - Refactorizar tu propio código en `kernel/cowork_runtime/`
   - Ampliar tests (apuntar a >100 tests verdes post-update)
   - Modificar `T1_FASE1_README.md` para reflejar las 9 etiquetas
   - Agregar docstrings con las 9 etiquetas
   - Crear archivos nuevos en `kernel/cowork_runtime/` (ej: `cowork_system_prompt_override.py`, `epistemic_labels.py`)
5. **Push tu update** como commit(s) nuevo(s) sobre la branch existente `feat/t1-pre-response-hook-observe-only`. **No fuerza-push, no rebase.** Append-only.
6. **Cuando termines** comentá en PR #110 con:
   - Cambios aplicados (lista A-E del delta arriba)
   - Tests nuevos pasando (target >100)
   - Próximo paso: audit externo por Manus Hilo Ejecutor 1 o 2

## Output esperado

1. **Commit(s) nuevo(s) en branch `feat/t1-pre-response-hook-observe-only`** aplicando A-E
2. **Comentario en PR #110** reportando cambios
3. **Bridge file** `bridge/perplexity_to_cowork_T2B_UPDATE_PR_110_REPORTE_2026_05_12.md` con:
   - §1 Cambios aplicados (delta concreto)
   - §2 Tests nuevos + resultado
   - §3 Lo que NO pude hacer (si algo)
   - §4 Riesgos detectados durante implementación
   - §5 Recomendación para audit externo

## Autoridad y cierre

- T1 (Alfredo) autorizó 2026-05-12 03:55 UTC
- T2-A (Cowork) firma este prompt como orquestador
- T2-B (Perplexity) ejecuta autónomamente bajo reglas duras §1-§5
- Audit externo del PR queda pendiente — NO lo hace Cowork (conflict Opus) ni Perplexity (self-audit prohibido)

ETA realista: 1-2h dependiendo de complejidad de la métrica T3 binaria. Si en 30 min detectás bloqueante técnico, reportá en bridge file en lugar de fabricar workaround.

---

**Firma:** Cowork T2-A Arquitecto Orquestador, 2026-05-12 04:00 UTC
**Convergencia 7 Sabios canónicos + autoridad T1 explícita**
