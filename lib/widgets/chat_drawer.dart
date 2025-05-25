import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

/// ------------------------------------------------------------------
/// Model
/// ------------------------------------------------------------------
class Message {
  final String text;
  final String sender; // "You" or "Agent"
  final DateTime time;

  Message({required this.text, required this.sender, required this.time});
}

/// ------------------------------------------------------------------
/// Chat drawer / page widget
/// ------------------------------------------------------------------
class ChatDrawer extends StatefulWidget {
  /// Called after every *successful* command that might change tasks
  /// (e.g. /add, /sync, /plan) so parent UI can refresh providers.
  final VoidCallback? onCommandSent;
  const ChatDrawer({super.key, this.onCommandSent});

  @override
  State<ChatDrawer> createState() => _ChatDrawerState();
}

class _ChatDrawerState extends State<ChatDrawer> {
  final _messages = <Message>[];
  final _controller = TextEditingController();
  final _scrollController = ScrollController();
  bool _sending = false;

  // ----------------------- Networking ------------------------------ //
  static const _apiRoot = 'http://127.0.0.1:5000';

  Future<void> _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add(Message(text: text, sender: 'You', time: DateTime.now()));
      _sending = true;
    });
    _controller.clear();
    _jump();

    // -------- main /agent/chat call -------- //
    final resp = await http.post(
      Uri.parse('$_apiRoot/agent/chat'),
      headers: const {'Content-Type': 'application/json'},
      body: jsonEncode({'message': text}),
    );

    final reply = jsonDecode(resp.body)['content'] ?? '[No response]';
    setState(() {
      _messages.add(Message(text: reply, sender: 'Agent', time: DateTime.now()));
      _sending = false;
    });
    _jump();

    // trigger provider refresh for task-changing commands
    if (text.startsWith('/add') ||
        text.startsWith('/sync') ||
        text.startsWith('/plan')) {
      widget.onCommandSent?.call();
    }

    // -------- optional /summary helper -------- //
    if (text.toLowerCase() == '/summary') {
      final sum = await http.get(Uri.parse('$_apiRoot/summary'));
      final s = jsonDecode(sum.body);
      final md = '''
**Done**: ${s['done'].join(', ')}
**Next**: ${s['next'].join(', ')}
**Ideas**: ${s['ideas'].join(', ')}
**Insight**: ${s['insight']}
''';
      setState(() => _messages.add(
          Message(text: md, sender: 'Agent', time: DateTime.now())));
      _jump();
    }
  }

  void _jump() => WidgetsBinding.instance.addPostFrameCallback((_) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent + 72,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      });

  // ----------------------- UI -------------------------------------- //
  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: SafeArea(
        child: Column(
          children: [
            const Padding(
              padding: EdgeInsets.all(8),
              child: Text('AI Agent Chat', style: TextStyle(fontSize: 18)),
            ),
            const Divider(),
            Expanded(
              child: ListView.builder(
                controller: _scrollController,
                padding: const EdgeInsets.all(12),
                itemCount: _messages.length,
                itemBuilder: (ctx, i) {
                  final m = _messages[i], mine = m.sender == 'You';
                  return Align(
                    alignment:
                        mine ? Alignment.centerRight : Alignment.centerLeft,
                    child: Container(
                      margin: const EdgeInsets.symmetric(vertical: 4),
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: mine
                            ? Colors.blue.shade100
                            : Colors.green.shade100,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: SelectableText(m.text),
                    ),
                  );
                },
              ),
            ),
            const Divider(height: 1),
            Padding(
              padding: const EdgeInsets.all(8),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      onSubmitted: (_) => _sendMessage(),
                      decoration: const InputDecoration(
                        hintText: 'Type a command or message…',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton(
                    onPressed: _sending ? null : _sendMessage,
                    child: _sending
                        ? const SizedBox(
                            width: 18,
                            height: 18,
                            child:
                                CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Text('Send'),
                  )
                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}
