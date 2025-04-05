import 'package:shared_preferences/shared_preferences.dart';

class AppConfig {
  // 默认API基础地址
  static String _apiBaseUrl = 'http://localhost:5000/api';
  
  // 获取配置的API基础地址
  static Future<String> getApiBaseUrl() async {
    final prefs = await SharedPreferences.getInstance();
    final storedUrl = prefs.getString('api_base_url');
    return storedUrl ?? _apiBaseUrl;
  }
  
  // 设置新的API基础地址
  static Future<void> setApiBaseUrl(String url) async {
    _apiBaseUrl = url;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('api_base_url', url);
  }
  
  static const String appVersion = '1.0.0';
  
  // API路径
  static const String channelsPath = '/channels';
  static const String rulesPath = '/rules';
  static const String messagesPath = '/messages';
  static const String settingsPath = '/settings';
  static const String servicePath = '/service';
} 