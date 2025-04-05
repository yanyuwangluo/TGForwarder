import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config.dart';
import '../models/channel.dart';
import '../models/forward_rule.dart';
import '../models/message.dart';
import '../models/error_log.dart';
import '../services/auth_service.dart';

class ApiService {
  final String baseUrl;
  final http.Client _client = http.Client();
  final AuthService _authService = AuthService();
  String? _secretKey;
  
  ApiService({required this.baseUrl}) {
    _loadSecretKey();
  }
  
  Future<void> _loadSecretKey() async {
    _secretKey = await _authService.getSecretKey();
  }
  
  Map<String, String> get _headers {
    final headers = {'Content-Type': 'application/json'};
    if (_secretKey != null && _secretKey!.isNotEmpty) {
      headers['Authorization'] = 'Bearer $_secretKey';
    }
    return headers;
  }
  
  Future<List<Channel>> getChannels() async {
    final url = Uri.parse('$baseUrl/channels');
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
      Uri.parse('$baseUrl${AppConfig.rulesPath}'),
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
      Uri.parse('$baseUrl${AppConfig.messagesPath}?page=$page'),
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
    final url = Uri.parse('$baseUrl/status');
    final response = await _client.get(url, headers: _headers);
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('获取状态失败，状态码：${response.statusCode}');
    }
  }
  
  Future<bool> startService() async {
    final url = Uri.parse('$baseUrl/start');
    final response = await _client.post(url, headers: _headers);
    
    if (response.statusCode == 200) {
      return true;
    } else {
      throw Exception('启动服务失败，状态码：${response.statusCode}');
    }
  }
  
  Future<bool> stopService() async {
    final url = Uri.parse('$baseUrl/stop');
    final response = await _client.post(url, headers: _headers);
    
    if (response.statusCode == 200) {
      return true;
    } else {
      throw Exception('停止服务失败，状态码：${response.statusCode}');
    }
  }
  
  Future<Map<String, dynamic>> getSettings() async {
    final url = Uri.parse('$baseUrl/settings');
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
    final url = Uri.parse('$baseUrl/settings');
    
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
    final url = Uri.parse('$baseUrl/error_logs?page=$page&per_page=$itemsPerPage');
    final response = await _client.get(url, headers: _headers);
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return ErrorLogResult.fromJson(data);
    } else {
      throw Exception('获取错误日志失败，状态码：${response.statusCode}');
    }
  }
}