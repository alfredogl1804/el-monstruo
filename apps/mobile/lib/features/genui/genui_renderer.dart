import 'package:flutter/material.dart';

/// Placeholder GenUI Renderer
/// TODO: Implement full A2UI rendering when genui package is available
class GenUIRenderer extends StatelessWidget {
  const GenUIRenderer({super.key, required this.payload});
  final Map<String, dynamic>? payload;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.purple.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.auto_awesome, size: 16, color: Colors.purple),
              const SizedBox(width: 8),
              const Text(
                'Generative UI Component',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: Colors.purple,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            payload?.toString() ?? 'No payload',
            style: TextStyle(
              fontSize: 13,
              color: Colors.grey[400],
              fontFamily: 'monospace',
            ),
          ),
        ],
      ),
    );
  }
}
