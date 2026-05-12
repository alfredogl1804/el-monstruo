/// Smoke test mínimo de MonstruoApp.
///
/// El test legacy del scaffold de Flutter (Counter incrementa "0" → "1") fue
/// reemplazado en Sprint MOBILE-REALIGNMENT-001 al renombrar MyApp → MonstruoApp.
///
/// NOTA: NO se hace pumpWidget(MonstruoApp) porque el árbol completo inicia el
/// WebSocket del kernel_messenger, que queda como timer pendiente y rompe el
/// AutomatedTestWidgetsFlutterBinding (issue conocido de Flutter test). El
/// smoke binario real ocurre en T7 (Mac de Alfredo, app nativa).
library;

import 'package:flutter_test/flutter_test.dart';

import 'package:el_monstruo_app/app.dart';

void main() {
  test('MonstruoApp class is exported correctly', () {
    // Verifica que la clase MonstruoApp existe y es instanciable a nivel
    // de tipo (sin construir el widget tree completo, que iniciaría
    // WebSocket del kernel y dejaría timers pendientes).
    expect(MonstruoApp, isNotNull);
    const widget = MonstruoApp();
    expect(widget, isA<MonstruoApp>());
  });
}
