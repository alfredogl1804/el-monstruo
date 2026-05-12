/// El Monstruo — Thread Persistence Service
/// ============================================
/// Persiste el thread_id activo entre sesiones de la app.
/// Resuelve el Problema #1: Thread ID efímero.
///
/// Principio: El Monstruo NUNCA pierde el hilo de la conversación.
/// Cuando cierras la app y la vuelves a abrir, retomas donde quedaste.
///
/// Almacenamiento:
/// - SharedPreferences para acceso rápido (local, sincrónico tras init)
/// - Fallback: si SharedPreferences se borra, el boot endpoint del Gateway
///   busca el último thread activo en Supabase.
///
/// Sprint: Gateway Evolution — Cambio 1
/// Fecha: 2 mayo 2026

import 'package:logging/logging.dart';
import 'package:shared_preferences/shared_preferences.dart';

final _log = Logger('ThreadPersistence');

class ThreadPersistence {
  static const _activeThreadKey = 'monstruo_active_thread_id';
  static const _threadCreatedAtKey = 'monstruo_thread_created_at';
  static const _threadMessageCountKey = 'monstruo_thread_message_count';

  static SharedPreferences? _prefs;

  /// Initialize SharedPreferences instance.
  /// Call once at app startup (e.g., in main.dart before runApp).
  static Future<void> initialize() async {
    _prefs = await SharedPreferences.getInstance();
    _log.info('ThreadPersistence initialized');
  }

  /// Get the currently active thread ID.
  /// Returns null if no thread is persisted (first launch or after clear).
  static String? getActiveThread() {
    final threadId = _prefs?.getString(_activeThreadKey);
    if (threadId != null) {
      _log.fine('Retrieved active thread: $threadId');
    }
    return threadId;
  }

  /// Persist a thread ID as the active conversation thread.
  /// Called when:
  /// - The Gateway responds with a thread_id in run_start
  /// - A new thread is explicitly created by the user
  static Future<void> setActiveThread(String threadId) async {
    await _prefs?.setString(_activeThreadKey, threadId);
    // Also store when this thread was set (for staleness detection)
    await _prefs?.setString(
      _threadCreatedAtKey,
      DateTime.now().toUtc().toIso8601String(),
    );
    _log.info('Active thread set: $threadId');
  }

  /// Increment the local message count for the active thread.
  /// Useful for knowing if the thread has meaningful content.
  static Future<void> incrementMessageCount() async {
    final current = _prefs?.getInt(_threadMessageCountKey) ?? 0;
    await _prefs?.setInt(_threadMessageCountKey, current + 1);
  }

  /// Get the message count for the active thread.
  static int getMessageCount() {
    return _prefs?.getInt(_threadMessageCountKey) ?? 0;
  }

  /// Get when the active thread was created/set.
  /// Returns null if no thread is active.
  static DateTime? getThreadCreatedAt() {
    final iso = _prefs?.getString(_threadCreatedAtKey);
    if (iso == null) return null;
    return DateTime.tryParse(iso);
  }

  /// Check if the active thread is "stale" (older than maxAge).
  /// A stale thread might indicate the user wants a fresh conversation.
  /// Default: 24 hours.
  static bool isThreadStale({Duration maxAge = const Duration(hours: 24)}) {
    final createdAt = getThreadCreatedAt();
    if (createdAt == null) return true;
    return DateTime.now().toUtc().difference(createdAt) > maxAge;
  }

  /// Clear the active thread.
  /// Called when:
  /// - User explicitly starts a new conversation (newThread button)
  /// - Thread is detected as stale and user confirms reset
  static Future<void> clearThread() async {
    await _prefs?.remove(_activeThreadKey);
    await _prefs?.remove(_threadCreatedAtKey);
    await _prefs?.remove(_threadMessageCountKey);
    _log.info('Active thread cleared');
  }

  /// Check if there is an active thread persisted.
  static bool hasActiveThread() {
    return getActiveThread() != null;
  }
}
