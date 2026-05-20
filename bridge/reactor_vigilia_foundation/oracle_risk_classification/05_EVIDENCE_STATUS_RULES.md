# Reglas de Estado de Evidencia

**SPRINT:** SPR-RISK-CLASSIFICATION-001
**Estado:** DOCTRINE_CANDIDATE

La disciplina de evidencia es crítica para evitar alucinaciones operativas. El Monstruo no debe asumir que una capacidad es funcional en tiempo real si solo ha sido deducida de su entrenamiento o de documentación estática.

## Estados de Evidencia Permitidos

1. **STATIC_CATALOG:** La capacidad fue propuesta basándose en el conocimiento interno del modelo (entrenamiento) o en la lectura de un documento estático. **No se realizó ninguna llamada a la API real del modelo propuesto.**
2. **REALTIME_VERIFIED:** Se realizó una llamada exitosa a la API real del modelo propuesto, ejecutando un prompt de prueba y validando la respuesta.
3. **NO_SOURCE:** La capacidad fue propuesta sin ninguna base justificable.
4. **ACCESS_BLOCKED:** Se intentó verificar en tiempo real, pero el acceso a la API fue denegado (ej. falta de credenciales, bloqueo de red).

## Regla Estricta: No REALTIME claim sin API

**Si no se conectaron APIs reales durante el sprint de descubrimiento, NINGÚN capability puede quedar clasificado como `REALTIME_VERIFIED`.**

En el caso del catálogo v0 generado por el Oráculo en SPR-EMBRION-PERITO-LOOP-001, no se conectaron APIs externas. Por lo tanto, el overlay de clasificación de riesgo debe forzar el `evidence_status` de todas las capacidades a `STATIC_CATALOG`.

Como consecuencia de la regla de clasificación (ver Rúbrica), cualquier capacidad con estado `STATIC_CATALOG` recibe automáticamente un `risk_class` de **R0** y un `required_autonomy_level` de **A0/A1**, limitando severamente lo que el Monstruo puede hacer con ella hasta que sea verificada en tiempo real (lo cual requerirá el desbloqueo del Oráculo M2).
