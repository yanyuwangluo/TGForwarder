import 'package:flutter/material.dart';
import '../models/channel.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

class ChannelsScreen extends StatefulWidget {
  const ChannelsScreen({super.key});

  @override
  State<ChannelsScreen> createState() => _ChannelsScreenState();
}

class _ChannelsScreenState extends State<ChannelsScreen> with SingleTickerProviderStateMixin {
  List<Channel> _sources = [];
  List<Channel> _destinations = [];
  bool _isLoading = true;
  late TabController _tabController;
  ApiService? _apiService;
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _initApiService();
  }
  
  Future<void> _initApiService() async {
    final authService = AuthService();
    final serverUrl = await authService.getServerUrl();
    
    if (serverUrl != null && serverUrl.isNotEmpty) {
      _apiService = ApiService(baseUrl: serverUrl);
      _loadChannels();
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
  
  Future<void> _loadChannels() async {
    if (_apiService == null) return;
    
    try {
      final channels = await _apiService!.getChannels();
      
      setState(() {
        _sources = channels.where((c) => c.isSource).toList();
        _destinations = channels.where((c) => c.isDestination).toList();
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('加载频道失败：$e')),
        );
      }
    }
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('频道管理'),
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(text: '监听源 (${_sources.length})'),
            Tab(text: '目标频道 (${_destinations.length})'),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : _loadChannels,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                _buildChannelList(_sources, true),
                _buildChannelList(_destinations, false),
              ],
            ),
    );
  }
  
  Widget _buildChannelList(List<Channel> channels, bool isSource) {
    if (channels.isEmpty) {
      return Center(
        child: Text(
          isSource ? '暂无监听源' : '暂无目标频道', 
          style: const TextStyle(fontSize: 16, color: Colors.grey),
        ),
      );
    }
    
    return ListView.builder(
      itemCount: channels.length,
      itemBuilder: (context, index) {
        final channel = channels[index];
        return Card(
          margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: isSource ? Colors.blue : Colors.green,
              child: Text(
                channel.channelTitle.isNotEmpty 
                    ? channel.channelTitle[0].toUpperCase() 
                    : '?',
                style: const TextStyle(color: Colors.white),
              ),
            ),
            title: Text(channel.channelTitle),
            subtitle: Text(
              channel.channelId,
              style: const TextStyle(fontSize: 12),
            ),
          ),
        );
      },
    );
  }
} 