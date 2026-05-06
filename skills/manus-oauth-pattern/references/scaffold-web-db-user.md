# Scaffold web-db-user del Monstruo — qué incluye respecto a Manus-Oauth

> El scaffold `web-db-user` del agente Manus (cuando creas un proyecto vía `webdev_init_project`) ya integra Manus-Oauth out of the box. Este doc explica qué te da hecho y qué tienes que ajustar.

---

## Qué viene preinstalado

| Componente | Estado |
|---|---|
| Tabla `users` con schema canónico | ✅ Drizzle migration auto-aplicada |
| Endpoints `/api/v1/auth/callback`, `/logout`, `/me` | ✅ Stubs generados |
| Middleware de auth | ✅ Inyectado en `lib/auth/` |
| Variables de entorno `MANUS_OAUTH_*` | ✅ Auto-pobladas en deployment |
| Botón `<SignInWithManusButton />` | ✅ En página default `/login` |
| Token encryption at rest | ✅ Con key del Manus secret manager |

---

## Qué tienes que ajustar tú

| Componente | Acción |
|---|---|
| Branding del botón | Override `text` y `variant` según marca del proyecto-hijo (siempre desde `@monstruo/design-tokens`, NUNCA primary/secondary) |
| Páginas protegidas | Agregar middleware o layout protector según routing |
| Scopes adicionales | Si necesitas más allá de `openid profile email`, agregar al `MANUS_OAUTH_SCOPE` |
| Webhook de Manus para eventos de user | Opcional. Útil si quieres reaccionar a "user actualizó perfil" o "user fue suspendido" |
| Tests E2E | Adaptar fixtures al routing del proyecto |

---

## Estructura generada por scaffold

```
mi-proyecto/
├── src/
│   ├── api/
│   │   └── v1/auth/         ← endpoints canónicos
│   ├── lib/
│   │   ├── auth/            ← middleware + crypto
│   │   └── db/              ← Drizzle schema
│   ├── components/
│   │   └── auth/
│   │       └── SignInWithManusButton.tsx ← from @monstruo/design-tokens
│   └── app/
│       ├── login/page.tsx
│       └── (protected)/...
├── drizzle/
│   └── 0001_initial_users.sql ← migration canónica
├── .env.example                ← template con MANUS_OAUTH_*
└── package.json                ← incluye @monstruo/design-tokens
```

---

## Verificación post-init

Después de `webdev_init_project --scaffold web-db-user`:

```bash
# 1. Verificar que las migraciones se aplicaron
pnpm drizzle-kit migrate
mysql -e "DESCRIBE users" mi-db | grep manus_token

# 2. Verificar que los endpoints existen
curl http://localhost:3000/api/v1/auth/me
# Esperado: 401 (no estás logueado)

# 3. Verificar que el botón está en /login
curl http://localhost:3000/login | grep "Sign in with Manus"
# Esperado: aparece el texto

# 4. Verificar que las env vars están en .env.example
grep MANUS_OAUTH_ .env.example
# Esperado: ve los nombres de variables
```

---

## Cuándo NO usar el scaffold

Si tu proyecto:
- Es una app móvil pura (Expo) — usar scaffold `mobile-app` (también integra Manus-Oauth pero diferente)
- Es estático sin auth (landing page, blog) — usar scaffold `web-static` (NO incluye Manus-Oauth)
- Es un servicio interno del Monstruo (kernel ↔ kernel) — no usar OAuth, usar JWT firmados con keys del Vault

---

## Cross-links

- `webdev_init_project` tool — invocación oficial
- DSC-X-003 — restricción dura del provider
- `templates/` — base de los archivos generados
- `references/checklist-integracion.md` — verificación final

— Hilo Catastro, Sprint Catastro-B 2026-05-06
