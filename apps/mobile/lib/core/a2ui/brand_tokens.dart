/// A2UI Brand DNA Tokens — canon literal del Monstruo.
///
/// Origen: `bridge/a2ui_spec_draft_FIRMADO_2026_05_11.md` + DSC-G-004.
///
/// NUNCA improvisar paleta. Si necesitas un color nuevo, propone
/// cambio al `bridge/` y espera firma de Cowork antes de extender.
library;

import 'package:flutter/material.dart';

/// Brand DNA literal del Monstruo.
class A2UIBrand {
  A2UIBrand._();

  // Colores base canon firmado.
  static const Color forja = Color(0xFFF97316); // naranja forja (acento, CTA)
  static const Color graphite = Color(0xFF1C1917); // fondo / superficies
  static const Color acero = Color(0xFFA8A29E); // texto secundario / borders

  // Derivados consistentes para superficies (mantienen DNA).
  static const Color graphiteSurface = Color(0xFF26221F);
  static const Color graphiteSurfaceHigh = Color(0xFF332D29);
  static const Color textPrimary = Color(0xFFF5F5F4);
  static const Color textSecondary = acero;
  static const Color border = Color(0xFF44403C);

  // Semánticos discretos (uso solo cuando el widget lo requiere semánticamente).
  static const Color success = Color(0xFF65A30D);
  static const Color warning = Color(0xFFF59E0B);
  static const Color danger = Color(0xFFDC2626);
  static const Color info = Color(0xFF2563EB);

  // Spacing canon (escala 4pt).
  static const double s2 = 2;
  static const double s4 = 4;
  static const double s8 = 8;
  static const double s12 = 12;
  static const double s16 = 16;
  static const double s24 = 24;
  static const double s32 = 32;

  // Radius canon.
  static const double rSm = 6;
  static const double rMd = 10;
  static const double rLg = 14;

  // Tipografía base.
  static const TextStyle titleLg = TextStyle(
    fontSize: 20,
    fontWeight: FontWeight.w700,
    color: textPrimary,
    height: 1.25,
  );
  static const TextStyle titleMd = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w600,
    color: textPrimary,
    height: 1.3,
  );
  static const TextStyle body = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.w400,
    color: textPrimary,
    height: 1.4,
  );
  static const TextStyle caption = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w500,
    color: textSecondary,
    height: 1.3,
  );
  static const TextStyle code = TextStyle(
    fontSize: 13,
    fontFamily: 'monospace',
    color: textPrimary,
    height: 1.4,
  );
}
