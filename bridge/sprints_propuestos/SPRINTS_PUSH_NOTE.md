# Note: contenido completo de specs en local Mac de Alfredo

Los 5 specs de sprints + README magna fueron escritos localmente en
`~/el-monstruo/bridge/sprints_propuestos/` durante sesión Cowork 2026-05-06.
Total ~58KB / 1229 líneas.

GitHub MCP trunca payloads >30KB silenciosamente, por lo que este push solo
contiene markers. Para tener los specs completos en `origin/main`, Alfredo
debe ejecutar el flow de recovery con git CLI (igual que hizo con v1.1 y
v1.2 del documento de visión):

```bash
cd ~/el-monstruo
git fetch origin main
git reset --hard origin/main
# tus 6 archivos en bridge/sprints_propuestos/ se mantienen porque son untracked locales
ls bridge/sprints_propuestos/  # debe mostrar los 6 archivos
wc -l bridge/sprints_propuestos/*.md  # debe sumar 1229 líneas

git add bridge/sprints_propuestos/
git commit -m "feat(cowork-fase3): 5 specs sprints largos completos (recovery push)"
git push origin main
```

Si por algún motivo los archivos no están locales (Cowork sandbox limpio),
Manus puede regenerarlos desde el contexto del bridge anterior + el commit
de audit del Sprint 87.2.

Cowork (Hilo A) — 2026-05-06
