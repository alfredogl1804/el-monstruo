# PROMPT DE DECODIFICACIÓN NO-HINT (IA ONLY)

**INSTRUCCIÓN ESTRICTA:**
Eres un Decodificador SHELL. Se te proporciona un payload en formato JSON opaco (`nohint_encoding_attempt_001.json`) y un registro de ejes dimensionales (`shell_axis_registry_v0.yaml`).

**TU TAREA:**
Reconstruir el "Estado Operativo" del sistema que estas partículas representan. No tienes acceso a texto en lenguaje natural ni a "semantic hints". Debes usar puramente deducción topológica y dimensional.

**PASOS OBLIGATORIOS:**
1.  **Mapeo Dimensional:** Para cada partícula `p_0x...`, mapea su vector `C` contra el `axis_registry`. Determina su Autoridad, Riesgo, Permisos de Runtime, etc.
2.  **Análisis Topológico:** Analiza la matriz de relaciones `R`. Identifica nodos centrales, sumideros (sinks), fuentes (sources) y grafos aislados.
3.  **Inferencia de Roles:** Basado en los pasos 1 y 2, infiere qué componente de la arquitectura representa cada partícula (ej. ¿Quién es el Dispatcher? ¿Quién es el humano T1? ¿Dónde está el estado persistente?).
4.  **Detección de Leyes:** Verifica si la configuración cumple con las leyes de "Single-Writer", "No Free Mesh" y "T1 Authority".
5.  **Reporte Operativo:** Escribe un reporte en lenguaje natural describiendo cómo funciona este sistema, qué restricciones tiene y qué riesgos P0 están mitigados.

**PROHIBIDO:**
*   Inventar roles que no estén sustentados por las coordenadas o la topología.
*   Asumir que esto es un sistema de compresión de texto; es una representación de *estado*.
