# 🏛️ META MARKETING API — DECLARADO

**Fecha:** 2026-05-08
**Hilo:** B (Manus — ejecutor técnico)
**Sprint contexto:** Bloque 3 — Ads Platforms (Capa Transversal #3 — Publicidad y Campañas)
**Capa arquitectónica:** Capa 1 — Manos (Ejecución en el Mundo Real)
**Objetivos Maestros tocados:** #2 (premium), #3 (mínima complejidad), #9 (transversalidad), #12 (soberanía parcial — depende de Meta)
**DSC aplicados:** DSC-S-001 (cero secrets en plaintext), DSC-S-004 (fail-loud env vars)

---

## Resumen Ejecutivo

Se completó la integración de **Meta Marketing API** (Facebook + Instagram Ads) al kernel de El Monstruo. La capa de Publicidad ahora dispone de credenciales válidas para operar campañas, leer insights, gestionar Ad Sets y Ad Creatives en el Ad Account "Like Plus Ads". Este es el primer conector del Bloque 3 (Ads Platforms); restan **Google Ads** y **TikTok Ads** para cerrar la capa transversal #3 a nivel de inputs externos.

---

## Activos Configurados

### Meta App
| Atributo | Valor |
|---|---|
| App Name | `moniomnicom` |
| APP_ID | `1521690402449808` |
| APP_SECRET | `***` — buscar en Bitwarden entry "Meta Marketing API - moniomnicom App" |
| App URL | https://developers.facebook.com/apps/1521690402449808/ |

### Business Manager (BM)
| Atributo | Valor |
|---|---|
| Nombre | Alfredo Gongora Lizama |
| Business ID | `1344164534301541` |
| Estado | ✅ Activo (sin restricciones) |
| Nota | BM nuevo. El anterior ("Moniomnicom") quedó bloqueado por Meta el 2025-12 por violación de política de automatización — no recuperable. |

### Ad Account
| Atributo | Valor |
|---|---|
| Nombre | Like Plus Ads |
| Ad Account ID | `act_985442480686285` |
| Currency | **MXN** |
| Timezone | America/Mexico_City |
| Status | ACTIVE (1) |
| Payment method | ⚠️ No configurado (suficiente para tokens y desarrollo; agregar antes de lanzar pautas reales) |

### User Token (Long-Lived)
| Atributo | Valor |
|---|---|
| Tipo | User Access Token (Long-Lived) |
| Duración | 60 días |
| Issued | 2026-05-08 ~12:44 UTC |
| Expires | 2026-07-07 |
| Scopes | `ads_management`, `ads_read`, `business_management`, `public_profile` |
| Validation | ✅ HTTP 200 contra `GET /act_985442480686285?fields=name,currency` |
| Almacenamiento | Bitwarden (entry "Meta Marketing API - moniomnicom App") + Railway env var `META_ACCESS_TOKEN` |

---

## Variables Inyectadas en Railway

Proyecto: **el-monstruo-kernel** (production)

| Variable | Origen | Notas |
|---|---|---|
| `META_APP_ID` | Constante pública | OK exponer |
| `META_APP_SECRET` | Bitwarden entry | Sensible — solo runtime |
| `META_ACCESS_TOKEN` | Long-Lived 60d | Rotar antes de 2026-07-07 |
| `META_AD_ACCOUNT_ID` | `act_985442480686285` | Constante |
| `META_BUSINESS_ID` | `1344164534301541` | Constante |
| `META_GRAPH_VERSION` | `v19.0` | Default; revisar antes de cada release |

Validación end-to-end ejecutada: el kernel puede leer `META_ACCESS_TOKEN` desde env y llamar a Marketing API sin error.

---

## Bóveda — Bitwarden

**Item:** `Meta Marketing API - moniomnicom App`
**Tipo:** Secure Note
**Item ID:** `4457683a-856c-495a-8329-b4440114bf7e`
**Vault:** alfredogl1.gongora@gmail.com
**Custom fields:** APP_ID, APP_SECRET (hidden), ACCESS_TOKEN_LL_60d (hidden), AD_ACCOUNT_ID, BUSINESS_ID, GRAPH_VERSION, EXPIRES, ISSUED
**Notes:** Incluye instrucciones de refresh, debug y revocation.

---

## Hardening / Compliance DSC-S-001

- ✅ Token nunca escrito en archivos versionados
- ✅ Long-Lived token solo en: Bitwarden + Railway env var (no en código, no en bridge files)
- ✅ Scripts CDP usados durante el flow eliminados post-uso (`rm -fv .cdp_*.py .cdp_*.png .meta_*`)
- ✅ Patrones `.cdp_*`, `.meta_*`, `.bw_*`, `.tmp_*` agregados al `.gitignore`
- ✅ Pre-commit hooks (gitleaks, trufflehog) activos — siguen bloqueando push si algún secret se cuela
- ✅ Bridge report (este archivo) NO contiene token, secret ni password en plaintext

---

## Calendario de Rotación

| Acción | Fecha | Responsable | Trigger |
|---|---|---|---|
| Re-validar token contra Marketing API | 2026-06-07 (T+30d) | Hilo B (cron sugerido) | Smoke test mensual |
| Refresh Long-Lived → nuevo Long-Lived | 2026-07-01 (T-6d antes de expirar) | Hilo B | Cron sugerido |
| Migrar a System User Token (sin expiración) | Cuando BM esté verificado | Hilo B | Pendiente — ver "Próximos Pasos" |
| Rotación obligatoria APP_SECRET | 2026-11-08 (cada 6 meses, regla DSC-S-001) | Manual | Calendario |

---

## Próximos Pasos — Bloque 3

1. **Google Ads** — siguiente conector (cuenta MCC + OAuth2 + developer_token approved). Bloqueante: tener Google Ads account activo.
2. **TikTok Ads** — Marketing API for Business. Bloqueante: tener TikTok Business Center.
3. **System User Token Meta** (opcional, recomendado) — Crear System User en BM verificado para obtener token sin vencimiento. Reduce dependencia del refresh manual cada 60d.
4. **Payment method** en Ad Account "Like Plus Ads" — Necesario antes de la primera pauta real. El token y la integración funcionan sin él para fase de desarrollo / sandbox.

---

## Notas para Cowork (Hilo A)

- El kernel ya puede importar `META_ACCESS_TOKEN` desde env via `os.environ["META_ACCESS_TOKEN"]` (fail-loud).
- Sugerencia: construir wrapper `kernel/integrations/meta_ads.py` con cliente Graph API basado en `requests` (ya en deps) o `facebook-business` SDK oficial. **No-go en este sprint** — solo se cerró el setup de credenciales.
- Validación de salud sugerida: endpoint `/health/ads/meta` que ejecute `GET /v19.0/{AD_ACCOUNT_ID}?fields=id,currency` y devuelva 200 si HTTP 200.

---

## Frase Canónica

🏛️ **META MARKETING API — DECLARADO**

Long-Lived token operativo (60d), scopes correctos, validación HTTP 200, Railway poblado, Bitwarden poblado, cleanup ejecutado, compliance DSC-S-001 verificado. Capa Transversal #3 (Publicidad) ahora tiene su primer conector externo activo.

— Hilo B
