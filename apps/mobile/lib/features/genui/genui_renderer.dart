import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

import '../../theme/monstruo_theme.dart';

/// Renders A2UI (Generative UI) components sent by the kernel.
///
/// The kernel sends a JSON payload describing a UI component,
/// and this renderer materializes it into Flutter widgets.
///
/// Supported component types:
/// - chart (bar, line, pie)
/// - table
/// - card
/// - progress
/// - metric
/// - form
/// - image
/// - code_block
/// - action_buttons
class GenUIRenderer extends StatelessWidget {
  const GenUIRenderer({
    super.key,
    required this.payload,
    this.onAction,
  });

  final Map<String, dynamic> payload;
  final void Function(String action, Map<String, dynamic> data)? onAction;

  @override
  Widget build(BuildContext context) {
    final componentType = payload['type'] as String? ?? 'unknown';

    return switch (componentType) {
      'chart' => _ChartComponent(data: payload),
      'table' => _TableComponent(data: payload),
      'card' => _CardComponent(data: payload),
      'progress' => _ProgressComponent(data: payload),
      'metric' => _MetricComponent(data: payload),
      'metric_grid' => _MetricGridComponent(data: payload),
      'form' => _FormComponent(data: payload, onAction: onAction),
      'code_block' => _CodeBlockComponent(data: payload),
      'action_buttons' => _ActionButtonsComponent(data: payload, onAction: onAction),
      'status_card' => _StatusCardComponent(data: payload),
      _ => _UnknownComponent(type: componentType, data: payload),
    };
  }
}

// ─── Chart Component ───
class _ChartComponent extends StatelessWidget {
  const _ChartComponent({required this.data});
  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    final chartType = data['chart_type'] as String? ?? 'bar';
    final title = data['title'] as String? ?? '';
    final items = List<Map<String, dynamic>>.from(data['items'] ?? []);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: MonstruoTheme.surface,
        borderRadius: BorderRadius.circular(MonstruoTheme.radiusMd),
        border: Border.all(color: MonstruoTheme.divider, width: 0.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (title.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Text(
                title,
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  color: MonstruoTheme.onBackground,
                ),
              ),
            ),
          SizedBox(
            height: 200,
            child: switch (chartType) {
              'bar' => _buildBarChart(items),
              'line' => _buildLineChart(items),
              'pie' => _buildPieChart(items),
              _ => _buildBarChart(items),
            },
          ),
          if (data['source'] != null)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text(
                'Fuente: ${data['source']}',
                style: const TextStyle(
                  fontSize: 10,
                  color: MonstruoTheme.onSurfaceDim,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildBarChart(List<Map<String, dynamic>> items) {
    final colors = [
      MonstruoTheme.primary,
      MonstruoTheme.secondary,
      MonstruoTheme.tertiary,
      MonstruoTheme.success,
      MonstruoTheme.warning,
    ];

    return BarChart(
      BarChartData(
        barGroups: items.asMap().entries.map((entry) {
          final value = (entry.value['value'] as num?)?.toDouble() ?? 0;
          return BarChartGroupData(
            x: entry.key,
            barRods: [
              BarChartRodData(
                toY: value,
                color: colors[entry.key % colors.length],
                width: 20,
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(4),
                ),
              ),
            ],
          );
        }).toList(),
        borderData: FlBorderData(show: false),
        gridData: const FlGridData(show: false),
        titlesData: FlTitlesData(
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                final idx = value.toInt();
                if (idx >= 0 && idx < items.length) {
                  return Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text(
                      items[idx]['label'] as String? ?? '',
                      style: const TextStyle(
                        fontSize: 10,
                        color: MonstruoTheme.onSurfaceDim,
                      ),
                    ),
                  );
                }
                return const SizedBox.shrink();
              },
            ),
          ),
          leftTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          topTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          rightTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
        ),
      ),
    );
  }

  Widget _buildLineChart(List<Map<String, dynamic>> items) {
    final spots = items.asMap().entries.map((entry) {
      final value = (entry.value['value'] as num?)?.toDouble() ?? 0;
      return FlSpot(entry.key.toDouble(), value);
    }).toList();

    return LineChart(
      LineChartData(
        lineBarsData: [
          LineChartBarData(
            spots: spots,
            isCurved: true,
            color: MonstruoTheme.primary,
            barWidth: 2,
            dotData: const FlDotData(show: true),
            belowBarData: BarAreaData(
              show: true,
              color: MonstruoTheme.primary.withValues(alpha: 0.1),
            ),
          ),
        ],
        borderData: FlBorderData(show: false),
        gridData: const FlGridData(show: false),
        titlesData: const FlTitlesData(show: false),
      ),
    );
  }

  Widget _buildPieChart(List<Map<String, dynamic>> items) {
    final colors = [
      MonstruoTheme.primary,
      MonstruoTheme.secondary,
      MonstruoTheme.tertiary,
      MonstruoTheme.success,
      MonstruoTheme.warning,
      MonstruoTheme.error,
    ];

    return PieChart(
      PieChartData(
        sections: items.asMap().entries.map((entry) {
          final value = (entry.value['value'] as num?)?.toDouble() ?? 0;
          final label = entry.value['label'] as String? ?? '';
          return PieChartSectionData(
            value: value,
            title: label,
            color: colors[entry.key % colors.length],
            radius: 80,
            titleStyle: const TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w600,
              color: Colors.white,
            ),
          );
        }).toList(),
        centerSpaceRadius: 30,
      ),
    );
  }
}

