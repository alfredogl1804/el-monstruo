/// Threads — placeholder del Daily.
///
/// Sprint MOBILE-REALIGNMENT-001 T4 crea el placeholder. La implementación
/// real (lista de threads de chat persistidos via thread_persistence.dart)
/// llega en Sprint Mobile-2 Daily Fase 1.
library;

import 'package:flutter/material.dart';
import '../../../core/theme/brand_dna.dart';

class ThreadsScreen extends StatelessWidget {
  const ThreadsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: MonstruoTheme.background,
      appBar: AppBar(
        backgroundColor: MonstruoTheme.surface,
        title: const Text(
          'Threads',
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
              Icon(Icons.forum_outlined, size: 56, color: MonstruoTheme.onSurfaceDim),
              SizedBox(height: 16),
              Text(
                'Tus conversaciones',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: MonstruoTheme.onBackground,
                ),
              ),
              SizedBox(height: 8),
              Text(
                'El Monstruo nunca pierde el hilo. La lista completa de threads llega en Sprint Mobile-2.',
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
