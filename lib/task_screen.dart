import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class TaskScreen extends StatefulWidget {
  const TaskScreen({super.key});

  @override
  State<TaskScreen> createState() => _TaskScreenState();
}

class _TaskScreenState extends State<TaskScreen> {
  List<dynamic> _tasks = [];
  double? _estimatedMinutes;

  Future<void> _fetchTasks() async {
    final taskRes = await http.get(Uri.parse('http://127.0.0.1:5000/tasks'));
    final estimateRes = await http.get(Uri.parse('http://127.0.0.1:5000/tasks/estimate'));

    setState(() {
      _tasks = jsonDecode(taskRes.body);
      _estimatedMinutes = jsonDecode(estimateRes.body)['estimated_minutes']?.toDouble();
    });
  }

  Future<void> _startTask(String id) async {
    await http.post(
      Uri.parse("http://127.0.0.1:5000/tasks/start"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "id": id,
        "mood": 3,   // Replace with real input later
        "energy": 3,
        "focus": 3,
      }),
    );
    _fetchTasks();
  }

  Future<void> _completeTask(String id) async {
    await http.post(
      Uri.parse("http://127.0.0.1:5000/tasks/complete"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"id": id}),
    );
    _fetchTasks();
  }

  @override
  void initState() {
    super.initState();
    _fetchTasks();
  }

  Widget _buildActionButtons(String id, String status) {
    if (status == "todo") {
      return ElevatedButton(
        onPressed: () => _startTask(id),
        child: const Text("Start"),
      );
    } else if (status == "in_progress") {
      return ElevatedButton(
        onPressed: () => _completeTask(id),
        child: const Text("Complete"),
      );
    } else {
      return const Icon(Icons.check_circle, color: Colors.green);
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: _tasks.length,
      padding: const EdgeInsets.all(12),
      itemBuilder: (context, index) {
        final task = _tasks[index];
        final id = task["id"] ?? task["title"]; // fallback ID
        final status = task["status"];
        final est = status == "todo" ? _estimatedMinutes?.toStringAsFixed(1) : null;

        return Card(
          child: ListTile(
            title: Text(task['title'] ?? 'No title'),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("Status: $status"),
                if (est != null) Text("Est: $est min"),
                if (task["duration"] != null)
                  Text("Took: ${task['duration'].toStringAsFixed(1)} min"),
              ],
            ),
            trailing: _buildActionButtons(id, status),
          ),
        );
      },
    );
  }
}
