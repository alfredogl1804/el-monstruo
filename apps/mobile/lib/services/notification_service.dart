import 'dart:convert';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:http/http.dart' as http;

import '../core/config.dart';

/// Handles push notifications for async task completion.
///
/// When the user sends a task to the Monstruo and closes the app,
/// the kernel sends a push notification when the task completes.
///
/// Uses Firebase Cloud Messaging (FCM) for both iOS and Android.
class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();

  String? _fcmToken;
  bool _initialized = false;

  String? get fcmToken => _fcmToken;

  /// Initialize notification service
  Future<void> initialize() async {
    if (_initialized) return;

    // Initialize Firebase
    await Firebase.initializeApp();

    // Initialize local notifications
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );
    const initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _localNotifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );

    // Request permission
    final messaging = FirebaseMessaging.instance;
    final settings = await messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
    );

    if (settings.authorizationStatus == AuthorizationStatus.authorized ||
        settings.authorizationStatus == AuthorizationStatus.provisional) {
      // Get FCM token
      _fcmToken = await messaging.getToken();
      debugPrint('[Notifications] FCM Token: $_fcmToken');

      // Register token with gateway
      if (_fcmToken != null) {
        await _registerTokenWithGateway(_fcmToken!);
      }

      // Listen for token refresh
      messaging.onTokenRefresh.listen((newToken) {
        _fcmToken = newToken;
        _registerTokenWithGateway(newToken);
      });

      // Handle foreground messages
      FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

      // Handle background/terminated messages
      FirebaseMessaging.onMessageOpenedApp.listen(_handleMessageOpenedApp);

      // Check for initial message (app opened from notification)
      final initialMessage = await messaging.getInitialMessage();
      if (initialMessage != null) {
        _handleMessageOpenedApp(initialMessage);
      }
    }

    _initialized = true;
  }

  /// Register FCM token with the AG-UI Gateway
  Future<void> _registerTokenWithGateway(String token) async {
    try {
      final url = Uri.parse('${AppConfig.gatewayUrl}/api/push/register');
      await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'token': token,
          'platform': Platform.isIOS ? 'ios' : 'android',
          'device_id': null, // TODO: Get unique device ID
        }),
      );
      debugPrint('[Notifications] Token registered with gateway');
    } catch (e) {
      debugPrint('[Notifications] Failed to register token: $e');
    }
  }

  /// Handle foreground messages — show local notification
  void _handleForegroundMessage(RemoteMessage message) {
    debugPrint('[Notifications] Foreground message: ${message.notification?.title}');

    final notification = message.notification;
    if (notification == null) return;

    _showLocalNotification(
      title: notification.title ?? 'El Monstruo',
      body: notification.body ?? '',
      payload: jsonEncode(message.data),
    );
  }

  /// Handle when user taps notification to open app
  void _handleMessageOpenedApp(RemoteMessage message) {
    debugPrint('[Notifications] Opened from notification: ${message.data}');

    final data = message.data;
    final taskId = data['task_id'];
    final threadId = data['thread_id'];

    // TODO: Navigate to the specific task/thread in the app
    // This will be handled by the router
  }

  /// Handle local notification tap
  void _onNotificationTapped(NotificationResponse response) {
    debugPrint('[Notifications] Local notification tapped: ${response.payload}');

    if (response.payload != null) {
      try {
        final data = jsonDecode(response.payload!) as Map<String, dynamic>;
        // TODO: Navigate based on payload
      } catch (_) {}
    }
  }

  /// Show a local notification
  Future<void> _showLocalNotification({
    required String title,
    required String body,
    String? payload,
  }) async {
    const androidDetails = AndroidNotificationDetails(
      'monstruo_tasks',
      'Tareas del Monstruo',
      channelDescription: 'Notificaciones de tareas completadas por El Monstruo',
      importance: Importance.high,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
      color: Color(0xFF00E5FF),
    );

    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    const details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _localNotifications.show(
      DateTime.now().millisecondsSinceEpoch.remainder(100000),
      title,
      body,
      details,
      payload: payload,
    );
  }

  /// Show a task completion notification
  Future<void> showTaskComplete({
    required String taskTitle,
    String? summary,
    String? threadId,
  }) async {
    await _showLocalNotification(
      title: 'Tarea completada',
      body: summary ?? taskTitle,
      payload: jsonEncode({
        'type': 'task_complete',
        'task_title': taskTitle,
        'thread_id': threadId,
      }),
    );
  }

  /// Show an embrion activity notification
  Future<void> showEmbrionActivity({
    required String activity,
    String? details,
  }) async {
    await _showLocalNotification(
      title: 'Embrión — Actividad Autónoma',
      body: activity,
      payload: jsonEncode({
        'type': 'embrion_activity',
        'activity': activity,
        'details': details,
      }),
    );
  }

  /// Show a kernel alert notification
  Future<void> showKernelAlert({
    required String title,
    required String message,
    String severity = 'info',
  }) async {
    await _showLocalNotification(
      title: 'Monstruo: $title',
      body: message,
      payload: jsonEncode({
        'type': 'kernel_alert',
        'severity': severity,
      }),
    );
  }
}

/// Color class for notification (Android)
class Color {
  final int value;
  const Color(this.value);
}
