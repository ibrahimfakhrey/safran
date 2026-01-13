# 📱 Flutter Push Notifications Integration Guide

## Overview
The IPI backend now supports Firebase Cloud Messaging (FCM) push notifications. This guide explains how to integrate notifications in the Flutter mobile app.

---

## 🔧 **Setup Requirements**

### **1. Add Dependencies** (`pubspec.yaml`)
```yaml
dependencies:
  firebase_core: ^2.24.2
  firebase_messaging: ^14.7.10
  flutter_local_notifications: ^16.3.0
```

### **2. Firebase Configuration**
- Add `google-services.json` to `android/app/`
- Add `GoogleService-Info.plist` to `ios/Runner/`

---

## 📋 **Implementation Steps**

### **Step 1: Initialize Firebase** (`main.dart`)
```dart
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

// Background message handler (must be top-level)
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print('Background message: ${message.messageId}');
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  
  // Set up background handler
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  
  runApp(MyApp());
}
```

### **Step 2: Create Notification Service** (`lib/services/notification_service.dart`)
```dart
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _localNotifications = FlutterLocalNotificationsPlugin();
  
  String? _fcmToken;
  String? get fcmToken => _fcmToken;

  Future<void> initialize() async {
    // Request permission
    NotificationSettings settings = await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );
    
    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      print('Notification permission granted');
      
      // Get FCM token
      _fcmToken = await _messaging.getToken();
      print('FCM Token: $_fcmToken');
      
      // Listen for token refresh
      _messaging.onTokenRefresh.listen((newToken) {
        _fcmToken = newToken;
        _sendTokenToBackend(newToken);
      });
      
      // Initialize local notifications
      await _initLocalNotifications();
      
      // Handle foreground messages
      FirebaseMessaging.onMessage.listen(_handleForegroundMessage);
      
      // Handle notification tap (app in background)
      FirebaseMessaging.onMessageOpenedApp.listen(_handleNotificationTap);
    }
  }

  Future<void> _initLocalNotifications() async {
    const AndroidInitializationSettings androidSettings = 
        AndroidInitializationSettings('@mipmap/ic_launcher');
    
    const DarwinInitializationSettings iosSettings = 
        DarwinInitializationSettings(
          requestAlertPermission: true,
          requestBadgePermission: true,
          requestSoundPermission: true,
        );
    
    const InitializationSettings initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );
    
    await _localNotifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: (response) {
        _handleLocalNotificationTap(response.payload);
      },
    );
    
    // Create Android notification channel
    const AndroidNotificationChannel channel = AndroidNotificationChannel(
      'ipi_notifications',
      'IPI Notifications',
      description: 'Notifications from IPI Investment Platform',
      importance: Importance.high,
    );
    
    await _localNotifications
        .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
        ?.createNotificationChannel(channel);
  }

  void _handleForegroundMessage(RemoteMessage message) {
    print('Foreground message: ${message.notification?.title}');
    
    // Show local notification
    _showLocalNotification(
      title: message.notification?.title ?? 'IPI',
      body: message.notification?.body ?? '',
      payload: jsonEncode(message.data),
    );
  }

  void _handleNotificationTap(RemoteMessage message) {
    print('Notification tapped: ${message.data}');
    _navigateToScreen(message.data);
  }

  void _handleLocalNotificationTap(String? payload) {
    if (payload != null) {
      Map<String, dynamic> data = jsonDecode(payload);
      _navigateToScreen(data);
    }
  }

  void _navigateToScreen(Map<String, dynamic> data) {
    String? screen = data['screen'];
    String? type = data['type'];
    
    // Navigate based on notification type
    switch (screen) {
      case 'investments':
        // Navigate to investments screen
        break;
      case 'wallet':
        // Navigate to wallet screen
        break;
      case 'requests':
        // Navigate to investment requests screen
        break;
      case 'dashboard':
        // Navigate to dashboard
        break;
      case 'market':
        // Navigate to market
        break;
      case 'profile':
        // Navigate to profile
        break;
    }
  }

  Future<void> _showLocalNotification({
    required String title,
    required String body,
    String? payload,
  }) async {
    const AndroidNotificationDetails androidDetails = AndroidNotificationDetails(
      'ipi_notifications',
      'IPI Notifications',
      channelDescription: 'Notifications from IPI Investment Platform',
      importance: Importance.high,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
    );
    
    const DarwinNotificationDetails iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );
    
    const NotificationDetails details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );
    
    await _localNotifications.show(
      DateTime.now().millisecondsSinceEpoch ~/ 1000,
      title,
      body,
      details,
      payload: payload,
    );
  }

  // Send FCM token to backend
  Future<void> sendTokenToBackend(String accessToken) async {
    if (_fcmToken == null) return;
    await _sendTokenToBackend(_fcmToken!, accessToken: accessToken);
  }

  Future<void> _sendTokenToBackend(String token, {String? accessToken}) async {
    if (accessToken == null) return;
    
    try {
      final response = await http.post(
        Uri.parse('https://your-api-url.com/api/v1/user/update-fcm-token'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
        body: jsonEncode({'fcm_token': token}),
      );
      
      if (response.statusCode == 200) {
        print('FCM token sent to backend successfully');
      } else {
        print('Failed to send FCM token: ${response.body}');
      }
    } catch (e) {
      print('Error sending FCM token: $e');
    }
  }
}
```

