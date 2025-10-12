
-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    
    -- 约束
    CONSTRAINT users_username_check CHECK (length(username) >= 3),
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- 创建K线数据表
CREATE TABLE IF NOT EXISTS kline_data (
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open_price DECIMAL(20, 8) NOT NULL,
    high_price DECIMAL(20, 8) NOT NULL,
    low_price DECIMAL(20, 8) NOT NULL,
    close_price DECIMAL(20, 8) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    amount DECIMAL(30, 8) NOT NULL DEFAULT 0,
    
    -- 约束
    CONSTRAINT kline_data_prices_check CHECK (
        open_price > 0 AND high_price > 0 AND low_price > 0 AND close_price > 0
        AND high_price >= low_price
        AND high_price >= open_price
        AND high_price >= close_price
        AND low_price <= open_price
        AND low_price <= close_price
    ),
    CONSTRAINT kline_data_volume_check CHECK (volume >= 0),
    CONSTRAINT kline_data_amount_check CHECK (amount >= 0),
    
    -- 主键
    PRIMARY KEY (symbol, timestamp)
);

-- K线数据表索引
CREATE INDEX IF NOT EXISTS idx_kline_data_symbol ON kline_data(symbol);
CREATE INDEX IF NOT EXISTS idx_kline_data_timestamp ON kline_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_kline_data_symbol_timestamp ON kline_data(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_kline_data_close_price ON kline_data(close_price);
CREATE INDEX IF NOT EXISTS idx_kline_data_volume ON kline_data(volume DESC);

-- 创建回测结果表
CREATE TABLE IF NOT EXISTS backtest_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    strategy_name VARCHAR(100) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ NOT NULL,
    initial_capital DECIMAL(20, 8) NOT NULL,
    final_capital DECIMAL(20, 8) NOT NULL,
    total_return DECIMAL(10, 4) NOT NULL,
    annual_return DECIMAL(10, 4) NOT NULL,
    max_drawdown DECIMAL(10, 4) NOT NULL,
    sharpe_ratio DECIMAL(10, 4),
    win_rate DECIMAL(5, 4),
    total_trades INTEGER NOT NULL DEFAULT 0,
    winning_trades INTEGER NOT NULL DEFAULT 0,
    losing_trades INTEGER NOT NULL DEFAULT 0,
    avg_trade_return DECIMAL(10, 4),
    parameters JSONB,
    performance_metrics JSONB,
    trade_history JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- 约束
    CONSTRAINT backtest_results_capital_check CHECK (initial_capital > 0),
    CONSTRAINT backtest_results_dates_check CHECK (end_date > start_date),
    CONSTRAINT backtest_results_trades_check CHECK (
        total_trades >= 0 AND winning_trades >= 0 AND losing_trades >= 0
        AND winning_trades + losing_trades <= total_trades
    )
);

-- 回测结果表索引
CREATE INDEX IF NOT EXISTS idx_backtest_results_user_id ON backtest_results(user_id);
CREATE INDEX IF NOT EXISTS idx_backtest_results_strategy ON backtest_results(strategy_name);
CREATE INDEX IF NOT EXISTS idx_backtest_results_symbol ON backtest_results(symbol);
CREATE INDEX IF NOT EXISTS idx_backtest_results_created_at ON backtest_results(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_backtest_results_return ON backtest_results(total_return DESC);

-- 创建策略配置表
CREATE TABLE IF NOT EXISTS strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    strategy_type VARCHAR(50) NOT NULL,
    parameters JSONB NOT NULL DEFAULT '{}',
    code TEXT,
    is_active BOOLEAN DEFAULT true,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- 约束
    CONSTRAINT strategies_name_user_unique UNIQUE(user_id, name),
    CONSTRAINT strategies_name_check CHECK (length(name) >= 1)
);

