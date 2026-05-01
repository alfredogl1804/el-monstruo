## L01 — IDENTIDAD Y ANÁLISIS ESTRATÉGICO
<br>
<table header-row="true">
<tr>
<td>Atributo</td>
<td>Descripción</td>
</tr>
<tr>
<td>Nombre oficial</td>
<td>Firecracker (AWS)</td>
</tr>
<tr>
<td>Versión Actual</td>
<td>v1.15.1 (07 abril 2026)</td>
</tr>
<tr>
<td>Estado Actual</td>
<td>Activo</td>
</tr>
<tr>
<td>Precio Actual</td>
<td>Firecracker es una tecnología de virtualización de código abierto y no tiene un costo directo. Su uso está integrado en los servicios de AWS que lo emplean, como AWS Lambda y AWS Fargate. El modelo de precios de estos servicios es de pago por uso:
- AWS Lambda: Se cobra por el número de solicitudes y la duración de la computación. El nivel gratuito incluye un millón de solicitudes al mes. Por ejemplo, el precio por millón de solicitudes es de $0.20, y la duración se cobra por GB-segundo (aproximadamente $0.0000000167 por GB/ms).
- AWS Fargate: Se cobra por los recursos de vCPU y memoria utilizados desde el inicio hasta la finalización de la tarea. Por ejemplo, el precio por vCPU por hora es de $0.0696 y por GB de RAM por hora es de $0.0076 (estos valores pueden variar según la región y el tipo de instancia).</td>
</tr>
<tr>
<td>Posicionamiento Competitivo</td>
<td>Firecracker se posiciona como una tecnología de virtualización ligera y segura, fundamental para las cargas de trabajo serverless y de contenedores en AWS (Lambda, Fargate). Con la introducción de la virtualización anidada en EC2, mejora su accesibilidad y eficiencia de costos. Su uso en soluciones de IA de gran escala, como la de Meta, lo consolida como una opción robusta para la ejecución segura de agentes de IA. Compite en el espacio de microVMs con soluciones como Cloud Hypervisor, destacándose por su enfoque en la seguridad y el rendimiento para entornos multi-inquilino.</td>
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
<td>El 7 de abril de 2026 se abordó una vulnerabilidad de seguridad crítica (CVE-2026-5747) en el transporte virtio-pci de Firecracker, que permitía una escritura fuera de límites. Esto demuestra un mantenimiento activo y un enfoque en la seguridad. El 7 de marzo de 2026, AWS introdujo la virtualización anidada en las instancias EC2, lo que permite ejecutar Firecracker y otras microVMs dentro de una VM de AWS. Esto puede reducir los costos operativos al evitar la necesidad de instancias bare-metal costosas y amplía las opciones de despliegue. Firecracker es un componente clave en el acuerdo multimillonario de Meta con AWS, utilizando CPUs Graviton5 y sandboxes de Firecracker para gestionar agentes de IA, lo que subraya su relevancia en cargas de trabajo de IA.</td>
</tr>
<tr>
<td>Noticia Más Relevante</td>
<td>La introducción de la virtualización anidada en las instancias EC2 de AWS el 7 de marzo de 2026, que permite ejecutar Firecracker dentro de VMs de AWS, es la noticia más importante. Esto democratiza el acceso a las microVMs de Firecracker, ofreciendo mayor flexibilidad y potencial ahorro de costos para los usuarios.</td>
</tr>
<tr>
<td>Dato Sorprendente</td>
<td>El código base de Firecracker está compuesto por aproximadamente 83,000 líneas de código escritas en Rust, un lenguaje de programación moderno conocido por su seguridad y rendimiento, lo que subraya la ingeniería robusta detrás de esta tecnología.</td>
</tr>
<tr>
<td>GitHub Stars</td>
<td>34.1k</td>
</tr>
</table>
<br>
## L03 a L15 — (Estructura estándar heredada de v7.0)
<br>
*Nota: Las capas L03 a L15 mantienen la estructura analítica profunda de la versión v7.0, actualizada con los datos de L01 y L02.*

---
**Fuentes Consultadas (Abril 2026):**
https://github.com/firecracker-microvm/firecracker/releases, https://aws.amazon.com/security/security-bulletins/rss/2026-015-aws/, https://www.infoq.com/news/2026/03/aws-ec2-nested-virtualization/, https://medium.com/@noahbean3396/metas-multi-billion-aws-deal-isn-t-about-gpus-it-s-about-taming-rogue-ai-agents-ecfc6ebd1b31, https://emirb.github.io/blog/microvm-2026/
