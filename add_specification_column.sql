-- 添加 specification 字段到 bidding_detail_items 表
ALTER TABLE bidding_detail_items 
ADD COLUMN specification VARCHAR(500) COMMENT '规格型号' AFTER name;
