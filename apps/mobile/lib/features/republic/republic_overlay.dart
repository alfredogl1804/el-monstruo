/// RepublicOverlay — Cara B Vitrina Cognitive Republic (Spotlight-style).
///
/// Activación: gesto pull-down desde el top de cualquier pantalla, o tap
/// en el ícono de constelación del shell.
///
/// Filosofía: la Cara A (Embrión + Daily/Cockpit) es la cara operativa
/// del Monstruo. La Cara B es la vitrina monumental de la república
/// cognitiva — los 13 módulos federados consumiendo `/v1/factory/*`.
///
/// El overlay es un `ModalBottomSheet` fullscreen-ish con animación de
/// entrada Cupertino-style: scale-in + fade + blur backdrop.
library;

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme/republic_theme.dart';
import 'republic_modules.dart';

/// Provider que controla si el overlay está abierto.
final republicOverlayOpenProvider = StateProvider<bool>((ref) => false);

/// Helpers para abrir/cerrar el overlay desde cualquier pantalla.
class RepublicOverlay {
  RepublicOverlay._();

  /// Abre el overlay como un fullscreen route.
  static Future<void> open(BuildContext context, WidgetRef ref) {
    ref.read(republicOverlayOpenProvider.notifier).state = true;
    return Navigator.of(context, rootNavigator: true).push(
      PageRouteBuilder(
        opaque: false,
        barrierDismissible: true,
        barrierColor: Colors.black.withValues(alpha: 0.4),
        transitionDuration: RepublicMotion.medium,
        reverseTransitionDuration: RepublicMotion.fast,
        pageBuilder: (_, animation, ___) {
          return _RepublicOverlayContent(animation: animation);
        },
        transitionsBuilder: (_, animation, __, child) {
          final scale = Tween<double>(begin: 0.92, end: 1.0).animate(
            CurvedAnimation(parent: animation, curve: RepublicMotion.spring),
          );
          final fade = Tween<double>(begin: 0.0, end: 1.0).animate(animation);
          return FadeTransition(
            opacity: fade,
            child: ScaleTransition(scale: scale, child: child),
          );
        },
      ),
    ).then((_) {
      if (context.mounted) {
        ref.read(republicOverlayOpenProvider.notifier).state = false;
      }
    });
  }

  /// Cierra el overlay.
  static void close(BuildContext context, WidgetRef ref) {
    ref.read(republicOverlayOpenProvider.notifier).state = false;
    Navigator.of(context, rootNavigator: true).maybePop();
  }
}

/// Contenido del overlay — lista cluster de los 13 módulos por cuadrante.
class _RepublicOverlayContent extends ConsumerWidget {
  final Animation<double> animation;

  const _RepublicOverlayContent({required this.animation});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final modules = RepublicModules.all;
    final byQuadrant = <String, List<RepublicModule>>{
      'soberana': RepublicModules.byQuadrant('soberana'),
      'gobernanza': RepublicModules.byQuadrant('gobernanza'),
      'operativa': RepublicModules.byQuadrant('operativa'),
      'continuidad': RepublicModules.byQuadrant('continuidad'),
    };

    return Scaffold(
      backgroundColor: RepublicColors.background,
      appBar: AppBar(
        backgroundColor: RepublicColors.surface,
        elevation: 0,
        scrolledUnderElevation: 0.5,
        surfaceTintColor: RepublicColors.background,
        leading: IconButton(
          icon: const Icon(Icons.close_rounded, color: RepublicColors.textPrimary),
          onPressed: () => Navigator.of(context).maybePop(),
          tooltip: 'Cerrar',
        ),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Cognitive Republic',
              style: RepublicTypography.headlineSmall.copyWith(
                color: RepublicColors.textPrimary,
                fontSize: 18,
                fontWeight: FontWeight.w700,
              ),
            ),
            Text(
              '${modules.length} módulos federados · vitrina monumental',
              style: RepublicTypography.labelSmall.copyWith(
                color: RepublicColors.textSecondary,
                fontSize: 11,
              ),
            ),
          ],
        ),
        centerTitle: false,
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(0, 8, 0, 32),
        children: [
          _QuadrantSection(
            title: 'Trilogía Soberana',
            subtitle: '3 módulos · primera ola visible',
            color: RepublicColors.teslaRed,
            modules: byQuadrant['soberana']!,
          ),
          _QuadrantSection(
            title: 'Cuadrante de Gobernanza',
            subtitle: '4 módulos · doctrina, drift, manifestaciones',
            color: RepublicColors.iosBlue,
            modules: byQuadrant['gobernanza']!,
          ),
          _QuadrantSection(
            title: 'Cuadrante Operativo',
            subtitle: '3 módulos · embriones, registry, power lanes',
            color: RepublicColors.iosGreen,
            modules: byQuadrant['operativa']!,
          ),
          _QuadrantSection(
            title: 'Cuadrante de Continuidad',
            subtitle: '3 módulos · misiones, recibos, vitrina',
            color: RepublicColors.iosOrange,
            modules: byQuadrant['continuidad']!,
          ),
        ],
      ),
    );
  }
}

class _QuadrantSection extends StatelessWidget {
  final String title;
  final String subtitle;
  final Color color;
  final List<RepublicModule> modules;

  const _QuadrantSection({
    required this.title,
    required this.subtitle,
    required this.color,
    required this.modules,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(20, 24, 20, 12),
          child: Row(
            children: [
              Container(
                width: 4,
                height: 22,
                decoration: BoxDecoration(
                  color: color,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: RepublicTypography.headlineMedium.copyWith(
                        color: RepublicColors.textPrimary,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      subtitle,
                      style: RepublicTypography.labelSmall.copyWith(
                        color: RepublicColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Column(
            children: modules
                .asMap()
                .entries
                .map(
                  (e) => Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: _ModuleCard(module: e.value, accentColor: color),
                  ).animate().fadeIn(
                        delay: Duration(milliseconds: 50 * e.key),
                        duration: RepublicMotion.fast,
                      ),
                )
                .toList(),
          ),
        ),
      ],
    );
  }
}

class _ModuleCard extends StatelessWidget {
  final RepublicModule module;
  final Color accentColor;

  const _ModuleCard({required this.module, required this.accentColor});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: RepublicColors.surface,
      borderRadius: BorderRadius.circular(RepublicRadius.md),
      elevation: 0,
      child: InkWell(
        borderRadius: BorderRadius.circular(RepublicRadius.md),
        onTap: () {
          Navigator.of(context).maybePop();
          Future.microtask(() {
            if (context.mounted) {
              context.go(module.route);
            }
          });
        },
        child: Container(
          decoration: BoxDecoration(
            border: Border.all(
              color: RepublicColors.hairline,
              width: 0.5,
            ),
            borderRadius: BorderRadius.circular(RepublicRadius.md),
          ),
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: accentColor.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(module.icon, color: accentColor, size: 22),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      module.name,
                      style: RepublicTypography.bodyLarge.copyWith(
                        color: RepublicColors.textPrimary,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      module.tagline,
                      style: RepublicTypography.bodySmall.copyWith(
                        color: RepublicColors.textSecondary,
                        height: 1.3,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              const Icon(
                Icons.chevron_right_rounded,
                size: 20,
                color: RepublicColors.textTertiary,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
