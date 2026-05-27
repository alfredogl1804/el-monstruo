/// RepublicTheme — Sistema de diseño canónico Apple/Tesla para Cognitive Republic.
///
/// Habilitante: DSC-G-019 + decisión T1 (Alfredo, 2026-05-27): "Apple/Tesla light premium".
///
/// Principios:
///   1. Blanco hueso #F5F5F7 como fondo (sin pantalla negra, sin fatiga visual).
///   2. SF Pro Display + SF Pro Text + SF Mono (sistema iOS nativo).
///   3. Rojo Tesla #E82127 SOLO para criticidad real (T1 pendiente, P0, irreversible).
///   4. Densidad Tesla cluster instrumental: muchos datos, hairlines, sin saturar.
///   5. Sombras sutiles Apple-style. Esquinas 12-16. Sin gradientes saturados.
library;

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

/// Paleta cromática soberana.
class RepublicColors {
  RepublicColors._();

  // ─── Fondos (Apple light system) ───
  static const Color background = Color(0xFFF5F5F7); // System gray 6 light, blanco hueso
  static const Color surface = Color(0xFFFFFFFF); // Cards y sheets
  static const Color surfaceElevated = Color(0xFFFAFAFC); // Drawers, modales

  // ─── Texto ───
  static const Color textPrimary = Color(0xFF000000); // Apple primary label
  static const Color textSecondary = Color(0xFF6E6E73); // Apple secondary label
  static const Color textTertiary = Color(0xFF8E8E93); // Apple tertiary label
  static const Color textOnAccent = Color(0xFFFFFFFF); // Texto sobre rojo/azul

  // ─── Hairlines y separadores (Tesla cluster) ───
  static const Color hairline = Color(0x1F000000); // 12% black, divisor 0.5px
  static const Color border = Color(0x29000000); // 16% black, borde card sutil

  // ─── Acento Tesla (criticidad real) ───
  static const Color teslaRed = Color(0xFFE82127); // Tesla brand red — T1 pendiente, P0
  static const Color teslaRedSoft = Color(0xFFFFF0F1); // Background red sutil

  // ─── Acentos sistema iOS ───
  static const Color iosBlue = Color(0xFF007AFF); // Acción primaria, links, CTAs
  static const Color iosBlueSoft = Color(0xFFE9F2FF);
  static const Color iosGreen = Color(0xFF34C759); // ONLINE, healthy, binario_100
  static const Color iosGreenSoft = Color(0xFFEAFBEF);
  static const Color iosOrange = Color(0xFFFF9500); // STANDBY, drift menor
  static const Color iosOrangeSoft = Color(0xFFFFF5E6);
  static const Color iosYellow = Color(0xFFFFCC00);
  static const Color iosPurple = Color(0xFFAF52DE); // Doctrine / DSCs
  static const Color iosIndigo = Color(0xFF5856D6); // Embriones / agentes
  static const Color iosTeal = Color(0xFF5AC8FA); // Datos memoria

  // ─── Mappings semánticos ───
  static Color forStatus(String status) {
    switch (status.toUpperCase()) {
      case 'ONLINE':
        return iosGreen;
      case 'STANDBY':
        return iosOrange;
      case 'DEGRADED':
        return iosOrange;
      case 'OFFLINE':
      case 'ERROR':
        return teslaRed;
      default:
        return textTertiary;
    }
  }

  static Color forTier(String tier) {
    switch (tier.toLowerCase()) {
      case 'core':
        return teslaRed; // El kernel es el sol — único nodo en rojo Tesla
      case 'inner':
        return iosBlue;
      case 'mid':
        return iosIndigo;
      case 'outer':
        return iosTeal;
      default:
        return textTertiary;
    }
  }

  static Color forQuadrant(String quadrant) {
    switch (quadrant.toLowerCase()) {
      case 'soberana':
        return teslaRed;
      case 'gobernanza':
        return iosBlue;
      case 'operativa':
        return iosGreen;
      case 'continuidad':
        return iosOrange;
      default:
        return textTertiary;
    }
  }
}

/// Tipografía SF Pro nativa iOS (Cupertino) + tamaños canon.
class RepublicTypography {
  RepublicTypography._();

  // SF Pro es la fuente del sistema iOS — Flutter la usa por defecto en iOS
  // si fontFamily es null. En Android se reemplaza por Roboto, lo cual es OK.

  static const String _displayFont = '.SF Pro Display';
  static const String _textFont = '.SF Pro Text';
  static const String _monoFont = '.SF Mono';

  // ─── Display (números grandes, KPIs hero, encabezados monumentales) ───
  static const TextStyle displayLarge = TextStyle(
    fontFamily: _displayFont,
    fontSize: 56,
    fontWeight: FontWeight.w700,
    letterSpacing: -1.2,
    height: 1.05,
    color: RepublicColors.textPrimary,
  );

