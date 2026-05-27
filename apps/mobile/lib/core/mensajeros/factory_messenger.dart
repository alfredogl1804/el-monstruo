/// FactoryMessenger — Cliente de los endpoints /v1/factory/* del kernel.
///
/// Habilitante: DSC-G-019 (Adopción narrativa Cognitive Republic).
/// Sprint: SPR-FACTORY-AGGREGATORS-000.
///
/// Pasa por el AG-UI Gateway, que ya tiene la KERNEL_API_KEY como env var
/// (regla dura #6: cero secrets en plaintext en el cliente). El gateway
/// proxea limpiamente /v1/factory/* al kernel y devuelve JSON tal cual.
library;

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:logging/logging.dart';

import '../config.dart';
import '../../models/cognitive_republic.dart';

final _log = Logger('FactoryMessenger');

const _kSecureKeyApiKey = 'monstruo_kernel_api_key';

/// Provider para el storage seguro de credenciales.
final secureStorageProvider = Provider<FlutterSecureStorage>((ref) {
  return const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
  );
});

/// Provider que lee la API key desde el storage seguro.
/// Si no hay key, devuelve null y la pantalla muestra estado "Sin credencial".
final monstruoApiKeyProvider = FutureProvider<String?>((ref) async {
  final storage = ref.watch(secureStorageProvider);
  return await storage.read(key: _kSecureKeyApiKey);
});

/// Helper para guardar la API key (usado en onboarding o settings).
Future<void> setMonstruoApiKey(WidgetRef ref, String key) async {
  final storage = ref.read(secureStorageProvider);
  if (key.isEmpty) {
    await storage.delete(key: _kSecureKeyApiKey);
  } else {
    await storage.write(key: _kSecureKeyApiKey, value: key);
  }
  ref.invalidate(monstruoApiKeyProvider);
}

/// FactoryMessenger — cliente HTTP autenticado al kernel.
///
/// Usa Dio configurado contra `gatewayBaseUrl`. El gateway inyecta
/// X-API-Key con su propia env var del kernel — el cliente no la ve.
class FactoryMessenger {
  FactoryMessenger({
    required String? apiKey,
    Dio? dio,
  })  : _apiKey = apiKey,
        _dio = dio ??
            Dio(
              BaseOptions(
                baseUrl: AppConfig.gatewayBaseUrl,
                connectTimeout: AppConfig.connectTimeout,
                receiveTimeout: AppConfig.receiveTimeout,
                headers: {
                  'Content-Type': 'application/json',
                  if (apiKey != null && apiKey.isNotEmpty) 'X-API-Key': apiKey,
                },
              ),
            );

  final Dio _dio;
  final String? _apiKey;

  /// Compat shim — siempre true porque la auth la hace el gateway.
  bool get hasApiKey => true;

  // ─── Endpoints ───

  Future<ConstellationResponse> fetchConstellation({
    String? tier,
    String? kind,
  }) async {
    try {
      final params = <String, dynamic>{};
      if (tier != null) params['tier'] = tier;
      if (kind != null) params['kind'] = kind;

      final res = await _dio.get(
        AppConfig.factoryConstellationEndpoint,
        queryParameters: params.isEmpty ? null : params,
      );
      return ConstellationResponse.fromJson(
        res.data as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      _log.severe('fetchConstellation failed', e);
      rethrow;
    }
  }

  Future<CognitiveEconomy> fetchEconomy({String window = '24h'}) async {
    try {
      final res = await _dio.get(
        AppConfig.factoryEconomyEndpoint,
        queryParameters: {'window': window},
      );
      return CognitiveEconomy.fromJson(res.data as Map<String, dynamic>);
    } on DioException catch (e) {
      _log.severe('fetchEconomy failed', e);
      rethrow;
    }
  }

  Future<List<SovereignTimelineEvent>> fetchTimeline({
    int limit = 100,
    String? kind,
  }) async {
    try {
      final params = <String, dynamic>{'limit': limit};
      if (kind != null) params['kind'] = kind;

      final res = await _dio.get(
        AppConfig.factoryTimelineEndpoint,
        queryParameters: params,
      );
      final data = res.data as Map<String, dynamic>;
      return (data['events'] as List?)
              ?.map((e) =>
                  SovereignTimelineEvent.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [];
    } on DioException catch (e) {
      _log.severe('fetchTimeline failed', e);
      rethrow;
    }
  }

  Future<RealityDiff> fetchDiff() async {
    try {
      final res = await _dio.get(AppConfig.factoryDiffEndpoint);
      return RealityDiff.fromJson(res.data as Map<String, dynamic>);
    } on DioException catch (e) {
      _log.severe('fetchDiff failed', e);
      rethrow;
    }
  }
}

/// Provider del FactoryMessenger — depende de la API key del usuario.
final factoryMessengerProvider = Provider<FactoryMessenger>((ref) {
  final apiKeyAsync = ref.watch(monstruoApiKeyProvider);
  final apiKey = apiKeyAsync.valueOrNull;
  return FactoryMessenger(apiKey: apiKey);
});

// ─── Providers de datos vivos (auto-refresh manual via invalidate) ───

final constellationProvider =
    FutureProvider.autoDispose<ConstellationResponse>((ref) async {
  final messenger = ref.watch(factoryMessengerProvider);
  return messenger.fetchConstellation();
});

final economyProvider =
    FutureProvider.autoDispose.family<CognitiveEconomy, String>(
  (ref, window) async {
    final messenger = ref.watch(factoryMessengerProvider);
    return messenger.fetchEconomy(window: window);
  },
);

final timelineProvider =
    FutureProvider.autoDispose<List<SovereignTimelineEvent>>((ref) async {
  final messenger = ref.watch(factoryMessengerProvider);
  return messenger.fetchTimeline(limit: 100);
});

final realityDiffProvider = FutureProvider.autoDispose<RealityDiff>((ref) async {
  final messenger = ref.watch(factoryMessengerProvider);
  return messenger.fetchDiff();
});
