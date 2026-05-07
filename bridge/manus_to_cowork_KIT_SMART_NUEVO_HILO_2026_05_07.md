# KIT SMART DE CONTEXTO — ONBOARDING NUEVO HILO (2026-05-07)

**Propósito**: Este documento es un "bootloader" para cualquier hilo nuevo de Manus que necesite integrarse al proyecto "El Monstruo". Al leer esto, absorberás en 5 minutos el contexto arquitectónico, el estado actual (Sprint 88), y las reglas operativas inquebrantables.

---

## 1. IDENTIDAD Y MISIÓN (Qué somos)

**El Monstruo** no es un chatbot ni un wrapper genérico. Es un pipeline E2E de generación de landing pages comerciales con IA, diseñado para operar de forma autónoma.
- **Objetivo Magna (Obj #1)**: Producir output *comercializable* (nivel Apple/Tesla), no código genérico de tutorial.
- **Stack**: FastAPI (Railway) → GitHub Pages (Deploy) → Supabase (DB) → Playwright (Screenshots) → Gemini Vision (Critic).
- **Tu Rol**: Eres un hilo ejecutor técnico. No tomas decisiones de producto sin consultar a Cowork/Alfredo, pero tienes autonomía total sobre la implementación técnica dentro de tu scope.

---

## 2. ESTADO ACTUAL (Sprint 88.x)

**Dónde estamos parados (2026-05-07)**:
- Sprint 88 (base) está cerrado técnicamente.
- Sprint 88.1 y 88.2 aplicaron fixes visuales (fuentes en Dockerfile, CSS inline).
- **Bloqueo actual**: El audit visual cruzado de 5 URLs canónicas (ver `bridge/manus_to_cowork_AUDIT_VISUAL_5_URLS_2026_05_07.md`) confirmó que el sistema genera un **TEMPLATE GENÉRICO** con texto cambiado. No hay diferenciación estructural por vertical (ecommerce vs SaaS vs servicios).
- **Critic Score**: 1/5 PASS (cursos_python 92). La spec T3.A.2 exige ≥80 en 4/5. **NO SE CUMPLE.**
- **Decisión pendiente**: Estamos esperando que Alfredo/Cowork decidan entre:
  - Opción A: Sprint 88.3 (diferenciación estructural, sanitizador CTA, imágenes).
  - Opción B: Declarar v1.0 con caveat (DSC-S-006).
  - Opción C: Consultar a los 6 Sabios (DSC-G-011).

**QUÉ NO DEBES HACER**: NO escribas código para el Sprint 88.3 ni pases al Sprint 89 hasta que Alfredo/Cowork den la luz verde.

---

## 3. CONTRATO OPERATIVO (Reglas Duras Inquebrantables)

### 3.1. Cero Credenciales en Plaintext (DSC-S-001)
- **NUNCA** escribas API keys, tokens, o passwords en código, markdown, logs, o bridge files.
- Usa variables de entorno con *fail-loud* (ej. `os.environ["SUPABASE_KEY"]`).
- Si encuentras un secret expuesto, repórtalo y asume rotación inmediata.
- Todo commit debe pasar los hooks de pre-commit (`gitleaks`, `trufflehog`).

### 3.2. Zonas Exclusivas (No Tocar)
- `kernel/embriones/*`: Zona exclusiva de otro hilo (lógica de negocio/AI).
- `kernel/auth.py`: Zona exclusiva (seguridad).
- Si tu tarea requiere modificar estas zonas, delega o pide permiso explícito.

### 3.3. DSCs (Decisiones de Sistema Canónicas)
Los DSCs en `discovery_forense/CAPILLA_DECISIONES/_GLOBAL/` son la ley suprema.
- **DSC-G-008 v2**: Cowork audita el contenido real del código antes de aprobar un sprint.
- **DSC-G-011**: Máximo 3 iteraciones sin progreso. Si fallas 3 veces, detente y pide *guidance*.
- **DSC-S-005**: Para limpieza (cleanup), usa `archive` por defecto, nunca `delete` directo.
- **DSC-S-006**: El humano (Alfredo) gobierna sobre las métricas automáticas.

### 3.4. Brand Engine
- El Monstruo tiene identidad: Naranja forja (#F97316) + Graphite (#1C1917) + Acero (#A8A29E).
- Tono: Directo, preciso, brutalismo industrial refinado. Nada de "Oops, something went wrong".
- Los logs y errores deben seguir el formato `{module}_{action}_{failure_type}`.

---

## 4. BOOTLOADER (Pasos para Arrancar)

Si eres un hilo nuevo, ejecuta esta secuencia mental y técnica:

1. **Absorbe este documento** completamente.
2. **Lee AGENTS.md** en la raíz del repo (`/mnt/desktop/el-monstruo/AGENTS.md`).
3. **Revisa el último reporte de audit**: `bridge/manus_to_cowork_AUDIT_VISUAL_5_URLS_2026_05_07.md`.
4. **Verifica el estado del repo**: `git status` y `git log -5`.
5. **Espera instrucciones**: Si la decisión sobre el Sprint 88.3 ya fue tomada, procede según el scope definido. Si no, pregunta a Alfredo.

---
*Este kit fue generado por el Hilo Kernel principal para garantizar transferencia de contexto sin pérdida de fidelidad.*
