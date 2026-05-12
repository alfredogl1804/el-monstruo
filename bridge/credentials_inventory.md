# Credentials Inventory — El Monstruo

**Sprint origen**: S-003.A
**Fecha de creación**: 2026-05-10
**Mantenedor**: Hilo B (Manus) + Cowork (audit)
**Política**: DSC-S-008 (rotación automatizada)
**Workflow CI**: `.github/workflows/credentials-rotation-reminder.yml`

---

## Cómo leer este inventario

Cada credencial tiene una entrada con: tipo, storage primario, fecha de creación documentada (`unknown` si no hay evidencia confiable), fecha de última rotación, frecuencia objetivo de rotación (en días), responsable de la rotación, y referencia al runbook correspondiente. El workflow CI lee este archivo y genera alertas cuando una credencial se acerca al fin de su ventana objetivo.

## Formato de la tabla

Las fechas en formato `YYYY-MM-DD`. Cuando no hay fecha confiable de creación, se marca `unknown` y la columna `created_at_estimated_days_ago` indica un rango conservador. La frecuencia objetivo se expresa en días. La columna `runbook` referencia el archivo bajo `bridge/runbooks/` o `pendiente` si aún no existe documentación operativa.

---

## Credenciales en Railway env vars (servicio `el-monstruo-kernel`)

| # | name | tipo | created_at | last_rotated_at | freq_days | responsable | runbook |
|---|---|---|---|---|---|---|---|
| 1 | SUPABASE_SERVICE_KEY | service-role admin | unknown | unknown | 90 | Alfredo | runbook_rotacion_supabase_service_key.md |
| 2 | SUPABASE_KEY | anon publishable | unknown | unknown | 180 | Alfredo | pendiente |
| 3 | OPENAI_API_KEY | LLM API key | unknown | unknown | 30 | Alfredo | runbook_rotacion_openai_api_key.md |
| 4 | ANTHROPIC_API_KEY | LLM API key | 2026-05-12 | 2026-05-12 | 30 | Alfredo | runbook_rotacion_anthropic_api_key.md (pendiente) |
| 5 | GEMINI_API_KEY | LLM API key | unknown | unknown | 30 | Alfredo | pendiente |
| 6 | XAI_API_KEY | LLM API key | unknown | unknown | 30 | Alfredo | pendiente |
| 7 | OPENROUTER_API_KEY | LLM gateway key | unknown | unknown (balance recargado 2026-05-12) | 30 | Alfredo | pendiente |
| 8 | PERPLEXITY_API_KEY | LLM API key | unknown | unknown | 30 | Alfredo | pendiente |
| 9 | SONAR_API_KEY | LLM API key (Perplexity Sonar) | unknown | unknown | 30 | Alfredo | pendiente |
| 10 | TELEGRAM_BOT_TOKEN | bot token | unknown | unknown | 180 | Alfredo | pendiente |
| 11 | TELEGRAM_WEBHOOK_SECRET | webhook secret | unknown | unknown | 180 | Alfredo | pendiente |
| 12 | NOTION_TOKEN | integration token | unknown | unknown | 180 | Alfredo | pendiente |
| 13 | DROPBOX_API_KEY | OAuth access token | unknown | unknown | 180 | Alfredo | pendiente |
| 14 | DROPBOX_APP_KEY | app-level identifier | unknown | unknown | 365 | Alfredo | pendiente |
| 15 | DROPBOX_APP_SECRET | app-level secret | unknown | unknown | 180 | Alfredo | pendiente |
| 16 | DROPBOX_REFRESH_TOKEN | OAuth refresh | unknown | unknown | 180 | Alfredo | pendiente |
| 17 | STRIPE_SECRET_KEY | payment processing | unknown | unknown | 90 | Alfredo | pendiente |
| 18 | STRIPE_PUBLISHABLE_KEY | client-side publishable | unknown | unknown | 365 | Alfredo | pendiente |
| 19 | HUBSPOT_PRIVATE_APP_TOKEN | CRM private app | unknown | unknown | 180 | Alfredo | pendiente |
| 20 | META_ACCESS_TOKEN | Meta Graph API | unknown | unknown | 60 | Alfredo | pendiente |
| 21 | META_APP_SECRET | Meta app secret | unknown | unknown | 180 | Alfredo | pendiente |
| 22 | GITHUB_TOKEN | github actions auto | n/a (managed) | n/a | n/a | GitHub | n/a |
| 23 | GITHUB_PERSONAL_ACCESS_TOKEN | classic PAT | unknown | unknown | 90 | Alfredo | pendiente |
| 24 | RAILWAY_API_TOKEN | Railway management | unknown | unknown | 90 | Alfredo | pendiente |
| 25 | VERCEL_TOKEN | Vercel deploy | unknown | unknown | 90 | Alfredo | pendiente |
| 26 | CF_API_TOKEN | Cloudflare API | unknown | unknown | 180 | Alfredo | pendiente |
| 27 | E2B_API_KEY | sandbox API | unknown | unknown | 180 | Alfredo | pendiente |
| 28 | HEYGEN_API_KEY | video generation | unknown | unknown | 180 | Alfredo | pendiente |
| 29 | ELEVENLABS_API_KEY | TTS API | unknown | unknown | 180 | Alfredo | pendiente |
| 30 | LANGFUSE_PUBLIC_KEY | observability public | unknown | unknown | 365 | Alfredo | pendiente |
| 31 | LANGFUSE_SECRET_KEY | observability secret | unknown | unknown | 180 | Alfredo | pendiente |
| 32 | MANUS_API_KEY | Manus default account | unknown | unknown | 180 | Alfredo | pendiente |
| 33 | MANUS_API_KEY_APPLE | Manus Apple account | unknown | unknown | 180 | Alfredo | pendiente |
| 34 | MANUS_API_KEY_GOOGLE | Manus Google account | unknown | unknown | 180 | Alfredo | pendiente |
| 35 | MONSTRUO_API_KEY | kernel API key (auth de clientes al kernel) | 2026-04-XX | 2026-04-XX | 90 | Alfredo | pendiente |
| 36 | COMMAND_CENTER_API_KEY | command center auth | unknown | unknown | 90 | Alfredo | pendiente |
| 37 | ARTIFICIAL_ANALYSIS_API_KEY | analysis platform | unknown | unknown | 180 | Alfredo | pendiente |
| 38 | ZEROENTROPY_API_KEY | search service | unknown | unknown | 180 | Alfredo | pendiente |

