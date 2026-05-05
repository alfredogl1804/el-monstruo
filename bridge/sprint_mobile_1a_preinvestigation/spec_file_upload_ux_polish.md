# Sprint Mobile 1.A — File Upload + UX Polish · Pre-investigación

> **Autor:** Cowork (Hilo B)
> **Fecha:** 2026-05-05
> **Estado:** Spec firmado, listo para arranque INMEDIATO en paralelo con Sprint 87 (Ejecutor) y Sprint 86.7 (Catastro)
> **Sprint asignado:** Hilo Manus Memento
> **Dependencias:** ninguna externa — la app Flutter ya tiene `image_picker` + `file_picker` en pubspec.yaml
> **Cierra:** primer gap CRÍTICO de la app Flutter + 5 gaps de UX polish

---

## Política Cowork ratificada

> **Mientras Alfredo coordina activamente, NINGÚN hilo Manus entra en standby.**
> Sprint Mobile 1.A arranca **en paralelo** con Sprint 87 NUEVO E2E (Ejecutor) y Sprint 86.7 Catastro Macroárea 4. Cero colisión de archivos: zona del Memento es `apps/mobile/lib/`, las otras zonas son `kernel/e2e/*` y `kernel/catastro/*`.

---

## Contexto

La app Flutter es ~60% productiva. Bones excelentes (chat streaming, agent selector, dispatch end-to-end, foldable layout) pero tiene **3 gaps críticos puntuales**: GenUI, Voice, File Upload. Sprint Mobile 1.A cierra el más fácil de los 3 (File Upload) + 5 gaps de UX polish que están como TODOs específicos en el código.

Razón de priorizar 1.A primero:
- **NO requiere pre-requisitos externos** (los packages ya están en pubspec.yaml)
- Bloquea casos de uso simples: subir un PDF de tu negocio, una imagen de mockup, un docx para que el Monstruo lo procese
- UX polish da pulido inmediato visible

## Objetivo del Sprint

Cerrar el gap de file upload multimodal en el chat + 5 TODOs específicos de UX polish, dejando la app Flutter en estado donde Alfredo pueda subir cualquier archivo al Monstruo y recibir respuestas con UX pulida.

## Decisiones arquitectónicas firmes

### Decisión 1 — File Upload integrado en `ChatInput`

`apps/mobile/lib/features/chat/widgets/chat_input.dart` (o equivalente) gana un botón attachment con menú:
- 📷 Cámara (image_picker)
- 🖼️ Galería (image_picker)
- 📄 Archivo (file_picker, soporta PDF, docx, txt, code, csv, xlsx)

Múltiples archivos a la vez (hasta 5 simultáneos para no saturar el WebSocket).

### Decisión 2 — Protocolo de envío al kernel

Archivos se suben en 2 fases para no saturar WebSocket:

1. **Upload HTTP REST:** `POST /v1/files/upload` con multipart/form-data → kernel devuelve `file_id`
2. **Mensaje WS:** el chat envía mensaje normal con `attachments: [file_id_1, file_id_2]` en payload

El kernel resuelve `file_id` → contenido cuando el LLM o el agente lo necesita.

**Si el endpoint REST `/v1/files/upload` no existe en el kernel:** el spec del Memento incluye crearlo (~30 min). Tabla nueva `kernel_files` con `id, filename, content_type, size_bytes, storage_path, uploaded_at`.

### Decisión 3 — Preview thumbnails antes de enviar

El usuario ve thumbnails de los archivos seleccionados ANTES de mandar el mensaje (con botón × para descartar). Imagen → thumbnail real. PDF/docx/etc → ícono de tipo + nombre.

### Decisión 4 — UX polish: 5 TODOs específicos cerrados

| TODO | Archivo / línea | Comportamiento esperado |
|---|---|---|
| Embrion directive → kernel | `embrion_panel.dart:316` | Botón "Enviar directiva" hace `POST /v1/embrion/directive` con texto |
| Regenerate message | `message_bubble.dart:379` | Botón regenerate dispara mensaje con `regenerate=true` para retomar último prompt |
| File download | `file_viewer.dart:112` | Botón download usa `path_provider` + `share_plus` para guardar en device |
| Settings persistence | `settings_screen.dart:67` | Feature flags se persisten en `SharedPreferences`, hidratación al boot |
| Error toasts | global | Cualquier error de red / API muestra `SnackBar` con retry button + reason |

### Decisión 5 — Capa Memento aplicada a uploads

Operations registradas:
- `kernel_file_upload` — antes de aceptar el upload (preflight valida tamaño max 25MB + content-type whitelist)
- `kernel_file_attach_to_message` — antes de adjuntar al mensaje WebSocket

Si preflight falla (archivo muy grande, content-type no permitido) → toast claro al usuario con razón.

### Decisión 6 — Brand DNA en error UX

Toasts de error usan paleta El Monstruo:
- Background: `#1C1917` (graphite)
- Border: `#F97316` (forja)
- Texto: `#A8A29E` (acero)
- Tipo de error en formato `{módulo}_{action}_{failure_type}` legible al usuario

## Bloques del Sprint

