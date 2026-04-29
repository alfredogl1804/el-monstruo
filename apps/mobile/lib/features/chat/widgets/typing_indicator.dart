import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../../../theme/monstruo_theme.dart';

class TypingIndicator extends StatelessWidget {
  const TypingIndicator({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(
        left: 36 + 8, // avatar width + gap
        bottom: MonstruoTheme.spacingSm,
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: MonstruoTheme.surface,
              borderRadius: BorderRadius.circular(MonstruoTheme.radiusMd),
              border: Border.all(
                color: MonstruoTheme.divider,
                width: 0.5,
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: List.generate(3, (index) {
                return Padding(
                  padding: EdgeInsets.only(right: index < 2 ? 4 : 0),
                  child: Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      color: MonstruoTheme.primary.withValues(alpha: 0.6),
                      shape: BoxShape.circle,
                    ),
                  )
                      .animate(
                        onPlay: (controller) => controller.repeat(),
                      )
                      .scaleXY(
                        begin: 0.6,
                        end: 1.0,
                        duration: 600.ms,
                        delay: (index * 200).ms,
                        curve: Curves.easeInOut,
                      )
                      .then()
                      .scaleXY(
                        begin: 1.0,
                        end: 0.6,
                        duration: 600.ms,
                        curve: Curves.easeInOut,
                      ),
                );
              }),
            ),
          ),
        ],
      ),
    );
  }
}
