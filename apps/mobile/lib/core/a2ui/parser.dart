/// A2UI Parser v1.0.
///
/// Convierte payloads JSON (provenientes del kernel via WebSocket o HTTP)
/// en árboles `A2UINode` listos para render.
///
/// Reglas:
///  - Solo tipos del whitelist canon (`kA2UIWhitelist`) se mantienen.
///  - Tipos desconocidos → fallback Markdown con warning.
///  - JSON irrecuperable → `A2UIParseResult.failed`.
///  - Cero loops/condicionales runtime (anti-Turing) — el árbol es estático.
///  - Profundidad máxima 32 niveles para mitigar JSON adversarial.
library;

import 'dart:convert';

import 'types/a2ui_node.dart';

/// Profundidad máxima permitida en el árbol (anti DoS).
const int kA2UIMaxDepth = 32;

/// Tamaño máximo del JSON (anti DoS — 256 KB).
const int kA2UIMaxJsonBytes = 256 * 1024;

class A2UIParser {
  const A2UIParser();

  /// Parse desde un Map ya decodificado.
  A2UIParseResult parse(Map<String, dynamic> json) {
    final warnings = <A2UIWarning>[];
    final version = json['a2ui_version'];
    if (version is! String) {
      return A2UIParseResult.failed(
        'Missing or non-string a2ui_version (got ${version.runtimeType})',
      );
    }
    if (version != kA2UISupportedVersion) {
      warnings.add(
        A2UIWarning(
          level: A2UIWarningLevel.ignored,
          message:
              'Unsupported a2ui_version="$version", expected "$kA2UISupportedVersion"',
          path: r'$.a2ui_version',
        ),
      );
    }
    final rootJson = json['root'];
    if (rootJson is! Map) {
      return A2UIParseResult.failed(
        'Missing or non-object "root" (got ${rootJson.runtimeType})',
      );
    }
    final root = _parseNode(
      Map<String, dynamic>.from(rootJson),
      path: r'$.root',
      depth: 0,
      warnings: warnings,
    );
    return A2UIParseResult(root: root, warnings: warnings);
  }

  /// Parse desde un string JSON crudo. Aplica límite de tamaño.
  A2UIParseResult parseJson(String raw) {
    if (raw.length > kA2UIMaxJsonBytes) {
      return A2UIParseResult.failed(
        'Payload exceeds $kA2UIMaxJsonBytes bytes (got ${raw.length})',
      );
    }
    Object? decoded;
    try {
      decoded = jsonDecode(raw);
    } on FormatException catch (e) {
      return A2UIParseResult.failed('Invalid JSON: ${e.message}');
    }
    if (decoded is! Map) {
      return A2UIParseResult.failed(
        'Top-level JSON must be object (got ${decoded.runtimeType})',
      );
    }
    return parse(Map<String, dynamic>.from(decoded));
  }

  A2UINode _parseNode(
    Map<String, dynamic> node, {
    required String path,
    required int depth,
    required List<A2UIWarning> warnings,
  }) {
    if (depth > kA2UIMaxDepth) {
      warnings.add(
        A2UIWarning(
          level: A2UIWarningLevel.fallback,
          message: 'Max depth ($kA2UIMaxDepth) exceeded, truncated',
          path: path,
        ),
      );
      return const A2UINode(
        type: 'Text',
        props: {'content': '⚠️ Render aborted: tree too deep.'},
      );
    }

    final rawType = node['type'];
    if (rawType is! String) {
      warnings.add(
        A2UIWarning(
          level: A2UIWarningLevel.fallback,
          message: 'Missing or non-string "type" (got ${rawType.runtimeType})',
          path: path,
        ),
      );
      return const A2UINode(
        type: 'Text',
        props: {'content': '⚠️ Invalid node: missing type.'},
      );
    }

    var resolvedType = rawType;
    Map<String, dynamic> resolvedProps =
        node['props'] is Map ? Map<String, dynamic>.from(node['props'] as Map) : {};

    if (!kA2UIWhitelist.contains(rawType)) {
      warnings.add(
        A2UIWarning(
          level: A2UIWarningLevel.fallback,
          message: 'Type "$rawType" not in whitelist v$kA2UISupportedVersion',
          path: '$path.type',
        ),
      );
      resolvedProps = {
        ...resolvedProps,
        '__originalType': rawType,
        'content': _fallbackMarkdownFor(rawType, resolvedProps),
      };
      resolvedType = 'Markdown';
    }

    final children = <A2UINode>[];
    final rawChildren = node['children'];
    if (rawChildren is List) {
      for (var i = 0; i < rawChildren.length; i++) {
        final c = rawChildren[i];
        if (c is! Map) {
          warnings.add(
            A2UIWarning(
              level: A2UIWarningLevel.ignored,
              message: 'Non-object child ignored',
              path: '$path.children[$i]',
            ),
          );
          continue;
        }
        children.add(
          _parseNode(
            Map<String, dynamic>.from(c),
            path: '$path.children[$i]',
            depth: depth + 1,
            warnings: warnings,
          ),
        );
      }
    }

    final slots = <String, List<A2UINode>>{};
    final rawSlots = node['slots'];
    if (rawSlots is Map) {
      rawSlots.forEach((slotName, slotChildren) {
        if (slotName is! String || slotChildren is! List) return;
        final parsed = <A2UINode>[];
        for (var i = 0; i < slotChildren.length; i++) {
          final s = slotChildren[i];
          if (s is! Map) {
            warnings.add(
              A2UIWarning(
                level: A2UIWarningLevel.ignored,
                message: 'Non-object slot child ignored',
                path: '$path.slots.$slotName[$i]',
              ),
            );
            continue;
          }
          parsed.add(
            _parseNode(
              Map<String, dynamic>.from(s),
              path: '$path.slots.$slotName[$i]',
              depth: depth + 1,
              warnings: warnings,
            ),
          );
        }
        if (parsed.isNotEmpty) slots[slotName] = parsed;
      });
    }

    final actionId = node['action_id'] is String ? node['action_id'] as String : null;
    final actionPayload = node['action_payload'] is Map
        ? Map<String, dynamic>.from(node['action_payload'] as Map)
        : null;

    return A2UINode(
      type: resolvedType,
      props: resolvedProps,
      children: children,
      slots: slots,
      actionId: actionId,
      actionPayload: actionPayload,
    );
  }

  String _fallbackMarkdownFor(String unknownType, Map<String, dynamic> props) {
    final hint = props['content'] ?? props['text'] ?? props['label'] ?? '';
    return [
      '> ⚠️ Tipo `$unknownType` no soportado en A2UI v$kA2UISupportedVersion.',
      if (hint is String && hint.isNotEmpty) '>\n> $hint',
    ].join('\n');
  }
}
