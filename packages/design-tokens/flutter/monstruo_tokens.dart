// El Monstruo — Tokens Canónicos para Flutter
//
// Espejo Dart de packages/design-tokens/src/colors.ts.
// Source of truth: kernel/brand/brand_dna.py.
//
// Uso (en Sprint Mobile 1, recovery del theme actual que viola DSC-G-004):
//   import 'package:el_monstruo/tokens/monstruo_tokens.dart';
//   color: MonstruoTokens.forja[500]
//
// Naming inviolable (DSC-G-004): NUNCA `primary`, `secondary`, `tertiary`.

import 'package:flutter/material.dart';

class MonstruoTokens {
  MonstruoTokens._();

  // ── Forja (Naranja Forja) ─────────────────────────────────
  static const Map<int, Color> forja = {
    50: Color(0xFFFFF4ED),
    100: Color(0xFFFFE6D2),
    200: Color(0xFFFFC8A0),
    300: Color(0xFFFDA468),
    400: Color(0xFFFB8B3C),
    500: Color(0xFFF97316),
    600: Color(0xFFD75D0C),
    700: Color(0xFFA94609),
    800: Color(0xFF7B3306),
    900: Color(0xFF4D1F03),
  };

  // ── Graphite (Metal Templado) ─────────────────────────────
  static const Map<int, Color> graphite = {
    50: Color(0xFFF4F3F2),
    100: Color(0xFFE2E0DD),
    200: Color(0xFFBFBBB5),
    300: Color(0xFF8C857C),
    400: Color(0xFF5A554E),
    500: Color(0xFF3D3934),
    600: Color(0xFF2C2925),
    700: Color(0xFF1C1917),
    800: Color(0xFF14110F),
    900: Color(0xFF0A0807),
  };

  // ── Acero (Neutro Medio) ──────────────────────────────────
  static const Map<int, Color> acero = {
    50: Color(0xFFF7F7F6),
    100: Color(0xFFEBEAE8),
    200: Color(0xFFD2D0CD),
    300: Color(0xFFBBB8B4),
    400: Color(0xFFA8A29E),
    500: Color(0xFF8C8682),
    600: Color(0xFF6E6864),
    700: Color(0xFF524C49),
    800: Color(0xFF36322F),
    900: Color(0xFF1A1816),
  };

  // ── Estados ───────────────────────────────────────────────
  static const Color forjaQuemado = Color(0xFFC0392B); // rojo error
  static const Color patinaAcero = Color(0xFF2D6A4F); // verde success

  // ── Tokens semánticos ─────────────────────────────────────
  static Color get textDefault => acero[100]!;
  static Color get textSoft => acero[300]!;
  static Color get textMuted => acero[500]!;
  static Color get textOnForja => graphite[800]!;

  static Color get bgCanvas => graphite[700]!;
  static Color get bgElevated => graphite[600]!;
  static Color get bgRecessed => graphite[800]!;

  static Color get borderDefault => graphite[500]!;
  static Color get borderStrong => graphite[400]!;
  static Color get borderForja => forja[500]!;

  static Color get stateAction => forja[500]!;
  static Color get stateActionHover => forja[400]!;
  static Color get stateActionPressed => forja[600]!;
  static Color get stateError => forjaQuemado;
  static Color get stateSuccess => patinaAcero;
  static Color get stateWarn => forja[300]!;

  // ── Tipografía (familias canónicas) ───────────────────────
  // Uso con google_fonts:
  //   GoogleFonts.bebasNeue(...)  // display
  //   GoogleFonts.inter(...)       // body
  //   GoogleFonts.jetBrainsMono(...) // mono
  static const String fontDisplay = 'Bebas Neue';
  static const String fontBody = 'Inter';
  static const String fontMono = 'JetBrains Mono';

  // ── Spacing (px) ──────────────────────────────────────────
  static const double space0 = 0;
  static const double space0_5 = 2;
  static const double space1 = 4;
  static const double space1_5 = 6;
  static const double space2 = 8;
  static const double space3 = 12;
  static const double space4 = 16;
  static const double space5 = 20;
  static const double space6 = 24;
  static const double space8 = 32;
  static const double space10 = 40;
  static const double space12 = 48;
  static const double space16 = 64;
  static const double space20 = 80;
  static const double space24 = 96;
  static const double space32 = 128;

  // ── Radius (px) ───────────────────────────────────────────
  static const double radiusNone = 0;
  static const double radiusSm = 4;
  static const double radiusMd = 8;
  static const double radiusLg = 12;
  static const double radiusXl = 16;
  static const double radius2xl = 24;
  static const double radiusFull = 9999;

  // ── Animation durations ───────────────────────────────────
  static const Duration durationInstant = Duration(milliseconds: 60);
  static const Duration durationQuick = Duration(milliseconds: 120);
  static const Duration durationSteady = Duration(milliseconds: 240);
  static const Duration durationAmple = Duration(milliseconds: 400);
  static const Duration durationMassive = Duration(milliseconds: 640);
  static const Duration durationForge = Duration(milliseconds: 960);

  // ── Easing curves ─────────────────────────────────────────
  static const Curve easingIngot = Cubic(0.16, 0.84, 0.44, 1.0);
  static const Curve easingExtract = Cubic(0.55, 0, 0.84, 0.16);
  static const Curve easingStandard = Cubic(0.4, 0, 0.2, 1.0);
  static const Curve easingSpark = Cubic(0.7, 0, 0.3, 1.0);

  // ── Shadows con identidad ─────────────────────────────────
  static List<BoxShadow> get ember1 => [
        const BoxShadow(
          color: Color(0x66000000), // 40% black
          blurRadius: 2,
          offset: Offset(0, 1),
        ),
      ];

  static List<BoxShadow> get ember2 => [
        const BoxShadow(
          color: Color(0x80000000), // 50% black
          blurRadius: 8,
          offset: Offset(0, 4),
          spreadRadius: -2,
        ),
        const BoxShadow(
          color: Color(0x4D000000), // 30% black
          blurRadius: 4,
          offset: Offset(0, 2),
          spreadRadius: -2,
        ),
      ];

  static List<BoxShadow> get brasa => [
        const BoxShadow(
          color: Color(0x40F97316), // 25% forja-500
          blurRadius: 0,
          spreadRadius: 1,
        ),
        const BoxShadow(
          color: Color(0x66F97316), // 40% forja-500
          blurRadius: 16,
          spreadRadius: -4,
        ),
      ];

  static List<BoxShadow> get brasaStrong => [
        const BoxShadow(
          color: Color(0x8CF97316), // 55% forja-500
          blurRadius: 0,
          spreadRadius: 2,
        ),
        const BoxShadow(
          color: Color(0x8CF97316),
          blurRadius: 32,
          spreadRadius: -4,
        ),
      ];
}
