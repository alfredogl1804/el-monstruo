/// Cognitive Republic models — Mapped 1:1 from kernel /v1/factory/* responses.
///
/// Habilitante: DSC-G-019 (Adopción narrativa Cognitive Republic).
/// Sprint: SPR-FACTORY-AGGREGATORS-000.
///
/// Estos modelos son puros DTOs (sin lógica de negocio). La fuente única de
/// verdad es el kernel — la app solo deserializa y dibuja.
library;

// ============================================================================
// 1. ForgeNode — Nodo federado de la constelación
// ============================================================================

class ForgeNode {
  final String forgeId;
  final String name;
  final String tier; // core | inner | mid | outer
  final String kind;
  final bool isAggregate;
  final ForgeSubstrate substrate;
  final ForgeSovereignty sovereignty;
  final ForgeProduction production;
  final ForgeMemory memory;
  final String status; // ONLINE | STANDBY | DEGRADED | OFFLINE | UNKNOWN

  ForgeNode({
    required this.forgeId,
    required this.name,
    required this.tier,
    required this.kind,
    required this.isAggregate,
    required this.substrate,
    required this.sovereignty,
    required this.production,
    required this.memory,
    required this.status,
  });

  factory ForgeNode.fromJson(Map<String, dynamic> json) {
    return ForgeNode(
      forgeId: json['forge_id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      tier: json['tier'] as String? ?? 'unknown',
      kind: json['kind'] as String? ?? 'unknown',
      isAggregate: json['is_aggregate'] as bool? ?? false,
      substrate: ForgeSubstrate.fromJson(
        (json['substrate'] as Map<String, dynamic>?) ?? const {},
      ),
      sovereignty: ForgeSovereignty.fromJson(
        (json['sovereignty'] as Map<String, dynamic>?) ?? const {},
      ),
      production: ForgeProduction.fromJson(
        (json['production'] as Map<String, dynamic>?) ?? const {},
      ),
      memory: ForgeMemory.fromJson(
        (json['memory'] as Map<String, dynamic>?) ?? const {},
      ),
      status: json['status'] as String? ?? 'UNKNOWN',
    );
  }
}

class ForgeSubstrate {
  final String? runtime;
  final String? endpoint;
  final String? repo;

  ForgeSubstrate({this.runtime, this.endpoint, this.repo});

  factory ForgeSubstrate.fromJson(Map<String, dynamic> json) {
    return ForgeSubstrate(
      runtime: json['runtime'] as String?,
      endpoint: json['endpoint'] as String?,
      repo: json['repo'] as String?,
    );
  }
}

class ForgeSovereignty {
  final bool envelopeSupported;
  final String? signerKeyId;
  final bool courtBound;
  final List<String> t1RequiredLanes;

  ForgeSovereignty({
    required this.envelopeSupported,
    this.signerKeyId,
    required this.courtBound,
    required this.t1RequiredLanes,
  });

  factory ForgeSovereignty.fromJson(Map<String, dynamic> json) {
    return ForgeSovereignty(
      envelopeSupported: json['envelope_supported'] as bool? ?? false,
      signerKeyId: json['signer_key_id'] as String?,
      courtBound: json['court_bound'] as bool? ?? false,
      t1RequiredLanes: (json['t1_required_lanes'] as List?)
              ?.map((e) => e.toString())
              .toList() ??
          const [],
    );
  }
}

class ForgeProduction {
  final List<String> activeLines;
  final String? lastCycleAt;
  final int? artifacts24h;
  final int? evidenceReceipts24h;
  final int? failures24h;
  final double? cost24hUsd;

  ForgeProduction({
    required this.activeLines,
    this.lastCycleAt,
    this.artifacts24h,
    this.evidenceReceipts24h,
    this.failures24h,
    this.cost24hUsd,
  });

