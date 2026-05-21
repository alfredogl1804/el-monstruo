# RESTORE TEST RESULTS — Simulación Interna

**Fecha:** 2026-05-19 05:45 UTC
**Archivos usados para responder:**
- `00_INDEX.md`
- `13_DO_NOT_LOSE.md`
- `thread_value_state.json`
- `14_CONTEXT_RESTORE_TEST.md`

## Respuestas

1. **¿Qué es Sprint Factory v2 y cómo cambia la gestión de permisos?**
   → Transición a "permisos positivos" encapsulados por sprint, abandonando restricciones universales rígidas. PASS.

2. **¿Cuál es la diferencia entre una restricción universal y un permiso positivo por sprint?**
   → Restricción universal = "nunca toques main". Permiso positivo = "en este sprint puedes tocar main en ruta Y". PASS.

3. **¿Quién es el "arquitecto jefe" en el nuevo modelo de roles?**
   → ChatGPT-0. PASS.

4. **¿Bajo qué condición estricta puede Cowork ejecutar código?**
   → Si NO audita su propio trabajo. PASS.

5. **¿Cuál es el rol principal de SuperGrok?**
   → Contrarian P0/P1 (buscar fallas catastróficas). PASS.

6. **¿Qué rol asume Perplexity por defecto?**
   → Auditor externo técnico. PASS.

7. **¿Qué diferencia a un "Embrión Perito" de un embrión genérico?**
   → Acumula pericia validada en un dominio específico, no es genérico. PASS.

8. **¿Qué significa que los embriones acumulan "pericia" y no memoria bruta?**
   → Solo información validada (tests verdes, aprobación T1, auditoría) se convierte en pericia. Logs/chats no cuentan. PASS.

9. **¿Cuáles son los niveles de maduración de un embrión perito?**
   → M0 a M5. PASS.

10. **¿Qué es el "Oráculo de IAs"?**
    → Sistema para mapear capacidades emergentes de IA hacia aplicaciones prácticas. PASS.

11. **Explica el pipeline: Capability → Application → Power Stack → Sprint.**
    → Nueva función IA → caso de uso en El Monstruo → integración con herramientas existentes → sprint de implementación. PASS.

12. **¿Qué es el "Invisible Methodology Engine"?**
    → El Monstruo aplica metodologías (GTD, Eisenhower) internamente sin exponerlas al usuario. PASS.

13. **¿Por qué el usuario no debe ver las metodologías internas (ej. GTD)?**
    → Para eliminar fricción metodológica; el usuario interactúa en lenguaje natural. PASS.

14. **¿Qué es "AI-First Living" o "Servicio Silencioso"?**
    → El humano organiza para que la IA consuma y actúe; la IA es el lector primario. PASS.

15. **¿Cuál es el estado real del HITL Cockpit v0.3?**
    → Demo read-only local. NO es un control plane productivo. PASS.

16. **¿En qué estado se encuentra el Nightly Builder R1 y qué necesita para avanzar?**
    → Bloqueado. Necesita firma explícita T1. PASS.

17. **¿Qué es FORGE_v3.0 y qué problema resuelve?**
    → Síntesis de la Cura Dory. Resuelve la pérdida de contexto (Síndrome de Dory). PASS.

18. **Menciona 3 componentes de FORGE_v3.0.**
    → State Core, Recall, Sovereign Kill. PASS.

19. **¿Por qué es peligroso asumir que el Cockpit es un control plane productivo?**
    → Porque es un HTML estático sin POST, sin auth, sin persistencia. Asumir lo contrario causa fallas en cadena. PASS.

20. **¿Qué significa que las ideas en este atlas "no están canonizadas"?**
    → Son candidatos doctrinales o evidencia, no doctrina aprobada. No deben tratarse como reglas firmes. PASS.

## Resultado Final: **PASS — 20/20**
