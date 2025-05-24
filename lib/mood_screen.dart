import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class MoodScreen extends StatefulWidget {
  const MoodScreen({super.key});

  @override
  State<MoodScreen> createState() => _MoodScreenState();
}

class _MoodScreenState extends State<MoodScreen> {
  double _mood = 3;
  double _energy = 3;
  double _focus = 3;
  final TextEditingController _notes = TextEditingController();
  bool _submitted = false;

  Future<void> _submitMood() async {
    final res = await http.post(
      Uri.parse("http://127.0.0.1:5000/mood"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "mood": _mood.round(),
        "energy": _energy.round(),
        "focus": _focus.round(),
        "notes": _notes.text.trim(),
      }),
    );
    if (res.statusCode == 200) {
      setState(() {
        _submitted = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: _submitted
          ? const Center(child: Text("✅ Mood logged!"))
          : Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text("Mood (😞 → 😃)"),
                Slider(value: _mood, min: 1, max: 5, divisions: 4, label: _mood.round().toString(), onChanged: (v) => setState(() => _mood = v)),
                const Text("Energy (😴 → ⚡)"),
                Slider(value: _energy, min: 1, max: 5, divisions: 4, label: _energy.round().toString(), onChanged: (v) => setState(() => _energy = v)),
                const Text("Focus (😵 → 🎯)"),
                Slider(value: _focus, min: 1, max: 5, divisions: 4, label: _focus.round().toString(), onChanged: (v) => setState(() => _focus = v)),
                const SizedBox(height: 12),
                TextField(
                  controller: _notes,
                  decoration: const InputDecoration(
                    hintText: "Any notes?",
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 2,
                ),
                const SizedBox(height: 12),
                ElevatedButton(onPressed: _submitMood, child: const Text("Save Mood"))
              ],
            ),
    );
  }
}
