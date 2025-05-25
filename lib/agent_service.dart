// lib/services/agent_service.dart
import 'dart:convert';
import 'dart:io';

class AgentService {
  static final AgentService _ = AgentService._internal();
  factory AgentService() => _;
  AgentService._internal();

  final _client = HttpClient();

  Future<String> chat(String message, {Map<String, dynamic>? ctx}) async {
    final request = await _client.postUrl(
      Uri.parse('http://127.0.0.1:5000/agent/chat'),
    );
    // …encode body, await response…
    final response = await request.close();
    return jsonDecode(await response.transform(utf8.decoder).join())['content'];
  }
}
