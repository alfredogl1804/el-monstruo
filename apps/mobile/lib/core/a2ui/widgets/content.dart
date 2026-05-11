/// A2UI content widgets — Text, Markdown, Image, Link, Code, Divider.
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

import '../brand_tokens.dart';
import '../types/a2ui_action.dart';
import '../types/a2ui_node.dart';

/// Texto plano con variantes `title|body|caption`.
class A2UIText extends StatelessWidget {
  const A2UIText({super.key, required this.node});
  final A2UINode node;

  @override
  Widget build(BuildContext context) {
    final content = node.prop<String>('content') ?? '';
    final variant = node.prop<String>('variant') ?? 'body';
    final style = switch (variant) {
      'titleLg' => A2UIBrand.titleLg,
      'title' || 'titleMd' => A2UIBrand.titleMd,
      'caption' => A2UIBrand.caption,
      _ => A2UIBrand.body,
    };
    return Text(content, style: style);
  }
}

/// Markdown renderer con fuente clara y links activos.
class A2UIMarkdown extends StatelessWidget {
  const A2UIMarkdown({super.key, required this.node, this.onLinkTap});

  final A2UINode node;
  final void Function(String url)? onLinkTap;

  @override
  Widget build(BuildContext context) {
    final content = node.prop<String>('content') ?? '';
    return MarkdownBody(
      data: content,
      onTapLink: (text, href, title) {
        if (href != null) onLinkTap?.call(href);
      },
      styleSheet: MarkdownStyleSheet(
        p: A2UIBrand.body,
        h1: A2UIBrand.titleLg,
        h2: A2UIBrand.titleMd,
        h3: A2UIBrand.titleMd,
        a: A2UIBrand.body.copyWith(
          color: A2UIBrand.forja,
          decoration: TextDecoration.underline,
        ),
        code: A2UIBrand.code.copyWith(
          backgroundColor: A2UIBrand.graphite,
        ),
        codeblockDecoration: BoxDecoration(
          color: A2UIBrand.graphite,
          borderRadius: BorderRadius.circular(A2UIBrand.rSm),
          border: Border.all(color: A2UIBrand.border),
        ),
        blockquoteDecoration: BoxDecoration(
          border: Border(
            left: BorderSide(color: A2UIBrand.forja, width: 3),
          ),
        ),
      ),
    );
  }
}

/// Imagen con `src`, `alt`, `aspect` opcional.
class A2UIImage extends StatelessWidget {
  const A2UIImage({super.key, required this.node});
  final A2UINode node;

  @override
  Widget build(BuildContext context) {
    final src = node.prop<String>('src');
    final alt = node.prop<String>('alt') ?? 'imagen';
    final aspect = (node.prop<num>('aspect') ?? 16 / 9).toDouble();

    if (src == null || src.isEmpty) {
      return _ImagePlaceholder(label: alt);
    }
    return ClipRRect(
      borderRadius: BorderRadius.circular(A2UIBrand.rMd),
      child: AspectRatio(
        aspectRatio: aspect,
        child: Image.network(
          src,
          fit: BoxFit.cover,
          semanticLabel: alt,
          errorBuilder: (_, __, ___) => _ImagePlaceholder(label: alt),
          loadingBuilder: (_, child, p) =>
              p == null ? child : const _ImageLoading(),
        ),
      ),
    );
  }
}

class _ImagePlaceholder extends StatelessWidget {
  const _ImagePlaceholder({required this.label});
  final String label;
  @override
  Widget build(BuildContext context) {
    return Container(
      color: A2UIBrand.graphite,
      padding: const EdgeInsets.all(A2UIBrand.s12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.broken_image_outlined,
              color: A2UIBrand.textSecondary),
          const SizedBox(width: A2UIBrand.s8),
          Flexible(child: Text(label, style: A2UIBrand.caption)),
        ],
      ),
    );
  }
}

class _ImageLoading extends StatelessWidget {
  const _ImageLoading();
  @override
  Widget build(BuildContext context) => Container(
        color: A2UIBrand.graphite,
        alignment: Alignment.center,
        child: const SizedBox(
          width: 24,
          height: 24,
          child:
              CircularProgressIndicator(strokeWidth: 2, color: A2UIBrand.forja),
        ),
      );
}

/// Link textual con `label` + `href`. Dispatch via callback.
class A2UILink extends StatelessWidget {
  const A2UILink({super.key, required this.node, this.dispatcher});
  final A2UINode node;
  final A2UIActionDispatcher? dispatcher;

  @override
  Widget build(BuildContext context) {
    final label = node.prop<String>('label') ?? node.prop<String>('content') ?? '';
    final href = node.prop<String>('href');
    return InkWell(
      onTap: () {
        if (href != null) {
          dispatcher?.call(A2UIAction(
            actionId: node.actionId ?? 'open_link',
            sourceWidget: 'Link',
            payload: {'href': href, ...?node.actionPayload},
          ));
        }
      },
      child: Text(
        label,
        style: A2UIBrand.body.copyWith(
          color: A2UIBrand.forja,
          decoration: TextDecoration.underline,
        ),
      ),
    );
  }
}

/// Bloque de código con copia rápida.
class A2UICode extends StatelessWidget {
  const A2UICode({super.key, required this.node});
  final A2UINode node;

  @override
  Widget build(BuildContext context) {
    final content = node.prop<String>('content') ?? '';
    final language = node.prop<String>('language') ?? '';
    return Container(
      decoration: BoxDecoration(
        color: A2UIBrand.graphite,
        borderRadius: BorderRadius.circular(A2UIBrand.rSm),
        border: Border.all(color: A2UIBrand.border),
      ),
      padding: const EdgeInsets.all(A2UIBrand.s12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              if (language.isNotEmpty)
                Text(language, style: A2UIBrand.caption),
              const Spacer(),
              IconButton(
                tooltip: 'Copiar',
                icon: const Icon(Icons.copy_rounded, size: 16),
                color: A2UIBrand.textSecondary,
                visualDensity: VisualDensity.compact,
                onPressed: () => Clipboard.setData(ClipboardData(text: content)),
              ),
            ],
          ),
          const SizedBox(height: A2UIBrand.s4),
          SelectableText(content, style: A2UIBrand.code),
        ],
      ),
    );
  }
}

/// Línea divisoria horizontal.
class A2UIDivider extends StatelessWidget {
  const A2UIDivider({super.key, required this.node});
  final A2UINode node;
  @override
  Widget build(BuildContext context) =>
      const Divider(color: A2UIBrand.border, height: 1);
}
