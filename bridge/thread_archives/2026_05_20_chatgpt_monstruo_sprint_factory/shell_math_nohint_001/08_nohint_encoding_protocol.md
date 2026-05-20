# PROTOCOLO DE CODIFICACIÓN NO-HINT (v0)

El objetivo del "No-Hint Encoding" es forzar a la IA receptora a deducir el significado puramente a partir de la topología y las coordenadas matemáticas, eliminando las "muletas" de lenguaje natural.

## Reglas de Codificación (Restricciones)

1.  **Cero `semantic_hint`:** El campo `semantic_hint` está estrictamente prohibido.
2.  **IDs Opacos:** Los identificadores de partículas deben ser hashes o secuencias numéricas (ej. `p_0x1A`, no `p_unified_face`).
3.  **Vectores de Estado:** Las propiedades como Autoridad, Riesgo y Permisos deben representarse exclusivamente como arrays numéricos (ej. `C: [8, 0, 1]`), referenciando el `axis_registry`.
4.  **Relaciones Tipadas por ID:** Los tipos de relación deben usar identificadores numéricos (ej. `type: 0x0C` en lugar de `type: "write_access"`).
5.  **Metadatos Minimizados:** Los metadatos solo pueden contener flags numéricos o referencias abstractas, nunca explicaciones en lenguaje natural.

## Mecanismo de Reconstrucción
La IA receptora recibe el payload JSON (opaco) y el `axis_registry` (el diccionario de ejes). Debe cruzar los IDs opacos con las reglas topológicas (ver `06_decoder_rules_v0.md`) para reconstruir el estado operativo.

Si la IA logra reconstruir el modelo de Vigilia Sincrónica (Single-Writer, Rotor, T1 Authority) a partir de este payload opaco, se demuestra que la dimensionalidad y la topología son suficientes para transmitir el entendimiento operativo, validando la hipótesis central de SHELL.
