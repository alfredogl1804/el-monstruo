# Sistema de Memoria Persistente + Anti-Boicoteo

## Problema que resuelve

Los hilos de Manus pierden contexto al compactarse o al crearse nuevos. Esto causa:
- Uso de modelos obsoletos (gpt-4o en vez de gpt-5.5)
- Sobrescritura de código que ya funcionaba
- Ignorar decisiones arquitectónicas ya tomadas
- Pérdida de tiempo reparando lo que otros hilos rompieron

## Instalación en cualquier hilo nuevo

```bash
gh repo clone alfredogl1804/el-monstruo ~/el-monstruo && bash ~/el-monstruo/monstruo-memoria/bootstrap.sh
```

## Scripts

| Script | Función |
|--------|---------|
| `bootstrap.sh` | Instala todo en un hilo nuevo (un solo comando) |
| `guardia.py` | Valida reglas duras, detecta violaciones, bloquea boicoteo |
| `monstruo.py` | Maestro: detecta compactación, ejecuta inject/heartbeat |
| `inject.py` | Recupera contexto del kernel + archivos locales |
| `heartbeat.py` | Guarda estado actual en RECOVERY.md + kernel |
| `legacy.py` | Deposita conocimiento en kernel antes de morir |

## Uso diario

```bash
# Al arrancar cualquier hilo:
python3 ~/el-monstruo/monstruo-memoria/guardia.py

# Antes de escribir código del Monstruo:
python3 ~/el-monstruo/monstruo-memoria/guardia.py scan <archivo>

# Cada 15 minutos:
python3 ~/el-monstruo/monstruo-memoria/heartbeat.py

# Antes de cerrar el hilo:
python3 ~/el-monstruo/monstruo-memoria/legacy.py "resumen"
```

## Cómo actualizar reglas

Las reglas duras viven en `guardia.py` como código Python. Para cambiarlas:
1. Editar `REGLAS` en `guardia.py`
2. Push a GitHub
3. Los hilos nuevos las obtienen automáticamente al clonar

NO se actualizan por texto. Solo por código.
