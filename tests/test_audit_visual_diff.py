# tests/test_audit_visual_diff.py
"""
Tests del auditor visual (DSC-V-002).

Verifican que el score discrimina template (cascaron) de paginas diferenciadas.
NO requiere red — patcheamos `_fetch` para inyectar HTML sintetico.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest import mock

# Permite correr este test ejecutando directamente: python tests/test_audit_visual_diff.py
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import scripts.audit_visual_diff as avd  # noqa: E402


# ---- Fixtures: HTML sintetico ----

TEMPLATE_HTML = """
<!DOCTYPE html>
<html><head><title>{vertical} | El Monstruo</title></head>
<body>
  <h1>Bienvenido a El Monstruo {vertical}</h1>
  <h2>La mejor solucion del mundo</h2>
  <p>Construimos software de calidad Apple Tesla soberano premium magnanimo
  implacable preciso para tu negocio digital.</p>
  <h2>Nuestro plan</h2>
  <p>Implementamos las 7 capas transversales en cada producto vertical: ventas,
  SEO, publicidad, tendencias, operaciones, finanzas y resiliencia.</p>
  <button>Empezar ahora</button>
  <button>Hablar con ventas</button>
  <a href="#">Ver demo</a>
</body></html>
"""

# Tres paginas TEMPLATE (solo cambia {vertical})
TEMPLATE_PAGES = [
    ("interiorismo", TEMPLATE_HTML.format(vertical="Interiorismo")),
    ("bioguard",     TEMPLATE_HTML.format(vertical="BioGuard")),
    ("cip",          TEMPLATE_HTML.format(vertical="CIP")),
]


# Tres paginas DIFERENCIADAS (copy genuino per vertical)
DIFFERENTIATED_PAGES = [
    ("interiorismo", """
        <html><head><title>Disena tu hogar con interioristas verificados</title></head>
        <body>
          <h1>Encuentra interioristas en tu ciudad</h1>
          <h2>Catalogo curado de proyectos residenciales</h2>
          <p>Visualiza renders 3D antes de contratar. Compara estilos
          escandinavo industrial mediterraneo. Marketplace transparente con
          precios fijos por metro cuadrado y entrega garantizada.</p>
          <h2>Como funciona</h2>
          <p>Sube fotos de tu espacio, recibes propuestas en 48 horas,
          contratas con escrow y firmas digitalmente.</p>
          <button>Subir foto de mi espacio</button>
          <button>Explorar catalogo</button>
        </body></html>
    """),
    ("bioguard", """
        <html><head><title>Defensa biologica adversarial - BioGuard</title></head>
        <body>
          <h1>Detecta amenazas biologicas en tiempo real</h1>
          <h2>Sensor wearable para personal de primera respuesta</h2>
          <p>Espectroscopia Raman miniaturizada que clasifica patogenos
          aerosolizados en 200 milisegundos. Conectado al modelo causal
          predictivo via LoRa mesh resistente a jamming.</p>
          <h2>Para quien</h2>
          <p>Bomberos hazmat, equipos forenses, investigadores de campo
          en zonas con riesgo de exposicion bacteriologica o quimica.</p>
          <button>Solicitar demo BSL-2</button>
          <button>Especificaciones tecnicas</button>
        </body></html>
    """),
    ("cip", """
        <html><head><title>CIP - Cumplimiento fiscal mexicano automatizado</title></head>
        <body>
          <h1>Factura emite y concilia en SAT sin intervencion</h1>
          <h2>Para PYMES con ingresos menores a 35 millones MXN</h2>
          <p>Conexion directa al Buzon Tributario. Genera CFDI 4.0 con
          complementos carta porte nomina y pagos. Reconcilia movimientos
          bancarios con Banxico SPEI y emite declaraciones provisionales
          mensuales sin contador.</p>
          <h2>Integraciones</h2>
          <p>Bancomer Banamex Santander HSBC. Sincroniza con Contpaq
          Aspel SAE y exporta XML para auditoria del SAT.</p>
          <button>Conectar mi banco</button>
          <button>Ver casos de exito</button>
        </body></html>
    """),
]


def _make_fake_fetch(pages_dict):
    """Devuelve un _fetch que sirve HTML desde un dict {url: html_string}."""
    def _fake(url, timeout=30):
        if url in pages_dict:
            body = pages_dict[url].encode("utf-8")
            return True, 200, body, None
        return False, 404, b"", "url no fixture"
    return _fake


def _run_with_fixtures(pages):
    fixtures = {
        f"https://example.com/{vertical}": html for vertical, html in pages
    }
    urls_payload = {
        "verticals": [
            {"vertical": v, "url": f"https://example.com/{v}"} for v, _ in pages
        ]
    }
    urls_path = ROOT / "reports" / "_test_urls.json"
    output_path = ROOT / "reports" / "_test_output.json"
    urls_path.parent.mkdir(parents=True, exist_ok=True)
    urls_path.write_text(json.dumps(urls_payload))

    with mock.patch.object(avd, "_fetch", _make_fake_fetch(fixtures)):
        passed, result = avd.audit(urls_path, min_score=75.0, output_file=output_path)
    return passed, result


def test_template_pages_score_low():
    passed, result = _run_with_fixtures(TEMPLATE_PAGES)
    score = result["differentiation_score"]
    template_ratio = result["metrics"]["template_ratio"]

    print(f"[template] differentiation_score={score} template_ratio={template_ratio}")
    print(f"           interpretacion: {result['interpretacion']}")

    assert not passed, f"Template paginas DEBEN fallar el audit. score={score}"
    assert score < 75.0, f"score debe ser <75 para template. score={score}"
    assert template_ratio > 0.4, (
        f"template_ratio debe ser >0.4 para template. ratio={template_ratio}"
    )


def test_differentiated_pages_score_high():
    passed, result = _run_with_fixtures(DIFFERENTIATED_PAGES)
    score = result["differentiation_score"]
    template_ratio = result["metrics"]["template_ratio"]

    print(f"[diferenciado] differentiation_score={score} template_ratio={template_ratio}")
    print(f"               interpretacion: {result['interpretacion']}")

    assert passed, f"Paginas diferenciadas deben pasar el audit. score={score}"
    assert score >= 75.0, f"score debe ser >=75. score={score}"
    assert template_ratio < 0.3, (
        f"template_ratio debe ser <0.3 para paginas diferenciadas. ratio={template_ratio}"
    )


def test_pair_count_correct():
    """3 paginas → 3 pares (n*(n-1)/2)."""
    _, result = _run_with_fixtures(DIFFERENTIATED_PAGES)
    assert len(result["metrics"]["per_pair"]) == 3, (
        f"3 paginas deben producir 3 pares. got={len(result['metrics']['per_pair'])}"
    )


if __name__ == "__main__":
    test_template_pages_score_low()
    test_differentiated_pages_score_high()
    test_pair_count_correct()
    print("\n[ok] Los 3 tests pasaron.")
