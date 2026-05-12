/// A2UI containers — Stack (Column), Card (con header/footer slots), Section.
library;

import 'package:flutter/material.dart';

import '../brand_tokens.dart';
import '../types/a2ui_node.dart';

typedef ChildBuilder = Widget Function(A2UINode node);

/// Stack vertical (Column). Spacing canon `s12`.
class A2UIStack extends StatelessWidget {
  const A2UIStack({super.key, required this.node, required this.buildChild});

  final A2UINode node;
  final ChildBuilder buildChild;

  @override
  Widget build(BuildContext context) {
    final spacing = (node.prop<num>('spacing') ?? A2UIBrand.s12).toDouble();
    final children = <Widget>[];
    for (var i = 0; i < node.children.length; i++) {
      if (i > 0) children.add(SizedBox(height: spacing));
      children.add(buildChild(node.children[i]));
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: children,
    );
  }
}

/// Card con borde acero, fondo graphiteSurface, esquinas rLg. Soporta slots
/// `header` y `footer`.
class A2UICard extends StatelessWidget {
  const A2UICard({super.key, required this.node, required this.buildChild});

  final A2UINode node;
  final ChildBuilder buildChild;

  @override
  Widget build(BuildContext context) {
    final header = node.slots['header'] ?? const [];
    final footer = node.slots['footer'] ?? const [];

    return Container(
      decoration: BoxDecoration(
        color: A2UIBrand.graphiteSurface,
        borderRadius: BorderRadius.circular(A2UIBrand.rLg),
        border: Border.all(color: A2UIBrand.border),
      ),
      padding: const EdgeInsets.all(A2UIBrand.s16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          if (header.isNotEmpty) ...[
            for (final n in header) buildChild(n),
            const Padding(
              padding: EdgeInsets.symmetric(vertical: A2UIBrand.s12),
              child: Divider(color: A2UIBrand.border, height: 1),
            ),
          ],
          for (final c in node.children) buildChild(c),
          if (footer.isNotEmpty) ...[
            const Padding(
              padding: EdgeInsets.symmetric(vertical: A2UIBrand.s12),
              child: Divider(color: A2UIBrand.border, height: 1),
            ),
            for (final n in footer) buildChild(n),
          ],
        ],
      ),
    );
  }
}

/// Section con título opcional `title` y subtítulo `subtitle`.
class A2UISection extends StatelessWidget {
  const A2UISection({super.key, required this.node, required this.buildChild});

  final A2UINode node;
  final ChildBuilder buildChild;

  @override
  Widget build(BuildContext context) {
    final title = node.prop<String>('title');
    final subtitle = node.prop<String>('subtitle');
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (title != null) Text(title, style: A2UIBrand.titleMd),
        if (subtitle != null)
          Padding(
            padding: const EdgeInsets.only(top: A2UIBrand.s4),
            child: Text(subtitle, style: A2UIBrand.caption),
          ),
        if (title != null || subtitle != null)
          const SizedBox(height: A2UIBrand.s12),
        for (final c in node.children) buildChild(c),
      ],
    );
  }
}
