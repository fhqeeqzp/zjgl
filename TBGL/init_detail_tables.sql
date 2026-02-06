-- 投标明细表初始化脚本
-- 执行此脚本创建明细表结构

-- 创建投标明细主表
CREATE TABLE IF NOT EXISTS bidding_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bidding_id INT NOT NULL COMMENT '投标ID',
    summary_item_id INT COMMENT '关联的汇总项ID',
    version VARCHAR(20) DEFAULT 'V1.0' COMMENT '版本号',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(100) COMMENT '创建人',
    remark TEXT COMMENT '备注',
    FOREIGN KEY (bidding_id) REFERENCES biddings(id) ON DELETE CASCADE,
    FOREIGN KEY (summary_item_id) REFERENCES bidding_summary_items(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='投标明细表';

-- 创建投标明细项目表（包含所有字段）
CREATE TABLE IF NOT EXISTS bidding_detail_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    detail_id INT NOT NULL COMMENT '明细表ID',
    parent_id INT DEFAULT NULL COMMENT '父节点ID',
    sequence VARCHAR(50) COMMENT '序号',
    name VARCHAR(500) COMMENT '分部分项工程名称',
    specification VARCHAR(500) COMMENT '规格型号',
    description VARCHAR(1000) COMMENT '项目特征描述',
    unit VARCHAR(50) COMMENT '单位',
    quantity DECIMAL(15, 4) DEFAULT 0 COMMENT '工程量',
    unit_price DECIMAL(15, 2) DEFAULT 0 COMMENT '综合单价',
    total_price DECIMAL(15, 2) DEFAULT 0 COMMENT '合价',
    labor_price DECIMAL(15, 2) DEFAULT 0 COMMENT '人工单价',
    main_material_price DECIMAL(15, 2) DEFAULT 0 COMMENT '主材单价',
    main_material_loss_rate DECIMAL(5, 2) DEFAULT 0 COMMENT '主材损耗率(%)',
    aux_material_price DECIMAL(15, 2) DEFAULT 0 COMMENT '辅材单价',
    machinery_price DECIMAL(15, 2) DEFAULT 0 COMMENT '机械单价',
    other_price DECIMAL(15, 2) DEFAULT 0 COMMENT '其他单价',
    labor_total DECIMAL(15, 2) DEFAULT 0 COMMENT '人工合价',
    material_total DECIMAL(15, 2) DEFAULT 0 COMMENT '主材合价',
    auxiliary_total DECIMAL(15, 2) DEFAULT 0 COMMENT '辅材合价',
    machine_total DECIMAL(15, 2) DEFAULT 0 COMMENT '机械合价',
    other_total DECIMAL(15, 2) DEFAULT 0 COMMENT '其他合价',
    management_total DECIMAL(15, 2) DEFAULT 0 COMMENT '管理费合计',
    tax_total DECIMAL(15, 2) DEFAULT 0 COMMENT '税金合价',
    comprehensive_total DECIMAL(15, 2) DEFAULT 0 COMMENT '综合合价',
    remark VARCHAR(500) COMMENT '备注',
    sort_order INT DEFAULT 0 COMMENT '排序顺序',
    FOREIGN KEY (detail_id) REFERENCES bidding_details(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES bidding_detail_items(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='投标明细项目表';

-- 验证表是否创建成功
SELECT 'bidding_details' as table_name, COUNT(*) as column_count 
FROM information_schema.columns 
WHERE table_name = 'bidding_details' AND table_schema = DATABASE();

SELECT 'bidding_detail_items' as table_name, COUNT(*) as column_count 
FROM information_schema.columns 
WHERE table_name = 'bidding_detail_items' AND table_schema = DATABASE();
