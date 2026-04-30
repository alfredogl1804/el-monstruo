import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../../../models/chat_message.dart';
import '../../../theme/monstruo_theme.dart';

/// Premium message bubble widget with 2026 design patterns.
/// AI messages: full-width cards with glass effect.
/// User messages: right-aligned compact bubbles.
///
/// Sprint 45: Lightweight streaming renderer.
/// During streaming, uses SelectableText (plain text) instead of MarkdownBody
/// to avoid rebuilding the entire Markdown AST on every frame.
/// On stream completion, switches to full MarkdownBody for rich formatting.
/// This eliminates the #1 client-side bottleneck for perceived write speed.
class MessageBubble extends StatelessWidget {
  const MessageBubble({
    super.key,
    required this.message,
    this.isLast = false,
    this.showTimestamp = false,
  });

  final ChatMessage message;
  final bool isLast;
  final bool showTimestamp;

  @override
  Widget build(BuildContext context) {
    if (message.isGenUI) return _GenUIBubble(message: message);
    if (message.type == MessageType.toolResult) return _ToolResultBubble(message: message);
    if (message.isError) return _ErrorBubble(message: message);

    return message.isUser
        ? _UserBubble(message: message, isLast: isLast)
        : _AssistantBubble(message: message, isLast: isLast);
  }
}

// ─── User Message ───
class _UserBubble extends StatelessWidget {
  const _UserBubble({required this.message, required this.isLast});
  final ChatMessage message;
  final bool isLast;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        bottom: isLast ? MonstruoTheme.spacingMd : MonstruoTheme.spacingSm,
        left: 60, // Offset to keep user messages compact
      ),
      child: Align(
        alignment: Alignment.centerRight,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                MonstruoTheme.primary.withValues(alpha: 0.12),
                MonstruoTheme.secondary.withValues(alpha: 0.06),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: const BorderRadius.only(
              topLeft: Radius.circular(18),
              topRight: Radius.circular(18),
              bottomLeft: Radius.circular(18),
              bottomRight: Radius.circular(4),
            ),
            border: Border.all(
              color: MonstruoTheme.primary.withValues(alpha: 0.2),
              width: 0.5,
            ),
          ),
          child: Text(
            message.content,
            style: const TextStyle(
              color: MonstruoTheme.onBackground,
              fontSize: 15,
              height: 1.5,
              letterSpacing: -0.1,
            ),
          ),
        ),
      ),
    );
  }
}

// ─── Assistant Message ───
class _AssistantBubble extends StatefulWidget {
  const _AssistantBubble({required this.message, required this.isLast});
  final ChatMessage message;
  final bool isLast;

  @override
  State<_AssistantBubble> createState() => _AssistantBubbleState();
}

