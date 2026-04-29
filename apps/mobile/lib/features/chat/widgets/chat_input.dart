import 'package:flutter/material.dart';

import '../../../theme/monstruo_theme.dart';

class ChatInput extends StatefulWidget {
  const ChatInput({
    super.key,
    required this.onSend,
    this.isStreaming = false,
  });

  final void Function(String text) onSend;
  final bool isStreaming;

  @override
  State<ChatInput> createState() => _ChatInputState();
}

class _ChatInputState extends State<ChatInput> {
  final _controller = TextEditingController();
  final _focusNode = FocusNode();
  bool _hasText = false;

  @override
  void initState() {
    super.initState();
    _controller.addListener(() {
      final hasText = _controller.text.trim().isNotEmpty;
      if (hasText != _hasText) {
        setState(() => _hasText = hasText);
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _handleSend() {
    final text = _controller.text.trim();
    if (text.isEmpty || widget.isStreaming) return;

    widget.onSend(text);
    _controller.clear();
    _focusNode.requestFocus();
  }

  @override
  Widget build(BuildContext context) {
    final bottomPadding = MediaQuery.of(context).padding.bottom;

    return Container(
      padding: EdgeInsets.only(
        left: MonstruoTheme.spacingMd,
        right: MonstruoTheme.spacingSm,
        top: MonstruoTheme.spacingSm,
        bottom: bottomPadding + MonstruoTheme.spacingSm,
      ),
      decoration: const BoxDecoration(
        color: MonstruoTheme.surface,
        border: Border(
          top: BorderSide(color: MonstruoTheme.divider, width: 0.5),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          // Attachment button
          IconButton(
            icon: const Icon(Icons.add_circle_outline),
            color: MonstruoTheme.onSurfaceDim,
            iconSize: 24,
            onPressed: () {
              // TODO: Show attachment picker (files, images, camera)
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Adjuntos: próximamente')),
              );
            },
          ),

          // Text field
          Expanded(
            child: Container(
              constraints: const BoxConstraints(maxHeight: 120),
              decoration: BoxDecoration(
                color: MonstruoTheme.surfaceVariant,
                borderRadius: BorderRadius.circular(MonstruoTheme.radiusLg),
              ),
              child: TextField(
                controller: _controller,
                focusNode: _focusNode,
                maxLines: null,
                textInputAction: TextInputAction.newline,
                style: const TextStyle(
                  color: MonstruoTheme.onBackground,
                  fontSize: 15,
                ),
                decoration: InputDecoration(
                  hintText: 'Mensaje para El Monstruo...',
                  hintStyle: TextStyle(
                    color: MonstruoTheme.onSurfaceDim.withValues(alpha: 0.6),
                    fontSize: 15,
                  ),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 10,
                  ),
                ),
                onSubmitted: (_) => _handleSend(),
              ),
            ),
          ),

          const SizedBox(width: 4),

          // Send / Stop button
          AnimatedSwitcher(
            duration: const Duration(milliseconds: 200),
            child: widget.isStreaming
                ? IconButton(
                    key: const ValueKey('stop'),
                    icon: Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        color: MonstruoTheme.error,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Icon(
                        Icons.stop_rounded,
                        color: Colors.white,
                        size: 20,
                      ),
                    ),
                    onPressed: () {
                      // TODO: Cancel current stream
                    },
                  )
                : IconButton(
                    key: const ValueKey('send'),
                    icon: Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        gradient: _hasText
                            ? MonstruoTheme.agentGradient
                            : null,
                        color: _hasText ? null : MonstruoTheme.surfaceVariant,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        Icons.arrow_upward_rounded,
                        color: _hasText
                            ? Colors.white
                            : MonstruoTheme.onSurfaceDim,
                        size: 20,
                      ),
                    ),
                    onPressed: _hasText ? _handleSend : null,
                  ),
          ),
        ],
      ),
    );
  }
}
