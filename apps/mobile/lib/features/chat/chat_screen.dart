import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../providers/chat_provider.dart';
import '../../theme/monstruo_theme.dart';
import 'widgets/chat_input.dart';
import 'widgets/message_bubble.dart';
import 'widgets/tool_activity_bar.dart';
import 'widgets/typing_indicator.dart';

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final _scrollController = ScrollController();

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      Future.delayed(const Duration(milliseconds: 50), () {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOutCubic,
          );
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatProvider);
    final messages = chatState.messages;
    final activeTools = chatState.activeTools;
    final isThinking = chatState.isThinking;
    final isStreaming = chatState.isStreaming;

    // Auto-scroll when messages change or thinking state changes
    ref.listen(chatProvider, (prev, next) {
      if (prev?.messages.length != next.messages.length ||
          prev?.isThinking != next.isThinking ||
          prev?.isStreaming != next.isStreaming) {
        _scrollToBottom();
      }
    });

    return Column(
      children: [
        // Tool activity bar
        if (activeTools.isNotEmpty)
          ToolActivityBar(tools: activeTools),

        // Messages list
        Expanded(
          child: messages.isEmpty && !isThinking
              ? _buildEmptyState()
              : ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.only(
                    top: 16,
                    bottom: 8,
                  ),
                  itemCount: messages.length + (isThinking ? 1 : 0),
                  itemBuilder: (context, index) {
                    // Thinking indicator at the bottom
                    if (isThinking && index == messages.length) {
                      return ThinkingIndicator(
                        model: chatState.thinkingModel,
                        intent: chatState.thinkingIntent,
                        startTime: chatState.thinkingStartTime,
                        isThinking: true,
                      );
                    }

                    final message = messages[index];
                    return MessageBubble(
                      key: ValueKey(message.id),
                      message: message,
                    );
                  },
                ),
        ),

        // Input bar
        ChatInput(
          onSend: (content) {
            ref.read(chatProvider.notifier).sendMessage(content);
          },
          isStreaming: isStreaming,
          onStop: () {
            // TODO: implement stop streaming
          },
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Logo
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(24),
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  MonstruoTheme.primary.withValues(alpha: 0.3),
                  MonstruoTheme.secondary.withValues(alpha: 0.3),
                ],
              ),
            ),
            child: const Center(
              child: Text(
                'M',
                style: TextStyle(
                  color: MonstruoTheme.primary,
                  fontSize: 36,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'El Monstruo',
            style: TextStyle(
              color: MonstruoTheme.onBackground,
              fontSize: 22,
              fontWeight: FontWeight.bold,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Tu agente IA soberano',
            style: TextStyle(
              color: MonstruoTheme.onSurfaceDim,
              fontSize: 15,
              letterSpacing: -0.2,
            ),
          ),
          const SizedBox(height: 32),
          // Quick action chips
          Wrap(
            spacing: 8,
            runSpacing: 8,
            alignment: WrapAlignment.center,
            children: [
              _buildQuickAction('Estado del kernel', Icons.dns_outlined),
              _buildQuickAction('Estado del Embrión', Icons.psychology_outlined),
              _buildQuickAction('Buscar en web', Icons.language),
              _buildQuickAction('Ejecutar código', Icons.terminal),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickAction(String label, IconData icon) {
    return ActionChip(
      avatar: Icon(icon, size: 16, color: MonstruoTheme.primary),
      label: Text(
        label,
        style: const TextStyle(
          color: MonstruoTheme.onSurfaceDim,
          fontSize: 13,
        ),
      ),
      backgroundColor: MonstruoTheme.surface,
      side: BorderSide(
        color: MonstruoTheme.primary.withValues(alpha: 0.2),
        width: 0.5,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      onPressed: () {
        ref.read(chatProvider.notifier).sendMessage(label);
      },
    );
  }
}
