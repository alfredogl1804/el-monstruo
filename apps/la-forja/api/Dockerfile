# La Forja API — Dockerfile multi-stage para Railway (Railpack-compatible)
# Sprint LA-FORJA-001 v3.2 — D1 no-SQL scaffolding
# Doctrina: Regla Dura #4 (sin secretos en plaintext). Todos los secretos vienen del runtime
# environment de Railway. Este Dockerfile NO contiene API keys.

# ---- Etapa 1: build ----
FROM node:22.10.0-alpine AS builder
WORKDIR /app

# Copiar manifests primero para optimizar cache
COPY package.json ./
COPY tsconfig.json ./

# Instalar dependencias (incluyendo dev para el build)
RUN npm install --no-audit --no-fund

# Copiar fuente y compilar
COPY src ./src
RUN npm run build

# Limpiar dev deps después del build para reducir tamaño final
RUN npm prune --omit=dev


# ---- Etapa 2: runtime ----
FROM node:22.10.0-alpine AS runtime
WORKDIR /app

# Crear usuario non-root para mitigar riesgo de privilege escalation (Regla Dura #1)
RUN addgroup -g 1001 forja && adduser -D -u 1001 -G forja forja

# Copiar artifacts del build
COPY --from=builder --chown=forja:forja /app/node_modules ./node_modules
COPY --from=builder --chown=forja:forja /app/dist ./dist
COPY --from=builder --chown=forja:forja /app/package.json ./

# Cambiar a usuario non-root
USER forja

# Variables Railway-injected en runtime (NO hardcodeadas):
#   PORT, MANUS_API_KEY_GOOGLE, MANUS_API_KEY_APPLE,
#   ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, SONAR_API_KEY,
#   SUPABASE_URL, SUPABASE_SERVICE_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY
EXPOSE 8080

# Healthcheck para Railway
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "fetch('http://localhost:' + (process.env.PORT || 8080) + '/health').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"

CMD ["node", "dist/index.js"]
