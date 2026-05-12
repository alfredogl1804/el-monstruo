/// A2UI Renderer — dispatcher entre `A2UINode` y los widgets Flutter.
///
/// Contrato:
///   * Recibe un `A2UINode` raíz parseado.
///   * Devuelve un Widget Flutter listo para incrustar.
///   * Acciones (Button tap, Link tap, Stepper step) viajan vía `dispatcher`.
///
/// Anti-Turing: cero loops/condicionales runtime ejecutados desde JSON.
/// Anti-injection: cualquier tipo no whitelist ya fue substituido por
/// `Markdown` por el parser; aquí solo confiamos en `node.type`.
library;

import 'package:flutter/material.dart';

import 'brand_tokens.dart';
import 'types/a2ui_action.dart';
import 'types/a2ui_node.dart';
import 'widgets/actions.dart';
import 'widgets/containers.dart';
import 'widgets/content.dart';
import 'widgets/data.dart';
import 'widgets/progress.dart';
import 'widgets/specialized.dart';

/// Renderer A2UI v1.0.
class A2UIRenderer extends StatelessWidget {
  const A2UIRenderer({
    super.key,
    required this.root,
    this.dispatcher,
    this.onLinkTap,
  });

  /// Nodo raíz devuelto por `A2UIParser.parse(...)`.
  final A2UINode root;

  /// Callback global cuando un widget dispara un action (Button, Link,
  /// ContenidoCard tap, etc).
  final A2UIActionDispatcher? dispatcher;

  /// Callback adicional para taps en links de Markdown.
  final void Function(String url)? onLinkTap;

  @override
  Widget build(BuildContext context) => _buildNode(root);

  Widget _buildNode(A2UINode node) {
    switch (node.type) {
      // Contenedores
      case 'Stack':
        return A2UIStack(node: node, buildChild: _buildNode);
      case 'Card':
        return A2UICard(node: node, buildChild: _buildNode);
      case 'Section':
        return A2UISection(node: node, buildChild: _buildNode);

      // Contenido
      case 'Text':
        return A2UIText(node: node);
      case 'Markdown':
        return A2UIMarkdown(node: node, onLinkTap: onLinkTap);
      case 'Image':
        return A2UIImage(node: node);
      case 'Link':
        return A2UILink(node: node, dispatcher: dispatcher);
      case 'Code':
        return A2UICode(node: node);
      case 'Divider':
        return A2UIDivider(node: node);

      // Acción
      case 'Button':
        return A2UIButton(node: node, dispatcher: dispatcher);
      case 'ButtonGroup':
        return A2UIButtonGroup(node: node, dispatcher: dispatcher);

      // Datos
      case 'KeyValueList':
        return A2UIKeyValueList(node: node);
      case 'Table':
        return A2UITable(node: node);
      case 'Badge':
        return A2UIBadge(node: node);

      // Progreso
      case 'Progress':
        return A2UIProgress(node: node);
      case 'Stepper':
        return A2UIStepper(node: node);

      // Especializados Monstruo
      case 'EmpresaResultCard':
        return A2UIEmpresaResultCard(node: node, dispatcher: dispatcher);
      case 'LeadCard':
        return A2UILeadCard(node: node, dispatcher: dispatcher);
      case 'ContenidoCard':
        return A2UIContenidoCard(node: node, dispatcher: dispatcher);

      // Safety net: nunca debería caer acá (parser ya filtra al whitelist),
      // pero si el árbol fue manipulado in-memory tras el parser, renderizamos
      // un texto plano explicativo sin crashear.
      default:
        return _UnknownTypePlaceholder(type: node.type);
    }
  }
}

class _UnknownTypePlaceholder extends StatelessWidget {
  const _UnknownTypePlaceholder({required this.type});
  final String type;
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(A2UIBrand.s8),
      decoration: BoxDecoration(
        color: A2UIBrand.graphite,
        borderRadius: BorderRadius.circular(A2UIBrand.rSm),
        border: Border.all(color: A2UIBrand.danger.withValues(alpha: 0.4)),
      ),
      child: Text(
        'Tipo A2UI no manejado: $type',
        style: A2UIBrand.caption.copyWith(color: A2UIBrand.danger),
      ),
    );
  }
}