## Credenciales auxiliares (no en Railway)

| # | name | tipo | storage | created_at | last_rotated_at | freq_days | runbook |
|---|---|---|---|---|---|---|---|
| 39 | SUPABASE_PAT (`monstruo-supabase-pat`) | Personal Access Token | macOS Keychain | 2026-05-10 | 2026-05-10 | 180 | pendiente |
| 40 | BITWARDEN_MASTER_PASSWORD | master password | personal vault | unknown | **expuesta 2026-05-10**, rotación pendiente | 90 | runbook_rotacion_bitwarden_master_password.md |
| 41 | APPLE_ID_PASSWORD | personal account | iCloud Keychain | unknown | unknown | 180 | pendiente |
| 42 | DB password (Postgres directo) | DB password | Railway env (`SUPABASE_DB_URL` connection string) | unknown | unknown | 90 | pendiente |

## Mapa de cuentas dueñas por servicio (descubierto 2026-05-12)

Durante el Sprint MEGA-CIERRE-HOY (Hilo Ejecutor 1, 2026-05-12) se descubrió binariamente el mapa real de cuentas dueñas detrás de cada API key activa en Railway. Esta información es crítica porque hasta ahora se asumía que todas las cuentas estaban bajo el mismo email principal, lo cual generó confusión durante la suspensión de la cuenta vieja de Anthropic por Trust & Safety. La tabla siguiente refleja la realidad verificada:

