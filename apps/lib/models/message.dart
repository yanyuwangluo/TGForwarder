class ForwardedMessage {
  final int id;
  final int messageId;
  final String sourceChannelId;
  final String destinationChannelId;
  final String messageTitle;
  final DateTime forwardedAt;
  final int? forwardedMsgId;

  ForwardedMessage({
    required this.id,
    required this.messageId,
    required this.sourceChannelId,
    required this.destinationChannelId,
    required this.messageTitle,
    required this.forwardedAt,
    this.forwardedMsgId,
  });

  factory ForwardedMessage.fromJson(Map<String, dynamic> json) {
    return ForwardedMessage(
      id: json['id'],
      messageId: json['message_id'],
      sourceChannelId: json['source_channel_id'],
      destinationChannelId: json['destination_channel_id'],
      messageTitle: json['message_title'],
      forwardedAt: DateTime.parse(json['forwarded_at']),
      forwardedMsgId: json['forwarded_msg_id'],
    );
  }
}

class MessagePagination {
  final List<ForwardedMessage> items;
  final int page;
  final int totalPages;
  final int totalItems;
  
  MessagePagination({
    required this.items,
    required this.page,
    required this.totalPages,
    required this.totalItems,
  });
  
  factory MessagePagination.fromJson(Map<String, dynamic> json) {
    return MessagePagination(
      items: (json['items'] as List)
          .map((item) => ForwardedMessage.fromJson(item))
          .toList(),
      page: json['page'],
      totalPages: json['total_pages'],
      totalItems: json['total_items'],
    );
  }
} 