### Bloque 1 — Endpoint `/v1/files/upload` en kernel (si no existe) (30-45 min)
- Verificar si existe; si no, crearlo con multipart/form-data
- Tabla `kernel_files` migration 026 si no existe
- Tests unitarios del endpoint
- Storage local en kernel (volumen Railway) con cleanup automático >7d

### Bloque 2 — File Picker integrado en ChatInput (45-60 min)
- Botón attachment con menú modal (cámara + galería + archivo)
- Soporta múltiples (max 5)
- Preview thumbnails con descarte individual
- iOS / macOS permissions pre-flighted con plist actualizado

### Bloque 3 — Upload HTTP + adjuntar a mensaje WS (30-45 min)
- Service `kernel_files_service.dart` con `uploadFile(file) → file_id`
- ChatNotifier acepta `attachments` en `sendMessage()`
- Loading indicator por archivo durante upload

### Bloque 4 — UX polish (5 TODOs cerrados) (60-90 min)
- Embrion directive (botón + POST /v1/embrion/directive)
- Regenerate message (botón + regenerate=true en payload)
- File download (path_provider + share_plus)
- Settings persistence (SharedPreferences hydration)
- Error toasts globales con retry y razón legible

### Bloque 5 — Capa Memento + tests (30-45 min)
- 2 operations registradas en catálogo
- Tests widget de cada flujo (upload, attach, download, regenerate, embrion directive)
- Smoke productivo: subir 1 PDF + 1 imagen, recibir respuesta del Monstruo con ambos referenciados

### Bloque 6 — Bridge + reporte cierre (15-20 min)
- `bridge/MOBILE_1A_OPERATIONAL_GUIDE.md`
- Reporte de cierre en `bridge/manus_to_cowork.md` con `file_append` (NO heredoc — semilla 40 aplicada)

## ETA total recalibrada

6 bloques × ~40 min promedio = **3.5-5 horas reales**.

Si el patrón Sprint 86.5 → 86.6 → 86.4.5 B2 se mantiene, podríamos ver cierre en **2.5-3.5h**.

## Métricas de éxito

| Métrica | Target |
|---|---|
| Subir 1 PDF + 1 imagen + 1 docx en un mensaje | ✅ |
| Embrion directive funcional | ✅ |
| Regenerate message funcional | ✅ |
| File download al device | ✅ |
| Settings persistence al recargar app | ✅ |
| Error toasts con retry visible al desconectar Wi-Fi mid-chat | ✅ |
| Tests widget acumulados | ≥ 15 PASS |
| Suite kernel sin regresión | 453+ PASS |

## Disciplina obligatoria

- Capa Memento en upload + attach
- Brand DNA en error toasts (paleta forja + graphite + acero)
- Anti-Dory: stash → pull rebase → pop antes de cada commit
- Standby: ninguno mientras Alfredo activo
- NO heredoc al bridge (semilla 40 aplicada)
- Tests widget como mínimo (no bloquear cierre por suite full)

## Zona primaria

```
apps/mobile/lib/features/chat/widgets/chat_input.dart (modificación)
apps/mobile/lib/features/chat/widgets/message_bubble.dart (regenerate)
apps/mobile/lib/features/files/file_viewer.dart (download)
apps/mobile/lib/features/embrion/embrion_panel.dart (directive)
apps/mobile/lib/features/settings/settings_screen.dart (persistence)
apps/mobile/lib/services/kernel_files_service.dart (NUEVO)
apps/mobile/lib/services/error_toast_service.dart (NUEVO)
apps/mobile/lib/providers/chat_provider.dart (attachments support)
apps/mobile/test/widgets/chat_input_test.dart (NUEVO)
apps/mobile/test/services/kernel_files_service_test.dart (NUEVO)
kernel/files/routes.py (NUEVO si no existe)
scripts/026_sprint_mobile_1a_files_schema.sql (NUEVO si tabla no existe)
bridge/MOBILE_1A_OPERATIONAL_GUIDE.md (NUEVO)
```

## NO TOCÁS

- `apps/mobile/lib/features/genui/*` (zona Sprint Mobile 1.B, espera A2UI spec)
- `apps/mobile/lib/services/voice_service.dart` (zona Sprint Mobile 1.C, espera iOS setup)
- `kernel/catastro/*` (zona Sprint 86.7 Catastro)
- `kernel/e2e/*` (zona Sprint 87 Ejecutor)
- `kernel/memento/*` (zona cerrada)
- `kernel/embriones/*` (zona Sprint 88, solo invocás el endpoint directive existente)

## Conexión cross-sprint

| Sprint | Cómo se conecta |
|---|---|
| Sprint 87 NUEVO E2E (Ejecutor) | Cuando el pipeline produce URLs vivas, el `file_viewer` puede descargarlas. Cuando Alfredo sube un PDF de su negocio, el pipeline lo recibe via `attachments` y lo procesa. |
| Sprint Mobile 1.B (GenUI) | El sistema de attachments queda listo para que el GenUI pueda renderizar PDFs / imágenes inline. |
| Sprint Mobile 1.C (Voice) | El error toast service queda como infraestructura compartida. |

## Próximo sub-sprint después

Sprint Mobile 1.B — GenUI / A2UI Rendering. Espera firma del A2UI spec por Alfredo + Cowork.

— Cowork (Hilo B)
