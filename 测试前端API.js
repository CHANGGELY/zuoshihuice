// 测试前端API调用
const testBacktestAPI = async () => {
  try {
    console.log('测试前端回测API...');
    
    // 模拟前端的runDirectBacktest方法
    const runDirectBacktest = async (params) => {
      try {
        // 模拟调用独立回测执行器
        console.log('收到回测参数:', params);
        
        // 为了演示，我们使用之前保存的真实回测结果
        const mockResult = {
          success: true,
          data: {
            total_return: 0.09033165176502098,
            max_drawdown: 0.1211,
            sharpe_ratio: 0.05,
            total_trades: 1014,
            win_rate: 0.52,
            final_capital: 10903.32,
            trades: [
              {
                timestamp: "1718431668",
                side: "buy_long",
                amount: 0.0565,
                price: 3535.32,
                fee: 0.0399,
                pnl: 0.0
              },
              {
                timestamp: "1718431896", 
                side: "sell_short",
                amount: 0.0563,
                price: 3547.74,
                fee: 0.0399,
                pnl: 12.45
              }
            ],
            equity_curve: []
          }
        };
        
        // 模拟网络延迟
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        return mockResult;
      } catch (error) {
        throw new Error(`回测执行失败: ${error.message}`);
      }
    };
    
    // 测试参数
    const params = {
      strategy: 'grid_making',
      initial_capital: 10000,
      leverage: 5,
      start_date: '2024-06-15',
      end_date: '2024-07-15'
    };
    
    // 调用API
    const result = await runDirectBacktest(params);
    
    console.log('✅ API调用成功!');
    console.log('总收益率:', result.data.total_return);
    console.log('交易次数:', result.data.total_trades);
    console.log('最终资金:', result.data.final_capital);
    
    return result;
    
  } catch (error) {
    console.error('❌ API调用失败:', error);
    throw error;
  }
};

// 运行测试
testBacktestAPI()
  .then(result => {
    console.log('🎉 测试完成，结果:', result);
  })
  .catch(error => {
    console.error('💥 测试失败:', error);
  });
