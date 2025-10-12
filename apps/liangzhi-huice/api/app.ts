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
app.use('/api/v1/symbols', klineRoutes);
app.use('/api/v1/timeframes', klineRoutes);
app.use('/api/v1/signals', klineRoutes);
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