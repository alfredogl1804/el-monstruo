import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../../theme/monstruo_theme.dart';
import 'agent_selector.dart';

/// Premium chat input bar with glassmorphism, auto-expand, and micro-interactions.
class ChatInput extends StatefulWidget {
  const ChatInput({
    super.key,
    required this.onSend,
    required this.isStreaming,
    this.onStop,
  });

  final ValueChanged<String> onSend;
  final bool isStreaming;
  final VoidCallback? onStop;

  @override
  State<ChatInput> createState() => _ChatInputState();
}

class _ChatInputState extends State<ChatInput> with SingleTickerProviderStateMixin {
  final _controller = TextEditingController();
  final _focusNode = FocusNode();
  bool _hasText = false;
  bool _isFocused = false;

  @override
  void initState() {
    super.initState();
    _controller.addListener(() {
      final hasText = _controller.text.trim().isNotEmpty;
      if (hasText != _hasText) setState(() => _hasText = hasText);
    });
    _focusNode.addListener(() {
      setState(() => _isFocused = _focusNode.hasFocus);
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
    HapticFeedback.mediumImpact();
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
        top: MonstruoTheme.spacingSm + 4,
        bottom: bottomPadding + MonstruoTheme.spacingSm + 4,
      ),
      decoration: BoxDecoration(
        color: MonstruoTheme.background.withValues(alpha: 0.85),
        border: const Border(
          top: BorderSide(color: MonstruoTheme.divider, width: 0.5),
        ),
      ),
      child: ClipRRect(
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              // Agent selector
              const AgentSelector(),
              const SizedBox(width: 4),
              // Attachment button
              _AttachButton(onPressed: () {
                HapticFeedback.lightImpact();
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Adjuntos: próximamente')),
                );
              }),
              const SizedBox(width: 8),
              // Text field with animated border
              Expanded(
                child: AnimatedContainer(
                  duration: MonstruoTheme.animFast,
                  constraints: const BoxConstraints(maxHeight: 140),
                  decoration: BoxDecoration(
                    color: MonstruoTheme.surfaceVariant,
                    borderRadius: BorderRadius.circular(22),
                    border: Border.all(
                      color: _isFocused
                          ? MonstruoTheme.primary.withValues(alpha: 0.5)
                          : MonstruoTheme.divider,
                      width: _isFocused ? 1.5 : 0.5,
                    ),
                    boxShadow: _isFocused
                        ? [
                            BoxShadow(
                              color: MonstruoTheme.primary.withValues(alpha: 0.08),
                              blurRadius: 12,
                              spreadRadius: 0,
                            ),
                          ]
                        : null,
                  ),
                  child: TextField(
                    controller: _controller,
                    focusNode: _focusNode,
                    maxLines: null,
                    textInputAction: TextInputAction.newline,
                    style: const TextStyle(
                      color: MonstruoTheme.onBackground,
                      fontSize: 15,
                      height: 1.4,
                    ),
                    decoration: InputDecoration(
                      hintText: 'Mensaje para El Monstruo...',
                      hintStyle: TextStyle(
                        color: MonstruoTheme.onSurfaceDim.withValues(alpha: 0.5),
                        fontSize: 15,
                      ),
                      border: InputBorder.none,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 18,
                        vertical: 12,
                      ),
                    ),
                    onSubmitted: (_) => _handleSend(),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              // Send / Stop button
              _SendStopButton(
                hasText: _hasText,
                isStreaming: widget.isStreaming,
                onSend: _handleSend,
                onStop: widget.onStop,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─── Attachment Button ───
class _AttachButton extends StatelessWidget {
  const _AttachButton({required this.onPressed});
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 36,
      height: 36,
      child: IconButton(
        onPressed: onPressed,
        padding: EdgeInsets.zero,
        icon: const Icon(
          Icons.add_circle_outline_rounded,
          color: MonstruoTheme.onSurfaceDim,
          size: 22,
        ),
      ),
    );
  }
}

// ─── Send / Stop Button with animation ───
class _SendStopButton extends StatelessWidget {
  const _SendStopButton({
    required this.hasText,
    required this.isStreaming,
    required this.onSend,
    this.onStop,
  });

  final bool hasText;
  final bool isStreaming;
  final VoidCallback onSend;
  final VoidCallback? onStop;

  @override
  Widget build(BuildContext context) {
    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 200),
      transitionBuilder: (child, animation) {
        return ScaleTransition(scale: animation, child: child);
      },
      child: isStreaming
          ? _buildStopButton()
          : _buildSendButton(),
    );
  }

  Widget _buildStopButton() {
    return GestureDetector(
      key: const ValueKey('stop'),
      onTap: () {
        HapticFeedback.mediumImpact();
        onStop?.call();
      },
      child: Container(
        width: 36,
        height: 36,
        decoration: BoxDecoration(
          color: MonstruoTheme.error,
          borderRadius: BorderRadius.circular(10),
        ),
        child: const Icon(
          Icons.stop_rounded,
          color: Colors.white,
          size: 20,
        ),
      ),
    )
        .animate(onPlay: (c) => c.repeat(reverse: true))
        .scaleXY(begin: 1.0, end: 0.92, duration: 800.ms);
  }

  Widget _buildSendButton() {
    return GestureDetector(
      key: const ValueKey('send'),
      onTap: hasText ? onSend : null,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        width: 36,
        height: 36,
        decoration: BoxDecoration(
          gradient: hasText ? MonstruoTheme.sendButtonGradient : null,
          color: hasText ? null : MonstruoTheme.surfaceVariant,
          borderRadius: BorderRadius.circular(10),
          boxShadow: hasText
              ? [
                  BoxShadow(
                    color: MonstruoTheme.primary.withValues(alpha: 0.3),
                    blurRadius: 8,
                    spreadRadius: 0,
                  ),
                ]
              : null,
        ),
        child: Icon(
          Icons.arrow_upward_rounded,
          color: hasText ? Colors.white : MonstruoTheme.onSurfaceDim,
          size: 20,
        ),
      ),
    );
  }
}
