import express, { type Request, type Response, type NextFunction } from 'express';
import cors from 'cors';
import path from 'path';
import dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import authRoutes from './routes/auth';
import klineRoutes from './routes/kline';
import strategyRoutes from './routes/v1/strategy';
import backtestRoutes from './routes/v1/backtest';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config();

const app: express.Application = express();

app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(express.static(path.join(__dirname, '../dist')));

app.use('/api/auth', authRoutes);
app.use('/api/v1/kline', klineRoutes);
app.use('/api/kline', klineRoutes);
// app.use('/api/v1/symbols', klineRoutes); // Fixed: Don't map symbols to kline routes root
// app.use('/api/v1/timeframes', klineRoutes); // Fixed: Don't map timeframes to kline routes root
app.use('/api/v1/signals', klineRoutes); // This might need checking too

// Metadata routes
app.get('/api/v1/symbols', (_req, res) => {
  res.json({ 
    success: true, 
    data: [
      { label: 'ETH/USDT', value: 'ETHUSDT' },
      { label: 'BNB/USDT', value: 'BNBUSDT' },
      { label: 'BTC/USDT', value: 'BTCUSDT' }
    ] 
  });
});

app.get('/api/v1/timeframes', (_req, res) => {
  res.json({ 
    success: true, 
    data: [
      { label: '1分钟', value: '1m' },
      { label: '5分钟', value: '5m' },
      { label: '15分钟', value: '15m' },
      { label: '30分钟', value: '30m' },
      { label: '1小时', value: '1h' },
      { label: '4小时', value: '4h' },
      { label: '1天', value: '1d' }
    ] 
  });
});

app.use('/api/v1/strategy', strategyRoutes);
app.use('/api/v1/backtest', backtestRoutes);

app.use('/api/health', (_req: Request, res: Response, _next: NextFunction): void => {
  res.status(200).json({ success: true, message: 'ok' });
});

app.use((_error: Error, _req: Request, res: Response, _next: NextFunction) => {
  res.status(500).json({ success: false, error: 'Server internal error' });
});

app.get('*', (req: Request, res: Response) => {
  if (req.path.startsWith('/api')) {
    res.status(404).json({ success: false, error: 'API not found' });
  } else {
    res.sendFile(path.join(__dirname, '../dist/index.html'));
  }
});

export default app;