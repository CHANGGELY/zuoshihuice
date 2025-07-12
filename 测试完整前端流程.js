// 测试完整前端流程
const axios = require('axios');

async function testFrontendFlow() {
    console.log('🧪 开始测试完整前端流程...');
    
    // 1. 测试健康检查
    try {
        console.log('\n1️⃣ 测试健康检查...');
        const healthResponse = await axios.get('http://localhost:8000/api/v1/health');
        console.log('✅ 健康检查成功:', healthResponse.data);
    } catch (error) {
        console.log('❌ 健康检查失败:', error.message);
        return;
    }
    
    // 2. 测试回测API
    try {
        console.log('\n2️⃣ 测试回测API...');
        
        // 模拟前端发送的参数
        const params = {
            strategy: 'grid_making',
            initial_capital: 10000,
            leverage: 125,
            start_date: '2024-06-15',
            end_date: '2024-07-14',
            bid_spread: 0.002,
            ask_spread: 0.002
        };
        
        console.log('📋 发送参数:', params);
        
        const response = await axios.post(
            'http://localhost:8000/api/v1/backtest/run/',
            params,
            {
                headers: {
                    'Content-Type': 'application/json'
                },
                timeout: 300000 // 5分钟超时
            }
        );
        
        console.log('📊 响应状态码:', response.status);
        
        if (response.status === 200) {
            const result = response.data;
            
            if (result.success) {
                const data = result.data;
                console.log('✅ 回测API测试成功!');
                console.log('📈 总收益率:', (data.total_return * 100).toFixed(2) + '%');
                console.log('📉 最大回撤:', (data.max_drawdown * 100).toFixed(2) + '%');
                console.log('📊 交易次数:', data.total_trades);
                console.log('💰 最终资金:', data.final_capital.toFixed(2) + ' USDC');
                console.log('📝 交易记录数量:', data.trades ? data.trades.length : 0);
                
                // 检查是否是真实数据
                const trades = data.trades || [];
                if (trades.length > 100) {
                    console.log('✅ 这是真实的专业回测数据!');
                    console.log('🔍 第一笔交易:', trades[0]);
                } else {
                    console.log('❌ 交易数据不足，可能是模拟数据');
                }
                
                // 检查权益曲线
                const equityCurve = data.equity_curve || [];
                console.log('📈 权益曲线数据点:', equityCurve.length);
                
            } else {
                console.log('❌ 回测失败:', result.error);
            }
        } else {
            console.log('❌ HTTP错误:', response.status, response.statusText);
        }
        
    } catch (error) {
        console.log('❌ 回测API测试失败:', error.message);
        if (error.response) {
            console.log('📊 错误状态码:', error.response.status);
            console.log('📝 错误响应:', error.response.data);
        }
    }
    
    console.log('\n🎯 测试完成!');
}

// 运行测试
testFrontendFlow().catch(console.error);
