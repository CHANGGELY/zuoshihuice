import { Router, type Request, type Response } from 'express'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import { spawn } from 'child_process'
import { DEFAULT_CONFIG } from '@config/default.js'

const router = Router()
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Python脚本路径
const PYTHON_SCRIPT_PATH = path.join(__dirname, '..', 'scripts', 'read_h5.py')

interface KlineData {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

const resolveH5Path = (): string => {
  // @ts-ignore - 临时忽略类型检查，确保运行时兼容性
  const primary = DEFAULT_CONFIG.h5?.filePath || DEFAULT_CONFIG.data?.h5FilePath
  // @ts-ignore
  const backup = DEFAULT_CONFIG.h5?.backupPath || DEFAULT_CONFIG.data?.h5BackupPath
  
  // 自动扫描可能的H5文件
  const possibleFiles = [
    primary,
    backup,
    path.join(__dirname, '..', '..', '..', '..', 'services', 'backtest-engine', 'ETHUSDT_1m_test_2020-01-01_to_2020-01-03.h5'), // Add valid test file
    path.join(__dirname, '..', '..', '..', '..', 'services', 'backtest-engine', 'ethusdt_1m_2019-11-01_to_2025-06-15.h5'),
    path.join(__dirname, '..', '..', '..', '..', 'services', 'backtest-engine', 'ETHUSDT_1m_2025-08-09_to_2025-08-09_complete.h5'),
    path.join(process.cwd(), '..', '..', 'services', 'backtest-engine', 'ethusdt_1m_2019-11-01_to_2025-06-15.h5')
  ].filter(Boolean) as string[];

  for (const p of possibleFiles) {
    if (fs.existsSync(p)) {
      console.log(`[H5] Found data file: ${p}`);
      return p;
    }
  }

  throw new Error(`H5文件不存在: searched=${possibleFiles.join(', ')}`)
}

const loadH5Data = async (startTime?: number, endTime?: number, limit = 1000): Promise<KlineData[]> => {
  return new Promise((resolve, reject) => {
    try {
      const h5Path = resolveH5Path()

      // 准备Python脚本参数
      const args = [
        PYTHON_SCRIPT_PATH,
        h5Path,
        startTime ? startTime.toString() : 'null',
        endTime ? endTime.toString() : 'null',
        limit.toString()
      ]

      // 调用Python脚本 - 智能查找Python解释器
      const getPythonExecutable = () => {
        const possiblePaths = [
          // 1. 尝试项目根目录的 .venv (假设当前 cwd 是 apps/liangzhi-huice 或其他子目录)
          path.resolve(process.cwd(), '..', '..', '.venv'),
          // 2. 尝试当前目录的 .venv
          path.join(process.cwd(), '.venv'),
           // 3. 尝试从当前文件位置向上查找
          path.resolve(__dirname, '..', '..', '..', '..', '.venv')
        ];

        for (const venvPath of possiblePaths) {
          const pythonPath = process.platform === 'win32'
            ? path.join(venvPath, 'Scripts', 'python.exe')
            : path.join(venvPath, 'bin', 'python');
          if (fs.existsSync(pythonPath)) return pythonPath;
        }
        
        // 4. 如果都找不到，回退到系统 python
        return 'python';
      }

      const pythonExecutable = getPythonExecutable();

      const pythonProcess = spawn(pythonExecutable, args)
      let stdout = ''
      let stderr = ''

      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString()
      })

      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString()
      })

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Python脚本执行失败(code=${code}): ${stderr || '未知错误'}`))
          return
        }

        try {
          const trimmed = stdout.trim()
          if (!trimmed) {
            reject(new Error('Python脚本无输出，可能因路径或数据集名称错误导致'))
            return
          }
          const result = JSON.parse(trimmed)
          if (result.success) {
            resolve(result.data)
          } else {
            reject(new Error(result.error || '读取数据失败'))
          }
        } catch (e) {
          reject(new Error(`解析Python输出失败: ${(e as Error).message}; stdout=${stdout.substring(0,200)}; stderr=${stderr.substring(0,200)}`))
        }
      })

      pythonProcess.on('error', (error) => {
        reject(new Error(`启动Python进程失败: ${error.message}`))
      })

    } catch (e) {
      reject(new Error(`加载H5数据失败: ${e instanceof Error ? e.message : '未知错误'}`))
    }
  })
}

// Root endpoint for /api/v1/kline
router.get('/', async (req: Request, res: Response) => {
  try {
    const { start_time, end_time, limit = 1000 } = req.query;
    const startTime = start_time ? Number(start_time) : (start_time ? new Date(start_time as string).getTime() : undefined);
    const endTime = end_time ? Number(end_time) : (end_time ? new Date(end_time as string).getTime() : undefined);
    
    const data = await loadH5Data(startTime, endTime, Number(limit));
    
    res.json({
      success: true,
      data
    });
  } catch (e) {
    console.error('[Kline API] Error:', e);
    res.status(500).json({
      success: false,
      error: e instanceof Error ? e.message : '未知错误'
    });
  }
});

// K线数据范围查询接口
router.get('/range', async (req: Request, res: Response) => {
  try {
    const { start_time, end_time, limit = 1000 } = req.query;
    
    const startTime = start_time ? new Date(start_time as string).getTime() : undefined;
    const endTime = end_time ? new Date(end_time as string).getTime() : undefined;
    
    const rawData = await loadH5Data(startTime, endTime, Number(limit));
    
    // 转换为前端期望的格式
    const data = rawData.map(item => [
      item.timestamp,
      item.open,
      item.close,
      item.low,
      item.high
    ]);
    
    const volumes = rawData.map(item => [
      item.timestamp,
      item.volume
    ]);
    
    res.json({
      data,
      volumes
    });
  } catch (e) {
    res.status(500).json({
      success: false,
      error: e instanceof Error ? e.message : '未知错误'
    });
  }
});

// K线数据查询接口
router.get('/data', async (req: Request, res: Response) => {
  try {
    const { limit = 1000 } = req.query;
    const data = await loadH5Data(undefined, undefined, Number(limit));
    
    res.json({
      success: true,
      data
    });
  } catch (e) {
    res.status(500).json({
      success: false,
      error: e instanceof Error ? e.message : '未知错误'
    });
  }
});

// K线统计信息接口
router.get('/stats', async (_req: Request, res: Response) => {
  try {
    const data = await loadH5Data(undefined, undefined, 10000);
    const prices = data.map(d => d.close);
    const volumes = data.map(d => d.volume);
    
    res.json({
      success: true,
      stats: {
        total_records: data.length,
        price_range: {
          min: Math.min(...prices),
          max: Math.max(...prices),
          avg: prices.reduce((a, b) => a + b) / prices.length
        },
        volume_stats: {
          total: volumes.reduce((a, b) => a + b),
          avg: volumes.reduce((a, b) => a + b) / volumes.length,
          max: Math.max(...volumes)
        }
      }
    });
  } catch (e) {
    res.status(500).json({
      success: false,
      error: e instanceof Error ? e.message : '未知错误'
    });
  }
});

// 根路径K线数据接口 - 匹配前端 /api/kline 请求
router.get('/', async (req: Request, res: Response) => {
  try {
    const { symbol, timeframe, start_time, end_time, limit = 1000 } = req.query;
    
    const startTime = start_time ? new Date(start_time as string).getTime() : undefined;
    const endTime = end_time ? new Date(end_time as string).getTime() : undefined;
    
    const rawData = await loadH5Data(startTime, endTime, Number(limit));
    
    // 转换为前端期望的格式
    const data = rawData.map(item => ({
      timestamp: item.timestamp,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
      volume: item.volume
    }));
    
    res.json({
      success: true,
      data,
      symbol: symbol || 'ETHUSDT',
      timeframe: timeframe || '1m'
    });
  } catch (e) {
    res.status(500).json({
      success: false,
      error: e instanceof Error ? e.message : '未知错误'
    });
  }
});

// 交易信号接口 - 匹配前端 /api/signals 请求
router.get('/signals', async (req: Request, res: Response) => {
  try {
    const { symbol, timeframe, start_date, end_date } = req.query;
    
    const startTime = start_date ? new Date(start_date as string).getTime() : undefined;
    const endTime = end_date ? new Date(end_date as string).getTime() : undefined;
    
    // 获取K线数据用于生成信号
    const klineData = await loadH5Data(startTime, endTime, 1000);
    
    // 简单的交易信号生成逻辑（基于移动平均线）
    const signals: Array<{
      timestamp: number;
      type: 'buy' | 'sell';
      price: number;
      signal: string;
      strength: number;
      reason: string;
      volume?: number;
    }> = [];
    const shortMA = 5;
    const longMA = 20;
    
    for (let i = longMA; i < klineData.length; i++) {
      const shortSlice = klineData.slice(i - shortMA, i);
      const longSlice = klineData.slice(i - longMA, i);
      const prevShortSlice = klineData.slice(i - shortMA - 1, i - 1);
      const prevLongSlice = klineData.slice(i - longMA - 1, i - 1);

      const safeAvg = (arr: typeof klineData) => {
        const valid = arr.filter(d => d && typeof d.close === 'number' && !Number.isNaN(d.close));
        if (valid.length === 0) return NaN;
        return valid.reduce((sum, d) => sum + d.close, 0) / valid.length;
      };

      const shortAvg = safeAvg(shortSlice);
      const longAvg = safeAvg(longSlice);
      const prevShortAvg = safeAvg(prevShortSlice);
      const prevLongAvg = safeAvg(prevLongSlice);
      
      const current = klineData[i];
      const priceVal = (current && typeof current.close === 'number' && !Number.isNaN(current.close)) ? current.close : 0;

      // 金叉买入信号
      if (!Number.isNaN(shortAvg) && !Number.isNaN(longAvg) && !Number.isNaN(prevShortAvg) && !Number.isNaN(prevLongAvg)) {
        if (shortAvg > longAvg && prevShortAvg <= prevLongAvg) {
          signals.push({
            timestamp: current.timestamp,
            type: 'buy',
            price: priceVal,
            signal: 'MA_GOLDEN_CROSS',
            strength: 0.7,
            reason: 'MA_GOLDEN_CROSS',
          });
        } else if (shortAvg < longAvg && prevShortAvg >= prevLongAvg) {
          // 死叉卖出信号
          signals.push({
            timestamp: current.timestamp,
            type: 'sell',
            price: priceVal,
            signal: 'MA_DEATH_CROSS',
            strength: 0.7,
            reason: 'MA_DEATH_CROSS',
          });
        }
      }
    }

    // 字段完整性兜底（最终输出再做一层防御）
    const safeSignals = signals.map(s => ({
      timestamp: typeof s.timestamp === 'number' ? s.timestamp : Date.now(),
      type: s.type === 'buy' || s.type === 'sell' ? s.type : 'buy',
      price: (typeof s.price === 'number' && !Number.isNaN(s.price)) ? s.price : 0,
      volume: (typeof s.volume === 'number' && !Number.isNaN(s.volume)) ? s.volume : undefined,
      strength: (typeof s.strength === 'number' && !Number.isNaN(s.strength)) ? s.strength : 0,
      reason: typeof s.reason === 'string' && s.reason ? s.reason : 'N/A',
    }));
    
    res.json({
      success: true,
      data: safeSignals,
      symbol: (symbol as string) || 'ETHUSDT',
      timeframe: (timeframe as string) || '1h',
      strategy: 'MA_CROSSOVER'
    });
  } catch (e) {
    res.status(500).json({
      success: false,
      error: e instanceof Error ? e.message : '未知错误'
    });
  }
});

// 支持的交易对列表接口
router.get('/symbols', async (_req: Request, res: Response) => {
  try {
    // 目前只支持ETHUSDT，因为我们只有这个交易对的H5数据
    const symbols = ['ETHUSDT'];
    
    res.json({
      success: true,
      data: symbols
    });
  } catch (e) {
    res.status(500).json({
      success: false,
      error: e instanceof Error ? e.message : '获取交易对列表失败'
    });
  }
});

// 支持的时间周期列表接口
router.get('/timeframes', async (_req: Request, res: Response) => {
  try {
    // H5文件是1分钟数据，我们可以支持多个时间周期
    const timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d'];
    
    res.json({
      success: true,
      data: timeframes
    });
  } catch (e) {
    res.status(500).json({
      success: false,
      error: e instanceof Error ? e.message : '获取时间周期列表失败'
    });
  }
});

export default router;