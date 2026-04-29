# Runbook: Deploy a producción

## Deploy automático (normal)

Railway hace auto-deploy cuando se pushea a `main` en GitHub.

```bash
cd /home/ubuntu/like-kukulkan-tickets
git add -A && git commit -m "feat: descripción del cambio"
git push origin main
```

Railway detecta el push y deploya automáticamente. Verificar con:
```bash
python3 /home/ubuntu/skills/ticketlike-ops/scripts/railway_status.py
```

## Deploy manual (si auto-deploy no funciona)

```bash
python3 /home/ubuntu/skills/ticketlike-ops/scripts/railway_redeploy.py
```

## Verificación post-deploy

1. Verificar que Railway muestra status SUCCESS: `python3 scripts/railway_status.py`
2. Verificar que el sitio responde: `curl -s -o /dev/null -w "%{http_code}" https://ticketlike.mx/`
3. Verificar que la API responde: `curl -s "https://ticketlike.mx/api/trpc/events.listWithInventory" | python3 -m json.tool | head -20`
4. Verificar que el admin panel carga: `curl -s -o /dev/null -w "%{http_code}" https://ticketlike.mx/admin`

## Rollback

Railway permite revertir a un deploy anterior desde su dashboard. Si necesitas rollback:
1. Ir a Railway dashboard (o usar API GraphQL)
2. Encontrar el deploy anterior exitoso
3. Hacer rollback a ese deploy

## Clonar el repo (si no existe en el sandbox)

```bash
gh repo clone alfredogl1804/like-kukulkan-tickets /home/ubuntu/like-kukulkan-tickets
```
