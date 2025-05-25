import 'package:aiagent/chat_screen.dart';
import 'package:aiagent/task_board.dart';
import 'package:aiagent/task_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'idea_screen.dart';
import 'models/task.dart';
import 'mood_screen.dart';
import 'summary_screen.dart';
import 'widgets/chat_drawer.dart';

class MainTabView extends ConsumerWidget {
  const MainTabView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // callback to refresh tasks after slash-commands
    void refreshTasks() =>
        ref.read(tasksProvider.notifier).refresh();

    return DefaultTabController(
      length: 6,
      child: Scaffold(
        drawer: ChatDrawer(onCommandSent: refreshTasks), // ← slide-in chat
        appBar: AppBar(
          title: const Text('AI Dev Agent'),
          leading: Builder(
            builder: (ctx) => IconButton(
              icon: const Icon(Icons.menu),
              onPressed: () => Scaffold.of(ctx).openDrawer(),
            ),
          ),
          bottom: const TabBar(
            isScrollable: false,
            tabs: [
              Tab(text: 'Chat'),
              Tab(text: 'Tasks'),
              Tab(text: 'Task Board'),
              Tab(text: 'Ideas'),
              Tab(text: 'Summary'),
              Tab(text: 'Mood'),
            ],
          ),
        ),
        body: TabBarView(
          physics: const NeverScrollableScrollPhysics(),
          children: [
            const ChatScreen(),       
            const TaskScreen(),         // full chat screen
            const TasksBoardPage(),        // Kanban board
            const IdeaScreen(),             // later: list/grid of Obsidian ideas
            const SummaryScreen(),           // /summary endpoint view
            const MoodScreen(),              // mood tracker UI
          ],
        ),
      ),
    );
  }
}
