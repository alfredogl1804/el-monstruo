import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../services/kernel_service.dart';
import '../../theme/monstruo_theme.dart';

class SandboxScreen extends ConsumerStatefulWidget {
  const SandboxScreen({super.key});

  @override
  ConsumerState<SandboxScreen> createState() => _SandboxScreenState();
}

class _SandboxScreenState extends ConsumerState<SandboxScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final health = ref.watch(kernelHealthProvider);

    return Scaffold(
      backgroundColor: MonstruoTheme.background,
      appBar: AppBar(
        backgroundColor: MonstruoTheme.background,
        title: const Text('Sandbox & Herramientas'),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: MonstruoTheme.primary,
          labelColor: MonstruoTheme.primary,
          unselectedLabelColor: MonstruoTheme.onSurfaceDim,
          tabs: const [
            Tab(text: 'Terminal', icon: Icon(Icons.terminal, size: 18)),
            Tab(text: 'Browser', icon: Icon(Icons.language, size: 18)),
            Tab(text: 'Kernel', icon: Icon(Icons.monitor_heart, size: 18)),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _TerminalTab(),
          _BrowserTab(),
          _KernelTab(health: health),
        ],
      ),
    );
  }
}

class _TerminalTab extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      color: const Color(0xFF0D0D0D),
      padding: const EdgeInsets.all(MonstruoTheme.spacingMd),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Terminal header
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: MonstruoTheme.surfaceVariant,
              borderRadius: const BorderRadius.vertical(
                top: Radius.circular(MonstruoTheme.radiusSm),
              ),
            ),
            child: Row(
              children: [
                Container(width: 10, height: 10, decoration: const BoxDecoration(color: MonstruoTheme.error, shape: BoxShape.circle)),
                const SizedBox(width: 6),
                Container(width: 10, height: 10, decoration: const BoxDecoration(color: MonstruoTheme.warning, shape: BoxShape.circle)),
                const SizedBox(width: 6),
                Container(width: 10, height: 10, decoration: const BoxDecoration(color: MonstruoTheme.success, shape: BoxShape.circle)),
                const SizedBox(width: 12),
                const Text(
                  'E2B Sandbox',
                  style: TextStyle(fontSize: 12, color: MonstruoTheme.onSurfaceDim),
                ),
              ],
            ),
          ),
          // Terminal body
          Expanded(
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: const BoxDecoration(
                color: Color(0xFF0D0D0D),
                borderRadius: BorderRadius.vertical(
                  bottom: Radius.circular(MonstruoTheme.radiusSm),
                ),
              ),
              child: const SingleChildScrollView(
                child: SelectableText(
                  '> El Monstruo Sandbox v0.1.0\n'
                  '> Conectado a E2B Cloud Runtime\n'
                  '> Python 3.12 | Node 22 | Bash\n'
                  '>\n'
                  '> Esperando ejecución de código...\n'
                  '> Envía un mensaje al Monstruo pidiendo que ejecute código\n'
                  '> y verás la salida aquí en tiempo real.\n',
                  style: TextStyle(
                    fontFamily: 'monospace',
                    fontSize: 13,
                    color: MonstruoTheme.success,
                    height: 1.6,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _BrowserTab extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.language, size: 64, color: MonstruoTheme.onSurfaceDim.withValues(alpha: 0.3)),
          const SizedBox(height: 16),
          const Text(
            'Browser Autónomo',
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
              'Cuando El Monstruo navegue la web, verás las capturas de pantalla y acciones aquí en tiempo real.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 14,
                color: MonstruoTheme.onSurfaceDim,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _KernelTab extends StatelessWidget {
  const _KernelTab({required this.health});
  final AsyncValue health;

  @override
  Widget build(BuildContext context) {
    return health.when(
      loading: () => const Center(
        child: CircularProgressIndicator(color: MonstruoTheme.primary),
      ),
      error: (e, _) => Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.cloud_off, size: 48, color: MonstruoTheme.error),
            const SizedBox(height: 16),
            Text(
              'Error: $e',
              style: const TextStyle(color: MonstruoTheme.error),
            ),
          ],
        ),
      ),
      data: (kernelHealth) {
        final health = kernelHealth as dynamic;
        return ListView(
          padding: const EdgeInsets.all(MonstruoTheme.spacingMd),
          children: [
            // Status card
            _StatusCard(
              title: 'Kernel',
              status: health.status,
              version: health.version,
              isHealthy: health.isHealthy,
            ),
            const SizedBox(height: 12),

            // Embrion card
            if (health.embrionStatus != null)
              _StatusCard(
                title: 'Embrión',
                status: health.embrionStatus!,
                subtitle: '${health.embrionCycles ?? 0} ciclos hoy · \$${health.embrionCost?.toStringAsFixed(2) ?? "0.00"}',
                isHealthy: health.isEmbrionActive,
              ),
            const SizedBox(height: 12),

            // Components
            const Text(
              'Componentes',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: MonstruoTheme.onBackground,
              ),
            ),
            const SizedBox(height: 8),
            ...health.components.map<Widget>((c) => _ComponentTile(component: c)),

            const SizedBox(height: 16),

            // Models
            const Text(
              'Modelos IA',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: MonstruoTheme.onBackground,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: health.models.map<Widget>((m) => Chip(
                label: Text(m, style: const TextStyle(fontSize: 12)),
                backgroundColor: MonstruoTheme.surfaceVariant,
                side: BorderSide.none,
              )).toList(),
            ),
          ],
        );
      },
    );
  }
}

class _StatusCard extends StatelessWidget {
  const _StatusCard({
    required this.title,
    required this.status,
    this.version,
    this.subtitle,
    required this.isHealthy,
  });

  final String title;
  final String status;
  final String? version;
  final String? subtitle;
  final bool isHealthy;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: MonstruoTheme.surface,
        borderRadius: BorderRadius.circular(MonstruoTheme.radiusMd),
        border: Border.all(color: MonstruoTheme.divider, width: 0.5),
      ),
      child: Row(
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              color: isHealthy ? MonstruoTheme.success : MonstruoTheme.error,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: MonstruoTheme.onBackground,
                  ),
                ),
                if (version != null)
                  Text(version!, style: const TextStyle(fontSize: 12, color: MonstruoTheme.onSurfaceDim)),
                if (subtitle != null)
                  Text(subtitle!, style: const TextStyle(fontSize: 12, color: MonstruoTheme.onSurfaceDim)),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: isHealthy
                  ? MonstruoTheme.success.withValues(alpha: 0.15)
                  : MonstruoTheme.error.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(MonstruoTheme.radiusFull),
            ),
            child: Text(
              status.toUpperCase(),
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: isHealthy ? MonstruoTheme.success : MonstruoTheme.error,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ComponentTile extends StatelessWidget {
  const _ComponentTile({required this.component});
  final dynamic component;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: MonstruoTheme.surfaceVariant,
          borderRadius: BorderRadius.circular(MonstruoTheme.radiusSm),
        ),
        child: Row(
          children: [
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                color: component.isActive ? MonstruoTheme.success : MonstruoTheme.onSurfaceDim,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                component.name,
                style: const TextStyle(
                  fontSize: 13,
                  color: MonstruoTheme.onSurface,
                ),
              ),
            ),
            Text(
              component.status,
              style: TextStyle(
                fontSize: 11,
                color: component.isActive ? MonstruoTheme.success : MonstruoTheme.onSurfaceDim,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