class _AssistantBubbleState extends State<_AssistantBubble>
    with SingleTickerProviderStateMixin {
  late AnimationController _cursorController;
  bool _showActions = false;

  @override
  void initState() {
    super.initState();
    _cursorController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _cursorController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isStreaming = widget.message.isStreaming;

    return Padding(
      padding: EdgeInsets.only(
        bottom: widget.isLast ? MonstruoTheme.spacingMd : 12,
        right: 24,
      ),
      child: MouseRegion(
        onEnter: (_) => setState(() => _showActions = true),
        onExit: (_) => setState(() => _showActions = false),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Avatar + Name row
            Padding(
              padding: const EdgeInsets.only(bottom: 6, left: 2),
              child: Row(
                children: [
                  _AgentAvatar(size: 24),
                  const SizedBox(width: 8),
                  const Text(
                    'El Monstruo',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: MonstruoTheme.onSurfaceDim,
                    ),
                  ),
                  if (widget.message.model != null) ...[
                    const SizedBox(width: 8),
                    _MetadataPill(text: widget.message.model!),
                  ],
                ],
              ),
            ),
            // Message content card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: MonstruoTheme.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: isStreaming
                      ? MonstruoTheme.primary.withValues(alpha: 0.3)
                      : MonstruoTheme.divider,
                  width: 0.5,
                ),
                boxShadow: isStreaming ? MonstruoTheme.glowShadow : null,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Sprint 45: Lightweight streaming renderer
                  // During streaming: use SelectableText (no Markdown AST rebuild)
                  // On completion: switch to full MarkdownBody for rich formatting
                  if (isStreaming)
                    _StreamingTextRenderer(content: widget.message.content)
                  else
                    MarkdownBody(
                      data: widget.message.content,
                      selectable: true,
                      styleSheet: _markdownStyle(context),
                    ),
                  // Streaming cursor
                  if (isStreaming)
                    AnimatedBuilder(
                      animation: _cursorController,
                      builder: (context, child) {
                        return Opacity(
                          opacity: 0.3 + (_cursorController.value * 0.7),
                          child: Container(
                            width: 2,
                            height: 18,
                            margin: const EdgeInsets.only(top: 2),
                            decoration: BoxDecoration(
                              color: MonstruoTheme.primary,
                              borderRadius: BorderRadius.circular(1),
                            ),
                          ),
                        );
                      },
                    ),
                ],
              ),
            ),
            // Action bar (copy, regenerate)
            if (_showActions && !isStreaming)
              _ActionBar(message: widget.message),
            // Metadata footer
            if (!isStreaming && widget.message.tokenCount != null)
              Padding(
                padding: const EdgeInsets.only(top: 4, left: 4),
                child: Text(
                  _buildMetadata(),
                  style: const TextStyle(
                    fontSize: 11,
                    color: MonstruoTheme.onSurfaceDim,
                  ),
                ),
              ),
          ],
        ),
      ),
    )
        .animate()
        .slideY(begin: 0.02, end: 0, duration: 250.ms, curve: Curves.easeOutCubic)
        .fadeIn(duration: 200.ms);
  }

  String _buildMetadata() {
    final parts = <String>[];
    if (widget.message.model != null) parts.add(widget.message.model!);
    if (widget.message.tokenCount != null) parts.add('${widget.message.tokenCount} tokens');
    if (widget.message.cost != null) parts.add('\$${widget.message.cost!.toStringAsFixed(4)}');
    return parts.join(' · ');
  }

  MarkdownStyleSheet _markdownStyle(BuildContext context) {
    return MarkdownStyleSheet(
      p: const TextStyle(
        color: MonstruoTheme.onSurface,
        fontSize: 15,
        height: 1.65,
        letterSpacing: -0.2,
      ),
      h1: const TextStyle(
        color: MonstruoTheme.onBackground,
        fontSize: 22,
        fontWeight: FontWeight.w700,
        height: 1.3,
      ),
      h2: const TextStyle(
        color: MonstruoTheme.onBackground,
        fontSize: 19,
        fontWeight: FontWeight.w600,
        height: 1.3,
      ),
      h3: const TextStyle(
        color: MonstruoTheme.onBackground,
        fontSize: 16,
        fontWeight: FontWeight.w600,
        height: 1.4,
      ),
      code: const TextStyle(
        color: MonstruoTheme.primary,
        backgroundColor: MonstruoTheme.surfaceVariant,
        fontSize: 13,
        fontFamily: 'JetBrains Mono',
        letterSpacing: -0.3,
      ),
      codeblockDecoration: BoxDecoration(
        color: MonstruoTheme.surfaceVariant,
        borderRadius: BorderRadius.circular(MonstruoTheme.radiusSm),
        border: Border.all(color: MonstruoTheme.divider, width: 0.5),
      ),
      codeblockPadding: const EdgeInsets.all(14),
      blockquoteDecoration: BoxDecoration(
        border: Border(
          left: BorderSide(
            color: MonstruoTheme.primary.withValues(alpha: 0.5),
            width: 3,
          ),
        ),
      ),
      blockquotePadding: const EdgeInsets.only(left: 14, top: 4, bottom: 4),
      listBullet: const TextStyle(color: MonstruoTheme.primary, fontSize: 14),
      strong: const TextStyle(
        color: MonstruoTheme.onBackground,
        fontWeight: FontWeight.w600,
      ),
      em: const TextStyle(
        color: MonstruoTheme.onSurface,
        fontStyle: FontStyle.italic,
      ),
      a: const TextStyle(
        color: MonstruoTheme.primary,
        decoration: TextDecoration.underline,
      ),
      tableBorder: TableBorder.all(
        color: MonstruoTheme.divider,
        width: 0.5,
        borderRadius: BorderRadius.circular(6),
      ),
      tableHead: const TextStyle(
        fontWeight: FontWeight.w600,
        color: MonstruoTheme.onBackground,
        fontSize: 13,
      ),
      tableBody: const TextStyle(
        color: MonstruoTheme.onSurface,
        fontSize: 13,
      ),
      tableCellsPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
    );
  }
}

