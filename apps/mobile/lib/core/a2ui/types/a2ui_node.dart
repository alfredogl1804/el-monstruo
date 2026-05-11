/// A2UI v1.0 types — modelos tipados que el parser produce y el renderer consume.
///
/// Whitelist canon firmado en `bridge/a2ui_spec_draft_FIRMADO_2026_05_11.md`:
/// Contenedores: Stack, Card, Section
/// Contenido: Text, Markdown, Image, Link, Code, Divider
/// Acción: Button, ButtonGroup
/// Datos: KeyValueList, Table, Badge
/// Progreso: Progress, Stepper
/// Especializados Monstruo: EmpresaResultCard, LeadCard, ContenidoCard
///
/// Disciplina anti-injection: cualquier `type` fuera del whitelist → fallback Markdown.
/// Disciplina anti-Turing: cero loops/condicionales runtime — el árbol es estático.
library;

import 'package:flutter/foundation.dart';

/// Versión A2UI soportada por este renderer.
const String kA2UISupportedVersion = '1.0';

/// Whitelist canónico (cerrado, append-only via firma Cowork).
const Set<String> kA2UIWhitelist = {
  // Contenedores
  'Stack', 'Card', 'Section',
  // Contenido
  'Text', 'Markdown', 'Image', 'Link', 'Code', 'Divider',
  // Acción
  'Button', 'ButtonGroup',
  // Datos
  'KeyValueList', 'Table', 'Badge',
  // Progreso
  'Progress', 'Stepper',
  // Especializados Monstruo
  'EmpresaResultCard', 'LeadCard', 'ContenidoCard',
};

/// Nodo A2UI parseado.
///
/// Inmutable. `children` puede estar vacío para nodos hoja (Text, Divider...).
/// `props` contiene los attrs del tipo. `slots` permite zonas semánticas
/// (e.g. Card.header / Card.footer).
@immutable
class A2UINode {
  /// Tipo whitelist canon. Si el JSON original tenía un tipo no-whitelist,
  /// el parser lo reemplazó con `_Fallback` y dejó el original en
  /// `props['__originalType']`.
  final String type;
  final Map<String, dynamic> props;
  final List<A2UINode> children;

  /// Slots semánticos: `slots['header']` = lista de hijos del slot.
  /// Vacío para componentes que no soportan slots.
  final Map<String, List<A2UINode>> slots;

  /// `action_id` opcional cuando el nodo es accionable (Button, Link).
  /// El renderer lo envía por WebSocket al kernel al activarse.
  final String? actionId;

  /// Payload opcional asociado al `actionId`.
  final Map<String, dynamic>? actionPayload;

  const A2UINode({
    required this.type,
    this.props = const {},
    this.children = const [],
    this.slots = const {},
    this.actionId,
    this.actionPayload,
  });

  /// Indica si el tipo está dentro del whitelist v1.0.
  bool get isWhitelisted => kA2UIWhitelist.contains(type);

  /// Tipo original cuando fue convertido a fallback.
  String? get originalType => props['__originalType'] as String?;

  /// Helper de lectura tipada con default.
  T? prop<T>(String key) {
    final value = props[key];
    if (value is T) return value;
    return null;
  }

  /// Helper para listas tipadas en props (e.g. KeyValueList.items).
  List<Map<String, dynamic>> propList(String key) {
    final value = props[key];
    if (value is List) {
      return value
          .whereType<Map>()
          .map((m) => Map<String, dynamic>.from(m))
          .toList();
    }
    return const [];
  }

  @override
  String toString() =>
      'A2UINode(type=$type, props=${props.keys.toList()}, '
      'children=${children.length}, slots=${slots.keys.toList()})';
}

/// Resultado del parser A2UI.
///
/// `root` es null si el parser no pudo recuperar nada utilizable
/// (fallback final = renderizar markdown del mensaje original).
@immutable
class A2UIParseResult {
  /// Nodo raíz parseado. Null si el parse falló completamente.
  final A2UINode? root;

  /// Lista de warnings no-bloqueantes (tipos fallback aplicados, props ignoradas).
  final List<A2UIWarning> warnings;

  /// True cuando hubo al menos 1 fallback aplicado.
  bool get hasFallback => warnings.any((w) => w.level == A2UIWarningLevel.fallback);

  /// True cuando no hubo ninguna warning y el árbol es 100% whitelist.
  bool get isClean => warnings.isEmpty && root != null;

  const A2UIParseResult({this.root, this.warnings = const []});

  /// Constructor cuando todo el JSON es inválido y no hay nada que renderizar.
  factory A2UIParseResult.failed(String reason) => A2UIParseResult(
        root: null,
        warnings: [
          A2UIWarning(
            level: A2UIWarningLevel.fatal,
            message: reason,
            path: r'$',
          ),
        ],
      );
}

/// Severidad de warning del parser.
enum A2UIWarningLevel {
  /// Tipo fuera del whitelist → reemplazado por fallback Markdown.
  fallback,

  /// Prop inválida ignorada (e.g. color hex malformado).
  ignored,

  /// JSON irrecuperable (no hay árbol).
  fatal,
}

@immutable
class A2UIWarning {
  final A2UIWarningLevel level;
  final String message;

  /// JSON-path estilo `$.children[2].props.color` donde ocurrió.
  final String path;

  const A2UIWarning({
    required this.level,
    required this.message,
    required this.path,
  });

  @override
  String toString() => '[$level] $path: $message';
}
