/// Marker file — directorio reservado para componentes A2UI especializados.
///
/// Cuando Sprint MOBILE-1B A2UI (PR #92) se mergee, los 16 widgets whitelist
/// + 3 widgets especializados Monstruo vivirán acá:
///   - actions.dart, containers.dart, content.dart, data.dart, progress.dart
///   - specialized.dart (3 widgets Monstruo: agent_selector, tool_activity_bar, etc.)
///
/// Este marker existe únicamente para que `git` preserve el directorio (Dart
/// no carga este archivo en compilación porque no se importa desde ningún lado).
///
/// Sprint: MOBILE-REALIGNMENT-001 T2
library;
