/// ModuleStubScreen — Pantalla canónica para módulos aún no construidos.
///
/// Se renderiza con la metadata del [RepublicModule] (icon, name, tagline)
/// y muestra una marca clara de "Próxima ola" para que el usuario sepa
/// que la república ya tiene 13 módulos planificados — solo 4 están vivos
/// hoy (Constellation, Timeline, Economy, Reality Diff).
library;

import 'package:flutter/material.dart';

import '../../../core/theme/republic_theme.dart';
import '../republic_modules.dart';
import '../widgets/republic_widgets.dart';

class ModuleStubScreen extends StatelessWidget {
  final String moduleId;

  const ModuleStubScreen({super.key, required this.moduleId});

  @override
  Widget build(BuildContext context) {
    final module = RepublicModules.byId(moduleId);

    if (module == null) {
      return Scaffold(
        backgroundColor: RepublicColors.background,
        appBar: const RepublicAppBar(
          title: 'Módulo desconocido',
          showBackButton: true,
        ),
        body: const EmptyState(
          icon: Icons.help_outline,
          title: 'Este módulo no existe',
          subtitle: 'El catálogo no contiene un módulo con este id.',
        ),
      );
    }

    final accent = RepublicColors.forQuadrant(module.quadrant);

    return Scaffold(
      backgroundColor: RepublicColors.background,
      appBar: RepublicAppBar(
        title: module.name,
        caption: module.tagline,
        showBackButton: true,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(RepublicSpacing.xxl),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 88,
                height: 88,
                decoration: BoxDecoration(
                  color: accent.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(RepublicRadius.lg),
                  border: Border.all(
                    color: accent.withValues(alpha: 0.3),
                    width: 0.8,
                  ),
                ),
                child: Icon(module.icon, color: accent, size: 40),
              ),
              const SizedBox(height: RepublicSpacing.xl),
              Text(
                module.name,
                style: RepublicTypography.headlineLarge,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: RepublicSpacing.sm),
              Text(
                module.tagline,
                style: RepublicTypography.bodyMedium.copyWith(
                  color: RepublicColors.textSecondary,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: RepublicSpacing.xl),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: RepublicSpacing.md,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  color: RepublicColors.surface,
                  borderRadius: BorderRadius.circular(RepublicRadius.pill),
                  border: Border.all(
                    color: RepublicColors.hairline,
                    width: 0.5,
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      width: 6,
                      height: 6,
                      decoration: BoxDecoration(
                        color: RepublicColors.iosOrange,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Próxima ola · vitrina activa',
                      style: RepublicTypography.labelSmall,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: RepublicSpacing.xl),
              Container(
                padding: const EdgeInsets.all(RepublicSpacing.md),
                decoration: BoxDecoration(
                  color: RepublicColors.surface,
                  borderRadius: BorderRadius.circular(RepublicRadius.md),
                  border: Border.all(
                    color: RepublicColors.hairline,
                    width: 0.5,
                  ),
                ),
                child: Row(
                  children: [
                    const Icon(
                      Icons.info_outline,
                      size: 16,
                      color: RepublicColors.textTertiary,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'Cuadrante: ${module.quadrant}',
                        style: RepublicTypography.bodySmall,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
