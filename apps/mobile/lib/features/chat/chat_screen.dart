import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../models/chat_message.dart';
import '../../providers/chat_provider.dart';
import '../../services/kernel_service.dart';
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
      Future.delayed(const Duration(milliseconds: 100), () {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatProvider);
    final messages = chatState.messages;
    final isStreaming = chatState.isStreaming;
    final activeTools = chatState.activeTools;
    final connectionState = ref.watch(connectionStateProvider);

    // Auto-scroll when new messages arrive
    ref.listen(chatProvider, (prev, next) {
      if (prev?.messages.length != next.messages.length || next.isStreaming) {
        _scrollToBottom();
      }
    });

    return Scaffold(
      backgroundColor: MonstruoTheme.background,
      appBar: _buildAppBar(context, connectionState),
      body: Column(
        children: [
          // Active tools bar
          if (activeTools.isNotEmpty)
            ToolActivityBar(tools: activeTools),

          // Messages list
          Expanded(
            child: messages.isEmpty
                ? _buildEmptyState()
                : _buildMessageList(messages, isStreaming),
          ),

          // Input bar
          ChatInput(
            onSend: (text) {
              ref.read(chatProvider.notifier).sendMessage(text);
            },
            isStreaming: isStreaming,
          ),
        ],
      ),
    );
  }

  PreferredSizeWidget _buildAppBar(
    BuildContext context,
    AsyncValue<KernelConnectionState> connectionState,
  ) {
    return AppBar(
      backgroundColor: MonstruoTheme.background,
      title: Row(
        children: [
          // Monstruo avatar with connection indicator
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              gradient: MonstruoTheme.agentGradient,
              borderRadius: BorderRadius.circular(MonstruoTheme.radiusMd),
            ),
            child: const Center(
              child: Text(
                'M',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                  fontSize: 18,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'El Monstruo',
                style: TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w600,
                  color: MonstruoTheme.onBackground,
                ),
              ),
              connectionState.when(
                data: (state) => Text(
                  state == KernelConnectionState.connected
                      ? 'Kernel conectado'
                      : 'Desconectado',
                  style: TextStyle(
                    fontSize: 12,
                    color: state == KernelConnectionState.connected
                        ? MonstruoTheme.success
                        : MonstruoTheme.onSurfaceDim,
                  ),
                ),
                loading: () => const Text(
                  'Conectando...',
                  style: TextStyle(
                    fontSize: 12,
                    color: MonstruoTheme.warning,
                  ),
                ),
                error: (_, __) => const Text(
                  'Error',
                  style: TextStyle(
                    fontSize: 12,
                    color: MonstruoTheme.error,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.add_circle_outline, color: MonstruoTheme.onSurfaceDim),
          onPressed: () {
            ref.read(chatProvider.notifier).newThread();
          },
          tooltip: 'Nueva conversación',
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(MonstruoTheme.spacingXl),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Monstruo logo
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                gradient: MonstruoTheme.agentGradient,
                borderRadius: BorderRadius.circular(MonstruoTheme.radiusXl),
              ),
              child: const Center(
                child: Text(
                  'M',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w700,
                    fontSize: 40,
                  ),
                ),
              ),
            ),
            const SizedBox(height: MonstruoTheme.spacingLg),
            const Text(
              'El Monstruo',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.w700,
                color: MonstruoTheme.onBackground,
              ),
            ),
            const SizedBox(height: MonstruoTheme.spacingSm),
            const Text(
              'Tu agente IA soberano',
              style: TextStyle(
                fontSize: 16,
                color: MonstruoTheme.onSurfaceDim,
              ),
            ),
            const SizedBox(height: MonstruoTheme.spacingXl),
            // Quick action chips
            Wrap(
              spacing: MonstruoTheme.spacingSm,
              runSpacing: MonstruoTheme.spacingSm,
              alignment: WrapAlignment.center,
              children: [
                _QuickAction(
                  label: 'Estado del kernel',
                  icon: Icons.monitor_heart_outlined,
                  onTap: () => ref.read(chatProvider.notifier).sendMessage(
                    '¿Cuál es el estado actual del kernel?',
                  ),
                ),
                _QuickAction(
                  label: 'Estado del Embrión',
                  icon: Icons.psychology_outlined,
                  onTap: () => ref.read(chatProvider.notifier).sendMessage(
                    '¿Qué ha hecho el Embrión hoy?',
                  ),
                ),
                _QuickAction(
                  label: 'Buscar en web',
                  icon: Icons.language,
                  onTap: () => ref.read(chatProvider.notifier).sendMessage(
                    'Investiga las últimas noticias de IA de hoy',
                  ),
                ),
                _QuickAction(
                  label: 'Ejecutar código',
                  icon: Icons.terminal,
                  onTap: () => ref.read(chatProvider.notifier).sendMessage(
                    'Ejecuta un script de Python que muestre la fecha y hora actual',
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMessageList(List<ChatMessage> messages, bool isStreaming) {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.symmetric(
        horizontal: MonstruoTheme.spacingMd,
        vertical: MonstruoTheme.spacingSm,
      ),
      itemCount: messages.length + (isStreaming ? 1 : 0),
      itemBuilder: (context, index) {
        if (index == messages.length && isStreaming) {
          return const TypingIndicator();
        }
        return MessageBubble(
          message: messages[index],
          isLast: index == messages.length - 1,
        );
      },
    );
  }
}

class _QuickAction extends StatelessWidget {
  const _QuickAction({
    required this.label,
    required this.icon,
    required this.onTap,
  });

  final String label;
  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: MonstruoTheme.surfaceVariant,
      borderRadius: BorderRadius.circular(MonstruoTheme.radiusFull),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(MonstruoTheme.radiusFull),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 16, color: MonstruoTheme.primary),
              const SizedBox(width: 8),
              Text(
                label,
                style: const TextStyle(
                  fontSize: 13,
                  color: MonstruoTheme.onSurface,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
