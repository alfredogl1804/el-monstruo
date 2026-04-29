import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../theme/monstruo_theme.dart';

/// File viewer that renders different file types inline.
///
/// Supports:
/// - Images (png, jpg, gif, webp, svg)
/// - Markdown (md)
/// - Code files (py, ts, js, dart, etc.)
/// - PDFs (via external viewer)
/// - Plain text
class FileViewer extends StatelessWidget {
  const FileViewer({
    super.key,
    required this.filename,
    required this.url,
    this.mimeType,
    this.content,
  });

  final String filename;
  final String url;
  final String? mimeType;
  final String? content;

  @override
  Widget build(BuildContext context) {
    final ext = filename.split('.').last.toLowerCase();
    final type = _resolveType(ext, mimeType);

    return Scaffold(
      backgroundColor: MonstruoTheme.background,
      appBar: AppBar(
        backgroundColor: MonstruoTheme.surface,
        title: Text(
          filename,
          style: const TextStyle(
            fontSize: 14,
            color: MonstruoTheme.onBackground,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.open_in_new, size: 20),
            color: MonstruoTheme.onSurfaceDim,
            onPressed: () => _openExternal(url),
          ),
          IconButton(
            icon: const Icon(Icons.download, size: 20),
            color: MonstruoTheme.onSurfaceDim,
            onPressed: () => _download(context),
          ),
        ],
      ),
      body: switch (type) {
        _FileType.image => _ImageViewer(url: url),
        _FileType.markdown => _MarkdownViewer(content: content ?? ''),
        _FileType.code => _CodeViewer(content: content ?? '', language: ext),
        _FileType.pdf => _PdfPlaceholder(url: url),
        _FileType.text => _TextViewer(content: content ?? ''),
        _FileType.unknown => _UnknownViewer(filename: filename, url: url),
      },
    );
  }

  _FileType _resolveType(String ext, String? mime) {
    // Image types
    if (['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'bmp'].contains(ext)) {
      return _FileType.image;
    }
    // Markdown
    if (ext == 'md' || ext == 'markdown') {
      return _FileType.markdown;
    }
    // Code
    if ([
      'py', 'ts', 'js', 'dart', 'rs', 'go', 'java', 'kt', 'swift',
      'c', 'cpp', 'h', 'hpp', 'cs', 'rb', 'php', 'sh', 'bash', 'zsh',
      'yaml', 'yml', 'toml', 'json', 'xml', 'html', 'css', 'scss',
      'sql', 'graphql', 'proto', 'dockerfile', 'makefile',
    ].contains(ext)) {
      return _FileType.code;
    }
    // PDF
    if (ext == 'pdf') {
      return _FileType.pdf;
    }
    // Text
    if (['txt', 'log', 'csv', 'env', 'ini', 'cfg', 'conf'].contains(ext)) {
      return _FileType.text;
    }
    // Check MIME type
    if (mime != null) {
      if (mime.startsWith('image/')) return _FileType.image;
      if (mime.startsWith('text/')) return _FileType.text;
      if (mime == 'application/pdf') return _FileType.pdf;
    }
    return _FileType.unknown;
  }

  Future<void> _openExternal(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  void _download(BuildContext context) {
    // TODO: Implement download to device
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Descarga iniciada...'),
        backgroundColor: MonstruoTheme.surface,
      ),
    );
  }
}

enum _FileType { image, markdown, code, pdf, text, unknown }

// ─── Image Viewer ───
class _ImageViewer extends StatelessWidget {
  const _ImageViewer({required this.url});
  final String url;

