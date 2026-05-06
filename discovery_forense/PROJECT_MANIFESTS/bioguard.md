# BIOGUARD BioGuard — Manifest para Cowork

Slug: bioguard
Categoría: 🟠 En Diseño (corregida desde "Nominal" tras recuperación de hallazgos Fase II)
Última actualización: 2026-05-06
Generado por: Manus map paralelo + corrección post-recuperación Fase II

> ⚠️ **Cambio de categoría:** Este proyecto estaba marcado como "Nominal" en la primera versión del manifest. La recuperación de hallazgos Fase II (ver `_HALLAZGOS_FASE_II_RECUPERADOS.md` sección 7) confirmó que **tiene definición técnica clara documentada en 4 fuentes**, lo que lo recategoriza a "En Diseño".

## 1. Definición canónica (recuperada de Fase II)

**BioGuard es una app + dispositivo para detección rápida de drogas en muestras biológicas** (saliva, hisopo dérmico, opción sangre capilar). El objetivo es construir un **prototipo de diagnóstico semicuantitativo** para uso en consumo personal o revisión clínica.

A diferencia de otros proyectos del portfolio que solo aparecen como mención nominal en el SOP, BioGuard cuenta con **definición técnica documentada en 4 fuentes auditadas**, aunque carece de spec de ingeniería operativo, prototipo físico o roadmap fechado.

El proyecto se categoriza como "En Diseño" porque tiene visión clara pero aún no tiene plan de construcción, BOM (Bill of Materials), validación regulatoria, ni decisión de stack técnico.

## 2. Estado actual

| Métrica | Estado |
|---|---|
| Fase | 🟠 En Diseño (definición clara, sin spec/roadmap) |
| Vertical | Healthtech / Diagnóstico in vitro (IVD) |
| Mercado objetivo | Consumo personal + revisión clínica (mercado mexicano probable) |
| Stack técnico | Por definir (app móvil + hardware lector) |
| Modelo de negocio | Por confirmar (B2C app freemium / B2B clínicas / kit retail) |
| Última actividad documentada | Mención en `02_CLAUDE_AUDITORIA.md` y `MANUS_10_CORPUS_COMPLETO_SOP_EPIA.md` |

## 3. Ubicaciones canónicas (dónde vive el conocimiento)

| Fuente | Ubicación | Cómo accederla desde Cowork |
|---|---|---|
| Skill | — | No aplica (aún) |
| Repo GitHub | — | No aplica (aún) |
| Drive (definición técnica) | `02_CLAUDE_AUDITORIA.md`, `02a_CLAUDE_PARTE1.md`, `repaldo sop v3 181025.txt`, `MANUS_10_CORPUS_COMPLETO_SOP_EPIA.md` | `gws drive files list --params '{"q":"name contains \"CLAUDE_AUDITORIA\""}'` |
| Drive (cobertura general) | 4 archivos / 1 plan-like (solo SOP) | Buscar "BioGuard" en Drive |
| Notion | 43 páginas / **0 plan-like dedicado** | `manus-mcp-cli tool call notion-search --input '{"query":"BioGuard"}'` |
| Dropbox | Mención contextual en respaldos SOP | grep en `discovery_forense/raw_text/dropbox/normalized_md/` |
| S3 | — | No aplica |

## 4. Decisiones / pendientes clave (top 5)

1. **Validación regulatoria mexicana**: Determinar si BioGuard requiere registro COFEPRIS como dispositivo médico Clase I o II. (Estado: Pendiente, Bloqueante: Sí, Impacto: Crítico)
2. **Decisión de hardware**: Definir si el lector es propio (R&D + manufactura) o leverage de tiras reactivas existentes con app de lectura por cámara. (Estado: Pendiente, Bloqueante: Sí, Impacto: Alto)
3. **Substrato biológico inicial**: Confirmar si el MVP arranca con saliva (más fácil), hisopo dérmico (intermedio) o sangre capilar (más difícil pero más preciso). (Estado: Pendiente, Bloqueante: Sí, Impacto: Alto)
4. **Modelo de negocio**: Decidir entre venta de kit retail, app freemium, suscripción B2B clínicas, o combinación. (Estado: Pendiente, Bloqueante: Medio, Impacto: Alto)
5. **Auditoría exhaustiva de las 43 páginas Notion**: Extraer toda la información técnica y de mercado dispersa para consolidar en spec único. (Estado: Pendiente, Bloqueante: No, Impacto: Medio)

## 5. Próximos pasos sugeridos para Cowork

1. **Crear página `📜 BioGuard — Spec Maestro v1.0` en Notion** consolidando los 4 documentos Drive + las 43 páginas Notion en un spec único estructurado (problema, mercado, MVP, hardware, app, regulación, modelo de negocio, riesgos).
2. **Investigar landscape competitivo MX** vía sabios v7.3 con focus en COFEPRIS + dispositivos IVD existentes (Quick Test Mexico, Drug Test MX, Saliva-based testing 2026).
3. **Decidir hardware vs software-first**: consultar 6 sabios sobre viabilidad de leverage de tiras reactivas existentes con app de visión computacional.
4. **Crear repo `alfredogl1804/bioguard-platform`** (privado) con README inicial y estructura para dual track (mobile-app + hardware).

## 6. Riesgos / notas críticas

- **Riesgo regulatorio alto**: Dispositivos médicos en México requieren registro COFEPRIS, proceso largo (12-18 meses) y costoso ($USD 5K-30K).
- **Riesgo de manufactura**: Si se opta por hardware propio, requiere capital inicial significativo y supply chain validado.
- **Asimetría de documentación**: 43 páginas Notion (mucha) vs 4 archivos Drive (poca) sin plan-like dedicado en Notion. Indica brainstorming abundante sin consolidación.
- **Sensibilidad social**: Producto de detección de drogas tiene componente reputacional — comunicación cuidadosa.

## 7. Cross-links a otros proyectos del portfolio

- **El Monstruo (orquestador)**: BioGuard puede ser fabricado por El Monstruo como uno de los productos del portfolio (junto con CIP).
- **SOP Histórico**: Relación de origen (mencionado en `repaldo sop v3 181025.txt`).
- **CIES**: Posible adyacencia si CIES tiene componente healthtech (validar).
- **Vivir Sano**: Adyacencia clara — ambos son healthtech. Posible sinergia o canibalización.

## 8. Fuentes que canonizan este manifest

- `discovery_forense/PROJECT_MANIFESTS/_HALLAZGOS_FASE_II_RECUPERADOS.md` (sección 7)
- `discovery_forense/raw_text/dropbox/normalized_md/02_CLAUDE_AUDITORIA.md` (definición técnica)
- `discovery_forense/raw_text/dropbox/normalized_md/MANUS_10_CORPUS_COMPLETO_SOP_EPIA.md` (mención cruzada)
