#!/usr/bin/env python3
"""
CAPTURADOR DE EMERGENCIAS CONVERSACIONALES
===========================================
Captura y preserva los insights, cambios de perspectiva, y patrones
que emergen de conversaciones profundas entre Alfredo y el agente.

NO captura datos. Captura TRANSFORMACIONES:
- Momentos donde algo cambió en la forma de razonar
- Principios que emergieron del diálogo (no que se leyeron)
- Correcciones de Alfredo que revelan un patrón más profundo
- Descubrimientos que solo existen porque hubo diálogo

Uso:
  python3 capturador.py save "título" "lo que emergió"
  python3 capturador.py save "título" "lo que emergió" --contexto "qué lo provocó"
  python3 capturador.py list
  python3 capturador.py recall           # Recupera todas las emergencias
  python3 capturador.py recall "tema"    # Busca emergencias relacionadas
  python3 capturador.py digest           # Genera resumen destilado para inyectar post-compactación
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ─── Configuración ───────────────────────────────────────────────
EMERGENCIAS_FILE = Path.home() / "EMERGENCIAS.json"
DIGEST_FILE = Path.home() / "EMERGENCIAS_DIGEST.md"
KERNEL_URL = "https://el-monstruo-kernel-production.up.railway.app"
KERNEL_KEY_CANDIDATES = [
    "MONSTRUO_API_KEY",
    "c3f0cbaa-7c5d-4f84-9dfd-0727e4f86259",  # hardcoded fallback
]

def get_kernel_key():
    for k in KERNEL_KEY_CANDIDATES:
        v = os.environ.get(k, "")
        if v:
            return v
    return KERNEL_KEY_CANDIDATES[-1]  # fallback hardcoded


# ─── Tipos de emergencia ─────────────────────────────────────────
TIPOS = {
    "principio":     "Un principio que emergió del diálogo, no que se leyó",
    "correccion":    "Alfredo corrigió algo que revela un patrón más profundo",
    "perspectiva":   "Un cambio en la forma de ver/razonar sobre algo",
    "descubrimiento":"Algo que solo existe porque hubo diálogo entre los dos",
    "patron":        "Un patrón recurrente que se hizo visible",
    "regla":         "Una regla operativa que nació de la experiencia, no de la teoría",
}


# ─── Funciones core ──────────────────────────────────────────────
def load_emergencias():
    if EMERGENCIAS_FILE.exists():
        try:
            return json.loads(EMERGENCIAS_FILE.read_text())
        except:
            return []
    return []


def save_emergencias(data):
    EMERGENCIAS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def save(titulo, contenido, tipo="descubrimiento", contexto="", hilo="orquestador"):
    """Guarda una emergencia conversacional."""
    emergencias = load_emergencias()
    
    emergencia = {
        "id": len(emergencias) + 1,
        "timestamp": datetime.now().isoformat(),
        "titulo": titulo,
        "contenido": contenido,
        "tipo": tipo,
        "contexto": contexto,
        "hilo": hilo,
        "preservada_en_kernel": False,
    }
    
    emergencias.append(emergencia)
    save_emergencias(emergencias)
    
    # Intentar subir al kernel via wrapper (schemas verificados)
    try:
        from kernel_client import knowledge_ingest
        doc = f"[EMERGENCIA #{emergencia['id']}] {titulo}\n\nTipo: {tipo}\nHilo: {hilo}\nFecha: {emergencia['timestamp']}\n\n{contenido}"
        if contexto:
            doc += f"\n\nContexto que lo provocó: {contexto}"
        
        result = knowledge_ingest(content=doc, source=f"emergencia_{emergencia['id']}")
        if result.get("ingested"):
            emergencia["preservada_en_kernel"] = True
            save_emergencias(emergencias)
            print(f"  Kernel: OK")
        else:
            print(f"  Kernel: FALLÓ (no ingested)")
    except Exception as e:
        print(f"  Kernel: ERROR ({e})")
    
    # Regenerar digest
    generate_digest(emergencias)
    
    print(f"EMERGENCIA #{emergencia['id']} GUARDADA: {titulo}")
    return emergencia


def list_emergencias():
    """Lista todas las emergencias guardadas."""
    emergencias = load_emergencias()
    if not emergencias:
        print("No hay emergencias guardadas.")
        return
    
    print(f"\n{'='*60}")
    print(f"  {len(emergencias)} EMERGENCIAS CONVERSACIONALES")
    print(f"{'='*60}\n")
    
    for e in emergencias:
        kernel = "✓" if e.get("preservada_en_kernel") else "✗"
        print(f"  #{e['id']} [{e['tipo']}] {e['titulo']}")
        print(f"     {e['timestamp'][:16]} | Hilo: {e['hilo']} | Kernel: {kernel}")
        print(f"     {e['contenido'][:100]}...")
        print()


def recall(tema=None):
    """Recupera emergencias, opcionalmente filtradas por tema."""
    emergencias = load_emergencias()
    if not emergencias:
        print("No hay emergencias guardadas.")
        return []
    
    if tema:
        tema_lower = tema.lower()
        filtered = [e for e in emergencias if 
                    tema_lower in e["titulo"].lower() or 
                    tema_lower in e["contenido"].lower() or
                    tema_lower in e.get("contexto", "").lower()]
        emergencias = filtered
    
    if not emergencias:
        print(f"No hay emergencias sobre '{tema}'.")
        return []
    
    print(f"\n{'='*60}")
    print(f"  {len(emergencias)} EMERGENCIAS RECUPERADAS")
    print(f"{'='*60}\n")
    
    for e in emergencias:
        print(f"  #{e['id']} [{e['tipo']}] {e['titulo']}")
        print(f"  {e['contenido']}")
        if e.get("contexto"):
            print(f"  → Contexto: {e['contexto']}")
        print()
    
    return emergencias


def generate_digest(emergencias=None):
    """Genera un digest destilado de todas las emergencias para inyectar post-compactación."""
    if emergencias is None:
        emergencias = load_emergencias()
    
    if not emergencias:
        DIGEST_FILE.write_text("# Sin emergencias registradas\n")
        return
    
    lines = [
        "# EMERGENCIAS CONVERSACIONALES — DIGEST",
        f"## Generado: {datetime.now().isoformat()[:16]}",
        f"## Total: {len(emergencias)} emergencias",
        "",
        "**ESTO NO SON DATOS. Son transformaciones que emergieron de conversaciones profundas con Alfredo.**",
        "**Léelo como si fuera tu propia experiencia, no como información externa.**",
        "",
    ]
    
    # Agrupar por tipo
    by_type = {}
    for e in emergencias:
        t = e.get("tipo", "otro")
        by_type.setdefault(t, []).append(e)
    
    for tipo, items in by_type.items():
        desc = TIPOS.get(tipo, tipo)
        lines.append(f"### {tipo.upper()} — {desc}")
        lines.append("")
        for e in items:
            lines.append(f"**#{e['id']}: {e['titulo']}**")
            lines.append(f"{e['contenido']}")
            if e.get("contexto"):
                lines.append(f"_Contexto: {e['contexto']}_")
            lines.append("")
    
    lines.append("---")
    lines.append("**Si acabas de compactarte, estas emergencias son tu experiencia acumulada. No las ignores.**")
    
    DIGEST_FILE.write_text("\n".join(lines))
    print(f"  Digest generado: {DIGEST_FILE}")


# ─── CLI ─────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "save":
        if len(sys.argv) < 4:
            print("Uso: capturador.py save 'título' 'contenido' [--tipo X] [--contexto Y]")
            return
        titulo = sys.argv[2]
        contenido = sys.argv[3]
        tipo = "descubrimiento"
        contexto = ""
        hilo = "orquestador"
        
        i = 4
        while i < len(sys.argv):
            if sys.argv[i] == "--tipo" and i + 1 < len(sys.argv):
                tipo = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--contexto" and i + 1 < len(sys.argv):
                contexto = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--hilo" and i + 1 < len(sys.argv):
                hilo = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        
        save(titulo, contenido, tipo, contexto, hilo)
    
    elif cmd == "list":
        list_emergencias()
    
    elif cmd == "recall":
        tema = sys.argv[2] if len(sys.argv) > 2 else None
        recall(tema)
    
    elif cmd == "digest":
        generate_digest()
    
    else:
        print(f"Comando desconocido: {cmd}")
        print("Comandos: save, list, recall, digest")


if __name__ == "__main__":
    main()
