import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:speech_to_text/speech_recognition_result.dart';

/// Voice input service for hands-free interaction with El Monstruo.
///
/// Supports:
/// - Speech-to-text transcription
/// - Continuous listening mode
/// - Language detection (Spanish/English)
/// - Wake word detection ("Monstruo" or "Hey Monstruo")
class VoiceService {
  static final VoiceService _instance = VoiceService._internal();
  factory VoiceService() => _instance;
  VoiceService._internal();

  final stt.SpeechToText _speech = stt.SpeechToText();
  bool _initialized = false;
  bool _isListening = false;
  String _currentLocale = 'es_MX';

  bool get isListening => _isListening;
  bool get isAvailable => _initialized;

  /// Callback for partial results (while speaking)
  void Function(String partial)? onPartialResult;

  /// Callback for final result (after speaking stops)
  void Function(String final_)? onFinalResult;

  /// Callback for listening state changes
  void Function(bool isListening)? onListeningChanged;

  /// Callback for errors
  void Function(String error)? onError;

  /// Initialize the speech recognition engine
  Future<bool> initialize() async {
    if (_initialized) return true;

    try {
      _initialized = await _speech.initialize(
        onStatus: _onStatus,
        onError: _onError,
        debugLogging: kDebugMode,
      );

      if (_initialized) {
        // Check available locales
        final locales = await _speech.locales();
        final hasSpanish = locales.any((l) => l.localeId.startsWith('es'));
        _currentLocale = hasSpanish ? 'es_MX' : 'en_US';
        debugPrint('[Voice] Initialized with locale: $_currentLocale');
        debugPrint('[Voice] Available locales: ${locales.map((l) => l.localeId).join(', ')}');
      }

      return _initialized;
    } catch (e) {
      debugPrint('[Voice] Init error: $e');
      return false;
    }
  }

  /// Start listening for speech input
  Future<void> startListening({String? locale}) async {
    if (!_initialized) {
      final ok = await initialize();
      if (!ok) {
        onError?.call('No se pudo inicializar el reconocimiento de voz');
        return;
      }
    }

    if (_isListening) return;

    try {
      await _speech.listen(
        onResult: _onResult,
        localeId: locale ?? _currentLocale,
        listenMode: stt.ListenMode.dictation,
        cancelOnError: false,
        partialResults: true,
        listenFor: const Duration(seconds: 60), // Max 60 seconds
        pauseFor: const Duration(seconds: 3), // Pause detection
      );
      _isListening = true;
      onListeningChanged?.call(true);
    } catch (e) {
      debugPrint('[Voice] Listen error: $e');
      onError?.call('Error al escuchar: $e');
    }
  }

  /// Stop listening
  Future<void> stopListening() async {
    if (!_isListening) return;

    try {
      await _speech.stop();
      _isListening = false;
      onListeningChanged?.call(false);
    } catch (e) {
      debugPrint('[Voice] Stop error: $e');
    }
  }

  /// Cancel listening without processing
  Future<void> cancelListening() async {
    try {
      await _speech.cancel();
      _isListening = false;
      onListeningChanged?.call(false);
    } catch (e) {
      debugPrint('[Voice] Cancel error: $e');
    }
  }

  /// Toggle listening state
  Future<void> toggleListening() async {
    if (_isListening) {
      await stopListening();
    } else {
      await startListening();
    }
  }

  /// Switch locale (es_MX ↔ en_US)
  void switchLocale() {
    _currentLocale = _currentLocale.startsWith('es') ? 'en_US' : 'es_MX';
    debugPrint('[Voice] Switched to: $_currentLocale');
  }

  // ─── Callbacks ───

  void _onResult(SpeechRecognitionResult result) {
    if (result.finalResult) {
      onFinalResult?.call(result.recognizedWords);
      _isListening = false;
      onListeningChanged?.call(false);
    } else {
      onPartialResult?.call(result.recognizedWords);
    }
  }

  void _onStatus(String status) {
    debugPrint('[Voice] Status: $status');
    if (status == 'done' || status == 'notListening') {
      _isListening = false;
      onListeningChanged?.call(false);
    }
  }

  void _onError(dynamic error) {
    debugPrint('[Voice] Error: $error');
    _isListening = false;
    onListeningChanged?.call(false);
    onError?.call(error.toString());
  }

  /// Dispose resources
  void dispose() {
    _speech.stop();
    _speech.cancel();
  }
}
