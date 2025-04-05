import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  static const String _keyServerUrl = 'server_url';
  static const String _keySecretKey = 'secret_key';

  // 保存服务器URL到本地存储
  Future<void> saveServerUrl(String serverUrl) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyServerUrl, serverUrl);
  }

  // 从本地存储获取服务器URL
  Future<String?> getServerUrl() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keyServerUrl);
  }

  // 保存API密钥到本地存储
  Future<void> saveSecretKey(String secretKey) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keySecretKey, secretKey);
  }

  // 从本地存储获取API密钥
  Future<String?> getSecretKey() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_keySecretKey);
  }

  // 检查是否已设置服务器URL
  Future<bool> isServerConfigured() async {
    final serverUrl = await getServerUrl();
    return serverUrl != null && serverUrl.isNotEmpty;
  }

  // 清除所有存储的设置
  Future<void> clearSettings() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
} 