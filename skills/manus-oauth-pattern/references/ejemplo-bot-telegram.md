# Ejemplo: Manus-Oauth en Bot de Telegram (linking pattern)

> Bot de Telegram no puede hacer OAuth flow estándar (no hay browser persistente, no hay cookies HTTP). Se usa **linking pattern** que vincula el `chat_id` del Telegram con el `user_id` del Monstruo.

---

## Flow

```
1. User en Telegram envía /start o /link
2. Bot responde con un link único:
   https://tu-app.com/link/manus?code=ABC123XYZ&chat_id=12345
3. User abre el link en su browser → flow OAuth normal
4. Después del callback exitoso, el server asocia el chat_id con el user_id
5. Bot detecta la asociación (vía DB poll o webhook) y confirma:
   "✅ Tu cuenta de Telegram está vinculada con tu cuenta del Monstruo (alfredo@...)"
6. Para desvincular: /unlink desde Telegram → borra la asociación
```

---

## Schema adicional

```sql
CREATE TABLE telegram_links (
  id              VARCHAR(64) PRIMARY KEY,         -- UUID
  user_id         VARCHAR(64) NOT NULL,            -- FK a users(id)
  chat_id         BIGINT NOT NULL UNIQUE,          -- Telegram chat_id
  link_code       VARCHAR(32) UNIQUE,              -- código temporal para vinculación
  link_code_expires_at TIMESTAMP NULL,
  linked_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  unlinked_at     TIMESTAMP NULL,

  CONSTRAINT fk_telegram_links_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_telegram_links_chat_id ON telegram_links(chat_id);
CREATE INDEX idx_telegram_links_link_code ON telegram_links(link_code);
```

---

## Endpoints adicionales

- `POST /api/v1/auth/telegram/initiate` — bot llama esto cuando user envía `/link`. Retorna un `link_code` único válido por 10 min.
- `GET /link/manus?code=...&chat_id=...` — landing del browser. Si user no tiene cookie → redirige a Manus-Oauth con state que incluye link_code+chat_id. Si user tiene cookie → procesa linking directo.
- `POST /api/v1/auth/telegram/confirm` — internal endpoint que el callback de OAuth llama después del login para crear la entry en `telegram_links`.

---

## Implementación del bot (Python python-telegram-bot)

```python
from telegram.ext import ContextTypes, CommandHandler

async def link_command(update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # Llamar al backend para iniciar linking
    response = await context.bot_data['http'].post(
        f"{BACKEND_URL}/api/v1/auth/telegram/initiate",
        json={"chat_id": chat_id},
        headers={"X-Bot-Secret": BOT_INTERNAL_SECRET},
    )
    
    if not response.ok:
        await update.message.reply_text(
            "❌ Error iniciando vinculación. Intenta de nuevo."
        )
        return
    
    data = response.json()
    link_url = f"{FRONTEND_URL}/link/manus?code={data['link_code']}&chat_id={chat_id}"
    
    await update.message.reply_text(
        f"🔗 *Vincular cuenta del Monstruo*\n\n"
        f"Abre este link en tu browser:\n{link_url}\n\n"
        f"_El link expira en 10 minutos._",
        parse_mode="Markdown",
    )

async def unlink_command(update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    response = await context.bot_data['http'].delete(
        f"{BACKEND_URL}/api/v1/auth/telegram/unlink",
        params={"chat_id": chat_id},
        headers={"X-Bot-Secret": BOT_INTERNAL_SECRET},
    )
    
    if response.ok:
        await update.message.reply_text("✅ Desvinculado del Monstruo.")
    else:
        await update.message.reply_text("❌ No estabas vinculado.")
```

---

## Naming canónico (DSC-G-004)

Errores específicos del bot:

| Code | Cuándo |
|---|---|
| `auth_telegram_link_code_expired` | User abre link después de 10 min |
| `auth_telegram_link_code_invalid` | Code no existe |
| `auth_telegram_chat_already_linked` | Chat_id ya está vinculado a otro user |
| `auth_telegram_user_already_has_chat` | User ya tiene otro chat_id vinculado |

---

## Caso real

El **Bot del Monstruo en Telegram** (referenciado en skill `el-monstruo-bot`) usa este pattern. Ver `el-monstruo-bot` skill para detalles operacionales del bot deployed en Railway.

— Hilo Catastro, Sprint Catastro-B 2026-05-06
