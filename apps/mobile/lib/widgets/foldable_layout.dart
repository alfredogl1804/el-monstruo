import 'package:flutter/material.dart';

/// Foldable Layout Widget for dual-screen devices (OPPO N5)
/// Detects fold/hinge and splits UI accordingly
class FoldableLayout extends StatelessWidget {
  const FoldableLayout({
    super.key,
    required this.leftPanel,
    required this.rightPanel,
    this.singlePanel,
  });

  final Widget leftPanel;
  final Widget rightPanel;
  final Widget? singlePanel;

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    final isWideScreen = size.width > 600;

    if (!isWideScreen) {
      return singlePanel ?? leftPanel;
    }

    // Dual panel layout for foldable/wide screens
    return Row(
      children: [
        Expanded(child: leftPanel),
        Container(
          width: 1,
          color: Colors.grey[800],
        ),
        Expanded(child: rightPanel),
      ],
    );
  }
}
