/// ShellScaffold — refactor T5 Sprint MOBILE-REALIGNMENT-001.
///
/// Lee `modeProvider` de Riverpod y bifurca la navegación según el modo:
///
///   - **AppMode.daily** → BottomNavigationBar con 5 tabs:
///       Home, Threads, Pendientes, Conexiones, Perfil
///   - **AppMode.cockpit** → MOC Dashboard como home + Drawer cockpit con 5 features:
///       FinOps, Sandbox, Memory, Embrion, A2UI
///
/// **Toggle gestual:** swipe-down con 2 dedos OR long-press en el logo del
/// header invocan `ref.read(modeProvider.notifier).toggle()`.
///
/// Sprint MOBILE-REALIGNMENT-001 T5
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/mensajeros/embrion_messenger.dart';
import '../core/mensajeros/kernel_messenger.dart';
import '../core/state/mode_provider.dart';
import '../core/theme/brand_dna.dart';
import '../features/republic/republic_overlay.dart';

class ShellScaffold extends ConsumerWidget {
  const ShellScaffold({super.key, required this.child});

  final Widget child;

  /// 5 tabs del modo Daily (privado para no exponer _TabItem en API pública).
  static const List<_TabItem> _dailyTabs = [
    _TabItem(path: '/home', icon: Icons.home_outlined, activeIcon: Icons.home, label: 'Home'),
    _TabItem(path: '/threads', icon: Icons.forum_outlined, activeIcon: Icons.forum, label: 'Threads'),
    _TabItem(path: '/pendientes', icon: Icons.checklist_rtl, activeIcon: Icons.checklist, label: 'Pendientes'),
    _TabItem(path: '/conexiones', icon: Icons.hub_outlined, activeIcon: Icons.hub, label: 'Conexiones'),
    _TabItem(path: '/perfil', icon: Icons.person_outline, activeIcon: Icons.person, label: 'Perfil'),
  ];

  int _currentIndex(BuildContext context) {
    final location = GoRouterState.of(context).uri.toString();
    final idx = _dailyTabs.indexWhere((t) => location.startsWith(t.path));
    return idx >= 0 ? idx : 0;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final mode = ref.watch(modeProvider);
    final connectionState = ref.watch(connectionStateProvider);

    // Detectar swipe-down con 2 dedos: ScaleStartDetails / VerticalDragGesture
    // con multi-touch — usamos GestureDetector con onScaleUpdate como aproximación
    // multi-touch confiable.
    return GestureDetector(
      onScaleUpdate: (details) {
        // 2+ dedos detectados (pointerCount >= 2) + scale ~ 1.0 + drag vertical down
        if (details.pointerCount >= 2 && details.focalPointDelta.dy > 30) {
          ref.read(modeProvider.notifier).toggle();
                ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                mode == AppMode.daily
                    ? 'Modo Cockpit activado'
                    : 'Modo Daily activado',
                style: const TextStyle(fontSize: 13),
              ),
              duration: const Duration(seconds: 1),
              behavior: SnackBarBehavior.floating,
            ),
          );
        }
      },
      child: Scaffold(
        body: child,
        // Drawer solo en modo Cockpit (Daily usa BottomNav exclusivo).
        drawer: mode == AppMode.cockpit ? const _CockpitDrawer() : null,
        bottomNavigationBar: mode == AppMode.daily
            ? _buildDailyBottomNav(context, connectionState)
            : null,
        // Columna de FABs de la cabina:
        //   • Hilo de Manus (tareas complejas, Línea 2)
        //   • Bandeja del Embrión (propuestas autónomas, Línea 1) con badge
        //   • Cognitive Republic (Cara B vitrina)
        floatingActionButton: const _CockpitFabStack(),
        floatingActionButtonLocation: FloatingActionButtonLocation.endTop,
      ),
    );
  }

  Widget _buildDailyBottomNav(
    BuildContext context,
    AsyncValue<KernelConnectionState> connectionState,
  ) {
    final currentIdx = _currentIndex(context);
    return Container(
      decoration: const BoxDecoration(
        border: Border(
          top: BorderSide(color: MonstruoTheme.divider, width: 0.5),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Connection status banner (preservado del scaffold previo)
          connectionState.when(
            data: (state) {
              if (state == KernelConnectionState.connected) {
                return const SizedBox.shrink();
              }
              return _ConnectionBanner(state: state);
            },
            loading: () => const SizedBox.shrink(),
            error: (_, __) => const _ConnectionBanner(
              state: KernelConnectionState.error,
            ),
          ),
          // Bottom nav 5 tabs Daily
          BottomNavigationBar(
            type: BottomNavigationBarType.fixed,
            currentIndex: currentIdx,
            onTap: (idx) => context.go(_dailyTabs[idx].path),
            items: _dailyTabs
                .map((tab) => BottomNavigationBarItem(
                      icon: Icon(tab.icon),
                      activeIcon: Icon(tab.activeIcon),
                      label: tab.label,
                    ))
                .toList(),
          ),
        ],
      ),
    );
  }
}

