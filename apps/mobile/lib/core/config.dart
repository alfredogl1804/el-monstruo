/// El Monstruo App Configuration
/// All kernel connection settings and feature flags.
class AppConfig {
  AppConfig._();

  // ─── Kernel Connection ───
  static const String kernelBaseUrl =
      'https://el-monstruo-kernel-production.up.railway.app';

  static const String kernelWsUrl =
      'wss://el-monstruo-kernel-production.up.railway.app/ws';

  // ─── AG-UI Gateway ───
  static const String gatewayBaseUrl =
      'https://el-monstruo-gateway-production.up.railway.app';

  static const String gatewayWsUrl =
      'wss://el-monstruo-gateway-production.up.railway.app/agui/stream';

  // ─── API Endpoints ───
  static const String healthEndpoint = '/health';
  static const String chatEndpoint = '/api/chat';
  static const String runEndpoint = '/api/run';
  static const String memoryEndpoint = '/api/memory';
  static const String toolsEndpoint = '/api/tools';
  static const String filesEndpoint = '/api/files';
  static const String embrionEndpoint = '/api/embrion';

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