-- 策略表索引
CREATE INDEX IF NOT EXISTS idx_strategies_user_id ON strategies(user_id);
CREATE INDEX IF NOT EXISTS idx_strategies_type ON strategies(strategy_type);
CREATE INDEX IF NOT EXISTS idx_strategies_active ON strategies(is_active);
CREATE INDEX IF NOT EXISTS idx_strategies_public ON strategies(is_public);
CREATE INDEX IF NOT EXISTS idx_strategies_created_at ON strategies(created_at DESC);

-- 创建数据质量监控表
CREATE TABLE IF NOT EXISTS data_quality_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) NOT NULL,
    check_date DATE NOT NULL,
    total_records INTEGER NOT NULL DEFAULT 0,
    missing_records INTEGER NOT NULL DEFAULT 0,
    duplicate_records INTEGER NOT NULL DEFAULT 0,
    invalid_price_records INTEGER NOT NULL DEFAULT 0,
    zero_volume_records INTEGER NOT NULL DEFAULT 0,
    quality_score DECIMAL(5, 4) NOT NULL DEFAULT 0,
    issues JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- 约束
    CONSTRAINT data_quality_symbol_date_unique UNIQUE(symbol, check_date),
    CONSTRAINT data_quality_score_check CHECK (quality_score >= 0 AND quality_score <= 1)
);

-- 数据质量表索引
CREATE INDEX IF NOT EXISTS idx_data_quality_symbol ON data_quality_reports(symbol);
CREATE INDEX IF NOT EXISTS idx_data_quality_date ON data_quality_reports(check_date DESC);
CREATE INDEX IF NOT EXISTS idx_data_quality_score ON data_quality_reports(quality_score);
CREATE INDEX IF NOT EXISTS idx_data_quality_created_at ON data_quality_reports(created_at DESC);

-- 创建系统日志表
CREATE TABLE IF NOT EXISTS system_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    module VARCHAR(100),
    function_name VARCHAR(100),
    line_number INTEGER,
    user_id UUID REFERENCES users(id),
    request_id VARCHAR(100),
    extra_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- 约束
    CONSTRAINT system_logs_level_check CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
);

-- 系统日志表索引
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level);
CREATE INDEX IF NOT EXISTS idx_system_logs_module ON system_logs(module);
CREATE INDEX IF NOT EXISTS idx_system_logs_user_id ON system_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_system_logs_request_id ON system_logs(request_id);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为用户表添加更新时间触发器
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 为策略表添加更新时间触发器
DROP TRIGGER IF EXISTS update_strategies_updated_at ON strategies;
CREATE TRIGGER update_strategies_updated_at
    BEFORE UPDATE ON strategies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 启用行级安全性（RLS）
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE backtest_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_quality_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_logs ENABLE ROW LEVEL SECURITY;

-- 创建RLS策略
-- 用户只能访问自己的数据
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- 回测结果策略
CREATE POLICY "Users can view own backtest results" ON backtest_results
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own backtest results" ON backtest_results
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own backtest results" ON backtest_results
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own backtest results" ON backtest_results
    FOR DELETE USING (auth.uid() = user_id);

-- 策略配置策略
CREATE POLICY "Users can view own strategies" ON strategies
    FOR SELECT USING (auth.uid() = user_id OR is_public = true);

CREATE POLICY "Users can insert own strategies" ON strategies
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own strategies" ON strategies
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own strategies" ON strategies
    FOR DELETE USING (auth.uid() = user_id);

-- K线数据表允许所有认证用户读取
CREATE POLICY "Authenticated users can view kline data" ON kline_data
    FOR SELECT USING (auth.role() = 'authenticated');

-- 数据质量报告允许所有认证用户读取
CREATE POLICY "Authenticated users can view data quality reports" ON data_quality_reports
    FOR SELECT USING (auth.role() = 'authenticated');

-- 系统日志策略（仅管理员可访问）
CREATE POLICY "Only admins can view system logs" ON system_logs
    FOR SELECT USING (auth.jwt() ->> 'role' = 'admin');
