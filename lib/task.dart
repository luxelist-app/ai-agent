import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;

final tasksProvider = StateNotifierProvider<TaskNotifier, List<Task>>((ref) {
  return TaskNotifier()..load();
});

class Task {
  final int id;
  final String title;
  final String status;
  Task.fromJson(Map<String, dynamic> j)
      : id = j['id'], title = j['title'], status = j['status'];
}

class TaskNotifier extends StateNotifier<List<Task>> {
  TaskNotifier() : super([]);
  Future<void> load() async {
    final res = await http.get(Uri.parse('http://127.0.0.1:5000/tasks'));
    state = (jsonDecode(res.body) as List).map((j) => Task.fromJson(j)).toList();
  }
}