/// Drawer del modo Cockpit con las 5 features arquitectónicas.
class _CockpitDrawer extends ConsumerWidget {
  const _CockpitDrawer();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Drawer(
      backgroundColor: MonstruoTheme.background,
      child: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header con long-press para toggle a Daily
            GestureDetector(
              onLongPress: () {
                ref.read(modeProvider.notifier).setMode(AppMode.daily);
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Modo Daily activado',
                        style: TextStyle(fontSize: 13)),
                    duration: Duration(seconds: 1),
                    behavior: SnackBarBehavior.floating,
                  ),
                );
              },
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      MonstruoTheme.primary.withValues(alpha: 0.18),
                      MonstruoTheme.secondary.withValues(alpha: 0.10),
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
                          colors: [
                            MonstruoTheme.primary,
                            MonstruoTheme.secondary,
                          ],
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
                      'Cockpit',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w700,
                        color: MonstruoTheme.onBackground,
                      ),
                    ),
                    const SizedBox(height: 2),
                    const Text(
                      'Modo arquitectónico — long-press logo para Daily',
                      style: TextStyle(
                        fontSize: 12,
                        color: MonstruoTheme.onSurfaceDim,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 8),
            _DrawerItem(
              icon: Icons.hub,
              label: 'MOC',
              subtitle: 'Motor de Orquestación Central',
              color: const Color(0xFF00BCD4),
              onTap: () {
                Navigator.pop(context);
                context.go('/cockpit/moc');
              },
            ),
            _DrawerItem(
              icon: Icons.analytics,
              label: 'FinOps',
              subtitle: 'Costos y uso de modelos',
              color: MonstruoTheme.warning,
              onTap: () {
                Navigator.pop(context);
                context.go('/cockpit/finops');
              },
            ),
            _DrawerItem(
              icon: Icons.terminal,
              label: 'Sandbox',
              subtitle: 'Terminal + browser + kernel',
              color: const Color(0xFF7C4DFF),
              onTap: () {
                Navigator.pop(context);
                context.go('/cockpit/sandbox');
              },
            ),
            _DrawerItem(
              icon: Icons.memory,
              label: 'Memoria Soberana',
              subtitle: 'Buscar y explorar memorias',
              color: const Color(0xFF7C4DFF),
              onTap: () {
                Navigator.pop(context);
                context.go('/cockpit/memory');
              },
            ),
            _DrawerItem(
              icon: Icons.psychology,
              label: 'Embrión',
              subtitle: 'Agente autónomo 24/7',
              color: MonstruoTheme.success,
              onTap: () {
                Navigator.pop(context);
                context.go('/cockpit/embrion');
              },
            ),
            _DrawerItem(
              icon: Icons.auto_awesome,
              label: 'A2UI',
              subtitle: 'Generative UI components',
              color: MonstruoTheme.primary,
              onTap: () {
                Navigator.pop(context);
                context.go('/cockpit/a2ui');
              },
            ),
            const Spacer(),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                'v0.2.0-realignment',
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

  final KernelConnectionState state;

  @override
  Widget build(BuildContext context) {
    final (color, text, icon) = switch (state) {
      KernelConnectionState.connecting => (
          MonstruoTheme.warning,
          'Conectando al kernel...',
          Icons.sync,
        ),
      KernelConnectionState.reconnecting => (
          MonstruoTheme.warning,
          'Reconectando...',
          Icons.sync,
        ),
      KernelConnectionState.error => (
          MonstruoTheme.error,
          'Error de conexión',
          Icons.error_outline,
        ),
      KernelConnectionState.failed => (
          MonstruoTheme.error,
          'Sin conexión al kernel',
          Icons.cloud_off,
        ),
      KernelConnectionState.disconnected => (
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

/// Stack vertical de FABs de la cabina. Apilados en topRight.
/// Cada FAB es un tap directo a una ruta crítica del operador.
class _CockpitFabStack extends ConsumerWidget {
  const _CockpitFabStack();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Padding(
      padding: const EdgeInsets.only(top: 8, right: 4),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          // Hilo de Manus — botaca primaria (color de marca).
          FloatingActionButton.small(
            heroTag: 'fab_hilo',
            onPressed: () => GoRouter.of(context).push('/hilo'),
            backgroundColor: MonstruoTheme.primary,
            foregroundColor: Colors.black,
            elevation: 3,
            tooltip: 'Hilo de Manus',
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.bolt, size: 18),
          ),
          const SizedBox(height: 8),
          // Bandeja del Embrión con badge numérico de pendings.
          const _EmbrionInboxFab(),
          const SizedBox(height: 8),
          // Republic Overlay (Cara B vitrina).
          _RepublicFab(),
        ],
      ),
    );
  }
}

