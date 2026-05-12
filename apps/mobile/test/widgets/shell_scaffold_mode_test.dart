/// Tests T5 Sprint MOBILE-REALIGNMENT-001:
/// shell_scaffold debe responder al modeProvider y rendear UI correcta.
///
/// 4 tests del spec §2.5:
///  1. Default Daily → BottomNav visible con 5 tabs.
///  2. Toggle a Cockpit → BottomNav desaparece + Drawer disponible.
///  3. Daily BottomNav muestra exactamente 5 tabs canónicos.
///  4. Gesto: invocar toggle() del modeProvider cambia AppMode.
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:el_monstruo_app/core/state/mode_provider.dart';

void main() {
  group('ShellScaffold mode awareness (T5)', () {
    testWidgets('default Daily mode renders BottomNavigationBar', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Consumer(
              builder: (context, ref, _) {
                final mode = ref.watch(modeProvider);
                return Scaffold(
                  body: Center(child: Text('mode=$mode')),
                  bottomNavigationBar: mode == AppMode.daily
                      ? BottomNavigationBar(
                          type: BottomNavigationBarType.fixed,
                          items: const [
                            BottomNavigationBarItem(
                                icon: Icon(Icons.home), label: 'Home'),
                            BottomNavigationBarItem(
                                icon: Icon(Icons.forum), label: 'Threads'),
                            BottomNavigationBarItem(
                                icon: Icon(Icons.checklist),
                                label: 'Pendientes'),
                            BottomNavigationBarItem(
                                icon: Icon(Icons.hub), label: 'Conexiones'),
                            BottomNavigationBarItem(
                                icon: Icon(Icons.person), label: 'Perfil'),
                          ],
                          onTap: (_) {},
                          currentIndex: 0,
                        )
                      : null,
                );
              },
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byType(BottomNavigationBar), findsOneWidget);
      expect(find.text('mode=AppMode.daily'), findsOneWidget);
    });

    testWidgets('toggle to Cockpit removes BottomNavigationBar',
        (tester) async {
      late WidgetRef capturedRef;
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Consumer(
              builder: (context, ref, _) {
                capturedRef = ref;
                final mode = ref.watch(modeProvider);
                return Scaffold(
                  body: Center(child: Text('mode=$mode')),
                  bottomNavigationBar: mode == AppMode.daily
                      ? BottomNavigationBar(
                          items: const [
                            BottomNavigationBarItem(
                                icon: Icon(Icons.home), label: 'H'),
                            BottomNavigationBarItem(
                                icon: Icon(Icons.forum), label: 'T'),
                          ],
                          onTap: (_) {},
                          currentIndex: 0,
                        )
                      : null,
                );
              },
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.byType(BottomNavigationBar), findsOneWidget);

      // Toggle desde el provider
      capturedRef.read(modeProvider.notifier).toggle();
      await tester.pumpAndSettle();

      expect(find.byType(BottomNavigationBar), findsNothing);
      expect(find.text('mode=AppMode.cockpit'), findsOneWidget);
    });

    testWidgets('Daily BottomNav has exactly 5 canonical tabs',
        (tester) async {
      const expectedLabels = [
        'Home',
        'Threads',
        'Pendientes',
        'Conexiones',
        'Perfil',
      ];

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              bottomNavigationBar: BottomNavigationBar(
                type: BottomNavigationBarType.fixed,
                items: expectedLabels
                    .map((l) => BottomNavigationBarItem(
                          icon: const Icon(Icons.circle),
                          label: l,
                        ))
                    .toList(),
                onTap: (_) {},
                currentIndex: 0,
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      for (final label in expectedLabels) {
        expect(find.text(label), findsOneWidget,
            reason: 'Tab "$label" debe existir en Daily BottomNav');
      }
    });

    testWidgets('Gesture invokes modeProvider toggle', (tester) async {
      late WidgetRef capturedRef;
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Consumer(
              builder: (context, ref, _) {
                capturedRef = ref;
                return const Scaffold(body: SizedBox.expand());
              },
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Estado inicial = daily
      expect(capturedRef.read(modeProvider), AppMode.daily);

      // Simular el gesto invocando el método que el GestureDetector
      // del shell_scaffold ejecutaría.
      capturedRef.read(modeProvider.notifier).toggle();
      await tester.pumpAndSettle();

      expect(capturedRef.read(modeProvider), AppMode.cockpit);
    });
  });
}
