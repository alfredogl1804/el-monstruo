/// Daily Home — wrap del ChatScreen actual.
///
/// Sprint MOBILE-REALIGNMENT-001 T4 mapea el legacy `features/chat/chat_screen.dart`
/// al nuevo path canónico `modes/daily/home_screen.dart` SIN mover el archivo
/// original. Estrategia de proxy/re-export para preservar git history limpia
/// y permitir rollback trivial (regla 2 del spec).
///
/// Cuando Sprint Mobile-2 (Daily Fase 1) implemente Home propiamente, esta clase
/// se reemplazará por una pantalla Home dedicada que combine:
///   - Greeting card "¿Qué necesitás hoy?"
///   - Acceso rápido al chat
///   - Resumen de threads activos
///   - Pendientes urgentes
library;

export '../../features/chat/chat_screen.dart' show ChatScreen;

import 'package:flutter/material.dart';
import '../../features/chat/chat_screen.dart';

/// HomeScreen del modo Daily. Por ahora delega 100% al ChatScreen existente.
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const ChatScreen();
  }
}
