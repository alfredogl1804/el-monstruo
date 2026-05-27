/// embrion_models — Sprint SPR-MOBILE-EMBRION-INBOX-001
///
/// Modelos Dart inmutables para:
///   - EmbrionProposal: propuesta autónoma del Embrión esperando decisión.
///   - EmbrionEstado:    estado actual del loop autónomo (cycles, errores).
///   - AguiEvent:        un evento del stream SSE AG-UI (thinking → tool → done).
///   - Mission:          hilo persistente con tareas complejas.
///
/// Schema oficial respaldado por:
///   - kernel/embrion_routes.py (ProposeRequest, /proposals)
///   - kernel/agui_adapter.py   (AGUIEventType)
///   - kernel/mission_routes.py (MissionCreate)
library;

import 'package:flutter/foundation.dart';

// ═══════════════════════════════════════════════════════════════
// EmbrionProposal — propuesta autónoma
// ═══════════════════════════════════════════════════════════════

/// Status de una propuesta. Source of truth: write_policy table.
enum ProposalStatus {
  pending,
  approved,
  rejected,
  expired,
  executed,
  failed,
  unknown;

  static ProposalStatus fromString(String s) {
    return switch (s.toLowerCase()) {
      'pending' => ProposalStatus.pending,
      'approved' => ProposalStatus.approved,
      'rejected' => ProposalStatus.rejected,
      'expired' => ProposalStatus.expired,
      'executed' => ProposalStatus.executed,
      'failed' => ProposalStatus.failed,
      _ => ProposalStatus.unknown,
    };
  }

  String get label => switch (this) {
        ProposalStatus.pending => 'Pendiente',
        ProposalStatus.approved => 'Aprobada',
        ProposalStatus.rejected => 'Rechazada',
        ProposalStatus.expired => 'Expirada',
        ProposalStatus.executed => 'Ejecutada',
        ProposalStatus.failed => 'Falló',
        ProposalStatus.unknown => 'Desconocido',
      };
}

/// Nivel de riesgo de la propuesta. Determina urgencia y color UI.
enum ProposalRisk {
  low,
  medium,
  high,
  critical,
  unknown;

  static ProposalRisk fromString(String s) {
    return switch (s.toLowerCase()) {
      'low' => ProposalRisk.low,
      'medium' => ProposalRisk.medium,
      'high' => ProposalRisk.high,
      'critical' => ProposalRisk.critical,
      _ => ProposalRisk.unknown,
    };
  }

  String get label => switch (this) {
        ProposalRisk.low => 'Bajo',
        ProposalRisk.medium => 'Medio',
        ProposalRisk.high => 'Alto',
        ProposalRisk.critical => 'Crítico',
        ProposalRisk.unknown => '—',
      };
}

@immutable
class EmbrionProposal {
  final String id;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String proposedBy;
  final int? cycleId;
  final String? latidoId;
  final String proposalType;
  final String summary;
  final Map<String, dynamic> payload;
  final ProposalRisk riskLevel;
  final ProposalStatus status;
  final String? approvedBy;
  final DateTime? approvedAt;
  final String? rejectionReason;
  final DateTime? expiresAt;
  final DateTime? executedAt;
  final String? executor;
  final Map<String, dynamic>? result;

  const EmbrionProposal({
    required this.id,
    required this.createdAt,
    required this.updatedAt,
    required this.proposedBy,
    required this.cycleId,
    required this.latidoId,
    required this.proposalType,
    required this.summary,
    required this.payload,
    required this.riskLevel,
    required this.status,
    required this.approvedBy,
    required this.approvedAt,
    required this.rejectionReason,
    required this.expiresAt,
    required this.executedAt,
    required this.executor,
    required this.result,
  });

  factory EmbrionProposal.fromJson(Map<String, dynamic> json) {
    DateTime? parseDt(dynamic v) {
      if (v == null) return null;
      try {
        return DateTime.parse(v as String);
      } catch (_) {
        return null;
      }
    }

    return EmbrionProposal(
      id: json['id'] as String,
      createdAt: parseDt(json['created_at']) ?? DateTime.now(),
      updatedAt: parseDt(json['updated_at']) ?? DateTime.now(),
      proposedBy: json['proposed_by'] as String? ?? 'unknown',
      cycleId: json['cycle_id'] as int?,
      latidoId: json['latido_id'] as String?,
      proposalType: json['proposal_type'] as String? ?? 'other',
      summary: json['summary'] as String? ?? '(sin resumen)',
      payload: (json['payload_json'] as Map?)?.cast<String, dynamic>() ??
          const <String, dynamic>{},
      riskLevel: ProposalRisk.fromString(
          json['risk_level'] as String? ?? 'medium'),
      status: ProposalStatus.fromString(
          json['approval_status'] as String? ?? 'pending'),
      approvedBy: json['approved_by'] as String?,
      approvedAt: parseDt(json['approved_at']),
      rejectionReason: json['rejection_reason'] as String?,
      expiresAt: parseDt(json['expires_at']),
      executedAt: parseDt(json['executed_at']),
      executor: json['executor'] as String?,
      result: (json['result_json'] as Map?)?.cast<String, dynamic>(),
    );
  }
}

