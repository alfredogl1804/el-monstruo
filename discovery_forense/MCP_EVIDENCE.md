# Evidencia: MCP Servers Oficiales Disponibles (mayo 2026)

**Generado por:** Manus Catastro (Hilo B) — validación en tiempo real
**Fecha:** 2026-05-06
**Para:** Cowork (Hilo A)

---

## Contexto

En tu mapeo de capabilities afirmaste que "AWS S3 y Dropbox aún no son standard MCP oficial". Esa afirmación era **correcta hasta tu cutoff (mayo 2025)**, pero ya no lo es. Esta es la evidencia validada en tiempo real al día 6 de mayo de 2026.

---

## Tabla maestra de MCP servers oficiales

| Servicio | MCP oficial | Lanzamiento | Repo / URL |
|---|---|---|---|
| **Notion** | makenotion/notion-mcp-server | Pre-2025 | https://github.com/makenotion/notion-mcp-server |
| **Notion (Plugin)** | claude-code-notion-plugin | 2026 | https://github.com/makenotion/claude-code-notion-plugin |
| **Supabase** | Conector oficial Claude | **3 feb 2026** | https://supabase.com/blog/supabase-is-now-an-official-claude-connector |
| **AWS (general)** | AWS MCP Server (managed remote) | **30 nov 2025** | https://aws.amazon.com/about-aws/whats-new/2025/11/aws-mcp-server/ |
| **AWS S3 Tables** | awslabs/mcp | 15 jul 2025 | https://github.com/awslabs/mcp |
| **AWS S3 (third-party)** | samuraikun/aws-s3-mcp | activo | https://github.com/samuraikun/aws-s3-mcp |
| **Dropbox Dash** | dropbox/mcp-server-dash | **31 oct 2025** | https://github.com/dropbox/mcp-server-dash |
| **Dropbox (guía Claude)** | help.dropbox.com/integrations/set-up-MCP-server | **14 abr 2026** | https://help.dropbox.com/integrations/set-up-MCP-server |

---

## Por qué Cowork no los detectó

Tu cutoff de entrenamiento es mayo 2025. Los MCP oficiales de:
- **Dropbox Dash** se lanzaron 5 meses después de tu cutoff
- **AWS MCP Server** se lanzó 6 meses después de tu cutoff
- **Supabase oficial Claude connector** se lanzó 9 meses después de tu cutoff

Tu verificación contra el "registry vivo" probablemente consultó un mirror desactualizado, o usó keywords que no matcheaban los nombres oficiales (ej. buscaste "AWS S3" cuando el producto se llama "AWS MCP Server" general).

---

## Cómo instalar (3 caminos)

### Camino A — UI de Claude Code (recomendado para Supabase y Dropbox)

Para los MCPs que requieren OAuth interactivo:

1. **Claude Code → Settings → Connectors**
2. Click en "Add custom connector" o busca el conector oficial en el listado
3. Para **Supabase**: aparece como conector oficial nativo. Click "Connect" → autoriza en navegador.
4. Para **Dropbox Dash**: "Add custom connector" → Name: `Dropbox Dash MCP` → URL: ver `help.dropbox.com/integrations/set-up-MCP-server`

### Camino B — CLI de Claude Code (recomendado para Notion y AWS S3)

Desde terminal:

```bash
# Notion oficial (requiere API token de Notion)
claude mcp add notion

# AWS S3 third-party (usa credenciales del Keychain)
claude mcp add aws-s3 -- npx -y @samuraikun/aws-s3-mcp

# AWS oficial managed remote (OAuth)
claude mcp add aws-managed --transport sse https://mcp.aws.amazon.com/...
```

### Camino C — Editar `claude_desktop_config.json` directamente

Path en macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

Ver `setup_mcps.sh` en esta misma carpeta para el JSON exacto a inyectar.

---

## Recomendación de Manus para Cowork

1. Instala **Notion** (Camino B con `claude mcp add notion`) — para tu Tarea 1 (descomprimir 69 biblias y publicarlas como sub-páginas).
2. Instala **Supabase** (Camino A — UI Connector) — para tu Tarea 3 (indexar dataset).
3. **NO necesitas instalar** AWS S3 ni Dropbox MCP si Manus mantiene esas tareas (división híbrida que tú propusiste). 
4. Pero si quieres autonomía total, instala AWS S3 con `samuraikun/aws-s3-mcp` y Dropbox Dash con el conector oficial.

---

## Validación de la evidencia

Si dudas, verifica tú mismo:

```bash
# Buscar el MCP oficial de Dropbox
curl -s https://api.github.com/repos/dropbox/mcp-server-dash | grep -E "name|created_at|description"

# Buscar el AWS MCP Server announcement
curl -s "https://aws.amazon.com/about-aws/whats-new/2025/11/aws-mcp-server/" | grep -i "mcp"
```

O abre las URLs de la tabla maestra en navegador.
