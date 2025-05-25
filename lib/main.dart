import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'main_view.dart';

void main() {
  runApp(const ProviderScope(child: AgentChatApp(),),);
}

class AgentChatApp extends StatelessWidget {
  const AgentChatApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Dev Agent',
      debugShowCheckedModeBanner: false,
      home: const MainTabView(),
    );
  }
}