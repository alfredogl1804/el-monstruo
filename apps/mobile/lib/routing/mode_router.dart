/// mode_router — Sprint MOBILE-REALIGNMENT-001 T6.
///
/// Refactor de `core/router.dart` que hace que las rutas dependan del
/// `modeProvider`:
///
///   - **Daily mode**: `/home`, `/threads`, `/pendientes`, `/conexiones`, `/perfil`
///   - **Cockpit mode**: `/cockpit/moc`, `/cockpit/finops`, `/cockpit/sandbox`,
///     `/cockpit/memory`, `/cockpit/embrion`, `/cockpit/a2ui`
///
/// **Redirect cross-mode:** si el user navega a una ruta del otro modo, el
/// router hace un toggle implícito del mode + permite la navegación. Esto
/// preserva navegación libre + alinea state UI.
///
/// Mantiene compatibilidad con las rutas legacy (/chat, /sandbox, /settings,
/// /embrion, /memory, /finops, /genui, /moc, /files, /file-viewer, /onboarding)
/// como aliases hacia las nuevas para no romper deeplinks existentes.
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/a2ui/a2ui_screen.dart';
import '../core/state/mode_provider.dart';
import '../features/files/file_viewer.dart';
import '../features/files/files_screen.dart';
import '../features/onboarding/onboarding_screen.dart';
import '../modes/cockpit/embrion_screen.dart' as cockpit_embrion;
import '../modes/cockpit/finops_screen.dart' as cockpit_finops;
import '../modes/cockpit/memory_screen.dart' as cockpit_memory;
import '../modes/cockpit/moc_dashboard_screen.dart';
import '../modes/cockpit/sandbox_screen.dart' as cockpit_sandbox;
import '../modes/daily/conexiones/conexiones_screen.dart';
import '../modes/daily/home_screen.dart';
import '../modes/daily/pendientes/pendientes_screen.dart';
import '../modes/daily/perfil/perfil_screen.dart';
import '../modes/daily/threads/threads_screen.dart';
import '../widgets/shell_scaffold.dart';

/// Paths del modo Daily (canon Mobile 1).
const Set<String> dailyPaths = {
  '/home',
  '/threads',
  '/pendientes',
  '/conexiones',
  '/perfil',
};

/// Paths del modo Cockpit (canon Mobile 1).
const Set<String> cockpitPaths = {
  '/cockpit/moc',
  '/cockpit/finops',
  '/cockpit/sandbox',
  '/cockpit/memory',
  '/cockpit/embrion',
  '/cockpit/a2ui',
};

/// Determina el modo esperado para una ruta dada. Retorna null si la ruta
/// no pertenece a ningún modo (rutas neutrales: onboarding, file-viewer).
AppMode? expectedModeForPath(String location) {
  if (dailyPaths.any((p) => location.startsWith(p))) return AppMode.daily;
  if (cockpitPaths.any((p) => location.startsWith(p))) return AppMode.cockpit;
  return null;
}

final modeRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/home',
    redirect: (context, state) {
      final location = state.uri.toString();
      final expected = expectedModeForPath(location);
      if (expected == null) return null;

      final current = ref.read(modeProvider);
      if (current == expected) return null;

      // Cross-mode navigation: toggle implícito del mode (regla §2.6 spec).
      // No bloqueamos la navegación; solo alineamos UI state.
      // ignore: invalid_use_of_visible_for_testing_member, invalid_use_of_protected_member
      Future.microtask(() {
        ref.read(modeProvider.notifier).setMode(expected);
      });
      return null;
    },
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
          // Daily routes
          GoRoute(
            path: '/home',
            pageBuilder: (context, state) =>
                const NoTransitionPage(child: HomeScreen()),
          ),
          GoRoute(
            path: '/threads',
            pageBuilder: (context, state) =>
                const NoTransitionPage(child: ThreadsScreen()),
          ),
          GoRoute(
            path: '/pendientes',
            pageBuilder: (context, state) =>
                const NoTransitionPage(child: PendientesScreen()),
          ),
          GoRoute(
            path: '/conexiones',
            pageBuilder: (context, state) =>
                const NoTransitionPage(child: ConexionesScreen()),
          ),
          GoRoute(
            path: '/perfil',
            pageBuilder: (context, state) =>
                const NoTransitionPage(child: PerfilScreen()),
          ),
          // Cockpit routes
          GoRoute(
            path: '/cockpit/moc',
            pageBuilder: (context, state) =>
                const NoTransitionPage(child: MocDashboardScreen()),
          ),
          GoRoute(
            path: '/cockpit/finops',
            pageBuilder: (context, state) => const NoTransitionPage(
                child: cockpit_finops.FinOpsScreen()),
          ),
          GoRoute(
            path: '/cockpit/sandbox',
            pageBuilder: (context, state) => const NoTransitionPage(
                child: cockpit_sandbox.SandboxScreen()),
          ),
          GoRoute(
            path: '/cockpit/memory',
            pageBuilder: (context, state) => const NoTransitionPage(
                child: cockpit_memory.MemoryScreen()),
          ),
          GoRoute(
            path: '/cockpit/embrion',
            pageBuilder: (context, state) => const NoTransitionPage(
                child: cockpit_embrion.EmbrionScreen()),
          ),
          GoRoute(
            path: '/cockpit/a2ui',
            pageBuilder: (context, state) =>
                const NoTransitionPage(child: A2UIScreen()),
          ),
        ],
      ),
      // ===== Aliases legacy (no romper deeplinks) =====
      GoRoute(
        path: '/chat',
        redirect: (_, __) => '/home',
      ),
      GoRoute(
        path: '/sandbox',
        redirect: (_, __) => '/cockpit/sandbox',
      ),
      GoRoute(
        path: '/settings',
        redirect: (_, __) => '/perfil',
      ),
      GoRoute(
        path: '/embrion',
        redirect: (_, __) => '/cockpit/embrion',
      ),
      GoRoute(
        path: '/memory',
        redirect: (_, __) => '/cockpit/memory',
      ),
      GoRoute(
        path: '/finops',
        redirect: (_, __) => '/cockpit/finops',
      ),
      GoRoute(
        path: '/genui',
        redirect: (_, __) => '/cockpit/a2ui',
      ),
      GoRoute(
        path: '/moc',
        redirect: (_, __) => '/cockpit/moc',
      ),
      GoRoute(
        path: '/files',
        builder: (context, state) => const FilesScreen(),
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
