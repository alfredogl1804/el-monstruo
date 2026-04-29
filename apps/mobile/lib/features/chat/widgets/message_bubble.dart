import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

import '../../../models/chat_message.dart';
import '../../../theme/monstruo_theme.dart';

class MessageBubble extends StatelessWidget {
  const MessageBubble({
    super.key,
    required this.message,
    this.isLast = false,
  });

  final ChatMessage message;
  final bool isLast;

  @override
  Widget build(BuildContext context) {
    if (message.isGenUI) {
      return _GenUIBubble(message: message);
    }

    if (message.type == MessageType.toolResult) {
      return _ToolResultBubble(message: message);
    }

    if (message.isError) {
      return _ErrorBubble(message: message);
    }

    return Padding(
      padding: EdgeInsets.only(
        bottom: isLast ? MonstruoTheme.spacingMd : MonstruoTheme.spacingSm,
      ),
      child: Row(
        mainAxisAlignment:
            message.isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!message.isUser) ...[
            _AgentAvatar(),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(
                horizontal: MonstruoTheme.spacingMd,
                vertical: MonstruoTheme.spacingMd - 4,
              ),
              decoration: BoxDecoration(
                color: message.isUser
                    ? MonstruoTheme.primary.withValues(alpha: 0.15)
                    : MonstruoTheme.surface,
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(MonstruoTheme.radiusMd),
                  topRight: const Radius.circular(MonstruoTheme.radiusMd),
                  bottomLeft: Radius.circular(
                    message.isUser ? MonstruoTheme.radiusMd : 4,
                  ),
                  bottomRight: Radius.circular(
                    message.isUser ? 4 : MonstruoTheme.radiusMd,
                  ),
                ),
                border: Border.all(
                  color: message.isUser
                      ? MonstruoTheme.primary.withValues(alpha: 0.3)
                      : MonstruoTheme.divider,
                  width: 0.5,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Message content
                  if (message.isUser)
                    Text(
                      message.content,
                      style: const TextStyle(
                        color: MonstruoTheme.onBackground,
                        fontSize: 15,
                        height: 1.5,
                      ),
                    )
                  else
                    MarkdownBody(
                      data: message.content,
                      selectable: true,
                      styleSheet: MarkdownStyleSheet(
                        p: const TextStyle(
                          color: MonstruoTheme.onSurface,
                          fontSize: 15,
                          height: 1.6,
                        ),
                        h1: const TextStyle(
                          color: MonstruoTheme.onBackground,
                          fontSize: 22,
                          fontWeight: FontWeight.w700,
                        ),
                        h2: const TextStyle(
                          color: MonstruoTheme.onBackground,
                          fontSize: 19,
                          fontWeight: FontWeight.w600,
                        ),
                        h3: const TextStyle(
                          color: MonstruoTheme.onBackground,
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                        code: TextStyle(
                          color: MonstruoTheme.primary,
                          backgroundColor: MonstruoTheme.surfaceVariant,
                          fontSize: 13,
                          fontFamily: 'monospace',
                        ),
                        codeblockDecoration: BoxDecoration(
                          color: MonstruoTheme.surfaceVariant,
                          borderRadius: BorderRadius.circular(
                            MonstruoTheme.radiusSm,
                          ),
                        ),
                        codeblockPadding: const EdgeInsets.all(12),
                        blockquoteDecoration: BoxDecoration(
                          border: Border(
                            left: BorderSide(
                              color: MonstruoTheme.primary,
                              width: 3,
                            ),
                          ),
                        ),
                        blockquotePadding: const EdgeInsets.only(left: 12),
                        listBullet: const TextStyle(
                          color: MonstruoTheme.primary,
                        ),
                        a: const TextStyle(
                          color: MonstruoTheme.primary,
                          decoration: TextDecoration.underline,
                        ),
                        tableBorder: TableBorder.all(
                          color: MonstruoTheme.divider,
                          width: 0.5,
                        ),
                        tableHead: const TextStyle(
                          fontWeight: FontWeight.w600,
                          color: MonstruoTheme.onBackground,
                        ),
                        tableBody: const TextStyle(
                          color: MonstruoTheme.onSurface,
                        ),
                      ),
                    ),

                  // Streaming indicator
                  if (message.isStreaming)
                    Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: SizedBox(
                        width: 12,
                        height: 12,
                        child: CircularProgressIndicator(
                          strokeWidth: 1.5,
                          color: MonstruoTheme.primary,
                        ),
                      ),
                    ),

                  // Metadata row (model, tokens, cost)
                  if (!message.isUser && !message.isStreaming && message.model != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (message.model != null)
                            _MetaChip(text: message.model!),
                          if (message.tokenCount != null) ...[
                            const SizedBox(width: 6),
                            _MetaChip(text: '${message.tokenCount} tokens'),
                          ],
                          if (message.cost != null) ...[
                            const SizedBox(width: 6),
                            _MetaChip(text: '\$${message.cost!.toStringAsFixed(4)}'),
                          ],
                        ],
                      ),
                    ),
                ],
              ),
            ),
          ),
          if (message.isUser) const SizedBox(width: 8),
        ],
      ),
    );
  }
}

class _AgentAvatar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 28,
      height: 28,
      decoration: BoxDecoration(
        gradient: MonstruoTheme.agentGradient,
        borderRadius: BorderRadius.circular(8),
      ),
      child: const Center(
        child: Text(
          'M',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.w700,
            fontSize: 14,
          ),
        ),
      ),
    );
  }
}

class _MetaChip extends StatelessWidget {
  const _MetaChip({required this.text});
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

class _GenUIBubble extends StatelessWidget {
  const _GenUIBubble({required this.message});
  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: MonstruoTheme.spacingSm),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(MonstruoTheme.spacingMd),
        decoration: BoxDecoration(
          color: MonstruoTheme.surface,
          borderRadius: BorderRadius.circular(MonstruoTheme.radiusMd),
          border: Border.all(
            color: MonstruoTheme.primary.withValues(alpha: 0.3),
            width: 1,
          ),
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
            // TODO: Render A2UI component from message.genuiPayload
            Text(
              message.content,
              style: const TextStyle(
                color: MonstruoTheme.onSurface,
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ToolResultBubble extends StatelessWidget {
  const _ToolResultBubble({required this.message});
  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: MonstruoTheme.spacingSm),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: MonstruoTheme.surfaceVariant,
          borderRadius: BorderRadius.circular(MonstruoTheme.radiusSm),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(Icons.build_circle_outlined, size: 16, color: MonstruoTheme.tertiary),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (message.toolName != null)
                    Text(
                      message.toolName!,
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: MonstruoTheme.tertiary,
                      ),
                    ),
                  const SizedBox(height: 4),
                  Text(
                    message.content.length > 200
                        ? '${message.content.substring(0, 200)}...'
                        : message.content,
                    style: const TextStyle(
                      fontSize: 12,
                      color: MonstruoTheme.onSurfaceDim,
                      fontFamily: 'monospace',
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ErrorBubble extends StatelessWidget {
  const _ErrorBubble({required this.message});
  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: MonstruoTheme.spacingSm),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: MonstruoTheme.error.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(MonstruoTheme.radiusSm),
          border: Border.all(
            color: MonstruoTheme.error.withValues(alpha: 0.3),
            width: 0.5,
          ),
        ),
        child: Row(
          children: [
            const Icon(Icons.error_outline, size: 16, color: MonstruoTheme.error),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                message.content,
                style: const TextStyle(
                  fontSize: 13,
                  color: MonstruoTheme.error,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
