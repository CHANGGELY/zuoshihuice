import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '..', '..');
const backtestDataDir = path.resolve(repoRoot, 'services', 'backtest-engine');
const defaultH5Path = path.resolve(backtestDataDir, 'ethusdt_1m_2019-11-01_to_2025-06-15.h5');
const defaultBackupPath = path.resolve(backtestDataDir, 'ETHUSDT_1m_2025-08-09_to_2025-08-09_complete.h5');

export const DEFAULT_CONFIG = {
  backtest: {
    defaultEndMonthsBack: 3,
    maxConcurrentBacktests: 5,
    timeoutMinutes: 30
  },
  data: {
    h5FilePath: process.env.H5_FILE_PATH || defaultH5Path,
    h5BackupPath: process.env.H5_BACKUP_PATH || process.env.H5_FILE_PATH || defaultBackupPath,
    cacheSize: 1000,
    expectedColumns: ['timestamp', 'open', 'high', 'low', 'close', 'volume']
  },
  server: {
    port: parseInt(process.env.PORT || '8001'),
    cors: {
      origin: ['http://localhost:5173', 'http://localhost:3000'],
      credentials: true
    }
  }
};
