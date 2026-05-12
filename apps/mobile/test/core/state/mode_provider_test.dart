/// Tests para ModeNotifier — Sprint MOBILE-REALIGNMENT-001 T3.
///
/// 3 tests requeridos por el spec:
///   1. default state == AppMode.daily
///   2. toggle() alterna correctamente daily <-> cockpit
///   3. setMode(x) fija el estado explícitamente
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:el_monstruo_app/core/state/mode_provider.dart';

void main() {
  group('ModeNotifier', () {
    test('inicia en AppMode.daily por default', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      expect(container.read(modeProvider), AppMode.daily);
    });

    test('toggle() alterna daily <-> cockpit', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Estado inicial
      expect(container.read(modeProvider), AppMode.daily);

      // Primer toggle: daily -> cockpit
      container.read(modeProvider.notifier).toggle();
      expect(container.read(modeProvider), AppMode.cockpit);

      // Segundo toggle: cockpit -> daily
      container.read(modeProvider.notifier).toggle();
      expect(container.read(modeProvider), AppMode.daily);

      // Tercer toggle confirma idempotencia de la lógica
      container.read(modeProvider.notifier).toggle();
      expect(container.read(modeProvider), AppMode.cockpit);
    });

    test('setMode() fija el estado explícitamente', () {
      final container = ProviderContainer();
      addTearDown(container.dispose);

      // Setear daily explícitamente (aunque ya esté en daily) no falla
      container.read(modeProvider.notifier).setMode(AppMode.daily);
      expect(container.read(modeProvider), AppMode.daily);

      // Setear cockpit
      container.read(modeProvider.notifier).setMode(AppMode.cockpit);
      expect(container.read(modeProvider), AppMode.cockpit);

      // Volver a daily
      container.read(modeProvider.notifier).setMode(AppMode.daily);
      expect(container.read(modeProvider), AppMode.daily);
    });
  });
}
