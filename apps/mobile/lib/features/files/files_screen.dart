import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../theme/monstruo_theme.dart';

class FilesScreen extends ConsumerWidget {
  const FilesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: MonstruoTheme.background,
      appBar: AppBar(
        backgroundColor: MonstruoTheme.background,
        title: const Text('Archivos'),
        actions: [
          IconButton(
            icon: const Icon(Icons.sort, color: MonstruoTheme.onSurfaceDim),
            onPressed: () {},
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.folder_open,
              size: 64,
              color: MonstruoTheme.onSurfaceDim.withValues(alpha: 0.3),
            ),
            const SizedBox(height: 16),
            const Text(
              'Sin archivos aún',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: MonstruoTheme.onBackground,
              ),
            ),
            const SizedBox(height: 8),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 48),
              child: Text(
                'Los archivos generados por El Monstruo (documentos, imágenes, código, slides) aparecerán aquí.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  color: MonstruoTheme.onSurfaceDim,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
