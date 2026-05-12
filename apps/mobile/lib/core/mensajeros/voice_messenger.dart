import 'dart:async';
import 'package:logging/logging.dart';

final _log = Logger('VoiceService');

/// Voice Service - placeholder for speech-to-text
/// TODO: Add speech_to_text package when voice input is enabled (Phase 2)
class VoiceService {
  VoiceService._();
  static final instance = VoiceService._();

  bool _isListening = false;
  bool get isListening => _isListening;

  final _textController = StreamController<String>.broadcast();
  Stream<String> get onResult => _textController.stream;

  Future<bool> initialize() async {
    _log.info('Voice service initialized (disabled in Phase 1)');
    return false;
  }

  Future<void> startListening() async {
    _log.warning('Voice input not available in Phase 1');
  }

  Future<void> stopListening() async {
    _isListening = false;
  }

  void dispose() {
    _textController.close();
  }
}
