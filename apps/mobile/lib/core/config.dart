/// El Monstruo App Configuration
/// All kernel connection settings and feature flags.
///
/// Architecture:
///   [Flutter App] → [Gateway] → [Kernel]
///
/// The app talks to the Gateway (REST + WebSocket).
/// The Gateway proxies to the Kernel's /v1/* endpoints.
/// This keeps the app simple and the kernel untouched.
class AppConfig {
  AppConfig._();

  // ─── Gateway Connection (primary) ───
  // The gateway handles all mobile communication
  static String gatewayBaseUrl = const String.fromEnvironment(
    'GATEWAY_URL',
    defaultValue: 'https://el-monstruo-gateway-production.up.railway.app',
  );

  static String gatewayWsUrl = const String.fromEnvironment(
    'GATEWAY_WS_URL',
    defaultValue: 'wss://el-monstruo-gateway-production.up.railway.app/ws/chat',
  );

  // ─── Kernel Direct (fallback / health) ───
  static const String kernelBaseUrl =
      'https://el-monstruo-kernel-production.up.railway.app';

  // ─── API Endpoints (relative to gatewayBaseUrl) ───
  static const String healthEndpoint = '/health';
  static const String chatEndpoint = '/api/chat';
  static const String memoryStatsEndpoint = '/api/memory/stats';
  static const String memorySearchEndpoint = '/api/memory/search';
  static const String toolsEndpoint = '/api/tools';
  static const String embrionEndpoint = '/api/embrion';
  static const String finopsEndpoint = '/api/finops';
  static const String pushRegisterEndpoint = '/api/push/register';
  static const String aguiInfoEndpoint = '/api/agui/info';

  // ─── Timeouts ───
  static const Duration connectTimeout = Duration(seconds: 10);
  static const Duration receiveTimeout = Duration(seconds: 120);
  static const Duration wsReconnectDelay = Duration(seconds: 3);
  static const int wsMaxReconnectAttempts = 10;

  // ─── Feature Flags ───
  static const bool enableGenUI = true;
  static const bool enableSandboxViewer = true;
  static const bool enableFileViewer = true;
  static const bool enablePushNotifications = true;
  static const bool enableVoiceInput = false; // Phase 2
  static const bool enableFoldableLayout = true;

  // ─── App Info ───
  static const String appName = 'El Monstruo';
  static const String appVersion = '0.1.0';
  static const String appBuildNumber = '1';
}
