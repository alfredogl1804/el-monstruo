/// EmbrionMessenger — Sprint SPR-MOBILE-EMBRION-INBOX-001.
///
/// Cliente del inbox del Embrión. Habla con el AG-UI Gateway que proxea
/// /v1/embrion/* al kernel. Cero secrets en el cliente — el gateway
/// inyecta KERNEL_API_KEY como env var.
///
/// Endpoints consumidos:
///   GET  /v1/embrion/proposals?status=...&limit=...
///   POST /v1/embrion/approve/{proposal_id}
///   POST /v1/embrion/reject/{proposal_id}
///   GET  /v1/embrion/estado
library;

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logging/logging.dart';

import '../config.dart';
import '../../models/embrion_models.dart';

final _log = Logger('EmbrionMessenger');

class EmbrionMessenger {
  EmbrionMessenger({Dio? dio})
      : _dio = dio ??
            Dio(
              BaseOptions(
                baseUrl: AppConfig.gatewayBaseUrl,
                connectTimeout: AppConfig.connectTimeout,
                receiveTimeout: AppConfig.receiveTimeout,
                headers: const {'Content-Type': 'application/json'},
              ),
            );

  final Dio _dio;

  /// Lista propuestas del Embrión filtradas por status.
  /// Default: solo 'pending' (lo único accionable desde el iPhone).
  Future<List<EmbrionProposal>> fetchProposals({
    String status = 'pending',
    int limit = 50,
  }) async {
    try {
      final res = await _dio.get(
        AppConfig.embrionProposalsEndpoint,
        queryParameters: {'status': status, 'limit': limit},
      );
      final data = res.data as Map<String, dynamic>;
      final proposals = (data['proposals'] as List?) ?? const [];
      return proposals
          .map((p) => EmbrionProposal.fromJson(p as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      _log.severe('fetchProposals failed', e);
      rethrow;
    }
  }

  /// Aprueba una propuesta. El worker del kernel la ejecutará.
  Future<EmbrionProposal> approveProposal(
    String proposalId, {
    String approvedBy = 'iphone:alfredo',
    String? notes,
  }) async {
    try {
      final res = await _dio.post(
        '${AppConfig.embrionApproveEndpoint}/$proposalId',
        data: {
          'approved_by': approvedBy,
          if (notes != null && notes.isNotEmpty) 'notes': notes,
        },
      );
      final data = res.data as Map<String, dynamic>;
      // El endpoint puede regresar la propuesta actualizada como 'proposal'
      // o el body completo — cubrimos ambos casos.
      final body = (data['proposal'] as Map<String, dynamic>?) ?? data;
      return EmbrionProposal.fromJson(body);
    } on DioException catch (e) {
      _log.severe('approveProposal failed for $proposalId', e);
      rethrow;
    }
  }

  /// Rechaza una propuesta con razón obligatoria.
  Future<EmbrionProposal> rejectProposal(
    String proposalId, {
    required String reason,
    String approvedBy = 'iphone:alfredo',
  }) async {
    try {
      final res = await _dio.post(
        '${AppConfig.embrionRejectEndpoint}/$proposalId',
        data: {
          'approved_by': approvedBy,
          'reason': reason,
        },
      );
      final data = res.data as Map<String, dynamic>;
      final body = (data['proposal'] as Map<String, dynamic>?) ?? data;
      return EmbrionProposal.fromJson(body);
    } on DioException catch (e) {
      _log.severe('rejectProposal failed for $proposalId', e);
      rethrow;
    }
  }

  /// Estado del loop autónomo (running, cycles, errores, presupuesto).
  Future<EmbrionEstado> fetchEstado() async {
    try {
      final res = await _dio.get(AppConfig.embrionEstadoEndpoint);
      // El kernel embebe el estado en distintos paths; lo aplanamos.
      final root = res.data as Map<String, dynamic>;
      final loop = (root['embrion_loop'] as Map<String, dynamic>?) ?? root;
      return EmbrionEstado.fromJson(loop);
    } on DioException catch (e) {
      _log.severe('fetchEstado failed', e);
      rethrow;
    }
  }
}

// ═══════════════════════════════════════════════════════════════
// Riverpod providers
// ═══════════════════════════════════════════════════════════════

final embrionMessengerProvider = Provider<EmbrionMessenger>((ref) {
  return EmbrionMessenger();
});

/// Propuestas pendientes — fuente del badge numérico en el shell.
final embrionPendingProposalsProvider =
    FutureProvider.autoDispose<List<EmbrionProposal>>((ref) async {
  final m = ref.watch(embrionMessengerProvider);
  return m.fetchProposals(status: 'pending', limit: 50);
});

/// Stream completo (incluye históricos) para el detalle del inbox.
final embrionAllProposalsProvider =
    FutureProvider.autoDispose<List<EmbrionProposal>>((ref) async {
  final m = ref.watch(embrionMessengerProvider);
  return m.fetchProposals(status: 'all', limit: 100);
});

/// Estado del loop — útil para mostrar "El Embrión está despierto" en el header.
final embrionEstadoProvider =
    FutureProvider.autoDispose<EmbrionEstado>((ref) async {
  final m = ref.watch(embrionMessengerProvider);
  return m.fetchEstado();
});