  @override
  Widget build(BuildContext context) {
    return InteractiveViewer(
      minScale: 0.5,
      maxScale: 4.0,
      child: Center(
        child: Image.network(
          url,
          fit: BoxFit.contain,
          loadingBuilder: (context, child, progress) {
            if (progress == null) return child;
            return Center(
              child: CircularProgressIndicator(
                value: progress.expectedTotalBytes != null
                    ? progress.cumulativeBytesLoaded /
                        progress.expectedTotalBytes!
                    : null,
                color: MonstruoTheme.primary,
              ),
            );
          },
          errorBuilder: (context, error, stack) {
            return const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.broken_image, size: 48, color: MonstruoTheme.onSurfaceDim),
                  SizedBox(height: 8),
                  Text(
                    'No se pudo cargar la imagen',
                    style: TextStyle(color: MonstruoTheme.onSurfaceDim),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}

// ─── Markdown Viewer ───
class _MarkdownViewer extends StatelessWidget {
  const _MarkdownViewer({required this.content});
  final String content;

  @override
  Widget build(BuildContext context) {
    return Markdown(
      data: content,
      selectable: true,
      padding: const EdgeInsets.all(16),
      styleSheet: MarkdownStyleSheet(
        p: const TextStyle(
          fontSize: 14,
          color: MonstruoTheme.onSurface,
          height: 1.6,
        ),
        h1: const TextStyle(
          fontSize: 24,
          fontWeight: FontWeight.w700,
          color: MonstruoTheme.onBackground,
        ),
        h2: const TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: MonstruoTheme.onBackground,
        ),
        h3: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w600,
          color: MonstruoTheme.onBackground,
        ),
        code: TextStyle(
          fontFamily: 'monospace',
          fontSize: 13,
          color: MonstruoTheme.success,
          backgroundColor: MonstruoTheme.surfaceVariant,
        ),
        codeblockDecoration: BoxDecoration(
          color: MonstruoTheme.surfaceVariant,
          borderRadius: BorderRadius.circular(8),
        ),
        blockquoteDecoration: BoxDecoration(
          border: Border(
            left: BorderSide(
              color: MonstruoTheme.primary,
              width: 3,
            ),
          ),
        ),
        tableBorder: TableBorder.all(
          color: MonstruoTheme.divider,
          width: 0.5,
        ),
      ),
      onTapLink: (text, href, title) {
        if (href != null) {
          launchUrl(Uri.parse(href));
        }
      },
    );
  }
}

// ─── Code Viewer ───
class _CodeViewer extends StatelessWidget {
  const _CodeViewer({required this.content, required this.language});
  final String content;
  final String language;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: const Color(0xFF0D0D0D),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Language badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: const BoxDecoration(
              color: MonstruoTheme.surfaceVariant,
              border: Border(
                bottom: BorderSide(color: MonstruoTheme.divider, width: 0.5),
              ),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: MonstruoTheme.primary.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    language.toUpperCase(),
                    style: const TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w600,
                      color: MonstruoTheme.primary,
                    ),
                  ),
                ),
                const Spacer(),
                Text(
                  '${content.split('\n').length} líneas',
                  style: const TextStyle(
                    fontSize: 11,
                    color: MonstruoTheme.onSurfaceDim,
                  ),
                ),
              ],
            ),
          ),
          // Code content
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: SelectableText.rich(
                TextSpan(
                  children: content.split('\n').asMap().entries.map((entry) {
                    return TextSpan(
                      children: [
                        TextSpan(
                          text: '${(entry.key + 1).toString().padLeft(4)} ',
                          style: const TextStyle(
                            fontFamily: 'monospace',
                            fontSize: 12,
                            color: MonstruoTheme.onSurfaceDim,
                          ),
                        ),
                        TextSpan(
                          text: '${entry.value}\n',
                          style: const TextStyle(
                            fontFamily: 'monospace',
                            fontSize: 12,
                            color: MonstruoTheme.success,
                            height: 1.5,
                          ),
                        ),
                      ],
                    );
                  }).toList(),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ─── PDF Placeholder ───
class _PdfPlaceholder extends StatelessWidget {
  const _PdfPlaceholder({required this.url});
  final String url;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(
            Icons.picture_as_pdf,
            size: 64,
            color: MonstruoTheme.error,
          ),
          const SizedBox(height: 16),
          const Text(
            'Documento PDF',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: MonstruoTheme.onBackground,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Toca para abrir en el visor externo',
            style: TextStyle(
              fontSize: 14,
              color: MonstruoTheme.onSurfaceDim,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () async {
              final uri = Uri.parse(url);
              if (await canLaunchUrl(uri)) {
                await launchUrl(uri, mode: LaunchMode.externalApplication);
              }
            },
            icon: const Icon(Icons.open_in_new, size: 18),
            label: const Text('Abrir PDF'),
            style: ElevatedButton.styleFrom(
              backgroundColor: MonstruoTheme.primary,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ─── Unknown Viewer ───
class _UnknownViewer extends StatelessWidget {
  const _UnknownViewer({required this.filename, required this.url});
  final String filename;
  final String url;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(
            Icons.insert_drive_file,
            size: 64,
            color: MonstruoTheme.onSurfaceDim,
          ),
          const SizedBox(height: 16),
          Text(
            filename,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w500,
              color: MonstruoTheme.onBackground,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Vista previa no disponible para este tipo de archivo',
            style: TextStyle(
              fontSize: 14,
              color: MonstruoTheme.onSurfaceDim,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () async {
              final uri = Uri.parse(url);
              if (await canLaunchUrl(uri)) {
                await launchUrl(uri, mode: LaunchMode.externalApplication);
              }
            },
            icon: const Icon(Icons.download, size: 18),
            label: const Text('Descargar'),
            style: ElevatedButton.styleFrom(
              backgroundColor: MonstruoTheme.surfaceVariant,
              foregroundColor: MonstruoTheme.onSurface,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
