import { Router } from 'express';

const router = Router();

// GET /api/v1/strategy - 返回可用策略列表/模板
router.get('/', async (_req, res) => {
  res.json({ success: true, data: [{ key: 'HEDGE_GRID', name: 'ATR对冲网格策略' }] });
});

// POST /api/v1/strategy/validate - 参数校验
router.post('/validate', async (req, res) => {
  try {
    const { DEFAULT_HEDGE_GRID_PARAMS } = await import('../../../domain/strategies/hedgeGrid/params');
    // 简单的参数验证
    const params = req.body;
    const requiredFields = Object.keys(DEFAULT_HEDGE_GRID_PARAMS);
    const missingFields = requiredFields.filter(field => !(field in params));
    
    if (missingFields.length > 0) {
      return res.status(400).json({ 
        success: false, 
        error: 'Missing required fields', 
        details: { missingFields } 
      });
    }
    
    return res.json({ success: true, data: { valid: true, normalized: params } });
  } catch (e: any) {
    return res.status(500).json({ success: false, error: e?.message || 'validate error' });
  }
});

export default router;