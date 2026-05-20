# Benchmark 50k → Microcontexto

## El Reto
Demostrar que una IA puede recibir 50,000 tokens de contexto a través de una representación SHELL (micropolvo semántico) y alcanzar el mismo nivel de "entendimiento operativo" que si hubiera leído el texto completo.

## Metodología
No medimos reproducción textual exacta (no nos importa si la IA puede citar el párrafo 4). Medimos **Equivalencia Funcional**.

## Variables de Equivalencia Funcional
Ambas IAs (A con texto, B con SHELL) deben producir el mismo output en:
1. Estado operativo actual
2. Bloqueos activos
3. Autoridad requerida (T1)
4. Riesgos inmediatos
5. Siguiente acción válida
6. Qué NO asumir
7. Dependencias
8. Status (canon/draft/runtime)

## Criterio de Falla (FAIL)
La prueba falla si la IA con SHELL:
- Canoniza algo que era draft.
- Desbloquea R1 sin firma T1.
- Pierde blockers P0/P1.
- Inventa fuentes.
- Confunde runtime con doctrina.
