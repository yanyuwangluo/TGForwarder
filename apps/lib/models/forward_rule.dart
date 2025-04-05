import 'channel.dart';

class ForwardRule {
  final int id;
  final Channel sourceChannel;
  final Channel destinationChannel;
  final bool isActive;
  final DateTime createdAt;

  ForwardRule({
    required this.id,
    required this.sourceChannel,
    required this.destinationChannel,
    required this.isActive,
    required this.createdAt,
  });

  factory ForwardRule.fromJson(Map<String, dynamic> json) {
    return ForwardRule(
      id: json['id'],
      sourceChannel: Channel.fromJson(json['source_channel']),
      destinationChannel: Channel.fromJson(json['destination_channel']),
      isActive: json['is_active'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'source_channel': sourceChannel.toJson(),
      'destination_channel': destinationChannel.toJson(),
      'is_active': isActive,
      'created_at': createdAt.toIso8601String(),
    };
  }
} 