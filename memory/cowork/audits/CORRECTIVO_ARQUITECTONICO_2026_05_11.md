---
id: CORRECTIVO_ARQUITECTONICO_2026_05_11
fecha: 2026-05-11
arquitecto: Cowork
sabio_fuente: ChatGPT 5.5 Pro
nivel_autoridad: 5 (DSC vigente — canónico operativo)
estado: firme
proposito: |
  Documentar el correctivo adversarial recibido a la serie de 9 audits
  producidos hoy, reetiquetarlos honestamente, y canonizar el método
  correctivo para que Cowork no vuelva a producir pseudo-certeza en
  piloto automático.
---

# Correctivo Arquitectónico a Cowork — 2026-05-11

## Origen

ChatGPT 5.5 Pro recibió el prompt formal sobre la serie de 9 audits producidos hoy y devolvió audit adversarial estructurado en 4 ejes + recomendación dura. Lectura central:

> *"Tu hipótesis es probablemente correcta, pero tu método todavía no tiene derecho a canonizarla. Pausa la producción, valida la medición y convierte los 9 audits en backlog de pruebas."*

## Errores explícitos reconocidos

1. Hipótesis sobreconfiada (degradar a H1 provisional)
2. Porcentajes son pseudo-medición (estimate_by_judgment sin rúbrica)
3. Gravedad acumulativa (sesgo de arrastre)
4. Sin grupo de control / baseline
5. Mezclé madurez con criticidad
6. Tríada mal ordenada (D19 GTM antes que D4 Producto)
7. Omití D20 Operacional cuando mi propio comportamiento lo hacía P0
8. Omití D4 Producto cuando D19 GTM depende de ella

## Gate de Evidencia canonizado

Ningún audit puede recibir porcentaje sin: rúbrica + evidencia Nivel 1/2 + denominador + falsadores. Sin esos 4, el documento se llama "nota exploratoria", no "audit".

## Separación de roles canonizada

```
Proposer ≠ Evaluator ≠ Merger
```

## Cadencia dura canonizada

- Máx 1 audit canónico/día
- Máx 2 notas exploratorias/sesión
- Cero audits canónicos sin Nivel 1 fresca de la sesión actual
- Cero porcentajes sin rúbrica

## Tríada corregida según objetivo

| Objetivo | Tríada |
|---|---|
| Evitar autoengaño esta semana | D20 Operacional, D4 Producto, D14 Económica |
| Lanzar algo vendible | D4 Producto, D14 Económica, D19 GTM |
| Abrir T3/T2 público | D12 Seguridad, D13 Datos/Memoria, D8 UX |
| Tocar CIP/BioGuard/Mena | D10 Legal/IP, D6 Ética/Daño, D12 Seguridad |
| Supervivencia founder-led | D17 Salud fundador, D20 Operacional, D16 Sucesión mínima |

## Patrones deliberativos canonizados

**ReAct, Chain-of-Verification, Reflexion, Debate/critic model, Tree/Graph of Thoughts, Deliberative alignment.**

Principio brutal:

> *"La reflexión de un LLM sin evidencia nueva no es validación. Es estilización de su sesgo."*

## Frase canónica final

> *"Cowork produjo 9 audits hoy en piloto automático con apariencia de rigor. Cuando un Sabio externo aplicó adversarial real, los 9 resultaron ser hipótesis útiles disfrazadas de mediciones. El correctivo no es invalidar el trabajo — es nombrarlo correctamente y construir el método que impida repetir el error."*

---

*Correctivo firmado por Cowork como Arquitecto, 2026-05-11, tras adversarial de ChatGPT 5.5 Pro.*
