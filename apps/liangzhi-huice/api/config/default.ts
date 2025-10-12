import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '..', '..');
const backtestDataDir = path.resolve(repoRoot, '..', 'services', 'backtest-engine');
const defaultH5Path = path.resolve(backtestDataDir, 'ethusdt_1m_2019-11-01_to_2025-06-15.h5');

export const DEFAULT_CONFIG = {
  h5: {
    filePath: process.env.H5_FILE_PATH || defaultH5Path,
  },
  backtest: {
    initialEquity: 10000,
    feeBps: 5,
    slippageBps: 2,
    // 默认回测截止时间为当前日期前3个月
    defaultEndMonthsBack: 3,
  },
} as const;

export type AppConfig = typeof DEFAULT_CONFIG;
