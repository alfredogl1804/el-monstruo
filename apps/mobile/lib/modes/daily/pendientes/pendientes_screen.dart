/// Pendientes — placeholder del Daily.
///
/// Sprint MOBILE-REALIGNMENT-001 T4 crea el placeholder. Implementación
/// (tareas pendientes del Monstruo + recordatorios) llega en Sprint Mobile-2.
library;

import 'package:flutter/material.dart';
import '../../../core/theme/brand_dna.dart';

class PendientesScreen extends StatelessWidget {
  const PendientesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: MonstruoTheme.background,
      appBar: AppBar(
        backgroundColor: MonstruoTheme.surface,
        title: const Text(
          'Pendientes',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            color: MonstruoTheme.onBackground,
          ),
        ),
      ),
      body: const Center(
        child: Padding(
          padding: EdgeInsets.symmetric(horizontal: 32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.checklist_rtl, size: 56, color: MonstruoTheme.onSurfaceDim),
              SizedBox(height: 16),
              Text(
                'Lo que necesita tu atención',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: MonstruoTheme.onBackground,
                ),
              ),
              SizedBox(height: 8),
              Text(
                'Los pendientes proactivos del Monstruo aparecerán acá. Implementación en Sprint Mobile-2.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 13,
                  color: MonstruoTheme.onSurfaceDim,
                  height: 1.5,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
