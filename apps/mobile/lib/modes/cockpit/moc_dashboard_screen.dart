/// MOC Dashboard — proxy hacia features/moc/moc_screen.dart en modo Cockpit.
///
/// Sprint MOBILE-REALIGNMENT-001 T4 mapea el legacy `features/moc/moc_screen.dart`
/// (646 LOC, dashboard MOC) al path canónico `modes/cockpit/moc_dashboard_screen.dart`.
/// Sin mover el archivo original (regla 2 del spec).
///
/// MOC Dashboard es la "home" del modo Cockpit (modo arquitectónico).
library;

import 'package:flutter/material.dart';
import '../../features/moc/moc_screen.dart';

class MocDashboardScreen extends StatelessWidget {
  const MocDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const MocScreen();
  }
}
