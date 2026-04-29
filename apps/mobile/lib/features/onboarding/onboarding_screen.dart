import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../theme/monstruo_theme.dart';
import '../../core/config.dart';
import '../../services/kernel_service.dart';

/// Onboarding screen shown on first launch.
///
/// Steps:
/// 1. Welcome + branding
/// 2. Connect to kernel (enter URL or use default)
/// 3. Verify connection
/// 4. Done
class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final _pageController = PageController();
  int _currentPage = 0;
  final _kernelUrlController = TextEditingController(
    text: AppConfig.kernelUrl,
  );
  bool _connecting = false;
  bool _connected = false;
  String? _connectionError;
  Map<String, dynamic>? _kernelHealth;

  @override
  void dispose() {
    _pageController.dispose();
    _kernelUrlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: MonstruoTheme.background,
      body: SafeArea(
        child: Column(
          children: [
            // Progress dots
            Padding(
              padding: const EdgeInsets.all(24),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(3, (index) {
                  return Container(
                    width: index == _currentPage ? 24 : 8,
                    height: 8,
                    margin: const EdgeInsets.symmetric(horizontal: 4),
                    decoration: BoxDecoration(
                      color: index == _currentPage
                          ? MonstruoTheme.primary
                          : MonstruoTheme.surfaceVariant,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  );
                }),
              ),
            ),

            // Pages
            Expanded(
              child: PageView(
                controller: _pageController,
                physics: const NeverScrollableScrollPhysics(),
                onPageChanged: (page) => setState(() => _currentPage = page),
                children: [
                  _WelcomePage(onNext: _nextPage),
                  _ConnectPage(
                    controller: _kernelUrlController,
                    connecting: _connecting,
                    connected: _connected,
                    error: _connectionError,
                    health: _kernelHealth,
                    onConnect: _testConnection,
                    onNext: _nextPage,
                  ),
                  _DonePage(onFinish: _finish),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _nextPage() {
    _pageController.nextPage(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  Future<void> _testConnection() async {
    setState(() {
      _connecting = true;
      _connectionError = null;
      _connected = false;
    });

    try {
      final health = await KernelService().getHealth();
      setState(() {
        _connecting = false;
        _connected = true;
        _kernelHealth = health;
      });
    } catch (e) {
      setState(() {
        _connecting = false;
        _connectionError = e.toString();
      });
    }
  }

  Future<void> _finish() async {
    // Save onboarding complete flag
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('onboarding_complete', true);
    await prefs.setString('kernel_url', _kernelUrlController.text);

    if (mounted) {
      context.go('/chat');
    }
  }
}

// ─── Welcome Page ───
class _WelcomePage extends StatelessWidget {
  const _WelcomePage({required this.onNext});
  final VoidCallback onNext;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 32),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Logo
          Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  MonstruoTheme.primary,
                  MonstruoTheme.secondary,
                ],
              ),
              borderRadius: BorderRadius.circular(30),
              boxShadow: [
                BoxShadow(
                  color: MonstruoTheme.primary.withValues(alpha: 0.3),
                  blurRadius: 30,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: const Center(
              child: Text(
                'M',
                style: TextStyle(
                  fontSize: 64,
                  fontWeight: FontWeight.w900,
                  color: Colors.white,
                ),
              ),
            ),
          ),
          const SizedBox(height: 40),
          const Text(
            'El Monstruo',
            style: TextStyle(
              fontSize: 32,
              fontWeight: FontWeight.w800,
              color: MonstruoTheme.onBackground,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 12),
          const Text(
            'Tu agente IA soberano',
            style: TextStyle(
              fontSize: 16,
              color: MonstruoTheme.onSurfaceDim,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Sandbox · Browser · Deep Research · Generative UI\n4 modelos IA · Memoria soberana · Embrión autónomo',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 13,
              color: MonstruoTheme.onSurfaceDim,
              height: 1.6,
            ),
          ),
          const SizedBox(height: 48),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: onNext,
              style: ElevatedButton.styleFrom(
                backgroundColor: MonstruoTheme.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: const Text(
                'Comenzar',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ─── Connect Page ───
class _ConnectPage extends StatelessWidget {
  const _ConnectPage({
    required this.controller,
    required this.connecting,
    required this.connected,
    required this.error,
    required this.health,
    required this.onConnect,
    required this.onNext,
  });

  final TextEditingController controller;
  final bool connecting;
  final bool connected;
  final String? error;
  final Map<String, dynamic>? health;
  final VoidCallback onConnect;
  final VoidCallback onNext;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 32),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.link,
            size: 48,
            color: MonstruoTheme.primary,
          ),
          const SizedBox(height: 24),
          const Text(
            'Conectar al Kernel',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w700,
              color: MonstruoTheme.onBackground,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Ingresa la URL de tu kernel de El Monstruo en Railway',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 14,
              color: MonstruoTheme.onSurfaceDim,
            ),
          ),
          const SizedBox(height: 32),
          TextField(
            controller: controller,
            style: const TextStyle(
              fontSize: 14,
              color: MonstruoTheme.onBackground,
            ),
            decoration: InputDecoration(
              labelText: 'Kernel URL',
              hintText: 'https://el-monstruo-kernel-production.up.railway.app',
              labelStyle: const TextStyle(color: MonstruoTheme.onSurfaceDim),
              filled: true,
              fillColor: MonstruoTheme.surfaceVariant,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: MonstruoTheme.primary),
              ),
              suffixIcon: connected
                  ? const Icon(Icons.check_circle, color: MonstruoTheme.success)
                  : null,
            ),
          ),
          const SizedBox(height: 16),

          if (error != null)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: MonstruoTheme.error.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Icons.error_outline, size: 16, color: MonstruoTheme.error),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      error!,
                      style: const TextStyle(
                        fontSize: 12,
                        color: MonstruoTheme.error,
                      ),
                    ),
                  ),
                ],
              ),
            ),

          if (connected && health != null)
            Container(
              padding: const EdgeInsets.all(12),
              margin: const EdgeInsets.only(top: 8),
              decoration: BoxDecoration(
                color: MonstruoTheme.success.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.check_circle, size: 16, color: MonstruoTheme.success),
                      SizedBox(width: 8),
                      Text(
                        'Kernel conectado',
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                          color: MonstruoTheme.success,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Versión: ${health!['version'] ?? 'unknown'}',
                    style: const TextStyle(
                      fontSize: 12,
                      color: MonstruoTheme.onSurface,
                    ),
                  ),
                  Text(
                    'Componentes: ${(health!['active_components'] as List?)?.length ?? 0}',
                    style: const TextStyle(
                      fontSize: 12,
                      color: MonstruoTheme.onSurface,
                    ),
                  ),
                ],
              ),
            ),

          const SizedBox(height: 24),

          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: connecting ? null : (connected ? onNext : onConnect),
              style: ElevatedButton.styleFrom(
                backgroundColor: connected ? MonstruoTheme.success : MonstruoTheme.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: connecting
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : Text(
                      connected ? 'Continuar' : 'Conectar',
                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                    ),
            ),
          ),
        ],
      ),
    );
  }
}

// ─── Done Page ───
class _DonePage extends StatelessWidget {
  const _DonePage({required this.onFinish});
  final VoidCallback onFinish;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 32),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: MonstruoTheme.success.withValues(alpha: 0.15),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.check,
              size: 40,
              color: MonstruoTheme.success,
            ),
          ),
          const SizedBox(height: 32),
          const Text(
            'Todo listo',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.w800,
              color: MonstruoTheme.onBackground,
            ),
          ),
          const SizedBox(height: 12),
          const Text(
            'El Monstruo está conectado y listo para trabajar.\n\nEscribe un mensaje, usa voz, o envía archivos.\nEl agente ejecuta tareas en background y te notifica cuando termina.',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 14,
              color: MonstruoTheme.onSurfaceDim,
              height: 1.6,
            ),
          ),
          const SizedBox(height: 48),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: onFinish,
              style: ElevatedButton.styleFrom(
                backgroundColor: MonstruoTheme.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: const Text(
                'Abrir El Monstruo',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
