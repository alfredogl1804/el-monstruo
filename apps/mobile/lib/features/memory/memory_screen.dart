import 'dart:async';

import 'package:flutter/material.dart';

import '../../theme/monstruo_theme.dart';
import '../../services/kernel_service.dart';

/// Memory Palace viewer — browse the Monstruo's sovereign memory.
///
/// Shows:
/// - Memory categories (episodic, semantic, procedural)
/// - Search across all memories
/// - Recent memories timeline
/// - Memory stats (total, by type, storage used)
class MemoryScreen extends StatefulWidget {
  const MemoryScreen({super.key});

  @override
  State<MemoryScreen> createState() => _MemoryScreenState();
}

class _MemoryScreenState extends State<MemoryScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _searchController = TextEditingController();
  bool _loading = true;
  Map<String, dynamic>? _memoryStats;
  List<Map<String, dynamic>> _searchResults = [];
  bool _searching = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadStats();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadStats() async {
    try {
      final stats = await KernelService().getMemoryStats();
      if (mounted) {
        setState(() {
          _memoryStats = stats;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  Future<void> _search(String query) async {
    if (query.trim().isEmpty) {
      setState(() => _searchResults = []);
      return;
    }
    setState(() => _searching = true);
    try {
      final results = await KernelService().searchMemory(query);
      if (mounted) {
        setState(() {
          _searchResults = List<Map<String, dynamic>>.from(results);
          _searching = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _searching = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: MonstruoTheme.background,
      appBar: AppBar(
        backgroundColor: MonstruoTheme.surface,
        title: const Row(
          children: [
            Icon(Icons.psychology, size: 20, color: Color(0xFF7C4DFF)),
            SizedBox(width: 8),
            Text(
              'Memoria Soberana',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: MonstruoTheme.onBackground,
              ),
            ),
          ],
        ),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: MonstruoTheme.primary,
          labelColor: MonstruoTheme.primary,
          unselectedLabelColor: MonstruoTheme.onSurfaceDim,
          labelStyle: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
          tabs: const [
            Tab(text: 'Buscar'),
            Tab(text: 'Recientes'),
            Tab(text: 'Stats'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildSearchTab(),
          _buildRecentTab(),
          _buildStatsTab(),
        ],
      ),
    );
  }

  Widget _buildSearchTab() {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: TextField(
            controller: _searchController,
            style: const TextStyle(fontSize: 14, color: MonstruoTheme.onBackground),
            decoration: InputDecoration(
              hintText: 'Buscar en la memoria del Monstruo...',
              hintStyle: TextStyle(color: MonstruoTheme.onSurfaceDim.withValues(alpha: 0.5)),
              prefixIcon: const Icon(Icons.search, color: MonstruoTheme.onSurfaceDim, size: 20),
              filled: true,
              fillColor: MonstruoTheme.surfaceVariant,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
            ),
            onSubmitted: _search,
            textInputAction: TextInputAction.search,
          ),
        ),
        Expanded(
          child: _searchResults.isEmpty
              ? Center(
                  child: Text(
                    'Busca conversaciones, decisiones y conocimiento',
                    style: TextStyle(fontSize: 14, color: MonstruoTheme.onSurfaceDim),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: _searchResults.length,
                  itemBuilder: (context, index) => _MemoryCard(memory: _searchResults[index]),
                ),
        ),
      ],
    );
  }

  Widget _buildRecentTab() {
    return const Center(child: Text('Cargando...', style: TextStyle(color: MonstruoTheme.onSurfaceDim)));
  }

  Widget _buildStatsTab() {
    if (_loading) {
      return const Center(child: CircularProgressIndicator(color: MonstruoTheme.primary));
    }
    final stats = _memoryStats ?? {};
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _StatCard(icon: Icons.memory, label: 'Total', value: '${stats['total'] ?? 0}', color: MonstruoTheme.primary),
        const SizedBox(height: 12),
        _StatCard(icon: Icons.auto_stories, label: 'Episodicas', value: '${stats['episodic'] ?? 0}', color: const Color(0xFF7C4DFF)),
        const SizedBox(height: 12),
        _StatCard(icon: Icons.schema, label: 'Semanticas', value: '${stats['semantic'] ?? 0}', color: MonstruoTheme.warning),
        const SizedBox(height: 12),
        _StatCard(icon: Icons.build, label: 'Procedurales', value: '${stats['procedural'] ?? 0}', color: MonstruoTheme.success),
      ],
    );
  }
}

class _StatCard extends StatelessWidget {
  const _StatCard({required this.icon, required this.label, required this.value, required this.color});
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: MonstruoTheme.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: MonstruoTheme.divider, width: 0.5),
      ),
      child: Row(
        children: [
          Container(
            width: 44, height: 44,
            decoration: BoxDecoration(color: color.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(10)),
            child: Icon(icon, size: 22, color: color),
          ),
          const SizedBox(width: 16),
          Expanded(child: Text(label, style: const TextStyle(fontSize: 14, color: MonstruoTheme.onSurface))),
          Text(value, style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: color)),
        ],
      ),
    );
  }
}

class _MemoryCard extends StatelessWidget {
  const _MemoryCard({required this.memory});
  final Map<String, dynamic> memory;

  @override
  Widget build(BuildContext context) {
    final content = memory['content'] as String? ?? '';
    final type = memory['type'] as String? ?? 'unknown';
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: MonstruoTheme.surface,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(type.toUpperCase(), style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: MonstruoTheme.primary)),
          const SizedBox(height: 6),
          Text(content, style: const TextStyle(fontSize: 13, color: MonstruoTheme.onSurface, height: 1.4), maxLines: 4, overflow: TextOverflow.ellipsis),
        ],
      ),
    );
  }
}
