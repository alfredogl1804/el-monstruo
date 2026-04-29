# Ángulo: Infraestructura, Fierros y Hardware a Escala

Este documento desglosa las especificaciones exactas de hardware (CPU, RAM, GPU, Almacenamiento) necesarias para operar CIP y El Monstruo a diferentes escalas. Los datos se basan en costos reales de mercado y especificaciones técnicas a abril de 2026 [1] [2] [3].

A diferencia de una red social, CIP procesa transacciones financieras (donde la consistencia de la base de datos es crítica) y genera visualizaciones pesadas (donde el almacenamiento y ancho de banda son críticos). El Monstruo, como orquestador de agentes, es intensivo en CPU y RAM, pero no requiere GPU local ya que se conecta a APIs externas.

## 1. Desglose de Cargas de Trabajo (Workloads)

Antes de definir servidores, debemos entender qué hace cada parte del sistema y qué recursos consume:

| Carga de Trabajo | Rol en el Ecosistema | Cuello de Botella Principal | Requerimiento Crítico |
|------------------|----------------------|-----------------------------|-----------------------|
| **Base de Datos (PostgreSQL)** | Registro inmutable de tokens, balances, usuarios. | **IOPS (Discos) y RAM** | Discos NVMe Enterprise, mucha RAM para `shared_buffers` [4]. |
| **El Monstruo (LiteLLM/LangGraph)** | Orquestación de agentes, proxy de IA, memoria. | **CPU y RAM** | CPUs de alta frecuencia, RAM para mantener contexto [5]. |
| **Nodos Blockchain** | Validación de transacciones on-chain (ej. Polygon). | **CPU y Storage** | Discos NVMe rápidos, CPU multicore [6]. |
| **Almacenamiento Media** | Renders, imágenes de propiedades, catálogos. | **Ancho de Banda** | CDN Global (Cloudflare R2) para evitar *egress fees* [7]. |

## 2. Especificaciones de Hardware por Nivel de Escala

A continuación se detallan los "fierros" exactos que se necesitan en cada nivel, asumiendo que a partir del Nivel 3 se comienza a repatriar infraestructura (*Cloud Exit*) hacia servidores dedicados (ej. Hetzner o Colocation) [8].

### Nivel 1 y 2: El Arranque y la Tracción (1 a 100,000 Usuarios)

En esta etapa, **NO se recomienda comprar ni rentar servidores dedicados**. La infraestructura debe ser 100% Serverless/PaaS (Vercel, Supabase, Railway) para priorizar la velocidad del equipo [9].

Sin embargo, si se decidiera auto-alojar (Self-Host) por motivos de soberanía prematura, estos serían los fierros mínimos:

*   **Servidor Único (Todo en uno):** Equivalente a Hetzner AX41-NVMe [1].
    *   **CPU:** AMD Ryzen 5 3600 (6 cores / 12 threads @ 3.6 GHz).
    *   **RAM:** 64 GB DDR4.
    *   **Almacenamiento:** 2x 512 GB NVMe SSD (RAID 1).
    *   **Costo:** ~€38.40 / mes.

### Nivel 3: El Crecimiento Acelerado (100,000 a 1 Millón de Usuarios)

Aquí los costos de la nube pública (especialmente la base de datos y el orquestador) comienzan a doler. Es el momento de migrar el *Core* a servidores dedicados de alto rendimiento [8].

**Cluster de Servidores Dedicados (Ej. Hetzner AX/EX Line):**

1.  **Servidor de Base de Datos (PostgreSQL/Supabase Self-Hosted):**
    *   **Modelo:** Hetzner AX102 [1].
    *   **CPU:** AMD EPYC 7443P (24 cores / 48 threads @ 2.85 GHz).
    *   **RAM:** 128 GB DDR4 ECC (Error Correction Code, vital para bases de datos).
    *   **Almacenamiento:** 2x 1.92 TB NVMe SSD Datacenter Edition.
    *   **Costo:** ~€130 / mes.
2.  **Servidores del Monstruo (Orquestación, LiteLLM Proxy, LangGraph):**
    *   **Modelo:** 2x Hetzner EX44 (Balanceo de carga) [1].
    *   **CPU:** Intel Core i5-13500 (14 cores / 20 threads @ 2.5 GHz).
    *   **RAM:** 64 GB DDR4 por servidor.
    *   **Almacenamiento:** 2x 512 GB NVMe SSD Gen4.
    *   **Costo:** ~€88 / mes total (2 servidores).
3.  **Nodo Blockchain (Polygon Full Node):**
    *   **Requerimientos:** 16 cores, 64 GB RAM, 6 TB NVMe [6].
    *   **Modelo:** Hetzner AX52 (expandido) o similar.
    *   **Costo:** ~€60 - €80 / mes.

**Total Hardware Nivel 3:** ~$350 - $400 USD / mes.

### Nivel 4: La Escala Global (1 Millón a 100 Millones de Usuarios)

A este nivel, rentar servidores dedicados en Hetzner ya no es suficiente por cuestiones de redundancia geográfica y control absoluto de la red. Es el momento del *Colocation* (comprar hardware propio y alojarlo en centros de datos de terceros) [8].

**Hardware Propio (Colocation - Rack de 42U):**

