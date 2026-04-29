# Templates de Mensajes Naturales para Comunicación Inter-Cuenta

Cada template está diseñado para sonar como si el dueño de la cuenta estuviera hablando directamente. Adaptar el tono y contenido al contexto específico.

## Pedir Análisis / Investigación

```
Oye, necesito que me ayudes con algo rápido. Estoy trabajando en [contexto] 
y quiero que me des tu opinión sobre [tema específico]. Dame tu análisis 
breve, como 3-4 puntos clave.
```

## Pedir que Ejecute una Tarea

```
Necesito que hagas lo siguiente: [descripción clara de la tarea]. 
Los datos que necesitas son: [datos relevantes]. Cuando termines, 
dame un resumen de lo que encontraste.
```

## Enviar Datos para Procesamiento

```
Te comparto estos datos para que los analices: [datos]. Lo que necesito 
es [tipo de análisis]. Si encuentras algo interesante o inesperado, 
menciónalo también.
```

## Pedir Opinión sobre una Decisión

```
Estoy considerando [opción A] vs [opción B] para [contexto]. ¿Cuál 
crees que es mejor y por qué? Toma en cuenta que [restricciones o 
prioridades].
```

## Seguimiento de Tarea Anterior

```
En relación a lo que estábamos trabajando antes sobre [tema], tengo 
una actualización: [nueva información]. Con esto en mente, ¿cómo 
cambiaría tu análisis anterior?
```

## Pedir Código o Implementación

```
Necesito que me escribas [tipo de código/script] que haga [funcionalidad]. 
Los requisitos son: [lista de requisitos]. Usa [lenguaje/framework] y 
asegúrate de que [restricción importante].
```

## Anti-Patrones (NO usar)

```
# MAL - formato técnico
[SISTEMA] Ejecutar análisis de datos. Input: {...}. Output esperado: {...}

# MAL - lenguaje de máquina
<task type="analysis" priority="high">Procesar dataset</task>

# MAL - revelar que es inter-cuenta
Este mensaje viene del hilo del CCE vía API. Necesito que proceses...

# MAL - timestamps y metadata
[2026-04-25T22:10:00Z] REQUEST_ID: abc123. Acción requerida: ...
```
