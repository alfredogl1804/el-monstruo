/// A2UI data widgets — KeyValueList, Table, Badge.
library;

import 'package:flutter/material.dart';

import '../brand_tokens.dart';
import '../types/a2ui_node.dart';

/// Lista clave-valor para fichas y propiedades. Acepta `items: [{key,value}]`.
class A2UIKeyValueList extends StatelessWidget {
  const A2UIKeyValueList({super.key, required this.node});
  final A2UINode node;

  @override
  Widget build(BuildContext context) {
    final items = node.propList('items');
    if (items.isEmpty) {
      return Text('—', style: A2UIBrand.caption);
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        for (var i = 0; i < items.length; i++) ...[
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SizedBox(
                width: 110,
                child: Text(
                  items[i]['key']?.toString() ?? '',
                  style: A2UIBrand.caption,
                ),
              ),
              const SizedBox(width: A2UIBrand.s8),
              Expanded(
                child: Text(
                  items[i]['value']?.toString() ?? '',
                  style: A2UIBrand.body,
                ),
              ),
            ],
          ),
          if (i < items.length - 1)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: A2UIBrand.s8),
              child: Divider(color: A2UIBrand.border, height: 1),
            ),
        ],
      ],
    );
  }
}

/// Tabla simple. Props: `headers: [String]`, `rows: [[String]]`.
class A2UITable extends StatelessWidget {
  const A2UITable({super.key, required this.node});
  final A2UINode node;

  @override
  Widget build(BuildContext context) {
    final headers = (node.prop<List>('headers') ?? const [])
        .map((e) => e.toString())
        .toList();
    final rows = (node.prop<List>('rows') ?? const [])
        .whereType<List>()
        .map((r) => r.map((e) => e?.toString() ?? '').toList())
        .toList();

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        headingRowColor: WidgetStatePropertyAll(A2UIBrand.graphiteSurfaceHigh),
        dataRowColor: WidgetStatePropertyAll(A2UIBrand.graphiteSurface),
        dividerThickness: 0.5,
        columns: [
          for (final h in headers)
            DataColumn(label: Text(h, style: A2UIBrand.caption)),
        ],
        rows: [
          for (final row in rows)
            DataRow(cells: [
              for (final cell in row)
                DataCell(Text(cell, style: A2UIBrand.body)),
            ]),
        ],
      ),
    );
  }
}

/// Badge con variantes semánticas `info | success | warning | danger | neutral`.
class A2UIBadge extends StatelessWidget {
  const A2UIBadge({super.key, required this.node});
  final A2UINode node;

  @override
  Widget build(BuildContext context) {
    final label = node.prop<String>('label') ?? '';
    final variant = node.prop<String>('variant') ?? 'neutral';
    final color = switch (variant) {
      'success' => A2UIBrand.success,
      'warning' => A2UIBrand.warning,
      'danger' => A2UIBrand.danger,
      'info' => A2UIBrand.info,
      _ => A2UIBrand.acero,
    };
    return Container(
      padding:
          const EdgeInsets.symmetric(horizontal: A2UIBrand.s8, vertical: A2UIBrand.s2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(A2UIBrand.rSm),
        border: Border.all(color: color.withValues(alpha: 0.5)),
      ),
      child: Text(
        label,
        style: A2UIBrand.caption.copyWith(color: color, fontWeight: FontWeight.w600),
      ),
    );
  }
}
