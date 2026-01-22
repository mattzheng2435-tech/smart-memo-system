-- 智能备忘录系统 - 数据库 Schema
-- 适用于 Supabase PostgreSQL

-- 备忘录主表
CREATE TABLE IF NOT EXISTS memos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    what TEXT NOT NULL,                    -- 任务内容
    when_due TIMESTAMPTZ,                  -- 截止时间
    who TEXT,                              -- 相关人员
    status VARCHAR(20) DEFAULT 'pending',  -- pending/completed/cancelled
    priority VARCHAR(10) DEFAULT 'normal', -- high/normal/low
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    tags TEXT[],                           -- 标签数组
    context TEXT,                          -- 补充上下文
    category VARCHAR(50),                  -- work/personal/urgent
    metadata JSONB                         -- 扩展字段
);

-- 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_memos_status ON memos(status);
CREATE INDEX IF NOT EXISTS idx_memos_when_due ON memos(when_due);
CREATE INDEX IF NOT EXISTS idx_memos_priority ON memos(priority);

-- 全文搜索索引 (用于语义搜索)
CREATE INDEX IF NOT EXISTS idx_memos_fulltext
ON memos USING GIN(to_tsvector('english', what || ' ' || COALESCE(context, '')));

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_memos_updated_at
    BEFORE UPDATE ON memos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 任务对话历史表 (用于追问逻辑)
CREATE TABLE IF NOT EXISTS memo_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memo_id UUID REFERENCES memos(id) ON DELETE CASCADE,
    user_message TEXT,
    system_response TEXT,
    missing_fields JSONB,                  -- 记录缺失的 what/when/who
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_memo_id ON memo_conversations(memo_id);

-- 批量操作记录表
CREATE TABLE IF NOT EXISTS batch_operations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_type VARCHAR(20),           -- complete/delete/snooze
    memo_ids UUID[],                      -- 操作的备忘录ID列表
    criteria JSONB,                       -- 匹配条件 (模糊语义)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE memos IS '备忘录主表';
COMMENT ON TABLE memo_conversations IS '任务对话历史 - 记录追问过程';
COMMENT ON TABLE batch_operations IS '批量操作记录';
