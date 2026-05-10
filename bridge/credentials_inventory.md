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
| 4 | ANTHROPIC_API_KEY | LLM API key | unknown | unknown | 30 | Alfredo | pendiente |
| 5 | GEMINI_API_KEY | LLM API key | unknown | unknown | 30 | Alfredo | pendiente |
| 6 | XAI_API_KEY | LLM API key | unknown | unknown | 30 | Alfredo | pendiente |
| 7 | OPENROUTER_API_KEY | LLM gateway key | unknown | unknown | 30 | Alfredo | pendiente |
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

## Hallazgos críticos del inventario inicial

El inventario revela que **todas las credenciales tienen `created_at: unknown` y `last_rotated_at: unknown`** salvo el PAT de Supabase recién documentado y el incidente de Bitwarden. Esto significa que el proyecto opera con deuda total de fecha de rotación: no se puede saber si una credencial lleva 1 día o 1 año desde su última rotación. El primer ciclo del workflow CI tras el merge de S-003.A asumirá `last_rotated_at = 2026-05-10` (fecha de la creación de este inventario) como baseline conservadora, y empezará a alertar cuando cada credencial cumpla su frecuencia objetivo desde esa fecha.

Adicionalmente, la **master password de Bitwarden quedó expuesta en el log de chat del 2026-05-10** durante el sprint S-002.5. La rotación de esta credencial es el primer item operativo a ejecutar tras el merge de este sprint.

## Próximos pasos

Tras el merge de S-003.A, los siguientes items quedan en backlog operativo: rotar Bitwarden master password, completar runbooks pendientes de las 35 credenciales restantes (sprints S-003.1 a S-003.4 según prioridad), y actualizar `created_at` de cada credencial conforme se vaya verificando con evidencia en los respectivos dashboards. La doctrina es: ninguna credencial puede pasar más de 12 meses con `created_at: unknown` sin acción correctiva (verificación o rotación con documentación).

---

**Última actualización**: 2026-05-10 (creación del inventario, Sprint S-003.A)
