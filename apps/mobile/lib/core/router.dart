import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/chat/chat_screen.dart';
import '../features/sandbox/sandbox_screen.dart';
import '../features/files/files_screen.dart';
import '../features/files/file_viewer.dart';
import '../features/settings/settings_screen.dart';
import '../features/onboarding/onboarding_screen.dart';
import '../features/embrion/embrion_screen.dart';
import '../features/memory/memory_screen.dart';
import '../features/finops/finops_screen.dart';
import '../features/genui/genui_screen.dart';
import '../widgets/shell_scaffold.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/chat',
    routes: [
      GoRoute(
        path: '/onboarding',
        builder: (context, state) => const OnboardingScreen(),
      ),
      ShellRoute(
        builder: (context, state, child) {
          return ShellScaffold(child: child);
        },
        routes: [
          GoRoute(
            path: '/chat',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: ChatScreen(),
            ),
          ),
          GoRoute(
            path: '/sandbox',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: SandboxScreen(),
            ),
          ),
          GoRoute(
            path: '/files',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: FilesScreen(),
            ),
          ),
          GoRoute(
            path: '/settings',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: SettingsScreen(),
            ),
          ),
        ],
      ),
      GoRoute(
        path: '/embrion',
        builder: (context, state) => const EmbrionScreen(),
      ),
      GoRoute(
        path: '/memory',
        builder: (context, state) => const MemoryScreen(),
      ),
      GoRoute(
        path: '/finops',
        builder: (context, state) => const FinOpsScreen(),
      ),
      GoRoute(
        path: '/genui',
        builder: (context, state) => const GenUIScreen(),
      ),
      GoRoute(
        path: '/file-viewer',
        builder: (context, state) {
          final extra = state.extra as Map<String, dynamic>? ?? {};
          return FileViewer(
            filename: extra['filename'] as String? ?? 'file',
            url: extra['url'] as String? ?? '',
            mimeType: extra['mimeType'] as String?,
            content: extra['content'] as String?,
          );
        },
      ),
    ],
  );
});
