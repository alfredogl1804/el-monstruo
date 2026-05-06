#!/usr/bin/env python3
"""Download SOP/EPIA pair files from Dropbox using DROPBOX_API_KEY env."""
import os
import json
from pathlib import Path
import dropbox

OUT_DIR = Path("/home/ubuntu/discovery_2026_05_05/sop_epia_diff/dropbox")
OUT_DIR.mkdir(parents=True, exist_ok=True)

FILES = [
    ("/ENTREGABLE 2 \u2014 DOCUMENTO FUNDACIONAL SOP.docx", "ENTREGABLE_2_SOP_DBX.docx"),
    ("/EPIA \u2014 DOCUMENTO FUNDACIONAL MAESTRO.docx", "EPIA_FUNDACIONAL_DBX.docx"),
    ("/EPIA \u2014 DOCUMENTO FUNDACIONAL MAESTRO.md", "EPIA_FUNDACIONAL_DBX.md"),
    ("/ENTREGABLE 2 \u2014 DOCUMENTO FUNDACIONAL SOP.md", "ENTREGABLE_2_SOP_DBX.md"),
    ("/Genealog\u00eda Evolutiva del Ecosistema SOP y EPIA.docx", "GENEALOGIA_SOP_EPIA_DBX.docx"),
    ("/AUDITOR\u00cdA FINAL DEL SOP \u2014 6 SABIOS DE SEMILLA v7.3.md", "AUDITORIA_SOP_6SABIOS_DBX.md"),
    ("/Repositorio_Maestro_SOP_EPIA_v4_0_Live.docx", "REPOSITORIO_MAESTRO_SOP_EPIA_DBX.docx"),
    ("/SOP+EPIA \u2014 REESTRUCTURACI\u00d3N Y EVOLUCI\u00d3N (Abril 2026).md", "SOP_EPIA_REESTRUCTURACION_DBX.md"),
]

def parse_creds():
    blob = os.environ["DROPBOX_API_KEY"]
    parts = {}
    for tok in blob.split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            parts[k] = v
    return parts["DROPBOX_REFRESH_TOKEN"], parts["DROPBOX_APP_KEY"], parts["DROPBOX_APP_SECRET"]


def main():
    refresh, app_key, app_secret = parse_creds()
    dbx = dropbox.Dropbox(
        oauth2_refresh_token=refresh,
        app_key=app_key,
        app_secret=app_secret,
    )
    print(f"Authenticated as: {dbx.users_get_current_account().email}")
    for src, dst in FILES:
        out = OUT_DIR / dst
        try:
            md, res = dbx.files_download(src)
            out.write_bytes(res.content)
            print(f"  OK  {dst:55s} ({len(res.content)} bytes)")
        except Exception as e:
            print(f"  ERR {dst:55s} -> {type(e).__name__}: {str(e)[:120]}")

if __name__ == "__main__":
    main()
