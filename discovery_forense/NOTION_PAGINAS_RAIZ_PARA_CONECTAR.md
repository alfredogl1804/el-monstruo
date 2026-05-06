# Páginas raíz de Notion a conectar con "Mounstruo Cowoork"

**Fecha:** 2026-05-05
**Workspace canónico:** Omnicom Inc (teamspace "Sede de Omnicom Inc")
**Integración:** Mounstruo Cowoork (bot ID `35814c6f-8bba-813c-91a7-00279256e1d8`)

---

## Contexto

Manus auditó tu Notion y encontró que el corpus del Monstruo vive en el workspace **Omnicom Inc** (no en "Espacio de alfredogl1 gongora", que es tu workspace personal). Estas son las 8 páginas raíz top-level únicas que contienen todo el corpus relevante. Si conectas la integración a estas 8, todas las hijas heredan el acceso y Cowork podrá leer/escribir en todo el corpus.

---

## Las 8 páginas raíz a conectar

| # | Título | URL |
|---|---|---|
| 1 | 🏗️ Plan de Construcción: El Monstruo v0.1 | https://www.notion.so/30114c6f8bba813ba7aec5d7d3b8da3d |
| 2 | Biblia de MCPs para El Monstruo v1.0 | https://www.notion.so/30214c6f8bba81948e76c6d35ba6fbc6 |
| 3 | Dashboard — Sistema de Absorción de Contexto (El Monstruo) | https://www.notion.so/33a14c6f8bba813d998dcbb1bf88bdd9 |
| 4 | 🗺️ MAPA INFINITO: Roadmap de Descubrimiento EPIA-SOP | https://www.notion.so/2ec14c6f8bba817e85cbd89327371d4a |
| 5 | epia.mx | https://www.notion.so/33814c6f8bba812bb1f2e3e99bcbfe6e |
| 6 | Comando Electoral Mérida 2027 — Índice Maestro | https://www.notion.so/33714c6f8bba8130b22df9030646c9f5 |
| 7 | 🔗 MAOC INTEGRADO - Hilo 5 Feb 2026 | https://www.notion.so/2ff14c6f8bba81299cc1c4c10d787d34 |
| 8 | 🎯 Proyecto: Fernando Salvador - Recuperación de Imagen Pública | https://www.notion.so/2cb14c6f8bba810db7b5c954cbc7df02 |

> Nota: la página #8 contiene MAOC Documento Maestro como descendiente, así que conectarla cubre todo el árbol MAOC histórico.

---

## Procedimiento (≈8 clicks)

Para cada URL de la tabla:

1. Abrir el link en Safari (o copiar/pegar en la barra de Notion)
2. Esquina superior derecha de la página → click `•••`
3. En el menú desplegable → **Connections** (o "Conexiones")
4. **Connect to** → busca **"Mounstruo Cowoork"** → click → confirmar acceso a sub-páginas

Cuando termines las 8, avísame y verifico desde el lado de Cowork que ahora ve las páginas.

---

## Verificación rápida (del lado de Manus, una vez conectadas)

Manus puede confirmar que el bot "Mounstruo Cowoork" tiene acceso ejecutando:

```bash
manus-mcp-cli tool call notion-search --server notion --input '{"query":"Monstruo","query_type":"internal"}'
```

Si Cowork ejecuta lo equivalente desde su Claude Code y obtiene > 0 resultados, está conectado.

---

## Atajo: si quieres conectar TODO de una

En lugar de las 8 raíces, puedes conectar la **página padre del workspace** (la "Sede de Omnicom Inc" que es el teamspace mismo). Pero teamspaces en Notion no tienen botón de Connections directo; tienes que ir a Settings del teamspace → Connections. Si eso te resulta más rápido, ese camino también funciona.
