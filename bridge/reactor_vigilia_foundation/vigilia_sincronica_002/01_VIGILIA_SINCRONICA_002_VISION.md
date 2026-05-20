# Visión — Vigilia Sincrónica 002

**SPRINT:** SPR-VIGILIA-SINCRONICA-002
**Estado:** DOCTRINE_CANDIDATE

## 1. El Principio Doctrinal

> "Un solo rostro, muchas mentes, una memoria soberana, una autoridad humana. La malla simula continuidad para el usuario, pero nunca simula autoridad ante T1."

La Vigilia Sincrónica no es un daemon infinito corriendo en background. Es un **modelo de orquestación** donde múltiples loops finitos se relevan de forma controlada a través de un estado compartido (State Fabric) y un árbitro de permisos (Dispatcher), presentando finalmente una sola voz coherente al usuario (Unified Face).

## 2. El Objetivo del Sprint

Este sprint crea un orquestador real de cadena local controlada. Su objetivo es ejecutar los tres loops reales ya construidos (Oráculo, Auditor, Risk Classification) en una secuencia determinística, culminando en la Unified Face.

La meta es demostrar el relevo real entre loops mediante *handoff packets*, validando que el State Fabric, el Event Log y el Dispatcher pueden sostener una cadena de ejecución sin pérdida de contexto y sin violar las políticas de autonomía.

## 3. Lo que NO es este Sprint

Para garantizar la seguridad y evitar el *autonomy creep*, este sprint opera bajo restricciones estrictas (Nivel A3 máximo):

1. **No es un runtime productivo:** No hay daemon, no hay scheduler persistente, no hay bucle infinito.
2. **No activa APIs reales:** El Oráculo opera en M1 (STATIC_CATALOG). No se desbloquea M2.
3. **No es una malla libre (Mesh):** Los loops no se llaman entre sí directamente. Toda comunicación pasa por el State Fabric (Handoff Packets) y es autorizada por el Dispatcher.
4. **No canoniza ni aprueba:** No se falsifica la firma T1 (`T1_SIGNED`) ni se cierran decisiones que requieren autoridad humana.

## 4. La Cadena de Ejecución

La secuencia inmutable de este sprint es:

1. **Oráculo de IAs:** Lee el catálogo estático y propone capacidades.
2. **Handoff 1:** Oráculo → Auditor.
3. **Loop Auditor:** Valida los outputs del Oráculo sin modificarlos.
4. **Handoff 2:** Auditor → Risk Classification.
5. **Risk Classification:** Aplica el overlay de riesgo (R0/A1) a las capacidades.
6. **Handoff 3:** Risk Classification → Unified Face.
7. **Unified Face:** Genera un resumen coherente para T1.

Cada paso de la cadena está gobernado por el Dispatcher y registrado de forma *append-only* en el Event Log.