  factory ForgeProduction.fromJson(Map<String, dynamic> json) {
    return ForgeProduction(
      activeLines: (json['active_lines'] as List?)
              ?.map((e) => e.toString())
              .toList() ??
          const [],
      lastCycleAt: json['last_cycle_at'] as String?,
      artifacts24h: json['artifacts_24h'] as int?,
      evidenceReceipts24h: json['evidence_receipts_24h'] as int?,
      failures24h: json['failures_24h'] as int?,
      cost24hUsd: (json['cost_24h_usd'] as num?)?.toDouble(),
    );
  }
}

class ForgeMemory {
  final bool writesToMemory;
  final int? lessonsCanonized;
  final int? unresolvedGaps;

  ForgeMemory({
    required this.writesToMemory,
    this.lessonsCanonized,
    this.unresolvedGaps,
  });

  factory ForgeMemory.fromJson(Map<String, dynamic> json) {
    return ForgeMemory(
      writesToMemory: json['writes_to_memory'] as bool? ?? false,
      lessonsCanonized: json['lessons_canonized'] as int?,
      unresolvedGaps: json['unresolved_gaps'] as int?,
    );
  }
}

// ============================================================================
// 2. ForgeEdge — Conexión envelope mesh entre nodos
// ============================================================================

class ForgeEdge {
  final String fromForgeId;
  final String toForgeId;
  final String relation; // produces | consumes | governs | evidences | depends_on
  final String? signedAt;
  final String? envelopeKeyId;

  ForgeEdge({
    required this.fromForgeId,
    required this.toForgeId,
    required this.relation,
    this.signedAt,
    this.envelopeKeyId,
  });

  factory ForgeEdge.fromJson(Map<String, dynamic> json) {
    return ForgeEdge(
      fromForgeId: json['from'] as String? ?? '',
      toForgeId: json['to'] as String? ?? '',
      relation: json['relation'] as String? ?? 'unknown',
      signedAt: json['signed_at'] as String?,
      envelopeKeyId: json['envelope_key_id'] as String?,
    );
  }
}

// ============================================================================
// 3. ConstellationResponse — Wrapper completo del endpoint
// ============================================================================

class ConstellationResponse {
  final String version;
  final String generatedAt;
  final bool binario100;
  final String? sourceGenomeAt;
  final List<ForgeNode> nodes;
  final List<ForgeEdge> edges;
  final ConstellationTotals totals;

  ConstellationResponse({
    required this.version,
    required this.generatedAt,
    required this.binario100,
    this.sourceGenomeAt,
    required this.nodes,
    required this.edges,
    required this.totals,
  });

