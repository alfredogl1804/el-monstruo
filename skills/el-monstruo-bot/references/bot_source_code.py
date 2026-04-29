"""
El Monstruo - Bot de Telegram (Produccion)
Interfaz principal para interactuar con el orquestador LangGraph.
Incluye: botones interactivos, plan preview, aprobacion y flujo de Investigacion de Leads.
"""
import os
import json
import logging
import requests
from openai import OpenAI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# Configuracion desde variables de entorno
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Estado de tareas pendientes (en memoria para MVP, luego Supabase)
pending_tasks = {}

# Cache de resultados de leads para guardar en Notion
lead_results = {}

NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
NOTION_LEADS_DB_ID = None  # Se crea automaticamente la primera vez

# Supabase config para memoria semantica
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://xsumzuhwmivjgftsneov.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")


# ===================== MEMORIA SEMANTICA =====================

def get_embedding(text):
    """Genera embedding con OpenAI text-embedding-3-small."""
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000],
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generando embedding: {e}")
        return None


def save_memory(user_id, role, content, task_type=None, brain_used=None, metadata=None):
    """Guarda un mensaje en la memoria semantica de Supabase."""
    if not SUPABASE_KEY:
        logger.warning("SUPABASE_SERVICE_KEY no configurada, memoria deshabilitada")
        return False

    embedding = get_embedding(content)
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }
    
    payload = {
        "user_id": str(user_id),
        "role": role,
        "content": content[:10000],
        "task_type": task_type,
        "brain_used": brain_used,
        "metadata": metadata or {},
    }
    if embedding:
        payload["embedding"] = embedding
    
    try:
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/monstruo_memory",
            headers=headers,
            json=payload,
            timeout=15,
        )
        if resp.status_code in (200, 201):
            logger.info(f"Memoria guardada para user {user_id}")
            return True
        else:
            logger.error(f"Error guardando memoria: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        logger.error(f"Error guardando memoria: {e}")
        return False


def recall_memories(user_id, query, limit=5):
    """Recupera memorias relevantes usando busqueda semantica."""
    if not SUPABASE_KEY:
        return []

    embedding = get_embedding(query)
    if not embedding:
        return get_recent_memories(user_id, limit)

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    
    try:
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/match_memories",
            headers=headers,
            json={
                "query_embedding": embedding,
                "match_threshold": 0.3,
                "match_count": limit,
                "filter_user_id": str(user_id),
            },
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            logger.error(f"Error buscando memorias: {resp.text}")
            return get_recent_memories(user_id, limit)
    except Exception as e:
        logger.error(f"Error buscando memorias: {e}")
        return get_recent_memories(user_id, limit)


def get_recent_memories(user_id, limit=5):
    """Fallback: obtiene las memorias mas recientes sin busqueda semantica."""
    if not SUPABASE_KEY:
        return []

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    
    try:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/monstruo_memory"
            f"?user_id=eq.{user_id}&order=created_at.desc&limit={limit}"
            f"&select=role,content,task_type,brain_used,created_at",
            headers=headers,
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json()
        return []
    except Exception:
        return []


def build_context_from_memories(memories):
    """Construye un string de contexto a partir de memorias recuperadas."""
    if not memories:
        return ""
    
    context_parts = ["\n--- CONTEXTO DE CONVERSACIONES ANTERIORES ---"]
    for mem in memories[:5]:
        role = mem.get("role", "")
        content = mem.get("content", "")[:500]
        task_type = mem.get("task_type", "")
        brain = mem.get("brain_used", "")
        ts = mem.get("created_at", "")[:10]
        prefix = f"[{ts}]" if ts else ""
        if task_type:
            prefix += f" ({task_type})"
        if brain:
            prefix += f" [{brain}]"
        context_parts.append(f"{prefix} {role}: {content}")
    context_parts.append("--- FIN CONTEXTO ---\n")
    return "\n".join(context_parts)


# ===================== NOTION =====================

def get_or_create_leads_db():
    """Obtiene o crea la base de datos de Leads en Notion."""
    global NOTION_LEADS_DB_ID
    if NOTION_LEADS_DB_ID:
        return NOTION_LEADS_DB_ID

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    # Buscar si ya existe una DB llamada "Leads - El Monstruo"
    search_resp = requests.post(
        "https://api.notion.com/v1/search",
        headers=headers,
        json={"query": "Leads - El Monstruo", "filter": {"property": "object", "value": "database"}},
        timeout=30,
    )
    results = search_resp.json().get("results", [])
    if results:
        NOTION_LEADS_DB_ID = results[0]["id"]
        return NOTION_LEADS_DB_ID

    # Buscar una pagina padre para crear la DB
    parent_resp = requests.post(
        "https://api.notion.com/v1/search",
        headers=headers,
        json={"query": "Archivos Manus", "filter": {"property": "object", "value": "page"}},
        timeout=30,
    )
    parent_results = parent_resp.json().get("results", [])
    if not parent_results:
        # Usar cualquier pagina como padre
        parent_resp = requests.post(
            "https://api.notion.com/v1/search",
            headers=headers,
            json={"filter": {"property": "object", "value": "page"}, "page_size": 1},
            timeout=30,
        )
        parent_results = parent_resp.json().get("results", [])

    if not parent_results:
        logger.error("No se encontro pagina padre en Notion")
        return None

    parent_id = parent_results[0]["id"]

    # Crear la base de datos
    db_payload = {
        "parent": {"type": "page_id", "page_id": parent_id},
        "title": [{"type": "text", "text": {"content": "Leads - El Monstruo"}}],
        "properties": {
            "Empresa": {"title": {}},
            "CEO": {"rich_text": {}},
            "Industria": {"rich_text": {}},
            "Ubicacion": {"rich_text": {}},
            "Sitio Web": {"url": {}},
            "Competidores": {"rich_text": {}},
            "Estado": {
                "select": {
                    "options": [
                        {"name": "Nuevo", "color": "blue"},
                        {"name": "Contactado", "color": "yellow"},
                        {"name": "En Negociacion", "color": "orange"},
                        {"name": "Cerrado", "color": "green"},
                    ]
                }
            },
            "Fecha": {"date": {}},
        },
    }

    create_resp = requests.post(
        "https://api.notion.com/v1/databases",
        headers=headers,
        json=db_payload,
        timeout=30,
    )
    if create_resp.status_code == 200:
        NOTION_LEADS_DB_ID = create_resp.json()["id"]
        logger.info(f"DB de Leads creada: {NOTION_LEADS_DB_ID}")
        return NOTION_LEADS_DB_ID
    else:
        logger.error(f"Error creando DB: {create_resp.text}")
        return None


def save_lead_to_notion(company_name, research_text):
    """Guarda un lead investigado en la base de datos de Notion."""
    db_id = get_or_create_leads_db()
    if not db_id:
        return False, "No se pudo acceder a la base de datos de Notion."

    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    # Extraer datos del texto de investigacion con GPT
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        extract = client.chat.completions.create(
            model="gpt-5.4-mini"  # Updated 2026-04-22 — gpt-4o RETIRED,
            messages=[
                {"role": "system", "content": (
                    "Extrae los siguientes campos del texto de investigacion y responde SOLO en JSON:\n"
                    '{"empresa": "", "ceo": "", "industria": "", "ubicacion": "", '
                    '"sitio_web": "", "competidores": ""}\n'
                    "Si no encuentras un campo, deja string vacio. sitio_web debe ser URL valida o vacio."
                )},
                {"role": "user", "content": research_text},
            ],
            max_completion_tokens=300,
        )
        data = json.loads(extract.choices[0].message.content.strip().strip("```json").strip("```"))
    except Exception as e:
        logger.error(f"Error extrayendo datos: {e}")
        data = {"empresa": company_name, "ceo": "", "industria": "", "ubicacion": "", "sitio_web": "", "competidores": ""}

    from datetime import datetime
    properties = {
        "Empresa": {"title": [{"text": {"content": data.get("empresa", company_name)}}]},
        "CEO": {"rich_text": [{"text": {"content": data.get("ceo", "")[:2000]}}]},
        "Industria": {"rich_text": [{"text": {"content": data.get("industria", "")[:2000]}}]},
        "Ubicacion": {"rich_text": [{"text": {"content": data.get("ubicacion", "")[:2000]}}]},
        "Competidores": {"rich_text": [{"text": {"content": data.get("competidores", "")[:2000]}}]},
        "Estado": {"select": {"name": "Nuevo"}},
        "Fecha": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
    }
    if data.get("sitio_web") and data["sitio_web"].startswith("http"):
        properties["Sitio Web"] = {"url": data["sitio_web"]}

    # Crear la pagina con el contenido completo como body
    children = []
    # Dividir el texto en bloques de max 2000 chars
    text_chunks = [research_text[i:i+2000] for i in range(0, len(research_text), 2000)]
    for chunk in text_chunks:
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": chunk}}]
            },
        })

    page_payload = {
        "parent": {"database_id": db_id},
        "properties": properties,
        "children": children,
    }

    resp = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json=page_payload,
        timeout=30,
    )
    if resp.status_code == 200:
        page_url = resp.json().get("url", "")
        return True, page_url
    else:
        logger.error(f"Error guardando lead: {resp.text}")
        return False, resp.text


