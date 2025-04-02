-- 添加forwarded_msg_id字段到ForwardedMessage表
ALTER TABLE forwarded_message ADD COLUMN forwarded_msg_id INTEGER; 