// ─── Table Component ───
class _TableComponent extends StatelessWidget {
  const _TableComponent({required this.data});
  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    final title = data['title'] as String? ?? '';
    final headers = List<String>.from(data['headers'] ?? []);
    final rows = List<List<dynamic>>.from(
      (data['rows'] as List?)?.map((r) => List<dynamic>.from(r as List)) ?? [],
    );

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: MonstruoTheme.surface,
        borderRadius: BorderRadius.circular(MonstruoTheme.radiusMd),
        border: Border.all(color: MonstruoTheme.divider, width: 0.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (title.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Text(
                title,
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  color: MonstruoTheme.onBackground,
                ),
              ),
            ),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: DataTable(
              headingRowColor: WidgetStateProperty.all(
                MonstruoTheme.surfaceVariant,
              ),
              columns: headers
                  .map((h) => DataColumn(
                        label: Text(
                          h,
                          style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 12,
                            color: MonstruoTheme.onBackground,
                          ),
                        ),
                      ))
                  .toList(),
              rows: rows
                  .map((row) => DataRow(
                        cells: row
                            .map((cell) => DataCell(
                                  Text(
                                    cell.toString(),
                                    style: const TextStyle(
                                      fontSize: 12,
                                      color: MonstruoTheme.onSurface,
                                    ),
                                  ),
                                ))
                            .toList(),
                      ))
                  .toList(),
            ),
          ),
        ],
      ),
    );
  }
}

// ─── Card Component ───
class _CardComponent extends StatelessWidget {
  const _CardComponent({required this.data});
  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    final title = data['title'] as String? ?? '';
    final subtitle = data['subtitle'] as String? ?? '';
    final body = data['body'] as String? ?? '';
    final iconName = data['icon'] as String?;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: MonstruoTheme.surface,
        borderRadius: BorderRadius.circular(MonstruoTheme.radiusMd),
        border: Border.all(color: MonstruoTheme.divider, width: 0.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              if (iconName != null) ...[
                Icon(Icons.auto_awesome, size: 20, color: MonstruoTheme.primary),
                const SizedBox(width: 8),
              ],
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: MonstruoTheme.onBackground,
                  ),
                ),
              ),
            ],
          ),
          if (subtitle.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Text(
                subtitle,
                style: const TextStyle(
                  fontSize: 13,
                  color: MonstruoTheme.onSurfaceDim,
                ),
              ),
            ),
          if (body.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text(
                body,
                style: const TextStyle(
                  fontSize: 14,
                  color: MonstruoTheme.onSurface,
                  height: 1.5,
                ),
              ),
            ),
        ],
      ),
    );
  }
}

// ─── Progress Component ───
class _ProgressComponent extends StatelessWidget {
  const _ProgressComponent({required this.data});
  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    final title = data['title'] as String? ?? '';
    final value = (data['value'] as num?)?.toDouble() ?? 0;
    final max = (data['max'] as num?)?.toDouble() ?? 100;
    final progress = (value / max).clamp(0.0, 1.0);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: MonstruoTheme.surface,
        borderRadius: BorderRadius.circular(MonstruoTheme.radiusMd),
        border: Border.all(color: MonstruoTheme.divider, width: 0.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                  color: MonstruoTheme.onBackground,
                ),
              ),
              Text(
                '${(progress * 100).toStringAsFixed(0)}%',
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: MonstruoTheme.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: progress,
              backgroundColor: MonstruoTheme.surfaceVariant,
              color: MonstruoTheme.primary,
              minHeight: 8,
            ),
          ),
        ],
      ),
    );
  }
}

