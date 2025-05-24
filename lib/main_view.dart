import 'package:flutter/material.dart';
import 'chat_screen.dart';
import 'task_screen.dart';
import 'idea_screen.dart';
import 'summary_screen.dart';
import 'mood_screen.dart';

class MainTabView extends StatelessWidget {
  const MainTabView({super.key});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 5,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('AI Dev Agent'),
          bottom: const TabBar(
            tabs: [
              Tab(text: 'Chat'),
              Tab(text: 'Tasks'),
              Tab(text: 'Ideas'),
              Tab(text: 'Summary'),
              Tab(text: 'Mood'),
            ],
          ),
        ),
        body: const TabBarView(
          children: [
            ChatScreen(),
            TaskScreen(),
            IdeaScreen(),
            SummaryScreen(),
            MoodScreen(),
          ],
        ),
      ),
    );
  }
}