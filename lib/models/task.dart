import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;

final tasksProvider = StateNotifierProvider<TaskNotifier, List<Task>>((ref) {
  return TaskNotifier()..load();
});

class Task {
  final int? id;
  final int? ghNumber;
  final String title;
  final String status;   // backlog | progress | done

  Task.fromJson(Map<String, dynamic> j)
      : id        = (j['id'] as num?)?.toInt(),
        ghNumber  = (j['gh_number'] as num?)?.toInt(),
        title     = j['title'] ?? '',
        status    = j['status'] ?? 'backlog';
}


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

  /// <- add this
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
