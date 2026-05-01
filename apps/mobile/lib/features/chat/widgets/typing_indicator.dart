import 'dart:async';
import 'dart:math';

import 'package:flutter/material.dart';

import '../../../theme/monstruo_theme.dart';

/// Structured thinking step from the kernel pipeline.
class ThinkingStep {
  ThinkingStep({
    required this.id,
    required this.label,
    required this.icon,
    required this.status,
    DateTime? startTime,
  }) : startTime = startTime ?? DateTime.now();

  final String id;
  final String label;
  final String icon;
  final String status; // 'in_progress' or 'completed'
  final DateTime startTime;

  bool get isCompleted => status == 'completed';
  bool get isInProgress => status == 'in_progress';

  ThinkingStep copyWith({String? status, String? label}) {
    return ThinkingStep(
      id: id,
      label: label ?? this.label,
      icon: icon,
      status: status ?? this.status,
      startTime: startTime,
    );
  }
}

/// Premium thinking indicator with single-line crossfade and expandable history.
///
/// Design (Gemini 3 Pro recommendation — Sprint 43):
///   - Single active step visible at a time with smooth crossfade
///   - Tap to expand/collapse history of completed steps
///   - Prevents flickering with fast 1.56s TTFT
///   - Model badge + elapsed timer
///   - Animated orbs spinner
class ThinkingIndicator extends StatefulWidget {
  const ThinkingIndicator({
    super.key,
    this.model,
    this.intent,
    this.startTime,
    this.isThinking = true,
    this.steps = const [],
  });

  final String? model;
  final String? intent;
  final DateTime? startTime;
  final bool isThinking;
  final List<ThinkingStep> steps;

  @override
  State<ThinkingIndicator> createState() => _ThinkingIndicatorState();
}

class _ThinkingIndicatorState extends State<ThinkingIndicator>
    with TickerProviderStateMixin {
  late AnimationController _orbController;
  late AnimationController _pulseController;
  Timer? _elapsedTimer;
  Duration _elapsed = Duration.zero;
  bool _isExpanded = false;

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

  /// Get the current (most recent) step label, or fallback to legacy behavior.
  String get _currentLabel {
    if (widget.steps.isNotEmpty) {
      return widget.steps.last.label;
    }
    // Legacy fallback: no step events, use model name
    final badge = _modelBadge;
    if (badge.isNotEmpty) {
      return 'Pensando con $badge';
    }
    return 'Pensando...';
  }

  /// Completed steps (all except the last one if it's in_progress).
  List<ThinkingStep> get _completedSteps {
    if (widget.steps.length <= 1) return [];
    return widget.steps
        .sublist(0, widget.steps.length - 1)
        .where((s) => s.isCompleted)
        .toList();
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

  IconData _iconForStep(String iconName) {
    switch (iconName) {
      case 'brain':
        return Icons.psychology;
      case 'memory':
        return Icons.folder_open;
      case 'sparkles':
        return Icons.auto_awesome;
      case 'search':
        return Icons.search;
      case 'build':
        return Icons.build;
      // Sprint 48: Task Planner icons
      case 'code':
        return Icons.terminal;
      case 'file':
        return Icons.description;
      case 'deploy':
      case 'rocket':
        return Icons.rocket_launch;
      case 'globe':
      case 'web':
        return Icons.web;
      case 'scaffold':
      case 'architecture':
        return Icons.architecture;
      case 'sandbox':
      case 'cloud':
        return Icons.cloud;
      case 'plan':
        return Icons.account_tree;
      case 'check':
      case 'done':
        return Icons.check_circle;
      case 'error':
        return Icons.error_outline;
      default:
        return Icons.hourglass_empty;
    }
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
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              // ── Active step row (always visible) ──
              GestureDetector(
                onTap: _completedSteps.isNotEmpty
                    ? () => setState(() => _isExpanded = !_isExpanded)
                    : null,
                behavior: HitTestBehavior.opaque,
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Animated orbs
                    _AnimatedOrbs(controller: _orbController),
                    const SizedBox(width: 12),

                    // Single-line crossfade label
                    Flexible(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              // Smooth crossfade between step labels
                              Flexible(
                                child: AnimatedSwitcher(
                                  duration: const Duration(milliseconds: 300),
                                  transitionBuilder: (child, animation) {
                                    return FadeTransition(
                                      opacity: animation,
                                      child: SlideTransition(
                                        position: Tween<Offset>(
                                          begin: const Offset(0.0, 0.3),
                                          end: Offset.zero,
                                        ).animate(CurvedAnimation(
                                          parent: animation,
                                          curve: Curves.easeOut,
                                        )),
                                        child: child,
                                      ),
                                    );
                                  },
                                  child: Text(
                                    _currentLabel,
                                    key: ValueKey<String>(_currentLabel),
                                    style: const TextStyle(
                                      color: MonstruoTheme.onSurfaceDim,
                                      fontSize: 13,
                                      fontWeight: FontWeight.w500,
                                      letterSpacing: -0.2,
                                    ),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
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
                                    color: MonstruoTheme.primary
                                        .withValues(alpha: 0.15),
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
                          Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Text(
                                _elapsedText,
                                style: TextStyle(
                                  color: MonstruoTheme.onSurfaceDim
                                      .withValues(alpha: 0.6),
                                  fontSize: 11,
                                  fontFeatures: const [
                                    FontFeature.tabularFigures()
                                  ],
                                ),
                              ),
                              // Expand/collapse chevron (only if there are completed steps)
                              if (_completedSteps.isNotEmpty) ...[
                                const SizedBox(width: 6),
                                Icon(
                                  _isExpanded
                                      ? Icons.expand_less
                                      : Icons.expand_more,
                                  size: 14,
                                  color: MonstruoTheme.onSurfaceDim
                                      .withValues(alpha: 0.4),
                                ),
                              ],
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              // ── Expandable history of completed steps ──
              AnimatedSize(
                duration: const Duration(milliseconds: 300),
                curve: Curves.easeInOut,
                child: _isExpanded && _completedSteps.isNotEmpty
                    ? Padding(
                        padding: const EdgeInsets.only(top: 10, left: 4),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: _completedSteps.map((step) {
                            return Padding(
                              padding: const EdgeInsets.only(bottom: 6),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(
                                    Icons.check_circle_outline,
                                    size: 14,
                                    color: const Color(0xFF4CAF50)
                                        .withValues(alpha: 0.8),
                                  ),
                                  const SizedBox(width: 10),
                                  Flexible(
                                    child: Text(
                                      step.label,
                                      style: TextStyle(
                                        fontSize: 12,
                                        color: MonstruoTheme.onSurfaceDim
                                            .withValues(alpha: 0.5),
                                        letterSpacing: -0.1,
                                      ),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                            );
                          }).toList(),
                        ),
                      )
                    : const SizedBox.shrink(),
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
                        color:
                            MonstruoTheme.primary.withValues(alpha: opacity * 0.4),
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
