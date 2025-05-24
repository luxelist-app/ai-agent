import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class IdeaScreen extends StatefulWidget {
  const IdeaScreen({super.key});

  @override
  State<IdeaScreen> createState() => _IdeaScreenState();
}

class _IdeaScreenState extends State<IdeaScreen> {
  List<dynamic> _ideas = [];

  Future<void> _fetchIdeas() async {
    final response = await http.get(Uri.parse('http://127.0.0.1:5000/ideas'));
    setState(() {
      _ideas = jsonDecode(response.body);
    });
  }

  @override
  void initState() {
    super.initState();
    _fetchIdeas();
  }

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: _ideas.length,
      padding: const EdgeInsets.all(12),
      itemBuilder: (context, index) {
        final idea = _ideas[index];
        return Card(
          child: ListTile(
            title: Text(idea['description'] ?? 'No description'),
            subtitle: Text("Status: ${idea['status']}"),
            trailing: Text(idea['timestamp'].toString().split('T').first),
          ),
        );
      },
    );
  }
}
