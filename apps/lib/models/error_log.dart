class ErrorLog {
  final int id;
  final String errorTitle;
  final String errorDetails;
  final String sourceTitle;
  final String destTitle;
  final String sourceId;
  final String destId;
  final int messageId;
  final DateTime timestamp;

  ErrorLog({
    required this.id,
    required this.errorTitle,
    required this.errorDetails,
    required this.sourceTitle,
    required this.destTitle,
    required this.sourceId,
    required this.destId,
    required this.messageId,
    required this.timestamp,
  });

  factory ErrorLog.fromJson(Map<String, dynamic> json) {
    return ErrorLog(
      id: json['id'] as int,
      errorTitle: json['error_title'] as String,
      errorDetails: json['error_details'] as String,
      sourceTitle: json['source_title'] as String,
      destTitle: json['dest_title'] as String,
      sourceId: json['source_id'] as String,
      destId: json['dest_id'] as String,
      messageId: json['message_id'] as int,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'error_title': errorTitle,
      'error_details': errorDetails,
      'source_title': sourceTitle,
      'dest_title': destTitle,
      'source_id': sourceId,
      'dest_id': destId,
      'message_id': messageId,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}

class ErrorLogResult {
  final List<ErrorLog> logs;
  final int totalPages;
  final int currentPage;
  final int totalItems;

  ErrorLogResult({
    required this.logs,
    required this.totalPages,
    required this.currentPage,
    required this.totalItems,
  });

  factory ErrorLogResult.fromJson(Map<String, dynamic> json) {
    return ErrorLogResult(
      logs: (json['items'] as List)
          .map((item) => ErrorLog.fromJson(item))
          .toList(),
      totalPages: json['total_pages'] as int,
      currentPage: json['current_page'] as int,
      totalItems: json['total_items'] as int,
    );
  }
} 