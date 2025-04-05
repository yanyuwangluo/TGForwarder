class Channel {
  final String channelId;
  final String channelTitle;
  final bool isSource;
  final bool isDestination;

  Channel({
    required this.channelId,
    required this.channelTitle,
    required this.isSource,
    required this.isDestination,
  });

  factory Channel.fromJson(Map<String, dynamic> json) {
    return Channel(
      channelId: json['channel_id'] as String,
      channelTitle: json['channel_title'] as String,
      isSource: json['is_source'] as bool,
      isDestination: json['is_destination'] as bool,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'channel_id': channelId,
      'channel_title': channelTitle,
      'is_source': isSource,
      'is_destination': isDestination,
    };
  }
} 