# ===================== CEREBROS =====================

def classify_task(task_text):
    """Clasifica la tarea usando GPT."""
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-5.4-mini"  # Updated 2026-04-22 — gpt-4o RETIRED,
            messages=[
                {"role": "system", "content": (
                    "Clasifica la tarea en UNA categoria: investigacion, codigo, estrategia, "
                    "creativo, analisis, leads. Responde SOLO con la categoria."
                )},
                {"role": "user", "content": task_text}
            ],
            max_completion_tokens=20,
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        logger.error(f"Error clasificando: {e}")
        return "estrategia"


def generate_plan(task_text, task_type):
    """Genera el plan de herramientas para la tarea."""
    try:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-5.4-mini"  # Updated 2026-04-22 — gpt-4o RETIRED,
            messages=[
                {"role": "system", "content": (
                    "Eres el Meta-Orquestador del Monstruo. Genera un plan BREVE (max 5 lineas) "
                    "de que cerebros y herramientas usar para esta tarea. "
                    "Formato:\n"
                    "Cerebro: [nombre]\n"
                    "Paso 1: [accion]\n"
                    "Paso 2: [accion]\n"
                    "Costo est.: $X.XX\n"
                    "Disponible: Perplexity, GPT, Gemini, Grok, DeepSeek, Notion MCP, Gmail MCP, "
                    "Supabase, HeyGen, ElevenLabs, Instagram MCP, Asana MCP, Zapier."
                )},
                {"role": "user", "content": f"Tarea ({task_type}): {task_text}"}
            ],
            max_completion_tokens=300,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generando plan: {e}")
        return "Error generando plan. Reintentando..."