  static const TextStyle displayMedium = TextStyle(
    fontFamily: _displayFont,
    fontSize: 40,
    fontWeight: FontWeight.w700,
    letterSpacing: -0.8,
    height: 1.1,
    color: RepublicColors.textPrimary,
  );

  static const TextStyle displaySmall = TextStyle(
    fontFamily: _displayFont,
    fontSize: 32,
    fontWeight: FontWeight.w600,
    letterSpacing: -0.5,
    height: 1.15,
    color: RepublicColors.textPrimary,
  );

  // ─── Headline ───
  static const TextStyle headlineLarge = TextStyle(
    fontFamily: _displayFont,
    fontSize: 28,
    fontWeight: FontWeight.w600,
    letterSpacing: -0.4,
    height: 1.2,
    color: RepublicColors.textPrimary,
  );

  static const TextStyle headlineMedium = TextStyle(
    fontFamily: _displayFont,
    fontSize: 22,
    fontWeight: FontWeight.w600,
    letterSpacing: -0.3,
    height: 1.25,
    color: RepublicColors.textPrimary,
  );

  static const TextStyle headlineSmall = TextStyle(
    fontFamily: _displayFont,
    fontSize: 18,
    fontWeight: FontWeight.w600,
    letterSpacing: -0.2,
    height: 1.3,
    color: RepublicColors.textPrimary,
  );

  // ─── Body ───
  static const TextStyle bodyLarge = TextStyle(
    fontFamily: _textFont,
    fontSize: 17,
    fontWeight: FontWeight.w400,
    letterSpacing: -0.1,
    height: 1.4,
    color: RepublicColors.textPrimary,
  );

  static const TextStyle bodyMedium = TextStyle(
    fontFamily: _textFont,
    fontSize: 15,
    fontWeight: FontWeight.w400,
    letterSpacing: -0.05,
    height: 1.4,
    color: RepublicColors.textPrimary,
  );

  static const TextStyle bodySmall = TextStyle(
    fontFamily: _textFont,
    fontSize: 13,
    fontWeight: FontWeight.w400,
    letterSpacing: 0,
    height: 1.4,
    color: RepublicColors.textSecondary,
  );

  // ─── Labels (caps para etiquetas tipo cluster Tesla) ───
  static const TextStyle labelLarge = TextStyle(
    fontFamily: _textFont,
    fontSize: 13,
    fontWeight: FontWeight.w600,
    letterSpacing: 0.5,
    height: 1.3,
    color: RepublicColors.textSecondary,
  );

  static const TextStyle labelMedium = TextStyle(
    fontFamily: _textFont,
    fontSize: 11,
    fontWeight: FontWeight.w600,
    letterSpacing: 0.8,
    height: 1.3,
    color: RepublicColors.textSecondary,
  );

  static const TextStyle labelSmall = TextStyle(
    fontFamily: _textFont,
    fontSize: 10,
    fontWeight: FontWeight.w700,
    letterSpacing: 1.2,
    height: 1.2,
    color: RepublicColors.textTertiary,
  );

  // ─── Mono (datos técnicos: hashes, IDs, uptime, números densos) ───
  static const TextStyle monoLarge = TextStyle(
    fontFamily: _monoFont,
    fontSize: 17,
    fontWeight: FontWeight.w500,
    letterSpacing: 0,
    height: 1.3,
    color: RepublicColors.textPrimary,
  );

  static const TextStyle monoMedium = TextStyle(
    fontFamily: _monoFont,
    fontSize: 14,
    fontWeight: FontWeight.w500,
    letterSpacing: 0,
    height: 1.3,
    color: RepublicColors.textPrimary,
  );

  static const TextStyle monoSmall = TextStyle(
    fontFamily: _monoFont,
    fontSize: 12,
    fontWeight: FontWeight.w500,
    letterSpacing: 0,
    height: 1.3,
    color: RepublicColors.textSecondary,
  );
}

/// Espaciado canónico (sistema 4pt).
class RepublicSpacing {
  RepublicSpacing._();

  static const double xs = 4;
  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 24;
  static const double xxl = 32;
  static const double xxxl = 48;
  static const double huge = 64;
}

/// Esquinas canónicas (Apple-leaning con guiño Tesla).
class RepublicRadius {
  RepublicRadius._();

  static const double xs = 4;
  static const double sm = 8;
  static const double md = 12; // Cards de datos densos
  static const double lg = 16; // Sheets, modales
  static const double xl = 24; // Sheets monumentales (Cognitive Republic shell)
  static const double pill = 999;
}

/// Sombras Apple-style sutiles (depth sin saturación).
class RepublicShadows {
  RepublicShadows._();

  static const List<BoxShadow> card = [
    BoxShadow(
      color: Color(0x0A000000), // 4% black
      blurRadius: 8,
      offset: Offset(0, 2),
    ),
  ];

