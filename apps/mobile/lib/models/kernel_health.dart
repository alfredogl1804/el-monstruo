class KernelHealth {
  KernelHealth({
    required this.status,
    required this.version,
    required this.components,
    required this.models,
    this.embrionStatus,
    this.embrionCycles,
    this.embrionCost,
    this.uptime,
  });

  final String status;
  final String version;
  final List<KernelComponent> components;
  final List<String> models;
  final String? embrionStatus;
  final int? embrionCycles;
  final double? embrionCost;
  final String? uptime;

  bool get isHealthy => status == 'healthy';
  bool get isEmbrionActive => embrionStatus == 'running';

  factory KernelHealth.fromJson(Map<String, dynamic> json) {
    final componentsList = (json['components'] as Map<String, dynamic>?)
        ?.entries
        .map((e) => KernelComponent(
              name: e.key,
              status: (e.value as Map<String, dynamic>)['status'] as String? ?? 'unknown',
              details: e.value as Map<String, dynamic>,
            ))
        .toList() ?? [];

    final modelsList = (json['models'] as Map<String, dynamic>?)
        ?.keys
        .toList() ?? [];

    return KernelHealth(
      status: json['status'] as String? ?? 'unknown',
      version: json['version'] as String? ?? 'unknown',
      components: componentsList,
      models: modelsList,
      embrionStatus: json['embrion']?['status'] as String?,
      embrionCycles: json['embrion']?['cycles_today'] as int?,
      embrionCost: (json['embrion']?['cost_today'] as num?)?.toDouble(),
      uptime: json['uptime'] as String?,
    );
  }

  factory KernelHealth.offline() {
    return KernelHealth(
      status: 'offline',
      version: 'unknown',
      components: [],
      models: [],
    );
  }
}

class KernelComponent {
  KernelComponent({
    required this.name,
    required this.status,
    this.details,
  });

  final String name;
  final String status;
  final Map<String, dynamic>? details;

  bool get isActive => status == 'active' || status == 'running';
}
