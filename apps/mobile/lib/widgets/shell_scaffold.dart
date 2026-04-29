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
      // Drawer for secondary screens
      drawer: _MonstruoDrawer(),
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

class _MonstruoDrawer extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Drawer(
      backgroundColor: MonstruoTheme.background,
      child: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    MonstruoTheme.primary.withValues(alpha: 0.15),
                    MonstruoTheme.secondary.withValues(alpha: 0.08),
                  ],
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [MonstruoTheme.primary, MonstruoTheme.secondary],
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Center(
                      child: Text(
                        'M',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.w900,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'El Monstruo',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w700,
                      color: MonstruoTheme.onBackground,
                    ),
                  ),
                  const SizedBox(height: 2),
                  const Text(
                    'Agente IA Soberano',
                    style: TextStyle(
                      fontSize: 13,
                      color: MonstruoTheme.onSurfaceDim,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 8),

            // Navigation items
            _DrawerItem(
              icon: Icons.auto_awesome,
              label: 'Generative UI',
              subtitle: 'Interfaces dinámicas del agente',
              color: MonstruoTheme.primary,
              onTap: () {
                Navigator.pop(context);
                context.push('/genui');
              },
            ),
            _DrawerItem(
              icon: Icons.psychology,
              label: 'Embrión',
              subtitle: 'Agente autónomo 24/7',
              color: MonstruoTheme.success,
              onTap: () {
                Navigator.pop(context);
                context.push('/embrion');
              },
            ),
            _DrawerItem(
              icon: Icons.memory,
              label: 'Memoria Soberana',
              subtitle: 'Buscar y explorar memorias',
              color: const Color(0xFF7C4DFF),
              onTap: () {
                Navigator.pop(context);
                context.push('/memory');
              },
            ),
            _DrawerItem(
              icon: Icons.analytics,
              label: 'FinOps',
              subtitle: 'Costos y uso de modelos',
              color: MonstruoTheme.warning,
              onTap: () {
                Navigator.pop(context);
                context.push('/finops');
              },
            ),

            const Spacer(),

            // Version info
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                'v0.1.0-alpha',
                style: TextStyle(
                  fontSize: 11,
                  color: MonstruoTheme.onSurfaceDim.withValues(alpha: 0.5),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DrawerItem extends StatelessWidget {
  const _DrawerItem({
    required this.icon,
    required this.label,
    required this.subtitle,
    required this.color,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, size: 20, color: color),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: MonstruoTheme.onBackground,
                    ),
                  ),
                  Text(
                    subtitle,
                    style: const TextStyle(
                      fontSize: 11,
                      color: MonstruoTheme.onSurfaceDim,
                    ),
                  ),
                ],
              ),
            ),
            const Icon(
              Icons.chevron_right,
              size: 18,
              color: MonstruoTheme.onSurfaceDim,
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