// ─── Metric Component ───
class _MetricComponent extends StatelessWidget {
  const _MetricComponent({required this.data});
  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    final label = data['label'] as String? ?? '';
    final value = data['value']?.toString() ?? '—';
    final unit = data['unit'] as String? ?? '';
    final trend = data['trend'] as String?; // "up", "down", "neutral"

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: MonstruoTheme.surface,
        borderRadius: BorderRadius.circular(MonstruoTheme.radiusMd),
        border: Border.all(color: MonstruoTheme.divider, width: 0.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontSize: 12,
              color: MonstruoTheme.onSurfaceDim,
            ),
          ),
          const SizedBox(height: 4),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                value,
                style: const TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.w700,
                  color: MonstruoTheme.onBackground,
                ),
              ),
              if (unit.isNotEmpty) ...[
                const SizedBox(width: 4),
                Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Text(
                    unit,
                    style: const TextStyle(
                      fontSize: 14,
                      color: MonstruoTheme.onSurfaceDim,
                    ),
                  ),
                ),
              ],
              if (trend != null) ...[
                const SizedBox(width: 8),
                Icon(
                  trend == 'up'
                      ? Icons.trending_up
                      : trend == 'down'
                          ? Icons.trending_down
                          : Icons.trending_flat,
                  size: 20,
                  color: trend == 'up'
                      ? MonstruoTheme.success
                      : trend == 'down'
                          ? MonstruoTheme.error
                          : MonstruoTheme.onSurfaceDim,
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }
}

// ─── Metric Grid Component ───
class _MetricGridComponent extends StatelessWidget {
  const _MetricGridComponent({required this.data});
  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    final metrics = List<Map<String, dynamic>>.from(data['metrics'] ?? []);

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 8,
        mainAxisSpacing: 8,
        childAspectRatio: 1.8,
      ),
      itemCount: metrics.length,
      itemBuilder: (context, index) {
        return _MetricComponent(data: metrics[index]);
      },
    );
  }
}

// ─── Form Component ───
class _FormComponent extends StatelessWidget {
  const _FormComponent({required this.data, this.onAction});
  final Map<String, dynamic> data;
  final void Function(String action, Map<String, dynamic> data)? onAction;

  @override
  Widget build(BuildContext context) {
    final title = data['title'] as String? ?? '';
    final fields = List<Map<String, dynamic>>.from(data['fields'] ?? []);
    final submitLabel = data['submit_label'] as String? ?? 'Enviar';

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: MonstruoTheme.surface,
        borderRadius: BorderRadius.circular(MonstruoTheme.radiusMd),
        border: Border.all(color: MonstruoTheme.primary.withValues(alpha: 0.3), width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (title.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Text(
                title,
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  color: MonstruoTheme.onBackground,
                ),
              ),
            ),
          ...fields.map((field) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: TextField(
                  decoration: InputDecoration(
                    labelText: field['label'] as String? ?? '',
                    hintText: field['placeholder'] as String? ?? '',
                    labelStyle: const TextStyle(color: MonstruoTheme.onSurfaceDim),
                    hintStyle: TextStyle(
                      color: MonstruoTheme.onSurfaceDim.withValues(alpha: 0.5),
                    ),
                    filled: true,
                    fillColor: MonstruoTheme.surfaceVariant,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: BorderSide.none,
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(8),
                      borderSide: const BorderSide(color: MonstruoTheme.primary),
                    ),
                  ),
                  style: const TextStyle(color: MonstruoTheme.onBackground),
                ),
              )),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                onAction?.call('form_submit', data);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: MonstruoTheme.primary,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
              child: Text(submitLabel),
            ),
          ),
        ],
      ),
    );
  }
}

