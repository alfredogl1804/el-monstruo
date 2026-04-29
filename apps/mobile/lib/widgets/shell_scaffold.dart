import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../services/kernel_service.dart';
import '../theme/monstruo_theme.dart';

class ShellScaffold extends ConsumerWidget {
  const ShellScaffold({super.key, required this.child});

  final Widget child;

  static const _tabs = [
    _TabItem(path: '/chat', icon: Icons.chat_bubble_outline, activeIcon: Icons.chat_bubble, label: 'Chat'),
    _TabItem(path: '/sandbox', icon: Icons.terminal_outlined, activeIcon: Icons.terminal, label: 'Sandbox'),
    _TabItem(path: '/files', icon: Icons.folder_outlined, activeIcon: Icons.folder, label: 'Archivos'),
    _TabItem(path: '/settings', icon: Icons.settings_outlined, activeIcon: Icons.settings, label: 'Config'),
  ];

  int _currentIndex(BuildContext context) {
    final location = GoRouterState.of(context).uri.toString();
    final idx = _tabs.indexWhere((t) => location.startsWith(t.path));
    return idx >= 0 ? idx : 0;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentIdx = _currentIndex(context);
    final connectionState = ref.watch(connectionStateProvider);

    return Scaffold(
      body: child,
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          border: Border(
            top: BorderSide(
              color: MonstruoTheme.divider,
              width: 0.5,
            ),
          ),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Connection status indicator
            connectionState.when(
              data: (state) {
                if (state == ConnectionState.connected) {
                  return const SizedBox.shrink();
                }
                return _ConnectionBanner(state: state);
              },
              loading: () => const SizedBox.shrink(),
              error: (_, __) => const _ConnectionBanner(
                state: ConnectionState.error,
              ),
            ),
            // Bottom nav
            BottomNavigationBar(
              currentIndex: currentIdx,
              onTap: (idx) => context.go(_tabs[idx].path),
              items: _tabs
                  .map((tab) => BottomNavigationBarItem(
                        icon: Icon(tab.icon),
                        activeIcon: Icon(tab.activeIcon),
                        label: tab.label,
                      ))
                  .toList(),
            ),
          ],
        ),
      ),
    );
  }
}

class _TabItem {
  const _TabItem({
    required this.path,
    required this.icon,
    required this.activeIcon,
    required this.label,
  });

  final String path;
  final IconData icon;
  final IconData activeIcon;
  final String label;
}

class _ConnectionBanner extends StatelessWidget {
  const _ConnectionBanner({required this.state});

  final ConnectionState state;

  @override
  Widget build(BuildContext context) {
    final (color, text, icon) = switch (state) {
      ConnectionState.connecting => (
          MonstruoTheme.warning,
          'Conectando al kernel...',
          Icons.sync,
        ),
      ConnectionState.reconnecting => (
          MonstruoTheme.warning,
          'Reconectando...',
          Icons.sync,
        ),
      ConnectionState.error => (
          MonstruoTheme.error,
          'Error de conexión',
          Icons.error_outline,
        ),
      ConnectionState.failed => (
          MonstruoTheme.error,
          'Sin conexión al kernel',
          Icons.cloud_off,
        ),
      ConnectionState.disconnected => (
          MonstruoTheme.onSurfaceDim,
          'Desconectado',
          Icons.cloud_off,
        ),
      _ => (
          MonstruoTheme.success,
          'Conectado',
          Icons.cloud_done,
        ),
    };

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 16),
      color: color.withValues(alpha: 0.15),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 6),
          Text(
            text,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}
