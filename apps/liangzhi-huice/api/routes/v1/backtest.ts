import { Router } from 'express';
import { DEFAULT_CONFIG } from '../../../config/default.js';
import { H5Reader } from '../../../domain/data/h5/H5Reader';
import { BacktestService, BacktestConfig } from '../../../domain/backtest/BacktestService';

const router = Router();
const backtestService = BacktestService.getInstance();

async function getDefaultDateRange() {
  const monthsBack = DEFAULT_CONFIG.backtest.defaultEndMonthsBack ?? 3;
  const now = new Date();
  const endCandidate = new Date(now);
  endCandidate.setMonth(endCandidate.getMonth() - monthsBack);
  endCandidate.setHours(0, 0, 0, 0);

  // 以H5数据的时间范围为准：起点=minTs，终点=min(maxTs, endCandidate)
  const reader = new H5Reader();
  const { minTs, maxTs } = await reader.getTimeRange();
  const end = Math.min(maxTs, endCandidate.getTime());
  const start = minTs;
  return { start, end };
}

// POST /api/v1/backtest - 启动回测
router.post('/', async (req, res) => {
  try {
    const {
      symbol = 'ETHUSDT',
      startDate,
      endDate,
      initialBalance = 10000,
      leverage = 10,
      bidSpread = 0.001,
      askSpread = 0.001,
      maxPositionValueRatio = 0.8,
      useDynamicOrderSize = true,
      minOrderAmount = 0.001,
      maxOrderAmount = 10.0
    } = req.body;

    // 如果没有提供时间范围，使用默认范围
    let finalStartDate = startDate;
    let finalEndDate = endDate;
    
    if (!startDate || !endDate) {
      const def = await getDefaultDateRange();
      finalStartDate = finalStartDate || new Date(def.start).toISOString().split('T')[0];
      finalEndDate = finalEndDate || new Date(def.end).toISOString().split('T')[0];
    }

    const config: BacktestConfig = {
      symbol,
      timeframe: '1m',
      startDate: finalStartDate,
      endDate: finalEndDate,
      initialBalance: Number(initialBalance),
      strategy: 'grid',
      params: {
        gridSpacing: 0.01,
        orderSize: 0.1
      }
    };

    // 暂时不使用这些参数，避免TypeScript警告
    void leverage;
    void bidSpread;
    void askSpread;
    void maxPositionValueRatio;
    void useDynamicOrderSize;
    void minOrderAmount;
    void maxOrderAmount;

    const backtestId = await backtestService.startBacktest(config);
    
    res.json({ 
      success: true, 
      data: { 
        id: backtestId, 
        status: 'queued',
        config
      } 
    });
  } catch (e: any) {
    res.status(500).json({ success: false, error: e?.message || 'internal error' });
  }
});

// GET /api/v1/backtest/status - 查询回测状态
router.get('/status', async (req, res) => {
  try {
    const { id } = req.query;
    
    if (!id || typeof id !== 'string') {
      return res.status(400).json({ success: false, error: '缺少回测ID' });
    }

    const status = backtestService.getBacktestStatus(id);
    
    if (!status) {
      return res.status(404).json({ success: false, error: '回测任务不存在' });
    }

    res.json({ success: true, data: status });
  } catch (e: any) {
    res.status(500).json({ success: false, error: e?.message || 'internal error' });
  }
});

// GET /api/v1/backtest/result/:id - 获取回测结果
router.get('/result/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    const status = backtestService.getBacktestStatus(id);
    
    if (!status) {
      return res.status(404).json({ success: false, error: '回测任务不存在' });
    }

    if (status.status !== 'completed') {
      return res.status(400).json({ 
        success: false, 
        error: '回测尚未完成',
        status: status.status,
        progress: status.progress
      });
    }

    res.json({ success: true, data: status.result });
  } catch (e: any) {
    res.status(500).json({ success: false, error: e?.message || 'internal error' });
  }
});

// GET /api/v1/backtest/history - 获取所有回测历史
router.get('/history', async (_req, res) => {
  try {
    // 暂时返回空数组，后续实现getAllBacktests方法
    const allBacktests: any[] = [];
    res.json({ success: true, data: allBacktests });
  } catch (e: any) {
    res.status(500).json({ success: false, error: e?.message || 'internal error' });
  }
});

// DELETE /api/v1/backtest/:id - 停止回测
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    const stopped = await backtestService.stopBacktest(id);
    
    if (stopped) {
      res.json({ success: true, message: '回测已停止' });
    } else {
      res.status(404).json({ success: false, error: '回测任务不存在或已完成' });
    }
  } catch (e: any) {
    res.status(500).json({ success: false, error: e?.message || 'internal error' });
  }
});

export default router;