// ─── Code Block Component ───
class _CodeBlockComponent extends StatelessWidget {
  const _CodeBlockComponent({required this.data});
  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    final code = data['code'] as String? ?? '';
    final language = data['language'] as String? ?? '';
    final filename = data['filename'] as String? ?? '';

    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF0D0D0D),
        borderRadius: BorderRadius.circular(MonstruoTheme.radiusSm),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: const BoxDecoration(
              color: MonstruoTheme.surfaceVariant,
              borderRadius: BorderRadius.vertical(
                top: Radius.circular(MonstruoTheme.radiusSm),
              ),
            ),
            child: Row(
              children: [
                if (filename.isNotEmpty)
                  Text(
                    filename,
                    style: const TextStyle(
                      fontSize: 12,
                      color: MonstruoTheme.onSurfaceDim,
                    ),
                  ),
                const Spacer(),
                if (language.isNotEmpty)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: MonstruoTheme.primary.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      language,
                      style: const TextStyle(
                        fontSize: 10,
                        color: MonstruoTheme.primary,
                      ),
                    ),
                  ),
              ],
            ),
          ),
          // Code
          Padding(
            padding: const EdgeInsets.all(12),
            child: SelectableText(
              code,
              style: const TextStyle(
                fontFamily: 'monospace',
                fontSize: 12,
                color: MonstruoTheme.success,
                height: 1.5,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ─── Action Buttons Component ───
class _ActionButtonsComponent extends StatelessWidget {
  const _ActionButtonsComponent({required this.data, this.onAction});
  final Map<String, dynamic> data;
  final void Function(String action, Map<String, dynamic> data)? onAction;

  @override
  Widget build(BuildContext context) {
    final buttons = List<Map<String, dynamic>>.from(data['buttons'] ?? []);

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: buttons.map((btn) {
        final label = btn['label'] as String? ?? '';
        final action = btn['action'] as String? ?? '';
        final variant = btn['variant'] as String? ?? 'default';

        return ElevatedButton(
          onPressed: () => onAction?.call(action, btn),
          style: ElevatedButton.styleFrom(
            backgroundColor: variant == 'primary'
                ? MonstruoTheme.primary
                : variant == 'danger'
                    ? MonstruoTheme.error
                    : MonstruoTheme.surfaceVariant,
            foregroundColor: variant == 'primary' || variant == 'danger'
                ? Colors.white
                : MonstruoTheme.onSurface,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          ),
          child: Text(label, style: const TextStyle(fontSize: 13)),
        );
      }).toList(),
    );
  }
}

// ─── Status Card Component ───
class _StatusCardComponent extends StatelessWidget {
  const _StatusCardComponent({required this.data});
  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    final title = data['title'] as String? ?? '';
    final status = data['status'] as String? ?? 'unknown';
    final items = List<Map<String, dynamic>>.from(data['items'] ?? []);

    final isHealthy = status == 'healthy' || status == 'active' || status == 'running';

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: MonstruoTheme.surface,
        borderRadius: BorderRadius.circular(MonstruoTheme.radiusMd),
        border: Border.all(color: MonstruoTheme.divider, width: 0.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 10,
                height: 10,
                decoration: BoxDecoration(
                  color: isHealthy ? MonstruoTheme.success : MonstruoTheme.error,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 8),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  color: MonstruoTheme.onBackground,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: isHealthy
                      ? MonstruoTheme.success.withValues(alpha: 0.15)
                      : MonstruoTheme.error.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  status.toUpperCase(),
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.w600,
                    color: isHealthy ? MonstruoTheme.success : MonstruoTheme.error,
                  ),
                ),
              ),
            ],
          ),
          if (items.isNotEmpty) ...[
            const SizedBox(height: 12),
            ...items.map((item) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Row(
                    children: [
                      Container(
                        width: 6,
                        height: 6,
                        decoration: BoxDecoration(
                          color: (item['active'] == true)
                              ? MonstruoTheme.success
                              : MonstruoTheme.onSurfaceDim,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        item['name'] as String? ?? '',
                        style: const TextStyle(
                          fontSize: 12,
                          color: MonstruoTheme.onSurface,
                        ),
                      ),
                    ],
                  ),
                )),
          ],
        ],
      ),
    );
  }
}

// ─── Unknown Component ───
class _UnknownComponent extends StatelessWidget {
  const _UnknownComponent({required this.type, required this.data});
  final String type;
  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: MonstruoTheme.surfaceVariant,
        borderRadius: BorderRadius.circular(MonstruoTheme.radiusSm),
        border: Border.all(
          color: MonstruoTheme.warning.withValues(alpha: 0.3),
          width: 0.5,
        ),
      ),
      child: Row(
        children: [
          const Icon(Icons.warning_amber, size: 16, color: MonstruoTheme.warning),
          const SizedBox(width: 8),
          Text(
            'Componente no soportado: $type',
            style: const TextStyle(
              fontSize: 12,
              color: MonstruoTheme.warning,
            ),
          ),
        ],
      ),
    );
  }
}
