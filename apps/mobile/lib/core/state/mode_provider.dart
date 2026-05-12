/// Mode provider — toggle Daily/Cockpit canonizado por APP_VISION v1.3.
///
/// Sprint MOBILE-REALIGNMENT-001 T3 introduce el state management central
/// para el modo de la app. La app inicia en `AppMode.daily` (uso cotidiano:
/// chat, threads, pendientes, conexiones, perfil) y puede alternar a
/// `AppMode.cockpit` (modo arquitectónico: MOC dashboard, finops, sandbox,
/// memory, embrion).
///
/// Consumo típico:
/// ```dart
/// final mode = ref.watch(modeProvider);
/// final isDaily = mode == AppMode.daily;
///
/// // Toggle
/// ref.read(modeProvider.notifier).toggle();
///
/// // Set explícito
/// ref.read(modeProvider.notifier).setMode(AppMode.cockpit);
/// ```
///
/// El toggle gestual (swipe-down dos dedos / long-press logo) se implementa
/// en T5 dentro de `widgets/shell_scaffold.dart`.
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Modo de operación de la app. Mutuamente excluyentes.
enum AppMode {
  /// Uso cotidiano: pestañas Daily (Home, Threads, Pendientes, Conexiones, Perfil).
  daily,

  /// Modo arquitectónico: MOC dashboard + drawer cockpit con features avanzadas.
  cockpit,
}

/// Notifier que gestiona transiciones entre Daily y Cockpit.
///
/// Empieza siempre en [AppMode.daily] (regla de UX: el modo cotidiano es el
/// default; Cockpit requiere acción explícita del usuario).
class ModeNotifier extends StateNotifier<AppMode> {
  ModeNotifier() : super(AppMode.daily);

  /// Alterna entre Daily y Cockpit en una sola operación.
  void toggle() {
    state = state == AppMode.daily ? AppMode.cockpit : AppMode.daily;
  }

  /// Setea el modo de forma explícita (útil para deep links u onboarding).
  void setMode(AppMode mode) {
    state = mode;
  }
}

/// Provider global del modo. Disponible mediante `ref.watch(modeProvider)`.
final modeProvider = StateNotifierProvider<ModeNotifier, AppMode>(
  (ref) => ModeNotifier(),
);
