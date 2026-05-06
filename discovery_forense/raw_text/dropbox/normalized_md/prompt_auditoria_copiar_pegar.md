Necesito que realices una auditoría técnica exhaustiva de tu sandbox y un análisis de fallos de este hilo. El objetivo es diagnosticar cualquier ineficiencia o error para reportar al equipo de soporte de Manus.

## 1. EJECUTA ESTE SCRIPT DE AUDITORÍA TÉCNICA:

Guarda este script como `audit.sh`, hazlo ejecutable y córrelo. Guarda el output.

```bash
#!/bin/bash
echo "============================================================"
echo "    AUDITORÍA SANDBOX MANUS - DIAGNÓSTICO TÉCNICO"
echo "    Fecha y Hora: $(date)"
echo "    Timestamp ISO: $(date -Iseconds)"
echo "============================================================"

echo ""
echo "=== 1. INFORMACIÓN DEL SISTEMA ==="
echo "Kernel: $(uname -a)"
echo "Distribución: $(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d= -f2 | tr -d '"')"
echo "Variables de Entorno Clave:"
env | grep -E 'PATH|HOME|MANUS|USER|SHELL'

echo ""
echo "=== 2. UPTIME Y CARGA ==="
uptime

echo ""
echo "=== 3. MEMORIA Y SWAP ==="
free -h
echo "Swap:"
swapon -s 2>/dev/null || echo "Sin swap activo"

echo ""
echo "=== 4. DISCO ==="
echo "Espacio:"
df -h /home/ubuntu
echo "Inodes:"
df -i /home/ubuntu

echo ""
echo "=== 5. PROCESOS (Top 15 por Memoria y CPU) ==="
echo "--- Por Memoria ---"
ps aux --sort=-%mem | head -n 15
echo ""
echo "--- Por CPU ---"
ps aux --sort=-%cpu | head -n 15

echo ""
echo "=== 6. RED Y CONEXIONES ==="
echo "Puertos Escuchando:"
netstat -tuln 2>/dev/null || ss -tuln
echo ""
echo "Interfaces de Red:"
ip -brief addr show 2>/dev/null

echo ""
echo "=== 6B. DIAGNÓSTICO RED AVANZADO ==="
echo "Test HTTP saliente:"
timeout 5s curl -s -o /dev/null -w "%{http_code}" http://www.google.com 2>&1 || echo "No outbound HTTP"
echo ""
echo "Conexiones TIME_WAIT:"
netstat -an 2>/dev/null | grep TIME_WAIT | wc -l || ss -an | grep TIME-WAIT | wc -l || echo "0"
echo "DNS Resolution Test:"
nslookup google.com 2>/dev/null | grep -A1 "Name:" | head -2 || echo "DNS failed"

echo ""
echo "=== 6C. I/O Y RENDIMIENTO ==="
vmstat 1 3 2>/dev/null || echo "vmstat no disponible"

echo ""
echo "=== 6D. PROCESOS ZOMBIES ==="
ps aux | awk '$8 ~ /Z/ {print}' || echo "No hay procesos zombies"

echo ""
echo "=== 7. ARCHIVOS EN HOME (con fechas) ==="
ls -laht /home/ubuntu/ --time-style=long-iso

echo ""
echo "=== 8. ARCHIVOS MODIFICADOS ÚLTIMOS 3 DÍAS ==="
find /home/ubuntu -maxdepth 3 -type f -mtime -3 -ls 2>/dev/null

echo ""
echo "=== 9. TAMAÑO DIRECTORIO NAVEGADOR ==="
du -sh ~/.browser_data_dir/ 2>/dev/null || echo "No existe"

echo ""
echo "=== 10. MENSAJES DEL KERNEL (últimos 20) ==="
dmesg 2>/dev/null | tail -n 20 || echo "Sin acceso a dmesg"

echo ""
echo "=== 11. LOGS DEL SISTEMA (últimas 30 líneas) ==="
journalctl -n 30 --no-pager 2>/dev/null || tail -n 30 /var/log/syslog 2>/dev/null || echo "Sin acceso a logs"

echo ""
echo "=== 12. LÍMITES DEL SISTEMA ==="
ulimit -a

echo ""
echo "=== 13. ESTADO DE CONTENEDOR/SANDBOX ==="
cat /proc/1/cgroup 2>/dev/null | tail -n 5 || echo "No cgroup info"
mount | grep -E '(docker|overlay|tmpfs)' 2>/dev/null | head -5 || echo "No container mounts detectados"

echo ""
echo "=== 14. PYTHON Y VERSIONES ==="
echo "Python: $(python3 --version 2>/dev/null || echo 'No disponible')"
echo "Node: $(node --version 2>/dev/null || echo 'No disponible')"
echo "Paquetes pip (top 20):"
pip3 list --format=freeze 2>/dev/null | head -n 20 || echo "No pip"

echo ""
echo "=== 15. PROCESOS DE NAVEGADOR ==="
pgrep -a -f chromium 2>/dev/null || pgrep -a -f chrome 2>/dev/null || echo "No browser processes"

echo ""
echo "=== 16. MÉTRICAS RESUMEN ==="
echo "CPU Load: $(uptime | awk -F'load average:' '{print $2}' | cut -d',' -f1 | tr -d ' ')"
echo "Memoria Usada %: $(free | awk 'NR==2{printf "%.1f", $3*100/$2}')"
echo "Disco Usado %: $(df /home/ubuntu | awk 'NR==2{print $5}')"
echo "# Procesos: $(ps aux | wc -l)"
echo "# Errores kernel: $(dmesg 2>/dev/null | grep -i error | wc -l || echo 0)"

echo ""
echo "============================================================"
echo "    FIN AUDITORÍA TÉCNICA - $(date)"
echo "============================================================"
```

