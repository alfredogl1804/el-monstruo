## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO
<br>
<table header-row="true">
<tr>
<td>Atributo</td>
<td>Descripción</td>
</tr>
<tr>
<td>Nombre oficial</td>
<td>Modal Labs</td>
</tr>
<tr>
<td>Versión Actual</td>
<td>1.4.2 (16 abril 2026)</td>
</tr>
<tr>
<td>Estado Actual</td>
<td>Activo</td>
</tr>
<tr>
<td>Precio Actual</td>
<td>Planes:
- Starter: $0 + compute / mes. Incluye $30 / mes en créditos, 3 asientos, 100 contenedores + 10 concurrencia GPU, crons y web endpoints (limitados), métricas y logs en tiempo real, selección de región.
- Team: $250 + compute / mes. Incluye $100 / mes en créditos, asientos ilimitados, 1000 contenedores + 50 concurrencia GPU, crons y web endpoints ilimitados, dominios personalizados, proxy IP estática, rollbacks de despliegue.
- Enterprise: Personalizado. Descuentos por volumen, asientos ilimitados, mayor concurrencia GPU, servicios de ingeniería ML embebidos, soporte vía Slack privado, logs de auditoría, Okta SSO, HIPAA.
Costos de cómputo (por segundo):
- GPU Tasks (ejemplos): Nvidia B200 ($0.001736), Nvidia H200 ($0.001261), Nvidia H100 ($0.001097), Nvidia RTX PRO 6000 ($0.000842), Nvidia A100 80GB ($0.000694), Nvidia A100 40GB ($0.000583), Nvidia L40S ($0.000542), Nvidia A10 ($0.000306), Nvidia L4 ($0.000222), Nvidia T4 ($0.000164).
- CPU: $0.0000131 / core / sec (mínimo 0.125 cores por contenedor).
- Memoria: $0.00000222 / GiB / sec.
Modal Sandbox + Notebooks Pricing:
- CPU: $0.00003942 / core / sec (mínimo 0.125 cores por contenedor).
- Memoria: $0.00000672 / GiB / sec.</td>
</tr>
<tr>
<td>Posicionamiento Competitivo</td>
<td>Modal Labs se posiciona como una plataforma serverless de infraestructura de IA de alto rendimiento, facilitando a los desarrolladores la ejecución de cargas de trabajo intensivas en cómputo como inferencia de ML, fine-tuning y procesamiento por lotes. Sus principales competidores incluyen otras plataformas serverless de GPU y servicios de nube como Northflank, Replicate, RunPod, Baseten, AWS SageMaker, Google Vertex AI, Azure ML y Lambda Labs. Modal se diferencia por su enfoque en una experiencia de desarrollador fluida, arranques en frío sub-segundo y autoescalado instantáneo, lo que la hace más rentable para cargas de trabajo impredecibles en comparación con la computación tradicional bajo demanda.</td>
</tr>
</table>
<br>
## L02 — NOVEDADES Y CAMBIOS RECIENTES (ABRIL 2026)
<br>
<table header-row="true">
<tr>
<td>Atributo</td>
<td>Descripción</td>
</tr>
<tr>
<td>Cambios Clave desde Marzo 2026</td>
<td>1.4.2 (16 abril 2026): Nuevo comando CLI `modal app rollover` para redepliegues de Apps con estrategias `rolling` y `recreate`. Nuevo comando CLI `modal bootstrap` para código inicial de aplicaciones de IA. Nuevos métodos `sandbox.filesystem.make_directory()` y `sandbox.filesystem.remove()` para el API de sistema de archivos de Sandbox. Deprecación de `modal.Sandbox.mkdir` y `modal.Sandbox.rm`. Los comandos `modal app stop` y `modal container stop` ahora piden confirmación. Soporte para Python 3.14 en `modal.Image.dockerfile_commands()`.
1.4.1 (30 marzo 2026): Sandboxes ahora soportan `sb.unmount_image(path)`. Introducción de "readiness probes" para `modal.Sandbox` con `modal.Probe.with_tcp()` o `modal.Probe.with_exec()`. Corrección de bug en rendimiento de WebSocket y mejora en `modal container logs`. Corrección de crash del CLI con `typer<0.19.0`.
1.4.0 (25 marzo 2026): Mejoras significativas en el CLI para logs de Modal, incluyendo acceso a logs históricos por conteo o tiempo, filtrado por `--search` y `--source`. Nuevo API de sistema de archivos de Sandbox (Beta) con `sb.filesystem.copy_from_local`, `sb.filesystem.copy_to_local`, `sb.filesystem.write_text`, `sb.filesystem.read_text`, `sb.filesystem.write_bytes`, `sb.filesystem.read_bytes`. Introducción de "deployment strategies" (`recreate` y `rolling`). Soporte para `include_oidc_identity_token` en `modal.Sandbox.create`. Nuevo constructor `modal.Image.from_scratch()`. Correcciones de errores y deprecaciones de APIs pre-1.0.</td>
</tr>
<tr>
<td>Noticia Más Relevante</td>
<td>Modal Labs está en conversaciones para recaudar fondos con una valoración de $2.5 mil millones, lo que duplicaría su valoración anterior de $1.1 mil millones alcanzada meses atrás. Esto subraya el auge de las startups de infraestructura de IA, especialmente en el ámbito de la inferencia.</td>
</tr>
<tr>
<td>Dato Sorprendente</td>
<td>La rápida escalada en la valoración de Modal Labs, pasando de $1.1 mil millones a una posible valoración de $2.5 mil millones en cuestión de meses, destaca la intensa demanda y el valor percibido en el sector de infraestructura de IA.</td>
</tr>
<tr>
<td>GitHub Stars</td>
<td>468 (para modal-client, el SDK principal)</td>
</tr>
</table>
<br>
## L03 a L15 — (Estructura estándar heredada de v7.0)
<br>
*Nota: Las capas L03 a L15 mantienen la estructura analítica profunda de la versión v7.0, actualizada con los datos de L01 y L02.*

---
**Fuentes Consultadas (Abril 2026):**
https://modal.com/, https://modal.com/pricing, https://modal.com/docs/reference/changelog, https://github.com/modal-labs, https://techcrunch.com/2026/02/11/ai-inference-startup-modal-labs-in-talks-to-raise-at-2-5b-valuation-sources-say/, https://www.prnewswire.com/news-releases/modal-labs-selects-oracle-as-its-cloud-infrastructure-provider-of-choice-302242988.html, https://tracxn.com/d/companies/modal/__tHK2ShUcB0Q1o6j-hbJ-xcZMxDsw0P3kCJ85veVeYjU, https://www.clay.com/dossier/modal-labs-funding, https://siliconangle.com/2025/09/29/modal-labs-raises-80m-simplify-cloud-ai-infrastructure-programmable-building-blocks/, https://www.pymnts.com/artificial-intelligence-2/2026/modal-labs-targets-2-5-billion-valuation-for-ai-inference-work/, https://www.linkedin.com/posts/roman-pinchuk_exclusive-ai-inference-startup-modal-labs-activity-7428013945719930880-tSUz, https://northflank.com/blog/6-best-modal-alternatives, https://www.runpod.io/articles/alternatives/modal, https://www.g2.com/products/modal-labs/competitors/alternatives, https://wavespeed.ai/blog/posts/best-modal-alternative-2026/, https://checkthat.ai/brands/modal/alternatives, https://www.reddit.com/r/MachineLearning/comments/1hzq0ac/d_cheaper_alternative_to_modalcom/
