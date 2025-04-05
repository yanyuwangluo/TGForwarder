import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _formKey = GlobalKey<FormState>();
  final _serverUrlController = TextEditingController();
  final _apiIdController = TextEditingController();
  final _apiHashController = TextEditingController();
  final _phoneController = TextEditingController();
  final _secretKeyController = TextEditingController();
  bool _isLoading = false;
  bool _isLoadingSettings = false;
  late AuthService _authService;
  ApiService? _apiService;

  @override
  void initState() {
    super.initState();
    _authService = AuthService();
    _loadServerUrl();
    _loadSecretKey();
  }

  Future<void> _loadServerUrl() async {
    final serverUrl = await _authService.getServerUrl();
    if (serverUrl != null && serverUrl.isNotEmpty) {
      setState(() {
        _serverUrlController.text = serverUrl;
        _apiService = ApiService(baseUrl: serverUrl);
      });
      _loadSettings();
    }
  }
  
  Future<void> _loadSecretKey() async {
    final secretKey = await _authService.getSecretKey();
    if (secretKey != null && secretKey.isNotEmpty) {
      setState(() {
        _secretKeyController.text = secretKey;
      });
    }
  }

  Future<void> _loadSettings() async {
    if (_apiService == null) return;
    
    setState(() {
      _isLoadingSettings = true;
    });
    
    try {
      final settings = await _apiService!.getSettings();
      setState(() {
        _apiIdController.text = settings['api_id']?.toString() ?? '';
        _apiHashController.text = settings['api_hash'] ?? '';
        _phoneController.text = settings['phone'] ?? '';
        _isLoadingSettings = false;
      });
    } catch (e) {
      setState(() {
        _isLoadingSettings = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('加载设置失败: $e')),
      );
    }
  }

  Future<void> _saveSettings() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() {
      _isLoading = true;
    });
    
    try {
      // 保存服务器URL
      final serverUrl = _serverUrlController.text.trim();
      await _authService.saveServerUrl(serverUrl);
      
      // 保存密钥
      final secretKey = _secretKeyController.text.trim();
      await _authService.saveSecretKey(secretKey);
      
      // 创建API服务
      _apiService = ApiService(baseUrl: serverUrl);
      
      // 保存Telegram设置
      if (_apiIdController.text.isNotEmpty &&
          _apiHashController.text.isNotEmpty &&
          _phoneController.text.isNotEmpty) {
        await _apiService!.updateSettings(
          apiId: int.parse(_apiIdController.text.trim()),
          apiHash: _apiHashController.text.trim(),
          phone: _phoneController.text.trim(),
          serverUrl: serverUrl,
          secretKey: secretKey,
        );
      }
      
      setState(() {
        _isLoading = false;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('设置已保存')),
      );
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('保存设置失败: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('设置'),
      ),
      body: _isLoadingSettings
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '服务器设置',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _serverUrlController,
                      decoration: const InputDecoration(
                        labelText: '服务器地址',
                        border: OutlineInputBorder(),
                        hintText: 'http://localhost:5000/api',
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return '请输入服务器地址';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _secretKeyController,
                      decoration: const InputDecoration(
                        labelText: 'API密钥（Secret Key）',
                        border: OutlineInputBorder(),
                        hintText: '填写后端配置中的secret_key参数',
                      ),
                      obscureText: true,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return '请输入API密钥';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 24),
                    const Text(
                      'Telegram API 设置',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _apiIdController,
                      decoration: const InputDecoration(
                        labelText: 'API ID',
                        border: OutlineInputBorder(),
                      ),
                      keyboardType: TextInputType.number,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _apiHashController,
                      decoration: const InputDecoration(
                        labelText: 'API Hash',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _phoneController,
                      decoration: const InputDecoration(
                        labelText: '电话号码',
                        border: OutlineInputBorder(),
                        hintText: '+8613800138000',
                      ),
                    ),
                    const SizedBox(height: 32),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                        onPressed: _isLoading ? null : _saveSettings,
                        child: _isLoading
                            ? const CircularProgressIndicator()
                            : const Text('保存设置',
                                style: TextStyle(fontSize: 16)),
                      ),
                    ),
                  ],
                ),
              ),
            ),
    );
  }

  @override
  void dispose() {
    _serverUrlController.dispose();
    _apiIdController.dispose();
    _apiHashController.dispose();
    _phoneController.dispose();
    _secretKeyController.dispose();
    super.dispose();
  }
} 