import 'dart:async';
import 'dart:math';

import 'package:flutter/material.dart';

import '../../../theme/monstruo_theme.dart';

/// Premium thinking indicator that shows:
/// 1. Animated orbs while waiting for first token
/// 2. Model name (e.g., "GPT-5.5") when available
/// 3. Elapsed timer counting up
/// 4. Phase text (e.g., "Pensando con GPT-5.5")
class ThinkingIndicator extends StatefulWidget {
  const ThinkingIndicator({
    super.key,
    this.model,
    this.intent,
    this.startTime,
    this.isThinking = true,
  });

  final String? model;
  final String? intent;
  final DateTime? startTime;
  final bool isThinking;

  @override
  State<ThinkingIndicator> createState() => _ThinkingIndicatorState();
}

class _ThinkingIndicatorState extends State<ThinkingIndicator>
    with TickerProviderStateMixin {
  late AnimationController _orbController;
  late AnimationController _pulseController;
  Timer? _elapsedTimer;
  Duration _elapsed = Duration.zero;

  @override
  void initState() {
    super.initState();
    _orbController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1800),
    )..repeat();

    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);

    _startTimer();
  }

  void _startTimer() {
    _elapsedTimer?.cancel();
    final start = widget.startTime ?? DateTime.now();
    _elapsedTimer = Timer.periodic(const Duration(milliseconds: 100), (_) {
      if (mounted) {
        setState(() {
          _elapsed = DateTime.now().difference(start);
        });
      }
    });
  }

  @override
  void didUpdateWidget(ThinkingIndicator oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.startTime != oldWidget.startTime && widget.startTime != null) {
      _startTimer();
    }
  }

  @override
  void dispose() {
    _orbController.dispose();
    _pulseController.dispose();
    _elapsedTimer?.cancel();
    super.dispose();
  }

  String get _elapsedText {
    final seconds = _elapsed.inMilliseconds / 1000.0;
    return '${seconds.toStringAsFixed(1)}s';
  }

  String get _phaseText {
    final badge = _modelBadge;
    if (badge.isNotEmpty) {
      return 'Pensando con $badge';
    }
    return 'Pensando...';
  }

  String get _modelBadge {
    final model = widget.model ?? '';
    if (model.contains('gpt-5.5')) return 'GPT-5.5';
    if (model.contains('gpt-5')) return 'GPT-5';
    if (model.contains('gpt-4')) return 'GPT-4';
    if (model.contains('claude')) return 'Claude';
    if (model.contains('gemini')) return 'Gemini';
    if (model.contains('grok')) return 'Grok';
    if (model.isNotEmpty) {
      return model.split('/').last.split('-').take(3).join('-');
    }
    return '';
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _pulseController,
      builder: (context, child) {
        return Container(
          margin: const EdgeInsets.only(left: 16, right: 48, top: 4, bottom: 4),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: MonstruoTheme.surface.withValues(
              alpha: 0.6 + _pulseController.value * 0.15,
            ),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: MonstruoTheme.primary.withValues(
                alpha: 0.1 + _pulseController.value * 0.1,
              ),
              width: 0.5,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Animated orbs
              _AnimatedOrbs(controller: _orbController),
              const SizedBox(width: 12),

              // Phase text + elapsed time
              Flexible(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          _phaseText,
                          style: const TextStyle(
                            color: MonstruoTheme.onSurfaceDim,
                            fontSize: 13,
                            fontWeight: FontWeight.w500,
                            letterSpacing: -0.2,
                          ),
                        ),
                        if (_modelBadge.isNotEmpty) ...[
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: MonstruoTheme.primary.withValues(alpha: 0.15),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              _modelBadge,
                              style: TextStyle(
                                color: MonstruoTheme.primary,
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                letterSpacing: 0.3,
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 2),
                    Text(
                      _elapsedText,
                      style: TextStyle(
                        color: MonstruoTheme.onSurfaceDim.withValues(alpha: 0.6),
                        fontSize: 11,
                        fontFeatures: const [FontFeature.tabularFigures()],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

/// Three animated orbs with staggered wave animation
class _AnimatedOrbs extends StatelessWidget {
  const _AnimatedOrbs({required this.controller});

  final AnimationController controller;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 32,
      height: 16,
      child: AnimatedBuilder(
        animation: controller,
        builder: (context, _) {
          return Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: List.generate(3, (i) {
              final offset = i * 0.2;
              final t = (controller.value + offset) % 1.0;
              final scale = 0.5 + 0.5 * sin(t * pi);
              final opacity = 0.4 + 0.6 * sin(t * pi);
              return Transform.scale(
                scale: scale,
                child: Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: MonstruoTheme.primary.withValues(alpha: opacity),
                    boxShadow: [
                      BoxShadow(
                        color: MonstruoTheme.primary.withValues(alpha: opacity * 0.4),
                        blurRadius: 6,
                        spreadRadius: 1,
                      ),
                    ],
                  ),
                ),
              );
            }),
          );
        },
      ),
    );
  }
}
