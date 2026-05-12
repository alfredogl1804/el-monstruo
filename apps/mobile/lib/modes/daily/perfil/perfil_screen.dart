/// Perfil — proxy hacia SettingsScreen del modo Daily.
///
/// Sprint MOBILE-REALIGNMENT-001 T4 mapea el legacy `features/settings/settings_screen.dart`
/// (268 LOC) al path canónico `modes/daily/perfil/perfil_screen.dart`.
/// Sin mover el archivo original (regla 2 del spec — preserva git history).
library;

import 'package:flutter/material.dart';
import '../../../features/settings/settings_screen.dart';

class PerfilScreen extends StatelessWidget {
  const PerfilScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const SettingsScreen();
  }
}