/// Sprint 45: Lightweight streaming text renderer.
/// Uses SelectableText.rich with TextSpan instead of MarkdownBody during streaming.
/// This avoids rebuilding the entire Markdown AST tree on every frame/token batch.
/// The text style matches the Markdown paragraph style for visual consistency.
/// When streaming ends, the parent switches to full MarkdownBody seamlessly.
class _StreamingTextRenderer extends StatelessWidget {
  const _StreamingTextRenderer({required this.content});
  final String content;

  @override
  Widget build(BuildContext context) {
    return SelectableText.rich(
      TextSpan(
        text: content,
        style: const TextStyle(
          color: MonstruoTheme.onSurface,
          fontSize: 15,
          height: 1.65,
          letterSpacing: -0.2,
        ),
      ),
    );
  }
}

// ─── Action Bar (hover actions) ───
class _ActionBar extends StatelessWidget {
  const _ActionBar({required this.message});
  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 6, left: 4),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _ActionButton(
            icon: Icons.copy_rounded,
            tooltip: 'Copiar',
            onTap: () {
              Clipboard.setData(ClipboardData(text: message.content));
              HapticFeedback.lightImpact();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Copiado al portapapeles'),
                  duration: Duration(seconds: 1),
                ),
              );
            },
          ),
          const SizedBox(width: 4),
          _ActionButton(
            icon: Icons.refresh_rounded,
            tooltip: 'Regenerar',
            onTap: () {
              // TODO: Implement regenerate
            },
          ),
        ],
      ),
    ).animate().fadeIn(duration: 150.ms);
  }
}

class _ActionButton extends StatelessWidget {
  const _ActionButton({
    required this.icon,
    required this.tooltip,
    required this.onTap,
  });
  final IconData icon;
  final String tooltip;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: tooltip,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(6),
        child: Padding(
          padding: const EdgeInsets.all(6),
          child: Icon(icon, size: 16, color: MonstruoTheme.onSurfaceDim),
        ),
      ),
    );
  }
}

// ─── Agent Avatar ───
class _AgentAvatar extends StatelessWidget {
  const _AgentAvatar({this.size = 32});
  final double size;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        gradient: MonstruoTheme.agentGradient,
        borderRadius: BorderRadius.circular(size * 0.3),
      ),
      child: Center(
        child: Text(
          'M',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.w700,
            fontSize: size * 0.45,
          ),
        ),
      ),
    );
  }
}

// ─── Metadata Pill ───
class _MetadataPill extends StatelessWidget {
  const _MetadataPill({required this.text});
  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: MonstruoTheme.surfaceVariant,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        text,
        style: const TextStyle(
          fontSize: 10,
          color: MonstruoTheme.onSurfaceDim,
        ),
      ),
    );
  }
}

// ─── GenUI Bubble ───
class _GenUIBubble extends StatelessWidget {
  const _GenUIBubble({required this.message});
  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: MonstruoTheme.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: MonstruoTheme.primary.withValues(alpha: 0.3),
            width: 1,
          ),
          boxShadow: MonstruoTheme.glowShadow,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.auto_awesome, size: 16, color: MonstruoTheme.primary),
                const SizedBox(width: 8),
                const Text(
                  'Generative UI',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: MonstruoTheme.primary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              message.content,
              style: const TextStyle(
                color: MonstruoTheme.onSurface,
                fontSize: 14,
                height: 1.5,
              ),
            ),
          ],
        ),
      ),
    ).animate().fadeIn(duration: 250.ms).slideY(begin: 0.02, end: 0);
  }
}

// ─── Tool Result Bubble ───
class _ToolResultBubble extends StatelessWidget {
  const _ToolResultBubble({required this.message});
  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: MonstruoTheme.surfaceVariant,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: MonstruoTheme.divider, width: 0.5),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.build_circle_outlined, size: 14, color: MonstruoTheme.onSurfaceDim),
                const SizedBox(width: 6),
                Text(
                  message.toolName ?? 'Tool',
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: MonstruoTheme.onSurfaceDim,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              message.content,
              style: const TextStyle(
                color: MonstruoTheme.onSurface,
                fontSize: 13,
                height: 1.5,
                fontFamily: 'JetBrains Mono',
              ),
              maxLines: 5,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}

// ─── Error Bubble ───
class _ErrorBubble extends StatelessWidget {
  const _ErrorBubble({required this.message});
  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.red.withValues(alpha: 0.08),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.red.withValues(alpha: 0.3), width: 0.5),
        ),
        child: Row(
          children: [
            Icon(Icons.error_outline, size: 16, color: Colors.red.shade300),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                message.content,
                style: TextStyle(
                  color: Colors.red.shade200,
                  fontSize: 13,
                  height: 1.4,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
