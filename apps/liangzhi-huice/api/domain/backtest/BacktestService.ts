import { spawn, ChildProcess } from 'child_process';
import path from 'path';
import fs from 'fs/promises';
// import { v4 as uuidv4 } from 'uuid';
// 临时使用简单的ID生成器
function uuidv4(): string {
  return 'xxxx-xxxx-4xxx-yxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

export interface BacktestConfig {
  symbol: string;
  startDate?: string;
  endDate?: string;
  initialBalance: number;
  leverage: number;
  bidSpread: number;
  askSpread: number;
  maxPositionValueRatio: number;
  useDynamicOrderSize: boolean;
  minOrderAmount: number;
  maxOrderAmount: number;
}

export interface BacktestResult {
  success: boolean;
  symbol: string;
  startDate: string;
  endDate: string;
  initialCapital: number;
  finalEquity: number;
  totalReturn: number;
  totalTrades: number;
  winRate: number;
  maxDrawdown: number;
  sharpeRatio: number;
  liquidated: boolean;
  avgHoldingTime: number;
  trades: Array<{
    timestamp: number;
    action: string;
    side: string;
    amount: number;
    price: number;
    fee: number;
    leverage: string;
  }>;
  equityHistory: Array<[number, number]>;
}

export interface BacktestStatus {
  id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  progress: number;
  message: string;
  result?: BacktestResult;
  error?: string;
}

export class BacktestService {
  private static instance: BacktestService;
  private runningBacktests = new Map<string, BacktestStatus>();
  private processes = new Map<string, ChildProcess>();

  static getInstance(): BacktestService {
    if (!BacktestService.instance) {
      BacktestService.instance = new BacktestService();
    }
    return BacktestService.instance;
  }

  async startBacktest(config: BacktestConfig): Promise<string> {
    const backtestId = uuidv4();
    
    // 初始化状态
    this.runningBacktests.set(backtestId, {
      id: backtestId,
      status: 'queued',
      progress: 0,
      message: '准备启动回测...'
    });

    // 异步执行回测
    this.executeBacktest(backtestId, config).catch(error => {
      this.runningBacktests.set(backtestId, {
        id: backtestId,
        status: 'failed',
        progress: 0,
        message: '回测执行失败',
        error: error.message
      });
    });

    return backtestId;
  }

  private async executeBacktest(backtestId: string, config: BacktestConfig): Promise<void> {
    try {
      // 更新状态为运行中
      this.updateStatus(backtestId, {
        status: 'running',
        progress: 0.1,
        message: '正在准备回测环境...'
      });

      // 创建临时配置文件
      const configPath = await this.createTempConfig(backtestId, config);
      
      // 更新状态
      this.updateStatus(backtestId, {
        status: 'running',
        progress: 0.2,
        message: '正在启动Python回测脚本...'
      });

      // 执行Python脚本
      const result = await this.runPythonBacktest(backtestId, configPath);
      
      // 清理临时文件
      await this.cleanupTempFiles(configPath);
      
      // 更新最终状态
      this.runningBacktests.set(backtestId, {
        id: backtestId,
        status: 'completed',
        progress: 1,
        message: '回测完成',
        result
      });

    } catch (error: any) {
      this.runningBacktests.set(backtestId, {
        id: backtestId,
        status: 'failed',
        progress: 0,
        message: '回测执行失败',
        error: error.message
      });
    }
  }

  private async createTempConfig(backtestId: string, config: BacktestConfig): Promise<string> {
    const tempDir = path.join(process.cwd(), 'temp', 'backtest');
    await fs.mkdir(tempDir, { recursive: true });
    
    const configPath = path.join(tempDir, `config_${backtestId}.json`);
    
    const pythonConfig = {
      BACKTEST_CONFIG: {
        initial_balance: config.initialBalance,
        start_date: config.startDate,
        end_date: config.endDate,
        data_file_path: process.env.H5_FILE_PATH || path.join(process.cwd(), 'api', 'ETHUSDT_1m_2019-11-27_to_2025-08-09.h5')
      },
      STRATEGY_CONFIG: {
        leverage: config.leverage,
        bid_spread: config.bidSpread,
        ask_spread: config.askSpread,
        max_position_value_ratio: config.maxPositionValueRatio,
        use_dynamic_order_size: config.useDynamicOrderSize,
        min_order_amount: config.minOrderAmount,
        max_order_amount: config.maxOrderAmount
      }
    };
    
    await fs.writeFile(configPath, JSON.stringify(pythonConfig, null, 2));
    return configPath;
  }

  private async runPythonBacktest(backtestId: string, configPath: string): Promise<BacktestResult> {
    return new Promise((resolve, reject) => {
      const scriptPath = path.join(process.cwd(), '..', 'backtest_kline_trajectory.py');
      
      // 使用Python执行回测脚本
      const pythonProcess = spawn('python', ['-X', 'utf8', scriptPath, '--config', configPath], {
        cwd: process.cwd(),
        stdio: ['pipe', 'pipe', 'pipe']
      });

      this.processes.set(backtestId, pythonProcess);

      let stdout = '';
      let stderr = '';

      pythonProcess.stdout?.on('data', (data) => {
        stdout += data.toString();
        
        // 解析进度信息
        const lines = data.toString().split('\n');
        for (const line of lines) {
          if (line.includes('回测进度:')) {
            // 解析进度百分比
            const match = line.match(/(\d+)%/);
            if (match) {
              const progress = parseInt(match[1]) / 100;
              this.updateStatus(backtestId, {
                status: 'running',
                progress: 0.2 + progress * 0.7, // 20%-90%用于回测执行
                message: `回测进行中... ${match[1]}%`
              });
            }
          }
        }
      });

      pythonProcess.stderr?.on('data', (data) => {
        stderr += data.toString();
      });

      pythonProcess.on('close', (code) => {
        this.processes.delete(backtestId);
        
        if (code === 0) {
          try {
            // 解析Python脚本的输出结果
            const resultMatch = stdout.match(/BACKTEST_RESULT_JSON:(.+?)END_BACKTEST_RESULT/s);
            if (resultMatch) {
              const result = JSON.parse(resultMatch[1].trim());
              resolve(result);
            } else {
              // 如果没有找到JSON结果，创建一个默认结果
              resolve({
                success: true,
                symbol: 'ETHUSDT',
                startDate: '',
                endDate: '',
                initialCapital: 10000,
                finalEquity: 10000,
                totalReturn: 0,
                totalTrades: 0,
                winRate: 0,
                maxDrawdown: 0,
                sharpeRatio: 0,
                liquidated: false,
                avgHoldingTime: 0,
                trades: [],
                equityHistory: []
              });
            }
          } catch (error) {
            reject(new Error(`解析回测结果失败: ${error}`));
          }
        } else {
          reject(new Error(`Python脚本执行失败 (退出码: ${code}): ${stderr}`));
        }
      });

      pythonProcess.on('error', (error) => {
        this.processes.delete(backtestId);
        reject(new Error(`启动Python脚本失败: ${error.message}`));
      });
    });
  }

  private async cleanupTempFiles(configPath: string): Promise<void> {
    try {
      await fs.unlink(configPath);
    } catch (error) {
      console.warn('清理临时配置文件失败:', error);
    }
  }

  private updateStatus(backtestId: string, updates: Partial<BacktestStatus>): void {
    const current = this.runningBacktests.get(backtestId);
    if (current) {
      this.runningBacktests.set(backtestId, { ...current, ...updates });
    }
  }

  getBacktestStatus(backtestId: string): BacktestStatus | undefined {
    return this.runningBacktests.get(backtestId);
  }

  getAllBacktests(): BacktestStatus[] {
    return Array.from(this.runningBacktests.values());
  }

  async stopBacktest(backtestId: string): Promise<boolean> {
    const process = this.processes.get(backtestId);
    if (process) {
      process.kill('SIGTERM');
      this.processes.delete(backtestId);
      
      this.updateStatus(backtestId, {
        status: 'failed',
        message: '回测已被用户取消',
        error: '用户取消'
      });
      
      return true;
    }
    return false;
  }
}