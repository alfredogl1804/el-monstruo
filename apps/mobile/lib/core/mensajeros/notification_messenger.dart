import 'dart:async';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:logging/logging.dart';

final _log = Logger('NotificationService');

/// Notification Service - handles push notifications via Firebase
class NotificationService {
  NotificationService._();
  static final instance = NotificationService._();

  String? _fcmToken;
  String? get fcmToken => _fcmToken;

  final _messageController = StreamController<RemoteMessage>.broadcast();
  Stream<RemoteMessage> get onMessage => _messageController.stream;

  Future<void> initialize() async {
    try {
      final messaging = FirebaseMessaging.instance;
      
      // Request permission
      final settings = await messaging.requestPermission(
        alert: true,
        badge: true,
        sound: true,
      );
      _log.info('Notification permission: ${settings.authorizationStatus}');

      // Get FCM token
      _fcmToken = await messaging.getToken();
      _log.info('FCM Token: $_fcmToken');

      // Listen for foreground messages
      FirebaseMessaging.onMessage.listen((message) {
        _log.info('Foreground message: ${message.notification?.title}');
        _messageController.add(message);
      });

      // Handle token refresh
      messaging.onTokenRefresh.listen((token) {
        _fcmToken = token;
        _log.info('FCM Token refreshed');
      });
    } catch (e) {
      _log.warning('Failed to initialize notifications: $e');
    }
  }

  Future<void> showLocalNotification({
    required String title,
    required String body,
  }) async {
    // TODO: Implement local notifications when flutter_local_notifications is added
    _log.info('Local notification: $title - $body');
  }

  void dispose() {
    _messageController.close();
  }
}