  factory ConstellationResponse.fromJson(Map<String, dynamic> json) {
    return ConstellationResponse(
      version: json['version'] as String? ?? '1.0',
      generatedAt: json['generated_at'] as String? ?? '',
      binario100: json['binario_100'] as bool? ?? false,
      sourceGenomeAt: json['source_genome_at'] as String?,
      nodes: (json['nodes'] as List?)
              ?.map((e) => ForgeNode.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      edges: (json['edges'] as List?)
              ?.map((e) => ForgeEdge.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      totals: ConstellationTotals.fromJson(
        (json['totals'] as Map<String, dynamic>?) ?? const {},
      ),
    );
  }
}

class ConstellationTotals {
  final int nodesTotal;
  final Map<String, int> tiers;

  ConstellationTotals({required this.nodesTotal, required this.tiers});

  factory ConstellationTotals.fromJson(Map<String, dynamic> json) {
    return ConstellationTotals(
      nodesTotal: json['nodes_total'] as int? ?? 0,
      tiers: (json['tiers'] as Map<String, dynamic>?)
              ?.map((k, v) => MapEntry(k, (v as num).toInt())) ??
          const {},
    );
  }
}

// ============================================================================
// 4. CognitiveEconomy — KPIs Cognitive P&L
// ============================================================================

class CognitiveEconomy {
  final String generatedAt;
  final String window; // 24h | lifetime
  final Map<String, dynamic> kpis;
  final List<String> missingMetrics;

  CognitiveEconomy({
    required this.generatedAt,
    required this.window,
    required this.kpis,
    required this.missingMetrics,
  });

  factory CognitiveEconomy.fromJson(Map<String, dynamic> json) {
    return CognitiveEconomy(
      generatedAt: json['generated_at'] as String? ?? '',
      window: json['window'] as String? ?? '24h',
      kpis: (json['kpis'] as Map<String, dynamic>?) ?? const {},
      missingMetrics: (json['data_quality']?['missing_metrics'] as List?)
              ?.map((e) => e.toString())
              .toList() ??
          const [],
    );
  }

  /// KPIs reales con datos (excluye nulls).
  Map<String, dynamic> realKpis() {
    return Map<String, dynamic>.fromEntries(
      kpis.entries.where((e) => e.value != null),
    );
  }
}

// ============================================================================
// 5. SovereignTimelineEvent — Eventos civilizacionales
// ============================================================================

class SovereignTimelineEvent {
  final String eventId;
  final String at;
  final String kind; // dsc_signed | sprint_completed | incident_p0 | doctrine_revision | embrion_milestone
  final String title;
  final String? summary;
  final String? authorOrTrigger;
  final List<String> evidenceUrls;
  final String? signedBy;

  SovereignTimelineEvent({
    required this.eventId,
    required this.at,
    required this.kind,
    required this.title,
    this.summary,
    this.authorOrTrigger,
    required this.evidenceUrls,
    this.signedBy,
  });

  factory SovereignTimelineEvent.fromJson(Map<String, dynamic> json) {
    return SovereignTimelineEvent(
      eventId: json['event_id'] as String? ?? '',
      at: json['at'] as String? ?? '',
      kind: json['kind'] as String? ?? 'unknown',
      title: json['title'] as String? ?? '',
      summary: json['summary'] as String?,
      authorOrTrigger: json['author_or_trigger'] as String?,
      evidenceUrls: (json['evidence_urls'] as List?)
              ?.map((e) => e.toString())
              .toList() ??
          const [],
      signedBy: json['signed_by'] as String?,
    );
  }
}

// ============================================================================
// 6. RealityDiff — Reality Diff declared vs live
// ============================================================================

class RealityDiff {
  final String generatedAt;
  final bool binario100;
  final int driftCount;
  final Map<String, bool> coverageMatch;
  final List<RealityDiscrepancy> discrepancies;
  final RealityKernelHealth? kernelHealth;

  RealityDiff({
    required this.generatedAt,
    required this.binario100,
    required this.driftCount,
    required this.coverageMatch,
    required this.discrepancies,
    this.kernelHealth,
  });

  factory RealityDiff.fromJson(Map<String, dynamic> json) {
    return RealityDiff(
      generatedAt: json['generated_at'] as String? ?? '',
      binario100: json['binario_100'] as bool? ?? false,
      driftCount: json['drift_count'] as int? ?? 0,
      coverageMatch: (json['coverage_match'] as Map<String, dynamic>?)
              ?.map((k, v) => MapEntry(k, v as bool? ?? false)) ??
          const {},
      discrepancies: (json['discrepancies'] as List?)
              ?.map((e) =>
                  RealityDiscrepancy.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      kernelHealth: json['kernel_health'] != null
          ? RealityKernelHealth.fromJson(
              json['kernel_health'] as Map<String, dynamic>)
          : null,
    );
  }
}

class RealityDiscrepancy {
  final String domain;
  final String declared;
  final String live;
  final String severity; // info | warn | error

  RealityDiscrepancy({
    required this.domain,
    required this.declared,
    required this.live,
    required this.severity,
  });

  factory RealityDiscrepancy.fromJson(Map<String, dynamic> json) {
    return RealityDiscrepancy(
      domain: json['domain'] as String? ?? '',
      declared: json['declared']?.toString() ?? '',
      live: json['live']?.toString() ?? '',
      severity: json['severity'] as String? ?? 'info',
    );
  }
}

class RealityKernelHealth {
  final String? status;
  final int? uptimeSeconds;
  final String? version;

  RealityKernelHealth({this.status, this.uptimeSeconds, this.version});

  factory RealityKernelHealth.fromJson(Map<String, dynamic> json) {
    return RealityKernelHealth(
      status: json['status'] as String?,
      uptimeSeconds: json['uptime_seconds'] as int?,
      version: json['version'] as String?,
    );
  }
}
