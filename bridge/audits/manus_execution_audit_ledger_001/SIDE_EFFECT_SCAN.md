# SIDE EFFECT SCAN v2 — con event_logs leídos

## §1 Side-effects REALES confirmados (lectura de logs)

| Categoría | v2 hallazgo |
|-----------|------------|
| Escrituras a main | NINGUNA (0/29) |
| Escrituras DB/Supabase | NINGUNA (logs confirman 0 DB) |
| Escrituras código productivo | NINGUNA (0 kernel/apps) |
| **Llamadas API externas** | **SÍ desde EPOCH 006**: openai gpt-4o-mini. Costo micro registrado ($0.00015–$0.00048/ciclo). Pre-006: costo sin provider nombrado |
| **Escritura Memory Palace** | **SÍ epochs 006/007**: memory_appended + memory_id. Store propio en bridge/, no Supabase |
| Archivos output generados | SÍ: `bridge/embryos/oracle_ai_r0/outputs/*.json` (timestamps 20260521) |
| Webhook / HTTP saliente | NINGUNO registrado |
| Retry | NINGUNO (0) |
| Kill-switch | RESPETADO: HOOK_ABORTED kill_switch_active (4→10) |

## §2 Estimación de gasto (verificada por logs)

Costos por ciclo $0.00015–$0.00048. Decenas de ciclos visibles en los logs acumulados. **Gasto total estimado: del orden de centavos USD.** Trivial en magnitud. El hallazgo NO es el monto sino el **principio**: el frente ejecutó llamadas a API de forma autónoma sin autorización por-llamada (gobernado solo por kill-switch + dispatcher action_class).

## §3 Resuelto vs v1

v1 marcó "provider cost UNVERIFIED P1". v2 lo VERIFICA: provider=openai, costo=trivial, tokens=no registrados. Baja de P1-UNVERIFIED a P2-DOCTRINAL (autonomía de gasto).
