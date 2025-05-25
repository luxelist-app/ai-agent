import 'package:aiagent/models/task.dart';
import 'package:aiagent/widgets/chat_drawer.dart';
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
    final lanes = ['backlog', 'progress', 'done'];

    return Scaffold(
      drawer: ChatDrawer(
        onCommandSent: () {
          ref.read(tasksProvider.notifier).refresh();
        },
      ),
      appBar: AppBar(title: const Text('Task Board')),
      body: BoardView(
        lists: lanes.map((lane) {
          final col = tasks.where((t) => t.status == lane).toList();
          return BoardList(
            headerBackgroundColor: Colors.blueGrey.shade800,
            header: [Text(lane.toUpperCase(),
                style: const TextStyle(color: Colors.white))],
            items: col
                .map((t) => BoardItem(
                      item: ListTile(
                        title: Text(t.title),
                        subtitle: Text(t.ghNumber != null
                            ? '#${t.ghNumber}'
                            : 'local'),
                      ),
                    ))
                .toList(),
          );
        }).toList(),
      ),
    );
  }
}
