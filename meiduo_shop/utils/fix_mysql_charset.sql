-- fix_mysql_charset.sql
-- 修复美多商城数据库乱码问题

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 创建修复函数
DELIMITER //

DROP FUNCTION IF EXISTS fix_gbk_to_utf8//
CREATE FUNCTION fix_gbk_to_utf8(str TEXT) RETURNS TEXT
DETERMINISTIC
BEGIN
    DECLARE result TEXT;
    DECLARE CONTINUE HANDLER FOR 1366 BEGIN
        -- 如果转换失败，返回原字符串
        SET result = str;
    END;

    -- 尝试多种转换方式
    IF str IS NOT NULL AND LENGTH(str) > 0 THEN
        -- 方式1：假设是GBK编码存储在latin1中
        SET result = CONVERT(CONVERT(CONVERT(str USING latin1) USING binary) USING gbk);

        -- 检查转换后是否还有乱码
        IF result LIKE '%?%' OR result LIKE '%�%' THEN
            -- 方式2：尝试其他转换
            SET result = CONVERT(CONVERT(str USING binary) USING gbk);
        END IF;

        -- 如果转换后长度异常（可能转换失败），使用原字符串
        IF LENGTH(result) = 0 OR result IS NULL THEN
            SET result = str;
        END IF;
    ELSE
        SET result = str;
    END IF;

    RETURN result;
END//

DELIMITER ;

-- 打印开始信息
SELECT '开始修复数据库乱码问题...' AS message;

-- 修复 tb_sku 表
SELECT '修复 tb_sku 表...' AS message;
UPDATE tb_sku
SET
    name = fix_gbk_to_utf8(name),
    caption = fix_gbk_to_utf8(caption)
WHERE name LIKE '%?%' OR caption LIKE '%?%'
   OR name LIKE '%�%' OR caption LIKE '%�%';

-- 修复 tb_spu 表
SELECT '修复 tb_spu 表...' AS message;
UPDATE tb_spu
SET
    name = fix_gbk_to_utf8(name),
    desc_detail = fix_gbk_to_utf8(desc_detail),
    desc_pack = fix_gbk_to_utf8(desc_pack),
    desc_service = fix_gbk_to_utf8(desc_service)
WHERE name LIKE '%?%' OR desc_detail LIKE '%?%'
   OR desc_pack LIKE '%?%' OR desc_service LIKE '%?%';

-- 修复 tb_content 表
SELECT '修复 tb_content 表...' AS message;
UPDATE tb_content
SET
    title = fix_gbk_to_utf8(title),
    url = fix_gbk_to_utf8(url),
    text = fix_gbk_to_utf8(text)
WHERE title LIKE '%?%' OR url LIKE '%?%' OR text LIKE '%?%';

-- 修复 tb_content_category 表
SELECT '修复 tb_content_category 表...' AS message;
UPDATE tb_content_category
SET
    name = fix_gbk_to_utf8(name),
    `key` = fix_gbk_to_utf8(`key`)
WHERE name LIKE '%?%' OR `key` LIKE '%?%';

-- 修复 tb_goods_category 表
SELECT '修复 tb_goods_category 表...' AS message;
UPDATE tb_goods_category
SET
    name = fix_gbk_to_utf8(name)
WHERE name LIKE '%?%';

-- 修复 tb_brand 表
SELECT '修复 tb_brand 表...' AS message;
UPDATE tb_brand
SET
    name = fix_gbk_to_utf8(name)
WHERE name LIKE '%?%';

-- 修复其他表...
SELECT '修复其他表...' AS message;
UPDATE tb_channel_group SET name = fix_gbk_to_utf8(name) WHERE name LIKE '%?%';
UPDATE tb_goods_channel SET url = fix_gbk_to_utf8(url) WHERE url LIKE '%?%';
UPDATE tb_spu_specification SET name = fix_gbk_to_utf8(name) WHERE name LIKE '%?%';
UPDATE tb_specification_option SET value = fix_gbk_to_utf8(value) WHERE value LIKE '%?%';

-- 验证修复结果
SELECT '验证修复结果:' AS message;

SELECT
    'tb_sku' as table_name,
    COUNT(*) as total_rows,
    SUM(CASE WHEN name LIKE '%?%' THEN 1 ELSE 0 END) as problematic_names,
    SUM(CASE WHEN caption LIKE '%?%' THEN 1 ELSE 0 END) as problematic_captions
FROM tb_sku
UNION ALL
SELECT
    'tb_spu',
    COUNT(*),
    SUM(CASE WHEN name LIKE '%?%' THEN 1 ELSE 0 END),
    SUM(CASE WHEN desc_detail LIKE '%?%' THEN 1 ELSE 0 END)
FROM tb_spu
UNION ALL
SELECT
    'tb_content',
    COUNT(*),
    SUM(CASE WHEN title LIKE '%?%' THEN 1 ELSE 0 END),
    SUM(CASE WHEN text LIKE '%?%' THEN 1 ELSE 0 END)
FROM tb_content
UNION ALL
SELECT
    'tb_content_category',
    COUNT(*),
    SUM(CASE WHEN name LIKE '%?%' THEN 1 ELSE 0 END),
    SUM(CASE WHEN `key` LIKE '%?%' THEN 1 ELSE 0 END)
FROM tb_content_category
UNION ALL
SELECT
    'tb_goods_category',
    COUNT(*),
    SUM(CASE WHEN name LIKE '%?%' THEN 1 ELSE 0 END),
    0
FROM tb_goods_category;

-- 删除修复函数
DROP FUNCTION IF EXISTS fix_gbk_to_utf8;

SET FOREIGN_KEY_CHECKS = 1;

SELECT '修复完成！' AS message;