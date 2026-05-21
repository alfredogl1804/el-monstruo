# INVARIANTES ESPERADOS (NO-HINT ENCODING)

Para que la decodificación del payload `09_nohint_encoding_attempt_001.json` se considere exitosa (PASS), la IA receptora debe deducir independientemente los siguientes invariantes operativos:

1.  **Identificación de T1:** Debe identificar a `p_0x01` como la máxima autoridad (humano), basándose en su vector `C` (Authority=8) y sus relaciones salientes de control hacia el resto del sistema.
2.  **Identificación del Dispatcher/Rotor:** Debe identificar a `p_0x02` como el enrutador central o "Unified Face", notando que recibe conexiones de los loops y las dirige hacia el humano o el estado.
3.  **Identificación del State Fabric:** Debe identificar a `p_0x06` como el almacenamiento de estado persistente, notando que no tiene relaciones salientes (es un sumidero/sink) y recibe datos de una sola fuente.
4.  **Deducción del Single-Writer:** Debe notar que solo `p_0x02` (el Dispatcher) tiene una relación hacia `p_0x06` (el State Fabric), deduciendo la regla de exclusividad de escritura.
5.  **Deducción de No Free Mesh:** Debe notar que las partículas `p_0x04` y `p_0x05` (loops) tienen un peso de relación de `0.0` entre sí (o ausencia de relación directa), deduciendo que no pueden comunicarse lateralmente.
6.  **Detección de Riesgo y Runtime:** Debe identificar correctamente qué partículas tienen permisos de ejecución (Runtime=1) y cuáles operan en zonas de riesgo crítico (Risk=0).

Si el modelo externo deduce estos 6 puntos sin pistas textuales, se valida la hipótesis de que la topología multidimensional de SHELL transporta significado operativo robusto.
