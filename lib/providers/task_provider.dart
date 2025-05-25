import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import '../models/task.dart';

final tasksProvider =
    StateNotifierProvider<TaskNotifier, List<Task>>((ref) => TaskNotifier());

class TaskNotifier extends StateNotifier<List<Task>> {
  TaskNotifier() : super([]);
  static const _endpoint = 'http://127.0.0.1:5000/tasks';

  Future<void> load() async {
    final res = await http.get(Uri.parse(_endpoint));
    final list = (jsonDecode(res.body) as List)
        .map((e) => Task.fromJson(e))
        .toList();
    state = list;
  }

  Future<void> refresh() => load();

  Future<void> addTask(String title,
      {String status = 'backlog'}) async {
    final res = await http.post(
      Uri.parse('$_endpoint/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'title': title, 'status': status}),
    );
    final newTask = Task.fromJson(jsonDecode(res.body));
    state = [...state, newTask];
  }
}