  static const List<BoxShadow> elevated = [
    BoxShadow(
      color: Color(0x14000000), // 8% black
      blurRadius: 16,
      offset: Offset(0, 4),
    ),
  ];

  static const List<BoxShadow> heroPulse = [
    BoxShadow(
      color: Color(0x33E82127), // Rojo Tesla 20%
      blurRadius: 24,
      offset: Offset(0, 0),
    ),
  ];
}

/// Curvas de motion Apple-leaning (spring-like easing).
class RepublicMotion {
  RepublicMotion._();

  static const Duration fast = Duration(milliseconds: 200);
  static const Duration medium = Duration(milliseconds: 350);
  static const Duration slow = Duration(milliseconds: 600);
  static const Duration heroPulse = Duration(milliseconds: 1800);

  // Apple usa cubicEmphasized para transiciones premium
  static const Curve emphasized = Cubic(0.2, 0.0, 0.0, 1.0);
  static const Curve standard = Curves.easeInOutCubic;
  static const Curve spring = Curves.easeOutBack;
}

/// Theme global Material 3 alineado al sistema canónico.
class RepublicTheme {
  RepublicTheme._();

  static ThemeData light() {
    final base = ThemeData.light(useMaterial3: true);

    return base.copyWith(
      brightness: Brightness.light,
      scaffoldBackgroundColor: RepublicColors.background,
      canvasColor: RepublicColors.background,
      colorScheme: const ColorScheme.light(
        primary: RepublicColors.iosBlue,
        onPrimary: RepublicColors.textOnAccent,
        secondary: RepublicColors.teslaRed,
        onSecondary: RepublicColors.textOnAccent,
        surface: RepublicColors.surface,
        onSurface: RepublicColors.textPrimary,
        surfaceContainerLowest: RepublicColors.background,
        surfaceContainerLow: RepublicColors.surfaceElevated,
        surfaceContainer: RepublicColors.surface,
        error: RepublicColors.teslaRed,
        onError: RepublicColors.textOnAccent,
        outline: RepublicColors.border,
        outlineVariant: RepublicColors.hairline,
      ),
      textTheme: const TextTheme(
        displayLarge: RepublicTypography.displayLarge,
        displayMedium: RepublicTypography.displayMedium,
        displaySmall: RepublicTypography.displaySmall,
        headlineLarge: RepublicTypography.headlineLarge,
        headlineMedium: RepublicTypography.headlineMedium,
        headlineSmall: RepublicTypography.headlineSmall,
        bodyLarge: RepublicTypography.bodyLarge,
        bodyMedium: RepublicTypography.bodyMedium,
        bodySmall: RepublicTypography.bodySmall,
        labelLarge: RepublicTypography.labelLarge,
        labelMedium: RepublicTypography.labelMedium,
        labelSmall: RepublicTypography.labelSmall,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: RepublicColors.background,
        foregroundColor: RepublicColors.textPrimary,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        titleTextStyle: RepublicTypography.headlineMedium,
        toolbarHeight: 56,
      ),
      cardTheme: CardThemeData(
        color: RepublicColors.surface,
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(RepublicRadius.md),
          side: const BorderSide(color: RepublicColors.hairline, width: 0.5),
        ),
      ),
      dividerTheme: const DividerThemeData(
        color: RepublicColors.hairline,
        thickness: 0.5,
        space: 0.5,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: RepublicColors.iosBlue,
          foregroundColor: RepublicColors.textOnAccent,
          elevation: 0,
          padding: const EdgeInsets.symmetric(
            horizontal: RepublicSpacing.xl,
            vertical: RepublicSpacing.md,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(RepublicRadius.md),
          ),
          textStyle: RepublicTypography.bodyMedium.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: RepublicColors.teslaRed,
          foregroundColor: RepublicColors.textOnAccent,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(RepublicRadius.md),
          ),
          textStyle: RepublicTypography.bodyMedium.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: RepublicColors.iosBlue,
          textStyle: RepublicTypography.bodyMedium.copyWith(
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
      iconTheme: const IconThemeData(
        color: RepublicColors.textPrimary,
        size: 22,
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: RepublicColors.surface,
        selectedItemColor: RepublicColors.teslaRed,
        unselectedItemColor: RepublicColors.textTertiary,
        elevation: 0,
        showUnselectedLabels: true,
        type: BottomNavigationBarType.fixed,
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: RepublicColors.surface,
        indicatorColor: RepublicColors.teslaRedSoft,
        labelTextStyle: WidgetStatePropertyAll(
          RepublicTypography.labelMedium,
        ),
        iconTheme: const WidgetStatePropertyAll(
          IconThemeData(color: RepublicColors.textPrimary, size: 22),
        ),
      ),
      cupertinoOverrideTheme: const CupertinoThemeData(
        primaryColor: RepublicColors.iosBlue,
        scaffoldBackgroundColor: RepublicColors.background,
        barBackgroundColor: RepublicColors.surface,
      ),
    );
  }
}
