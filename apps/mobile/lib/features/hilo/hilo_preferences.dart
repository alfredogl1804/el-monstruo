/// El Monstruo — Hilo de Manus — Preferences
/// ============================================
/// Persiste preferencias UI del Hilo de Manus entre sesiones:
///   - Último agente seleccionado (auto, manus, claude, gpt, gemini, perplexity)
///
/// Storage: SharedPreferences (sincrónico tras init, ya inicializado en main.dart).
/// Sprint: Cabina Dual — Pulido 2026-05-27 (ítem G).
library;

import 'package:logging/logging.dart';
import 'package:shared_preferences/shared_preferences.dart';

final _log = Logger('HiloPreferences');

class HiloPreferences {
  static const _lastAgentKey = 'monstruo_hilo_last_agent';

  /// Default agent cuando no hay preferencia guardada.
  static const defaultAgent = 'auto';

  /// Lee el último agente seleccionado por el usuario.
  /// Retorna 'auto' si no hay preferencia guardada o si el storage falla.
  static Future<String> getLastAgent() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final agent = prefs.getString(_lastAgentKey) ?? defaultAgent;
      _log.fine('Last agent loaded: $agent');
      return agent;
    } catch (e) {
      _log.warning('Failed to load last agent, falling back to default', e);
      return defaultAgent;
    }
  }

  /// Persiste el último agente seleccionado.
  static Future<void> setLastAgent(String agent) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_lastAgentKey, agent);
      _log.fine('Last agent saved: $agent');
    } catch (e) {
      _log.warning('Failed to save last agent', e);
    }
  }
}
