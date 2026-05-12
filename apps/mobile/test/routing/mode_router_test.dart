/// Tests T6 Sprint MOBILE-REALIGNMENT-001:
/// mode_router debe clasificar paths por modo y hacer redirect cross-mode.
library;

import 'package:flutter_test/flutter_test.dart';

import 'package:el_monstruo_app/core/state/mode_provider.dart';
import 'package:el_monstruo_app/routing/mode_router.dart';

void main() {
  group('mode_router classification (T6)', () {
    test('Daily paths classified as AppMode.daily', () {
      for (final path in [
        '/home',
        '/threads',
        '/pendientes',
        '/conexiones',
        '/perfil',
        '/threads/123',
      ]) {
        expect(expectedModeForPath(path), AppMode.daily,
            reason: 'Path $path debe ser Daily');
      }
    });

    test('Cockpit paths classified as AppMode.cockpit', () {
      for (final path in [
        '/cockpit/moc',
        '/cockpit/finops',
        '/cockpit/sandbox',
        '/cockpit/memory',
        '/cockpit/embrion',
        '/cockpit/a2ui',
      ]) {
        expect(expectedModeForPath(path), AppMode.cockpit,
            reason: 'Path $path debe ser Cockpit');
      }
    });

    test('Neutral paths return null', () {
      for (final path in ['/onboarding', '/file-viewer', '/files']) {
        expect(expectedModeForPath(path), isNull,
            reason: 'Path $path no pertenece a ningún modo');
      }
    });

    test('dailyPaths y cockpitPaths son disjuntos', () {
      final intersection = dailyPaths.intersection(cockpitPaths);
      expect(intersection, isEmpty,
          reason: 'Daily y Cockpit no deben compartir paths');
    });

    test('Cockpit paths siempre empiezan con /cockpit/', () {
      for (final p in cockpitPaths) {
        expect(p.startsWith('/cockpit/'), isTrue,
            reason: 'Path Cockpit "$p" debe empezar con /cockpit/');
      }
    });
  });
}