/// FAB del Embrión con badge numérico de propuestas pendientes.
/// Lee `embrionPendingProposalsProvider` y muestra contador en burbuja.
class _EmbrionInboxFab extends ConsumerWidget {
  const _EmbrionInboxFab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pending = ref.watch(embrionPendingProposalsProvider);
    final count = pending.maybeWhen(
      data: (list) => list.length,
      orElse: () => 0,
    );
    return Stack(
      clipBehavior: Clip.none,
      children: [
        FloatingActionButton.small(
          heroTag: 'fab_embrion',
          onPressed: () => GoRouter.of(context).push('/embrion/inbox'),
          backgroundColor: MonstruoTheme.surfaceElevated,
          foregroundColor: MonstruoTheme.onBackground,
          elevation: 2,
          tooltip: 'Bandeja del Embrión',
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(
              color: MonstruoTheme.divider.withValues(alpha: 0.6),
              width: 0.5,
            ),
          ),
          child: const Icon(Icons.inbox_outlined, size: 18),
        ),
        if (count > 0)
          Positioned(
            top: -4,
            right: -4,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              constraints: const BoxConstraints(minWidth: 18, minHeight: 18),
              decoration: BoxDecoration(
                color: MonstruoTheme.error,
                borderRadius: BorderRadius.circular(10),
                boxShadow: [
                  BoxShadow(
                    color: MonstruoTheme.error.withValues(alpha: 0.5),
                    blurRadius: 6,
                  ),
                ],
              ),
              child: Text(
                count > 99 ? '99+' : count.toString(),
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 10,
                  fontWeight: FontWeight.w700,
                  height: 1.1,
                ),
              ),
            ),
          ),
      ],
    );
  }
}

/// Mini-FAB que abre el RepublicOverlay (Cara B — Cognitive Republic).
/// Visible en cualquier modo (Daily o Cockpit). Estilo Apple-leaning sutil.
class _RepublicFab extends ConsumerWidget {
  const _RepublicFab();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Padding(
      padding: const EdgeInsets.only(top: 8, right: 4),
      child: FloatingActionButton.small(
        onPressed: () => RepublicOverlay.open(context, ref),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 2,
        tooltip: 'Cognitive Republic',
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: const BorderSide(color: Color(0x1F000000), width: 0.5),
        ),
        child: const Icon(Icons.hub_outlined, size: 18),
      ),
    );
  }
}
