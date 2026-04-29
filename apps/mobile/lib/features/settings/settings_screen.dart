import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/config.dart';
import '../../services/kernel_service.dart';
import '../../theme/monstruo_theme.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final health = ref.watch(kernelHealthProvider);

    return Scaffold(
      backgroundColor: MonstruoTheme.background,
      appBar: AppBar(
        backgroundColor: MonstruoTheme.background,
        title: const Text('Configuración'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(MonstruoTheme.spacingMd),
        children: [
          // Kernel connection
          _SectionHeader(title: 'Conexión'),
          _SettingsTile(
            icon: Icons.cloud,
            title: 'Kernel URL',
            subtitle: AppConfig.kernelBaseUrl,
            trailing: health.when(
              data: (h) => Container(
                width: 10,
                height: 10,
                decoration: BoxDecoration(
                  color: h.isHealthy ? MonstruoTheme.success : MonstruoTheme.error,
                  shape: BoxShape.circle,
                ),
              ),
              loading: () => const SizedBox(
                width: 10,
                height: 10,
                child: CircularProgressIndicator(strokeWidth: 1.5, color: MonstruoTheme.primary),
              ),
              error: (_, __) => Container(
                width: 10,
                height: 10,
                decoration: const BoxDecoration(color: MonstruoTheme.error, shape: BoxShape.circle),
              ),
            ),
          ),
          _SettingsTile(
            icon: Icons.sync,
            title: 'Gateway URL',
            subtitle: AppConfig.gatewayBaseUrl,
          ),

          const SizedBox(height: MonstruoTheme.spacingLg),

          // Features
          _SectionHeader(title: 'Funciones'),
          _ToggleTile(
            icon: Icons.auto_awesome,
            title: 'Generative UI (A2UI)',
            subtitle: 'Interfaces dinámicas generadas por el agente',
            value: AppConfig.enableGenUI,
            onChanged: (v) {
              // TODO: Persist feature flags
            },
          ),
          _ToggleTile(
            icon: Icons.terminal,
            title: 'Sandbox Viewer',
            subtitle: 'Ver ejecución de código en tiempo real',
            value: AppConfig.enableSandboxViewer,
            onChanged: (v) {},
          ),
          _ToggleTile(
            icon: Icons.notifications,
            title: 'Push Notifications',
            subtitle: 'Notificaciones cuando el agente termina tareas',
            value: AppConfig.enablePushNotifications,
            onChanged: (v) {},
          ),
          _ToggleTile(
            icon: Icons.devices_fold,
            title: 'Layout Foldable',
            subtitle: 'Optimizar para OPPO Find N5 desplegado',
            value: AppConfig.enableFoldableLayout,
            onChanged: (v) {},
          ),

          const SizedBox(height: MonstruoTheme.spacingLg),

          // About
          _SectionHeader(title: 'Acerca de'),
          _SettingsTile(
            icon: Icons.info_outline,
            title: 'Versión',
            subtitle: '${AppConfig.appVersion} (${AppConfig.appBuildNumber})',
          ),
          _SettingsTile(
            icon: Icons.code,
            title: 'Kernel',
            subtitle: health.when(
              data: (h) => h.version,
              loading: () => 'Cargando...',
              error: (_, __) => 'No disponible',
            ),
          ),
          _SettingsTile(
            icon: Icons.psychology,
            title: 'Embrión',
            subtitle: health.when(
              data: (h) => h.embrionStatus ?? 'No disponible',
              loading: () => 'Cargando...',
              error: (_, __) => 'No disponible',
            ),
          ),

          const SizedBox(height: MonstruoTheme.spacingXl),

          // Doctrina
          Container(
            padding: const EdgeInsets.all(MonstruoTheme.spacingMd),
            decoration: BoxDecoration(
              color: MonstruoTheme.surface,
              borderRadius: BorderRadius.circular(MonstruoTheme.radiusMd),
              border: Border.all(color: MonstruoTheme.divider, width: 0.5),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    ShaderMask(
                      shaderCallback: (bounds) => MonstruoTheme.agentGradient.createShader(bounds),
                      child: const Text(
                        'El Monstruo',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                const Text(
                  'Agente IA Soberano de Alfredo Góngora.\n'
                  'Doctrina: SOP · EPIA · MAOC\n'
                  'Memoria soberana. Autonomía real. Cero dependencia.',
                  style: TextStyle(
                    fontSize: 13,
                    color: MonstruoTheme.onSurfaceDim,
                    height: 1.6,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.title});
  final String title;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8, top: 4),
      child: Text(
        title.toUpperCase(),
        style: const TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w600,
          color: MonstruoTheme.primary,
          letterSpacing: 1.2,
        ),
      ),
    );
  }
}

class _SettingsTile extends StatelessWidget {
  const _SettingsTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    this.trailing,
    this.onTap,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final Widget? trailing;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 2),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
        leading: Icon(icon, size: 20, color: MonstruoTheme.onSurfaceDim),
        title: Text(
          title,
          style: const TextStyle(fontSize: 14, color: MonstruoTheme.onBackground),
        ),
        subtitle: Text(
          subtitle,
          style: const TextStyle(fontSize: 12, color: MonstruoTheme.onSurfaceDim),
        ),
        trailing: trailing,
        onTap: onTap,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(MonstruoTheme.radiusSm),
        ),
      ),
    );
  }
}

class _ToggleTile extends StatelessWidget {
  const _ToggleTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.value,
    required this.onChanged,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final bool value;
  final ValueChanged<bool> onChanged;

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 2),
      child: SwitchListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
        secondary: Icon(icon, size: 20, color: MonstruoTheme.onSurfaceDim),
        title: Text(
          title,
          style: const TextStyle(fontSize: 14, color: MonstruoTheme.onBackground),
        ),
        subtitle: Text(
          subtitle,
          style: const TextStyle(fontSize: 12, color: MonstruoTheme.onSurfaceDim),
        ),
        value: value,
        onChanged: onChanged,
        activeColor: MonstruoTheme.primary,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(MonstruoTheme.radiusSm),
        ),
      ),
    );
  }
}