1.  **Cluster de Base de Datos Principal (Master + 2 Replicas):**
    *   **Modelo:** 3x Dell PowerEdge R660 (1U) [2].
    *   **CPU:** Dual Intel Xeon Platinum (32+ cores por procesador).
    *   **RAM:** 512 GB DDR5 ECC por servidor. (A esta escala, PostgreSQL necesita mucha RAM para mantener los índices en memoria [4]).
    *   **Almacenamiento:** 4x 3.2 TB Enterprise NVMe U.2 (RAID 10).
    *   **Inversión de Capital (CapEx):** ~$15,000 - $20,000 USD por servidor.
2.  **Cluster del Monstruo (Kubernetes Workers):**
    *   **Modelo:** 5x Dell PowerEdge R660 [2].
    *   **CPU:** Dual AMD EPYC 9004 Series (Enfoque en densidad de cores).
    *   **RAM:** 256 GB DDR5 por servidor.
    *   **Almacenamiento:** 2x 1.92 TB NVMe (Para logs locales y caché).
    *   **Inversión de Capital (CapEx):** ~$10,000 USD por servidor.
3.  **Nodos Blockchain y RPC:**
    *   **Requerimientos (Peor caso - Solana RPC):** AMD EPYC F-Series (Alta frecuencia), 1 TB RAM, 4+ TB NVMe Enterprise [3].
    *   **Inversión de Capital (CapEx):** ~$12,000 USD por nodo.

**Costos Operativos (OpEx) Nivel 4:**
*   Renta de espacio en Data Center (1 Rack, 10kW): ~$1,500 - $2,500 USD / mes.
*   Tránsito de Red (Dark Fiber / Uplinks de 10Gbps): ~$1,000 - $2,000 USD / mes.

### Nivel 5: La Escala Civilizatoria (100 Millones a 1,000 Millones de Usuarios)

A esta escala, la infraestructura se convierte en un activo estratégico. La arquitectura debe distribuirse en múltiples continentes (Multi-Region Active-Active) para garantizar latencia cero y cumplimiento regulatorio local (Data Sovereignty).

**Hardware y Arquitectura (Basado en modelos de Telegram y Discord):**

*   **Red de Data Centers Propios:** En lugar de un solo proveedor de Colocation, CIP operaría *Points of Presence* (PoPs) en Norteamérica, Europa, Asia y Latinoamérica.
*   **Servidores de Almacenamiento Masivo:** Cientos de servidores de alta densidad (ej. Dell PowerEdge R760) con Petabytes de almacenamiento NVMe distribuido (Ceph o similar) para el historial inmutable de transacciones y documentos legales [2].
*   **GPUs Propias (Opcional):** Solo en este nivel, si el costo de las APIs de IA externas (OpenAI, Replicate) supera el costo de amortización del hardware, se justificaría la compra de clusters de GPUs (NVIDIA H100/B200) para ejecutar modelos Open Source propios. Un servidor con 8x H100 cuesta aproximadamente $300,000 USD, y su *breakeven* frente a la nube se alcanza en unos 6-8 meses a carga máxima [10].

## 3. Resumen de Reglas de Hardware para CIP

1.  **RAM sobre CPU para la Base de Datos:** PostgreSQL a escala requiere que los índices vivan en memoria. Un servidor con 512 GB de RAM y CPUs promedio rendirá mejor que uno con 64 GB de RAM y los mejores CPUs del mercado [4].
2.  **NVMe Enterprise es Innegociable:** Los discos SSD SATA o NVMe de consumo (Consumer grade) morirán en meses bajo la carga de escrituras constantes de una base de datos financiera. Se deben usar discos Enterprise con alto TBW (Terabytes Written) [3].
3.  **El Monstruo es CPU-Bound:** LiteLLM y LangGraph requieren CPUs rápidos y muchos cores para manejar la concurrencia de miles de agentes y llamadas a APIs simultáneas [5].
4.  **Cero GPUs Locales (Al Principio):** Comprar GPUs para renders o inferencia antes del Nivel 5 es un error financiero. Las APIs son infinitamente más baratas y no requieren mantenimiento.

---

### Referencias

[1] Hetzner. (2026). *Find cheap dedicated servers with AMD & Intel CPUs*. https://www.hetzner.com/dedicated-rootserver/
[2] Dell. (2026). *Dell PowerEdge R660 vs R760 Rack Servers*.
[3] Earnpark. (2026). *Solana Node Setup: Cost, Hardware & ROI in 2026*.
[4] Zignuts. (2025). *PostgreSQL Performance Tuning: Essential 2026 Expert Guide*.
[5] LiteLLM. (2026). *Best Practices for Production*. https://docs.litellm.ai/docs/proxy/prod
[6] Polygon. (2025). *How to Run a Polygon Node: Requirements*.
[7] Cloudflare. (2026). *Cloudflare R2 vs AWS S3 | Review Pricing & Features*.
[8] Heinemeier Hansson, D. (2024). *Our cloud-exit savings will now top ten million over five years*.
[9] Reddit r/devops. (2025). *What does the cloud infrastructure costs at every stage of startup look like?*
[10] Spacelift. (2026). *Cloud vs On-Premise: Cost Comparison for 2026*.
