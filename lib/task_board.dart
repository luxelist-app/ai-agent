import 'package:aiagent/chat_screen.dart';
import 'package:aiagent/task.dart';
import 'package:flutter/material.dart';
import 'package:flutter_boardview/board_item.dart';
import 'package:flutter_boardview/board_list.dart';
import 'package:flutter_boardview/boardview.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class TasksBoardPage extends ConsumerWidget {
  const TasksBoardPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tasks = ref.watch(tasksProvider);
    Map<String, List<Task>> cols = {
      'backlog': [], 'progress': [], 'done': []
    };
    for (var t in tasks) {
      cols[t.status]!.add(t);
    }

    return Scaffold(
      drawer: ChatScreen(),   // embeds your existing chat widget
      appBar: AppBar(title: Text('Task Board')),
      body: BoardView(
        lists: cols.entries.map((e) {
          return BoardList(
            header: [Text(e.key.toUpperCase())],
            items: e.value.map((t) => BoardItem(
              item: ListTile(title: Text(t.title)),
            )).toList(),
          );
        }).toList(),
      ),
    );
  }
}