// ═══════════════════════════════════════════════════════════════
// EmbrionEstado — estado del loop
// ═══════════════════════════════════════════════════════════════

@immutable
class EmbrionEstado {
  final bool running;
  final int cycleCount;
  final int thoughtsToday;
  final double costTodayUsd;
  final double dailyBudgetUsd;
  final DateTime? lastThoughtAt;
  final List<String> recentErrors;

  const EmbrionEstado({
    required this.running,
    required this.cycleCount,
    required this.thoughtsToday,
    required this.costTodayUsd,
    required this.dailyBudgetUsd,
    required this.lastThoughtAt,
    required this.recentErrors,
  });

  factory EmbrionEstado.fromJson(Map<String, dynamic> json) {
    DateTime? parseDt(dynamic v) {
      if (v == null) return null;
      try {
        return DateTime.parse(v as String);
      } catch (_) {
        return null;
      }
    }

    final errors = (json['errors'] as List?)
            ?.map((e) =>
                (e as Map<String, dynamic>)['error']?.toString() ?? '')
            .where((s) => s.isNotEmpty)
            .toList() ??
        const <String>[];

    return EmbrionEstado(
      running: json['running'] as bool? ?? false,
      cycleCount: json['cycle_count'] as int? ?? 0,
      thoughtsToday: json['thoughts_today'] as int? ?? 0,
      costTodayUsd: (json['cost_today_usd'] as num?)?.toDouble() ?? 0.0,
      dailyBudgetUsd: (json['daily_budget_usd'] as num?)?.toDouble() ?? 0.0,
      lastThoughtAt: parseDt(json['last_thought_at']),
      recentErrors: errors,
    );
  }
}

// ═══════════════════════════════════════════════════════════════
// AguiEvent — evento del stream SSE (Hilo de Manus)
// ═══════════════════════════════════════════════════════════════

/// Tipos de eventos AG-UI (espejo de kernel/agui_adapter.py:AGUIEventType).
enum AguiEventType {
  runStarted,
  thinkingState,
  step,
  textMessageStart,
  textMessageContent,
  textMessageEnd,
  toolCallStart,
  toolCallArgs,
  toolCallEnd,
  runFinished,
  runError,
  heartbeat,
  unknown;

  static AguiEventType fromString(String s) {
    return switch (s) {
      'RUN_STARTED' => AguiEventType.runStarted,
      'THINKING_STATE' => AguiEventType.thinkingState,
      'STEP' => AguiEventType.step,
      'TEXT_MESSAGE_START' => AguiEventType.textMessageStart,
      'TEXT_MESSAGE_CONTENT' => AguiEventType.textMessageContent,
      'TEXT_MESSAGE_END' => AguiEventType.textMessageEnd,
      'TOOL_CALL_START' => AguiEventType.toolCallStart,
      'TOOL_CALL_ARGS' => AguiEventType.toolCallArgs,
      'TOOL_CALL_END' => AguiEventType.toolCallEnd,
      'RUN_FINISHED' => AguiEventType.runFinished,
      'RUN_ERROR' => AguiEventType.runError,
      'HEARTBEAT' => AguiEventType.heartbeat,
      _ => AguiEventType.unknown,
    };
  }
}

@immutable
class AguiEvent {
  final AguiEventType type;
  final Map<String, dynamic> raw;

  const AguiEvent({required this.type, required this.raw});

  factory AguiEvent.fromJson(Map<String, dynamic> json) {
    return AguiEvent(
      type: AguiEventType.fromString(json['type'] as String? ?? ''),
      raw: json,
    );
  }

  String? get textDelta => raw['delta'] as String? ?? raw['content'] as String?;
  String? get toolName => raw['tool_name'] as String? ?? raw['name'] as String?;
  String? get errorMessage => raw['error'] as String?;
  String? get stepLabel => raw['label'] as String? ?? raw['name'] as String?;
}

// ═══════════════════════════════════════════════════════════════
// Mission — hilo complejo persistente
// ═══════════════════════════════════════════════════════════════

@immutable
class Mission {
  final String id;
  final String name;
  final String description;
  final String status;
  final int priority;
  final List<String> tags;
  final DateTime? createdAt;
  final DateTime? updatedAt;

  const Mission({
    required this.id,
    required this.name,
    required this.description,
    required this.status,
    required this.priority,
    required this.tags,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Mission.fromJson(Map<String, dynamic> json) {
    DateTime? parseDt(dynamic v) {
      if (v == null) return null;
      try {
        return DateTime.parse(v as String);
      } catch (_) {
        return null;
      }
    }

    return Mission(
      id: json['id']?.toString() ?? '',
      name: json['name'] as String? ?? '(sin nombre)',
      description: json['description'] as String? ?? '',
      status: json['status'] as String? ?? 'open',
      priority: (json['priority'] as num?)?.toInt() ?? 5,
      tags: ((json['tags'] as List?) ?? const [])
          .map((e) => e.toString())
          .toList(),
      createdAt: parseDt(json['created_at']),
      updatedAt: parseDt(json['updated_at']),
    );
  }
}
