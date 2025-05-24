import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class SummaryScreen extends StatefulWidget {
  const SummaryScreen({super.key});

  @override
  State<SummaryScreen> createState() => _SummaryScreenState();
}

class _SummaryScreenState extends State<SummaryScreen> {
  Map<String, dynamic>? _summary;

  Future<void> _fetchSummary() async {
    final response = await http.get(Uri.parse('http://127.0.0.1:5000/summary'));
    setState(() {
      _summary = jsonDecode(response.body)['summary'];
    });
  }

  @override
  void initState() {
    super.initState();
    _fetchSummary();
  }

  @override
  Widget build(BuildContext context) {
    if (_summary == null) {
      return const Center(child: CircularProgressIndicator());
    }

    return Padding(
      padding: const EdgeInsets.all(16),
      child: ListView(
        children: [
          Text("✅ Done", style: Theme.of(context).textTheme.titleLarge),
          ..._summary!['done'].map<Widget>((t) => Text("- $t")).toList(),
          const SizedBox(height: 16),
          Text("📌 Next", style: Theme.of(context).textTheme.titleLarge),
          ..._summary!['next'].map<Widget>((t) => Text("- $t")).toList(),
          const SizedBox(height: 16),
          Text("💡 Ideas", style: Theme.of(context).textTheme.titleLarge),
          ..._summary!['ideas'].map<Widget>((t) => Text("- $t")).toList(),
          const SizedBox(height: 16),
          Text("📊 Insight: ${_summary!['insight']}",
              style: Theme.of(context).textTheme.bodyLarge),
        ],
      ),
    );
  }
}
