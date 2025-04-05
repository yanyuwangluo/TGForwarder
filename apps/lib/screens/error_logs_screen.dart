import 'package:flutter/material.dart';
import '../models/error_log.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'package:intl/intl.dart';

class ErrorLogsScreen extends StatefulWidget {
  const ErrorLogsScreen({super.key});

  @override
  State<ErrorLogsScreen> createState() => _ErrorLogsScreenState();
}

class _ErrorLogsScreenState extends State<ErrorLogsScreen> {
  List<ErrorLog> _errorLogs = [];
  bool _isLoading = true;
  ApiService? _apiService;
  int _currentPage = 1;
  int _totalPages = 1;
  final int _itemsPerPage = 20;
  
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
      _loadErrorLogs();
    } else {
      setState(() {
        _isLoading = false;
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('请先在设置中配置服务器地址')),
        );
      }
    }
  }
  
  Future<void> _loadErrorLogs({int page = 1}) async {
    if (_apiService == null) return;
    
    setState(() {
      _isLoading = true;
    });
    
    try {
      final result = await _apiService!.getErrorLogs(page: page, itemsPerPage: _itemsPerPage);
      
      setState(() {
        _errorLogs = result.logs;
        _currentPage = page;
        _totalPages = result.totalPages;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('加载错误日志失败：$e')),
        );
      }
    }
  }
  
  void _goToPage(int page) {
    if (page < 1 || page > _totalPages) return;
    _loadErrorLogs(page: page);
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('转发错误日志'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : () => _loadErrorLogs(page: _currentPage),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                Expanded(
                  child: _errorLogs.isEmpty
                      ? const Center(
                          child: Text(
                            '暂无错误日志',
                            style: TextStyle(fontSize: 16, color: Colors.grey),
                          ),
                        )
                      : ListView.builder(
                          itemCount: _errorLogs.length,
                          itemBuilder: (context, index) {
                            final errorLog = _errorLogs[index];
                            return Card(
                              margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              child: ListTile(
                                title: Text(
                                  errorLog.errorTitle,
                                  style: const TextStyle(fontWeight: FontWeight.bold),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                subtitle: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      '源: ${errorLog.sourceTitle} → 目标: ${errorLog.destTitle}',
                                      style: const TextStyle(fontSize: 12),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      errorLog.errorDetails,
                                      maxLines: 2,
                                      overflow: TextOverflow.ellipsis,
                                      style: const TextStyle(fontSize: 12, color: Colors.red),
                                    ),
                                  ],
                                ),
                                trailing: Text(
                                  DateFormat('yyyy-MM-dd HH:mm').format(errorLog.timestamp),
                                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                                ),
                                isThreeLine: true,
                              ),
                            );
                          },
                        ),
                ),
                if (_totalPages > 1)
                  Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        IconButton(
                          icon: const Icon(Icons.chevron_left),
                          onPressed: _currentPage > 1 ? () => _goToPage(_currentPage - 1) : null,
                        ),
                        Text('$_currentPage / $_totalPages'),
                        IconButton(
                          icon: const Icon(Icons.chevron_right),
                          onPressed: _currentPage < _totalPages ? () => _goToPage(_currentPage + 1) : null,
                        ),
                      ],
                    ),
                  ),
              ],
            ),
    );
  }
} 