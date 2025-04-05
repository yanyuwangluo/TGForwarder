import 'package:flutter/material.dart';
import 'screens/home_screen.dart';
import 'screens/channels_screen.dart';
import 'screens/rules_screen.dart';
import 'screens/messages_screen.dart';
import 'screens/settings_screen.dart';
import 'screens/error_logs_screen.dart';
import 'services/api_service.dart';

void main() {
  // 确保Flutter初始化完成
  WidgetsFlutterBinding.ensureInitialized();
  
  // 初始化ApiService (将在首次访问时自动加载配置)
  ApiService();
  
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TG转发器',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const HomeScreen(),
        '/channels': (context) => const ChannelsScreen(),
        '/rules': (context) => const RulesScreen(),
        '/messages': (context) => const MessagesScreen(),
        '/settings': (context) => const SettingsScreen(),
        '/error_logs': (context) => const ErrorLogsScreen(),
      },
    );
  }
} 