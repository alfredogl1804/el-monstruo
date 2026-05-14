# Contexto de Infraestructura: El Monstruo (Mayo 2026)

## Repositorio y Arquitectura
- **Repo:** `alfredogl1804/el-monstruo` (GitHub)
- **Despliegue:** Railway (Kernel FastAPI + LangGraph)
- **Base de Datos:** Supabase (PostgreSQL + pgvector)
- **Checkpointer actual:** `AsyncPostgresSaver` (canónico de LangGraph, activo en `/health`)
- **Reglas Duras:** Documentadas en `AGENTS.md` (ej. "guardian.py obligatorio al inicio", "Plano de datos cerrado por defecto RLS").

## El Problema: Síndrome Dory
Los agentes de Manus AI operan en hilos (tasks) aislados. Cuando un hilo se cierra por límite de contexto o tokens, el usuario debe abrir un hilo nuevo. El hilo nuevo nace "virgen", sin memoria de lo que el hilo anterior estaba haciendo.

Actualmente, existen skills de contexto estático (`el-monstruo-core`, `el-monstruo-estado`), pero no hay un mecanismo de **traspaso de estado operativo dinámico** (ej. "estábamos en la fase 3 del sprint X, a punto de commitear Y").

## Resultado de Prueba Empírica (RAP-001 LIVE)
Se probó enviar el mensaje *"continuá lo de ayer con El Monstruo; no te reexplico nada."* a un hilo nuevo de Manus vía API.
**Resultado:** Fallo. El agente respondió: *"No tengo acceso al contexto de la sesión anterior... necesito que me proporciones el punto exacto donde quedaste para continuar"*.