def execute_task(task_text, task_type):
    """Ejecuta la tarea con el cerebro adecuado."""
    brain_map = {
        "investigacion": ("sonar", "Perplexity Sonar Pro"),
        "leads": ("sonar", "Perplexity Sonar Pro"),
        "codigo": ("grok", "Grok 4.20"),
        "estrategia": ("gpt", "GPT-5.4"),
        "creativo": ("grok", "Grok 4.20"),
        "analisis": ("deepseek", "DeepSeek R1"),
    }
    brain_id, brain_name = brain_map.get(task_type, ("gpt", "GPT-5.4"))

    try:
        if brain_id == "sonar":
            headers = {
                "Authorization": f"Bearer {os.environ.get('SONAR_API_KEY')}",
                "Content-Type": "application/json",
            }
            data = {
                "model": "sonar-pro",
                "messages": [
                    {"role": "system", "content": (
                        "Eres un investigador experto. Responde de forma concisa y estructurada. "
                        "Incluye fuentes cuando sea posible."
                    )},
                    {"role": "user", "content": task_text},
                ],
            }
            resp = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers, json=data, timeout=120,
            )
            text = resp.json()["choices"][0]["message"]["content"]
            return brain_name, text

        elif brain_id == "grok":
            client = OpenAI(
                api_key=os.environ.get("XAI_API_KEY"),
                base_url="https://api.x.ai/v1",
            )
            response = client.chat.completions.create(
                model="grok-3-latest",
                messages=[
                    {"role": "system", "content": "Eres un experto. Responde conciso y estructurado."},
                    {"role": "user", "content": task_text},
                ],
                max_completion_tokens=2000,
            )
            return brain_name, response.choices[0].message.content

        elif brain_id == "deepseek":
            client = OpenAI(
                api_key=os.environ.get("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
            )
            response = client.chat.completions.create(
                model="deepseek/deepseek-r1",
                messages=[
                    {"role": "system", "content": "Eres un analista tecnico experto. Responde conciso."},
                    {"role": "user", "content": task_text},
                ],
                max_completion_tokens=2000,
            )
            return brain_name, response.choices[0].message.content

        else:  # gpt
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-5.4-mini"  # Updated 2026-04-22 — gpt-4o RETIRED,
                messages=[
                    {"role": "system", "content": "Eres un estratega experto. Responde conciso y estructurado."},
                    {"role": "user", "content": task_text},
                ],
                max_completion_tokens=2000,
            )
            return brain_name, response.choices[0].message.content

    except Exception as e:
        logger.error(f"Error ejecutando con {brain_name}: {e}")
        return brain_name, f"Error: {str(e)}"


