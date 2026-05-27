/// El Monstruo — Hilo de Manus — Historial local
/// ===============================================
/// Persiste el historial de hilos lanzados desde la app entre sesiones.
/// Cada entry guarda:
///   - id (UUID local)
///   - prompt original (texto del usuario)
///   - agent seleccionado al lanzar
///   - status: completed | cancelled | error
///   - stepsCount (cuántos steps generó)
///   - createdAt
///   - finishedAt
///   - errorMessage (si status==error)
///
/// Storage: Hive (caja persistente, ya en dependencias).
/// Caja: 'monstruo_hilo_historial'
///
/// NO guarda el contenido completo de los steps — el objetivo es trazabilidad
/// liviana, no replay. Replay completo requiere endpoint del kernel.
///
/// Sprint: Cabina Dual — Pulido 2026-05-27 (ítem A).
library;

import 'package:hive_flutter/hive_flutter.dart';
import 'package:logging/logging.dart';

final _log = Logger('HiloHistory');

class HiloHistoryEntry {
  final String id;
  final String prompt;
  final String agent;
  final String status; // completed | cancelled | error
  final int stepsCount;
  final DateTime createdAt;
  final DateTime? finishedAt;
  final String? errorMessage;

  HiloHistoryEntry({
    required this.id,
    required this.prompt,
    required this.agent,
    required this.status,
    required this.stepsCount,
    required this.createdAt,
    this.finishedAt,
    this.errorMessage,
  });

  Map<String, dynamic> toMap() => {
        'id': id,
        'prompt': prompt,
        'agent': agent,
        'status': status,
        'stepsCount': stepsCount,
        'createdAt': createdAt.toUtc().toIso8601String(),
        'finishedAt': finishedAt?.toUtc().toIso8601String(),
        'errorMessage': errorMessage,
      };

  factory HiloHistoryEntry.fromMap(Map<dynamic, dynamic> m) =>
      HiloHistoryEntry(
        id: m['id'] as String,
        prompt: m['prompt'] as String? ?? '',
        agent: m['agent'] as String? ?? 'auto',
        status: m['status'] as String? ?? 'completed',
        stepsCount: (m['stepsCount'] as num?)?.toInt() ?? 0,
        createdAt: DateTime.tryParse(m['createdAt'] as String? ?? '') ??
            DateTime.now().toUtc(),
        finishedAt: m['finishedAt'] != null
            ? DateTime.tryParse(m['finishedAt'] as String)
            : null,
        errorMessage: m['errorMessage'] as String?,
      );

  /// Resumen corto para listas (máx 60 chars del prompt).
  String get displayLabel {
    if (prompt.length <= 60) return prompt;
    return '${prompt.substring(0, 57)}…';
  }
}

class HiloHistory {
  static const _boxName = 'monstruo_hilo_historial';
  static const _maxEntries = 100; // cap para no crecer indefinidamente

  static Box? _box;

  /// Inicializa Hive y abre la caja. Llamar una vez en main.dart
  /// después de WidgetsFlutterBinding.ensureInitialized().
  static Future<void> initialize() async {
    try {
      await Hive.initFlutter();
      _box = await Hive.openBox(_boxName);
      _log.info('HiloHistory initialized — ${_box?.length ?? 0} entries');
    } catch (e) {
      _log.severe('Failed to initialize HiloHistory', e);
      // Fail-loud pero no rompe la app — el feature degrada a no-historial.
    }
  }

  /// Lista todas las entries ordenadas por createdAt descendente (más reciente primero).
  static List<HiloHistoryEntry> list() {
    final box = _box;
    if (box == null) return const [];
    try {
      final entries = box.values
          .whereType<Map>()
          .map((m) => HiloHistoryEntry.fromMap(m))
          .toList()
        ..sort((a, b) => b.createdAt.compareTo(a.createdAt));
      return entries;
    } catch (e) {
      _log.warning('Failed to list history', e);
      return const [];
    }
  }

  /// Agrega una nueva entry. Aplica el cap de _maxEntries borrando las más viejas.
  static Future<void> add(HiloHistoryEntry entry) async {
    final box = _box;
    if (box == null) return;
    try {
      await box.put(entry.id, entry.toMap());
      // Cap: si excedemos, borramos las más viejas.
      if (box.length > _maxEntries) {
        final all = list();
        final toRemove = all.skip(_maxEntries).map((e) => e.id).toList();
        for (final id in toRemove) {
          await box.delete(id);
        }
        _log.fine('History capped at $_maxEntries (removed ${toRemove.length})');
      }
    } catch (e) {
      _log.warning('Failed to add history entry', e);
    }
  }

  /// Actualiza una entry existente (típicamente cuando termina el hilo).
  static Future<void> update(HiloHistoryEntry entry) async {
    final box = _box;
    if (box == null) return;
    try {
      await box.put(entry.id, entry.toMap());
    } catch (e) {
      _log.warning('Failed to update history entry', e);
    }
  }

  /// Borra el historial completo (acción destructiva, requiere confirmación UI).
  static Future<void> clear() async {
    final box = _box;
    if (box == null) return;
    try {
      await box.clear();
      _log.info('History cleared');
    } catch (e) {
      _log.warning('Failed to clear history', e);
    }
  }

  /// Cuenta de entries actuales (para badges).
  static int get count => _box?.length ?? 0;
}
