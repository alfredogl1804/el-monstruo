import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'theme/monstruo_theme.dart';
import 'core/router.dart';

class MonstruoApp extends ConsumerWidget {
  const MonstruoApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'El Monstruo',
      debugShowCheckedModeBanner: false,
      theme: MonstruoTheme.dark,
      routerConfig: router,
    );
  }
}