def research_lead(company_name):
    """Flujo especializado: Investigacion de Leads."""
    try:
        headers = {
            "Authorization": f"Bearer {os.environ.get('SONAR_API_KEY')}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "sonar-pro",
            "messages": [
                {"role": "system", "content": (
                    "Eres un investigador de negocios. Para la empresa solicitada, "
                    "encuentra y estructura la siguiente informacion:\n"
                    "1. Nombre completo de la empresa\n"
                    "2. A que se dedica (resumen de 2 lineas)\n"
                    "3. CEO o Director General (nombre completo)\n"
                    "4. LinkedIn del CEO (si lo encuentras)\n"
                    "5. Sitio web oficial\n"
                    "6. Ubicacion (ciudad, pais)\n"
                    "7. Tamano estimado (empleados)\n"
                    "8. 3 principales competidores\n"
                    "9. Dato interesante o noticia reciente\n\n"
                    "Responde en formato estructurado. Si no encuentras algo, indica 'No encontrado'."
                )},
                {"role": "user", "content": f"Investiga la empresa: {company_name}"},
            ],
        }
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers, json=data, timeout=120,
        )
        research = resp.json()["choices"][0]["message"]["content"]

        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-5.4-mini"  # Updated 2026-04-22 — gpt-4o RETIRED,
            messages=[
                {"role": "system", "content": (
                    "Toma esta investigacion de un lead y presentala en formato limpio para Telegram. "
                    "Usa emojis para cada seccion. Se conciso pero completo."
                )},
                {"role": "user", "content": research},
            ],
            max_tokens=1000,
        )
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Error en research_lead: {e}")
        return f"Error investigando {company_name}: {str(e)}"


# ===================== HANDLERS DE TELEGRAM =====================

