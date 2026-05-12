/// SMP (Socialist Millionaires' Protocol) placeholder.
///
/// Sprint MOBILE-REALIGNMENT-001 T2 reserva este path para el futuro
/// Sprint Mobile-SMP-001 que implementará el handshake SMP de E2EE entre
/// el dispositivo de Alfredo y el kernel del Monstruo.
///
/// **NO IMPLEMENTAR SMP EN ESTE SPRINT** (regla dura #3 del spec).
///
/// Referencias:
///   - APP_VISION_v1.md §SMP — autenticación bidireccional sin compartir secret
///   - https://en.wikipedia.org/wiki/Socialist_millionaires_problem
library;

/// Stub que documenta la API esperada del Sprint Mobile-SMP-001.
abstract class SmpHandshake {
  /// Inicia el handshake con el kernel.
  ///
  /// Retorna un token de sesión si el handshake es exitoso.
  /// Lanza `SmpHandshakeException` si la prueba zero-knowledge falla.
  Future<String> initiate({required String sharedSecret});

  /// Verifica que la otra parte conozca el mismo secreto SIN revelarlo.
  Future<bool> verify({required String challenge, required String response});
}

/// Excepción específica de SMP — distinta de errores genéricos para que
/// la UI pueda mostrar mensajes específicos ("¿el secreto no coincide?").
class SmpHandshakeException implements Exception {
  const SmpHandshakeException(this.message);
  final String message;
  @override
  String toString() => 'SmpHandshakeException: $message';
}