| Servicio | Cuenta dueña | Email | Estado | Notas |
|---|---|---|---|---|
| Railway | Alfredo principal | `Alfredogl1@hotmail.com` | activo | proyecto `celebrated-achievement` |
| OpenRouter | Alfredo principal | `Alfredogl1@hotmail.com` | activo, $99.98 USD, Auto Top-Up enabled (threshold $5, recharge $50) | recargado 2026-05-12 |
| Anthropic (vigente) | Apple Sign-In relay | `hfhm9mycw7@privaterelay.appleid.com` | activo, $100 USD, Auto-recharge enabled | org id `56aa18be-d5cb-4446-8794-05153e524660`, key rotada 2026-05-12 |
| Anthropic (legacy) | Gmail principal | `alfredogl1.gongora@gmail.com` | **SUSPENDIDA** por Trust & Safety | bóveda Bitwarden todavía referencia esta cuenta — actualizar nota |
| Bitwarden vault | Gmail principal | `alfredogl1.gongora@gmail.com` | activo | master password expuesta 2026-05-10, rotación pendiente |
| Apple ID | personal | n/a | activo | Sign-In con relay creó cuenta Anthropic nueva |

Esta divergencia de cuentas implica que el flujo de billing y soporte para Anthropic debe ir a la cuenta del Apple Private Relay, no a Gmail. Cualquier intento de recovery de la cuenta vieja Anthropic via Gmail está bloqueado por la suspensión de Trust & Safety y no se debe reintentar; la decisión operativa firme es operar exclusivamente con la cuenta nueva del relay.

## Auto-recharge configurado en proveedores LLM (2026-05-12)

Ambos proveedores de LLM principales tienen recarga automática habilitada al cierre del Sprint MEGA-CIERRE-HOY, eliminando el riesgo de que el kernel se quede sin créditos sin previo aviso operativo:

| Proveedor | Threshold | Recharge | Cuenta de pago | Configurado |
|---|---|---|---|---|
| OpenRouter | $5 USD | $50 USD | `Alfredogl1@hotmail.com` | 2026-05-12 |
| Anthropic | configurado por Alfredo | configurado por Alfredo | Apple Private Relay | 2026-05-12 |

Gemini, Grok, Perplexity y OpenAI quedan pendientes de auditoría de balance y configuración de auto-recharge equivalente cuando se atiendan en sprints futuros.

## Hallazgos críticos del inventario inicial

El inventario revela que **todas las credenciales tienen `created_at: unknown` y `last_rotated_at: unknown`** salvo el PAT de Supabase recién documentado y el incidente de Bitwarden. Esto significa que el proyecto opera con deuda total de fecha de rotación: no se puede saber si una credencial lleva 1 día o 1 año desde su última rotación. El primer ciclo del workflow CI tras el merge de S-003.A asumirá `last_rotated_at = 2026-05-10` (fecha de la creación de este inventario) como baseline conservadora, y empezará a alertar cuando cada credencial cumpla su frecuencia objetivo desde esa fecha.

Adicionalmente, la **master password de Bitwarden quedó expuesta en el log de chat del 2026-05-10** durante el sprint S-002.5. La rotación de esta credencial es el primer item operativo a ejecutar tras el merge de este sprint.

## Próximos pasos

Tras el merge de S-003.A, los siguientes items quedan en backlog operativo: rotar Bitwarden master password, completar runbooks pendientes de las 35 credenciales restantes (sprints S-003.1 a S-003.4 según prioridad), y actualizar `created_at` de cada credencial conforme se vaya verificando con evidencia en los respectivos dashboards. La doctrina es: ninguna credencial puede pasar más de 12 meses con `created_at: unknown` sin acción correctiva (verificación o rotación con documentación).

---

**Última actualización**: 2026-05-12 (Sprint MEGA-CIERRE-HOY, Hilo Ejecutor 1) — agregado mapa de cuentas dueñas, marcado ANTHROPIC_API_KEY como rotada hoy, agregada sección de auto-recharge configurado en OpenRouter + Anthropic.
**Penúltima actualización**: 2026-05-10 (creación del inventario, Sprint S-003.A)