## 2. GENERA UN INFORME DE AUTO-ANÁLISIS Y FALLOS

Analiza la ejecución de este hilo y genera un informe estructurado con las siguientes secciones obligatorias. Sé lo más objetivo y detallado posible.

### A. RESUMEN DEL HILO
- **Tarea Original Solicitada:** [Describe la tarea inicial con tus propias palabras]
- **Tiempo Total Activo del Hilo:** [Basado en uptime y fechas de archivos - en horas/días]
- **# de Pasos/Tareas ejecutadas:** [Cuenta aproximada]
- **Herramientas usadas:** [shell, browser, search, file, etc.]
- **Estado de la Tarea:** [Completada / Parcialmente Completada / Fallida]
- **Conclusión Breve:** ¿Se logró el objetivo? ¿Por qué sí o no?

### B. ANÁLISIS DE RENDIMIENTO Y TIEMPOS
- **Tiempo Estimado Ideal (sin fallos):** [minutos]
- **Tiempo Real Transcurrido:** [minutos/horas/días]
- **Ratio de Eficiencia:** (Tiempo Estimado / Tiempo Real) * 100
- **Tiempo Perdido en Esperas/Fallos:** [estimación]
- **Latencia en tool calls:** [¿Hubo llamadas >30s? Indica ineficiencia]

### C. MÉTRICAS PARA SOPORTE

| Métrica | Valor Actual | Baseline Esperado | ¿Anómalo? |
|---------|--------------|-------------------|-----------|
| Memoria Usada % | XX% | <80% | Sí/No |
| CPU Load Avg | XX | <2.0 | Sí/No |
| Disco Usado % | XX% | <80% | Sí/No |
| Tamaño browser_data_dir | XX MB | <200MB | Sí/No |
| # Errores Tool Calls | XX | 0 | Sí/No |
| Tiempo Total Hilo | XX min | <30 min | Sí/No |
| # Reintentos fallidos | XX | 0 | Sí/No |

### D. ANÁLISIS DE FALLOS CON CAUSA RAÍZ

Lista TODOS los fallos, errores o interrupciones. Para cada uno, aplica análisis de Causa Raíz (pregunta "¿Por qué?" al menos 3 veces).

| # | Fallo Identificado | Herramienta Afectada | Mensaje/Síntoma | Causa Raíz (¿Por qué? x3) |
|---|-------------------|---------------------|-----------------|---------------------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

### E. COMPORTAMIENTOS ANORMALES E INEFICIENCIAS

Detalla cualquier comportamiento que fue pérdida de tiempo o desviación del camino óptimo:

- **Loops o Retries Excesivos (>3):** [Describe si intentaste algo múltiples veces sin éxito]
- **Navegador:** [Tiempos de carga excesivos, páginas que no cargan, interrupciones]
- **Búsquedas Ineficientes:** [Términos ambiguos, resultados no útiles, búsquedas repetidas]
- **Herramientas que fallaron repetidamente:** [browser_navigate, search, shell, etc.]
- **Procesos Zombies o Conexiones Colgantes:** [Si los detectaste en la auditoría]
- **Uso excesivo de browser_data_dir:** [Si >500MB, indica problema]

### F. RECOMENDACIONES PRIORIZADAS

Top 5 acciones para mejorar, con severidad:

| # | Recomendación | Severidad | Para Quién |
|---|---------------|-----------|------------|
| 1 | | Alta/Media/Baja | Usuario/Sistema/Manus |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

### G. TEMPLATE PARA TICKET DE SOPORTE

```
BUG REPORT - MANUS
==================
Título: [Resumen del problema principal]
Session/Hilo: [Nombre o identificador]
Fecha: [Fecha de la auditoría]
Duración del hilo: [Tiempo total]
Estado: [Completada/Fallida/Parcial]

Problema Principal:
[Descripción en 2-3 oraciones]

Métricas Clave:
- CPU Load: XX
- Memoria: XX%
- Disco: XX%
- # Errores: XX

Pasos para Reproducir:
1. [Paso 1]
2. [Paso 2]
3. [Paso 3]

Comportamiento Esperado:
[Qué debería haber pasado]

Comportamiento Actual:
[Qué pasó realmente]

Logs/Output Relevante:
[Incluir fragmentos clave]
```

## 3. FORMATO DE ENTREGA

Guarda TODO (output del script de auditoría + informe de auto-análisis) en un único archivo llamado:

**`auditoria_completa_hilo_[NOMBRE]_[FECHA].md`**

Donde:
- [NOMBRE] = palabra que identifique este hilo (ej: "vuelos", "website", "investigacion")
- [FECHA] = fecha en formato YYYYMMDD

Comparte el archivo conmigo cuando termines.
