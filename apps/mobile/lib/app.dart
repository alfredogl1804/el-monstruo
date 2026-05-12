import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/theme/brand_dna.dart';
import 'routing/mode_router.dart';

class MonstruoApp extends ConsumerWidget {
  const MonstruoApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(modeRouterProvider);

    return MaterialApp.router(
      title: 'El Monstruo',
      debugShowCheckedModeBanner: false,
      theme: MonstruoTheme.dark,
      routerConfig: router,
    );
  }
}