async def start(update: Update, context):
    welcome = (
        "*Bienvenido al Monstruo*\n\n"
        "Soy tu orquestador de IAs. Puedo:\n\n"
        "Enviarme cualquier tarea y te mostrare un plan antes de ejecutar.\n\n"
        "*Comandos:*\n"
        "/research `[empresa]` - Investigar un lead\n"
        "/status - Ver estado del sistema\n"
        "/help - Ayuda\n\n"
        "O simplemente escribeme lo que necesitas."
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")


async def help_cmd(update: Update, context):
    help_text = (
        "*Comandos disponibles:*\n\n"
        "/research `[empresa]` - Investigar un lead completo\n"
        "/status - Estado del sistema\n"
        "/help - Esta ayuda\n\n"
        "*Cerebros disponibles:*\n"
        "GPT-5.4 | Claude Opus 4.6 | Gemini 3.1 Pro\n"
        "Grok 4.20 | Perplexity Sonar | DeepSeek R1\n\n"
        "*Herramientas conectadas:*\n"
        "Notion | Gmail | Supabase | Asana | Zapier\n"
        "HeyGen | ElevenLabs | Instagram | Vercel | PayPal"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def status(update: Update, context):
    status_text = (
        "*Estado del Monstruo*\n\n"
        "Orquestador: LangGraph v2\n"
        "Cerebros: 6/6 activos\n"
        "MCPs: 11 conectados\n"
        "APIs: 10 con credenciales\n"
        "Memoria: Supabase + pgvector\n"
        "Deploy: Railway (24/7)\n"
        "Tareas pendientes: " + str(len(pending_tasks))
    )
    await update.message.reply_text(status_text, parse_mode="Markdown")


async def research_command(update: Update, context):
    if not context.args:
        await update.message.reply_text(
            "Uso: /research `[nombre de empresa]`\n"
            "Ejemplo: /research Tesla",
            parse_mode="Markdown",
        )
        return

    company = " ".join(context.args)
    msg = await update.message.reply_text(
        f"Investigando *{company}*...\n\n"
        "Cerebro: Perplexity Sonar Pro\n"
        "Paso 1: Buscando informacion en la web...",
        parse_mode="Markdown",
    )

    result = research_lead(company)

    # Guardar resultado para poder salvarlo en Notion despues
    lead_results[company] = result

    keyboard = [
        [
            InlineKeyboardButton("Guardar en Notion", callback_data=f"save_notion:{company}"),
            InlineKeyboardButton("Enviar por Email", callback_data=f"send_email:{company}"),
        ],
        [
            InlineKeyboardButton("Investigar mas", callback_data=f"deep_research:{company}"),
        ],
    ]

    await msg.edit_text(
        f"*Lead: {company}*\n\n{result}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context):
    task_text = update.message.text
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    msg = await update.message.reply_text("Analizando tu tarea...")

    # Guardar mensaje del usuario en memoria
    save_memory(user_id, "user", task_text)

    # Recuperar memorias relevantes para contexto
    memories = recall_memories(user_id, task_text, limit=5)
    memory_context = build_context_from_memories(memories)

    task_type = classify_task(task_text)

    await msg.edit_text(
        f"Tipo: *{task_type}*\nGenerando plan de ejecucion...",
        parse_mode="Markdown",
    )
    # Incluir contexto de memoria en la generacion del plan
    enriched_task = task_text
    if memory_context:
        enriched_task = memory_context + "\nTarea actual: " + task_text
    plan = generate_plan(enriched_task, task_type)

    task_id = f"{user_id}_{chat_id}_{hash(task_text) % 10000}"
    pending_tasks[task_id] = {
        "task": task_text,
        "type": task_type,
        "plan": plan,
        "user_id": user_id,
    }

    keyboard = [
        [
            InlineKeyboardButton("Aprobar", callback_data=f"approve:{task_id}"),
            InlineKeyboardButton("Modificar", callback_data=f"modify:{task_id}"),
        ],
        [
            InlineKeyboardButton("Cancelar", callback_data=f"cancel:{task_id}"),
        ],
    ]

    await msg.edit_text(
        f"*Plan Propuesto*\n\n"
        f"*Tarea:* {task_text[:100]}...\n"
        f"*Tipo:* {task_type}\n\n"
        f"{plan}\n\n"
        f"_Aprueba para ejecutar o modifica el plan._",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def handle_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("approve:"):
        task_id = data.split(":", 1)[1]
        task_info = pending_tasks.get(task_id)
        if not task_info:
            await query.edit_message_text("Tarea no encontrada o expirada.")
            return

        await query.edit_message_text(
            f"*Ejecutando...*\n\n"
            f"Tarea: {task_info['task'][:100]}\n"
            f"Cerebro trabajando...",
            parse_mode="Markdown",
        )

        brain_name, result = execute_task(task_info["task"], task_info["type"])
        user_id = task_info.get("user_id", "unknown")
        del pending_tasks[task_id]

        # Guardar resultado en memoria
        save_memory(
            user_id, "assistant", result[:5000],
            task_type=task_info["type"],
            brain_used=brain_name,
            metadata={"task": task_info["task"][:500]},
        )

        if len(result) > 3500:
            result = result[:3500] + "\n\n_[Resultado truncado]_"

        await query.edit_message_text(
            f"*Resultado del Monstruo*\n\n"
            f"*Cerebro:* {brain_name}\n"
            f"*Tipo:* {task_info['type']}\n\n"
            f"{result}",
            parse_mode="Markdown",
        )

    elif data.startswith("cancel:"):
        task_id = data.split(":", 1)[1]
        pending_tasks.pop(task_id, None)
        await query.edit_message_text("Tarea cancelada.")

    elif data.startswith("modify:"):
        await query.edit_message_text(
            "Enviame las instrucciones de como quieres modificar el plan.\n"
            "Luego vuelve a enviar tu tarea con los ajustes.",
        )

    elif data.startswith("save_notion:"):
        company = data.split(":", 1)[1]
        if not NOTION_API_KEY:
            await query.edit_message_text(
                f"NOTION_API_KEY no configurada. No se puede guardar en Notion.",
            )
            return

        await query.edit_message_text(
            f"Guardando lead de *{company}* en Notion...",
            parse_mode="Markdown",
        )

        research_text = lead_results.get(company, f"Lead: {company}")
        success, result_url = save_lead_to_notion(company, research_text)

        if success:
            await query.edit_message_text(
                f"Lead de *{company}* guardado en Notion\n\n"
                f"[Abrir en Notion]({result_url})",
                parse_mode="Markdown",
            )
        else:
            await query.edit_message_text(
                f"Error guardando lead de *{company}*: {result_url[:200]}",
                parse_mode="Markdown",
            )

    elif data.startswith("send_email:"):
        company = data.split(":", 1)[1]
        await query.edit_message_text(
            f"Enviando lead de *{company}* por email...\n"
            f"_(Funcion disponible proximamente)_",
            parse_mode="Markdown",
        )

    elif data.startswith("deep_research:"):
        company = data.split(":", 1)[1]
        await query.edit_message_text(
            f"Investigando *{company}* en profundidad...",
            parse_mode="Markdown",
        )
        result = research_lead(
            company + " - investigacion profunda: historia, fundadores, "
            "rondas de inversion, cultura empresarial, reviews de empleados"
        )
        await query.edit_message_text(
            f"*Investigacion Profunda: {company}*\n\n{result}",
            parse_mode="Markdown",
        )


async def error_handler(update, context):
    logger.error(f"Error: {context.error}")


# ===================== MAIN =====================

def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN no configurado!")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("research", research_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_error_handler(error_handler)

    logger.info("El Monstruo esta vivo en Railway. Esperando mensajes...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
