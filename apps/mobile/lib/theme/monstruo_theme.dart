import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// El Monstruo Design System — Premium Dark Theme 2026
/// Inspired by ChatGPT, Claude, Gemini latest interfaces
class MonstruoTheme {
  MonstruoTheme._();

  // ─── Core Colors ───
  static const Color primary = Color(0xFF00E5FF);
  static const Color primaryDim = Color(0xFF00B8D4);
  static const Color secondary = Color(0xFFBB86FC);
  static const Color tertiary = Color(0xFF64FFDA);
  static const Color error = Color(0xFFFF5252);
  static const Color success = Color(0xFF69F0AE);
  static const Color warning = Color(0xFFFFD740);

  // ─── Surfaces (Premium depth hierarchy) ───
  static const Color background = Color(0xFF0A0A10);
  static const Color surface = Color(0xFF14141E);
  static const Color surfaceVariant = Color(0xFF1C1C2A);
  static const Color surfaceElevated = Color(0xFF242436);
  static const Color surfaceGlass = Color(0x1AFFFFFF); // 10% white

  // ─── On-colors ───
  static const Color onBackground = Color(0xFFF5F5F7);
  static const Color onSurface = Color(0xFFE0E0E6);
  static const Color onSurfaceDim = Color(0xFF8E8E9A);
  static const Color onPrimary = Color(0xFF000000);

  // ─── Borders & Dividers ───
  static const Color divider = Color(0xFF2A2A3A);
  static const Color border = Color(0xFF333346);
  static const Color borderFocused = Color(0xFF00E5FF);

  // ─── Gradients ───
  static const LinearGradient backgroundGradient = LinearGradient(
    colors: [Color(0xFF0A0A10), Color(0xFF0D0D18)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  static const LinearGradient agentGradient = LinearGradient(
    colors: [Color(0xFF00E5FF), Color(0xFFBB86FC)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient sendButtonGradient = LinearGradient(
    colors: [Color(0xFF00E5FF), Color(0xFF00B8D4)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient glowGradient = LinearGradient(
    colors: [Color(0x4000E5FF), Color(0x40BB86FC)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  // ─── Spacing ───
  static const double spacingXs = 4.0;
  static const double spacingSm = 8.0;
  static const double spacingMd = 16.0;
  static const double spacingLg = 24.0;
  static const double spacingXl = 32.0;
  static const double spacingXxl = 48.0;

  // ─── Border Radius ───
  static const double radiusSm = 8.0;
  static const double radiusMd = 12.0;
  static const double radiusLg = 16.0;
  static const double radiusXl = 24.0;
  static const double radiusFull = 999.0;

  // ─── Shadows ───
  static List<BoxShadow> get glowShadow => [
        BoxShadow(
          color: primary.withValues(alpha: 0.15),
          blurRadius: 16,
          spreadRadius: 0,
        ),
      ];

  static List<BoxShadow> get subtleShadow => [
        const BoxShadow(
          color: Color(0x20000000),
          blurRadius: 8,
          offset: Offset(0, 2),
        ),
      ];

  // ─── Animation Durations ───
  static const Duration animFast = Duration(milliseconds: 150);
  static const Duration animNormal = Duration(milliseconds: 250);
  static const Duration animSlow = Duration(milliseconds: 400);
  static const Duration animStreaming = Duration(milliseconds: 30);

  // ─── Theme Data ───
  static ThemeData get dark {
    final textTheme = GoogleFonts.spaceGroteskTextTheme(
      ThemeData.dark().textTheme,
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: background,
      colorScheme: const ColorScheme.dark(
        primary: primary,
        onPrimary: onPrimary,
        secondary: secondary,
        surface: surface,
        onSurface: onSurface,
        error: error,
      ),
      textTheme: textTheme.copyWith(
        displayLarge: textTheme.displayLarge?.copyWith(
          color: onBackground,
          fontWeight: FontWeight.w700,
          letterSpacing: -1.5,
        ),
        headlineMedium: textTheme.headlineMedium?.copyWith(
          color: onBackground,
          fontWeight: FontWeight.w600,
          letterSpacing: -0.5,
        ),
        titleLarge: textTheme.titleLarge?.copyWith(
          color: onBackground,
          fontWeight: FontWeight.w600,
        ),
        titleMedium: textTheme.titleMedium?.copyWith(
          color: onSurface,
          fontWeight: FontWeight.w500,
        ),
        bodyLarge: textTheme.bodyLarge?.copyWith(
          color: onSurface,
          fontSize: 15,
          height: 1.65,
          letterSpacing: -0.2,
        ),
        bodyMedium: textTheme.bodyMedium?.copyWith(
          color: onSurface,
          fontSize: 14,
          height: 1.5,
        ),
        bodySmall: textTheme.bodySmall?.copyWith(
          color: onSurfaceDim,
          fontSize: 12,
        ),
        labelLarge: textTheme.labelLarge?.copyWith(
          color: primary,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.5,
        ),
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: background,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        titleTextStyle: textTheme.titleLarge?.copyWith(
          color: onBackground,
          fontWeight: FontWeight.w600,
        ),
        iconTheme: const IconThemeData(color: onBackground),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: surface,
        selectedItemColor: primary,
        unselectedItemColor: onSurfaceDim,
        type: BottomNavigationBarType.fixed,
        elevation: 0,
      ),
      cardTheme: CardThemeData(
        color: surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radiusMd),
          side: const BorderSide(color: divider, width: 0.5),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surfaceVariant,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusLg),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(radiusLg),
          borderSide: const BorderSide(color: primary, width: 1.5),
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: spacingMd,
          vertical: spacingMd,
        ),
        hintStyle: textTheme.bodyMedium?.copyWith(color: onSurfaceDim),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primary,
          foregroundColor: onPrimary,
          elevation: 0,
          padding: const EdgeInsets.symmetric(
            horizontal: spacingLg,
            vertical: spacingMd,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(radiusMd),
          ),
          textStyle: textTheme.labelLarge?.copyWith(
            color: onPrimary,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      iconTheme: const IconThemeData(
        color: onSurfaceDim,
        size: 24,
      ),
      dividerTheme: const DividerThemeData(
        color: divider,
        thickness: 0.5,
        space: 0,
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: surfaceElevated,
        contentTextStyle: textTheme.bodyMedium?.copyWith(color: onSurface),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(radiusMd),
        ),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
}
