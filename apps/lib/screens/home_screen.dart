import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _isServiceRunning = false;
  bool _isLoading = true;
  bool _isActionInProgress = false;
  String _statusMessage = '';
  ApiService? _apiService;
  
  @override
  void initState() {
    super.initState();
    _initApiService();
  }
  
  Future<void> _initApiService() async {
    final authService = AuthService();
    final serverUrl = await authService.getServerUrl();
    
    if (serverUrl != null && serverUrl.isNotEmpty) {
      _apiService = ApiService(baseUrl: serverUrl);
      _checkServiceStatus();
    } else {
      setState(() {
        _statusMessage = '请先在设置中配置服务器地址';
        _isLoading = false;
      });
    }
  }
  
  Future<void> _checkServiceStatus() async {
    if (_apiService == null) return;
    
    setState(() {
      _isLoading = true;
      _statusMessage = '正在获取服务状态...';
    });
    
    try {
      final status = await _apiService!.getStatus();
      setState(() {
        _isServiceRunning = status['running'] ?? false;
        _statusMessage = _isServiceRunning 
            ? '服务运行中 (${status['uptime'] ?? '未知'})'
            : '服务已停止';
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isServiceRunning = false;
        _statusMessage = '获取状态失败: $e';
        _isLoading = false;
      });
    }
  }
  
  Future<void> _toggleService() async {
    if (_apiService == null) return;
    
    setState(() {
      _isActionInProgress = true;
      _statusMessage = _isServiceRunning ? '正在停止服务...' : '正在启动服务...';
    });
    
    try {
      bool success;
      if (_isServiceRunning) {
        success = await _apiService!.stopService();
      } else {
        success = await _apiService!.startService();
      }
      
      if (success) {
        await _checkServiceStatus();
      } else {
        setState(() {
          _statusMessage = '操作失败';
          _isActionInProgress = false;
        });
      }
    } catch (e) {
      setState(() {
        _statusMessage = '操作失败: $e';
        _isActionInProgress = false;
      });
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('TG转发器'),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Card(
                elevation: 4,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      const Icon(
                        Icons.send,
                        size: 64,
                        color: Colors.blue,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        '服务状态',
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      const SizedBox(height: 8),
                      if (_isLoading)
                        const CircularProgressIndicator()
                      else
                        Text(
                          _statusMessage,
                          style: TextStyle(
                            color: _isServiceRunning ? Colors.green : Colors.red,
                            fontWeight: FontWeight.bold,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      const SizedBox(height: 24),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: _isServiceRunning ? Colors.red : Colors.green,
                            foregroundColor: Colors.white,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                          ),
                          onPressed: _isLoading || _isActionInProgress || _apiService == null
                              ? null
                              : _toggleService,
                          child: Text(
                            _isServiceRunning ? '停止服务' : '启动服务',
                            style: const TextStyle(fontSize: 16),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 32),
              _buildFeatureGrid(context),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildFeatureGrid(BuildContext context) {
    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      children: [
        _buildFeatureCard(
          context,
          '频道管理',
          Icons.public,
          Colors.blue,
          '/channels',
        ),
        _buildFeatureCard(
          context,
          '转发规则',
          Icons.rule,
          Colors.orange,
          '/rules',
        ),
        _buildFeatureCard(
          context,
          '错误日志',
          Icons.error_outline,
          Colors.red,
          '/error_logs',
        ),
        _buildFeatureCard(
          context,
          '设置',
          Icons.settings,
          Colors.grey,
          '/settings',
        ),
      ],
    );
  }
  
  Widget _buildFeatureCard(
    BuildContext context,
    String title,
    IconData icon,
    Color color,
    String route,
  ) {
    return Card(
      elevation: 2,
      child: InkWell(
        onTap: () {
          Navigator.pushNamed(context, route);
        },
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 48,
                color: color,
              ),
              const SizedBox(height: 12),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
} 