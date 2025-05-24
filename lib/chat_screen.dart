import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class Message {
  final String text;
  final String sender;
  final DateTime time;

  Message({required this.text, required this.sender, required this.time});
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final List<Message> _messages = [];
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _isLoading = false;

  Future<void> _sendMessage() async {
    final prompt = _controller.text.trim();
    if (prompt.isEmpty) return;

    setState(() {
      _messages.add(Message(text: prompt, sender: "You", time: DateTime.now()));
      _isLoading = true;
    });

    _controller.clear();
    _scrollToBottom();

    try {
      final response = await http.post(
        Uri.parse('http://127.0.0.1:5000/chat/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'prompt': prompt}),
      );

      final data = jsonDecode(response.body);
      final reply = data['response'] ?? '[No response]';

      setState(() {
        _messages.add(Message(
          text: reply,
          sender: "Agent",
          time: DateTime.now(),
        ));
        _isLoading = false;
      });

      _scrollToBottom();
    } catch (e) {
      setState(() {
        _messages.add(Message(
          text: '[Error: $e]',
          sender: "Agent",
          time: DateTime.now(),
        ));
        _isLoading = false;
      });
    }

    if (prompt.toLowerCase() == "/summary") {
      final summaryRes = await http.get(Uri.parse('http://127.0.0.1:5000/summary'));
      final summary = jsonDecode(summaryRes.body)['summary'];
      final text = '''
    Done: ${summary['done'].join(', ')}
    Next: ${summary['next'].join(', ')}
    Ideas: ${summary['ideas'].join(', ')}
    Insight: ${summary['insight']}
    ''';

      setState(() {
        _messages.add(Message(text: text, sender: "Agent", time: DateTime.now()));
        _isLoading = false;
      });

      _scrollToBottom();
      return;
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent + 80,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(title: const Text('AI Dev Agent')),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(12),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                final isUser = msg.sender == "You";
                return Container(
                  margin: const EdgeInsets.symmetric(vertical: 6),
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Column(
                    crossAxisAlignment:
                        isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
                    children: [
                      Container(
                        decoration: BoxDecoration(
                          color: isUser ? Colors.blue[100] : Colors.green[100],
                          borderRadius: BorderRadius.circular(12),
                        ),
                        padding: const EdgeInsets.all(10),
                        child: Text(msg.text),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        "${msg.sender} • ${msg.time.hour.toString().padLeft(2, '0')}:${msg.time.minute.toString().padLeft(2, '0')}",
                        style: const TextStyle(fontSize: 10, color: Colors.grey),
                      )
                    ],
                  ),
                );
              },
            ),
          ),
          const Divider(height: 1),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    onSubmitted: (_) => _sendMessage(),
                    decoration: const InputDecoration(
                      hintText: "Type a message...",
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: _isLoading ? null : _sendMessage,
                  child: _isLoading
                      ? const SizedBox(
                          width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Text("Send"),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}