### **Step 3: Call After Login** (`auth_provider.dart` or login logic)
```dart
// After successful login
final notificationService = NotificationService();
await notificationService.initialize();
await notificationService.sendTokenToBackend(accessToken);
```

---

## 📡 **Backend API Endpoint**

### **Update FCM Token**
```
POST /api/v1/user/update-fcm-token
Headers: Authorization: Bearer <access_token>
Body: { "fcm_token": "device_token_here" }
Response: { "success": true, "message": "تم تحديث رمز الإشعارات بنجاح" }
```

---

## 🔔 **Notification Types (Deep Linking)**

| **Type** | **Screen** | **Description** |
|----------|-----------|-----------------|
| `investment_approved` | investments | Investment approved |
| `investment_rejected` | requests | Investment rejected |
| `investment_under_review` | requests | Under review |
| `documents_missing` | requests | Missing documents |
| `withdrawal_approved` | wallet | Withdrawal approved |
| `withdrawal_rejected` | wallet | Withdrawal rejected |
| `rental_income` | wallet | Monthly rent added |
| `car_income` | wallet | Car income added |
| `rewards_payout` | wallet | Rewards transferred |
| `referral_reward` | wallet | Referral commission |
| `welcome` | dashboard | Welcome message |
| `password_changed` | profile | Password changed |
| `asset_closed` | investments | Asset closed |
| `new_asset` | market | New investment opportunity |

---

## 📱 **Android Configuration** (`android/app/src/main/AndroidManifest.xml`)
```xml
<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
<uses-permission android:name="android.permission.VIBRATE"/>

<application>
    <!-- FCM Default Channel -->
    <meta-data
        android:name="com.google.firebase.messaging.default_notification_channel_id"
        android:value="ipi_notifications" />
</application>
```

---

## 🍎 **iOS Configuration** (`ios/Runner/Info.plist`)
```xml
<key>UIBackgroundModes</key>
<array>
    <string>fetch</string>
    <string>remote-notification</string>
</array>
```

---

## ✅ **Checklist**

- [ ] Add Firebase dependencies to `pubspec.yaml`
- [ ] Add `google-services.json` (Android)
- [ ] Add `GoogleService-Info.plist` (iOS)
- [ ] Create `notification_service.dart`
- [ ] Initialize Firebase in `main.dart`
- [ ] Call notification service after login
- [ ] Send FCM token to backend
- [ ] Handle foreground notifications
- [ ] Handle notification tap (deep linking)
- [ ] Update AndroidManifest.xml permissions
- [ ] Update Info.plist for iOS
- [ ] Test on real devices

---

## 🧪 **Testing**

1. Run app on device (not emulator for iOS)
2. Allow notification permissions
3. Check logs for "FCM Token: ..."
4. Trigger an event from admin panel
5. Verify notification appears
