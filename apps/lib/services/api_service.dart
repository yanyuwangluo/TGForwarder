import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config.dart';
import '../models/channel.dart';
import '../models/forward_rule.dart';
import '../models/message.dart';
import '../models/error_log.dart';
import '../services/auth_service.dart';

class ApiService {
  String? _baseUrl;
  final http.Client _client = http.Client();
  final AuthService _authService = AuthService();
  String? _secretKey;
  
  // 单例模式
  static final ApiService _instance = ApiService._internal();
  
  factory ApiService() {
    return _instance;
  }
  
  ApiService._internal() {
    _init();
  }
  
  Future<void> _init() async {
    await _loadSecretKey();
    await _loadBaseUrl();
  }
  
  Future<void> _loadSecretKey() async {
    _secretKey = await _authService.getSecretKey();
  }
  
  Future<void> _loadBaseUrl() async {
    _baseUrl = await AppConfig.getApiBaseUrl();
  }
  
  // 确保在每次API调用前检查基础URL
  Future<String> get baseUrl async {
    if (_baseUrl == null) {
      await _loadBaseUrl();
    }
    return _baseUrl!;
  }
  
  Map<String, String> get _headers {
    final headers = {'Content-Type': 'application/json'};
    if (_secretKey != null && _secretKey!.isNotEmpty) {
      headers['Authorization'] = 'Bearer $_secretKey';
    }
    return headers;
  }
  
  Future<List<Channel>> getChannels() async {
    final url = Uri.parse('${await baseUrl}/channels');
    final response = await _client.get(url, headers: _headers);
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body) as List;
      return data.map((item) => Channel.fromJson(item)).toList();
    } else {
      throw Exception('获取频道列表失败，状态码：${response.statusCode}');
    }
  }
  
  Future<List<ForwardRule>> getForwardRules() async {
    final response = await http.get(
      Uri.parse('${await baseUrl}${AppConfig.rulesPath}'),
      headers: _headers
    );
    
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => ForwardRule.fromJson(json)).toList();
    } else {
      throw Exception('获取转发规则失败: ${response.statusCode}');
    }
  }
  
  Future<MessagePagination> getMessages({int page = 1}) async {
    final response = await http.get(
      Uri.parse('${await baseUrl}${AppConfig.messagesPath}?page=$page'),
      headers: _headers
    );
    
    if (response.statusCode == 200) {
      final Map<String, dynamic> data = json.decode(response.body);
      return MessagePagination.fromJson(data);
    } else {
      throw Exception('获取消息历史失败: ${response.statusCode}');
    }
  }
  
  Future<Map<String, dynamic>> getStatus() async {
    final url = Uri.parse('${await baseUrl}/status');
    final response = await _client.get(url, headers: _headers);
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('获取状态失败，状态码：${response.statusCode}');
    }
  }
  
  Future<bool> startService() async {
    final url = Uri.parse('${await baseUrl}/start');
    final response = await _client.post(url, headers: _headers);
    
    if (response.statusCode == 200) {
      return true;
    } else {
      throw Exception('启动服务失败，状态码：${response.statusCode}');
    }
  }
  
  Future<bool> stopService() async {
    final url = Uri.parse('${await baseUrl}/stop');
    final response = await _client.post(url, headers: _headers);
    
    if (response.statusCode == 200) {
      return true;
    } else {
      throw Exception('停止服务失败，状态码：${response.statusCode}');
    }
  }
  
  Future<Map<String, dynamic>> getSettings() async {
    final url = Uri.parse('${await baseUrl}/settings');
    final response = await _client.get(url, headers: _headers);
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('获取设置失败，状态码：${response.statusCode}');
    }
  }
  
  Future<bool> updateSettings({
    required int apiId,
    required String apiHash,
    required String phone,
    required String serverUrl,
    String? secretKey,
  }) async {
    // 更新API基础地址
    if (serverUrl.isNotEmpty && serverUrl != await baseUrl) {
      await AppConfig.setApiBaseUrl(serverUrl);
      await _loadBaseUrl();
    }
    
    final url = Uri.parse('${await baseUrl}/settings');
    
    // 如果提供了新的secretKey，更新本地存储
    if (secretKey != null && secretKey.isNotEmpty) {
      await _authService.saveSecretKey(secretKey);
      _secretKey = secretKey;
    }
    
    final response = await _client.post(
      url,
      headers: _headers,
      body: json.encode({
        'api_id': apiId,
        'api_hash': apiHash,
        'phone': phone,
      }),
    );
    
    if (response.statusCode == 200) {
      return true;
    } else {
      throw Exception('更新设置失败，状态码：${response.statusCode}');
    }
  }
  
  Future<ErrorLogResult> getErrorLogs({int page = 1, int itemsPerPage = 20}) async {
    final url = Uri.parse('${await baseUrl}/error_logs?page=$page&per_page=$itemsPerPage');
    final response = await _client.get(url, headers: _headers);
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return ErrorLogResult.fromJson(data);
    } else {
      throw Exception('获取错误日志失败，状态码：${response.statusCode}');
    }
  }
}