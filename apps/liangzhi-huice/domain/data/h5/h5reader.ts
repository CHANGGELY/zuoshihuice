import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';
import { DEFAULT_CONFIG } from '../../../config/default.js';

export interface TimeRange {
  minTs: number;
  maxTs: number;
}

export interface KlineData {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export class H5Reader {
  private h5FilePath: string;
  private backupPath: string;

  constructor() {
    this.h5FilePath = DEFAULT_CONFIG.data.h5FilePath;
    this.backupPath = DEFAULT_CONFIG.data.h5BackupPath;
  }

  private validateH5File(): string {
    if (this.h5FilePath && fs.existsSync(this.h5FilePath)) {
      return this.h5FilePath;
    }
    if (this.backupPath && fs.existsSync(this.backupPath)) {
      console.warn(`主H5文件不存在，使用备份文件: ${this.backupPath}`);
      return this.backupPath;
    }
    throw new Error(`H5文件不存在: ${this.h5FilePath || 'N/A'}`);
  }

  private getPythonExecutable(): string {
    if (process.platform === 'win32') {
      return path.join(process.cwd(), '.venv', 'Scripts', 'python.exe');
    }
    return path.join(process.cwd(), '.venv', 'bin', 'python');
  }

  private runPython(filePath: string, start: string, end: string, limit: string, fromEnd: boolean): Promise<KlineData[]> {
    return new Promise((resolve, reject) => {
      const pythonScript = path.join(process.cwd(), 'api', 'scripts', 'read_h5.py');
      const pythonExec = this.getPythonExecutable();

      const args = [
        pythonScript,
        filePath,
        start,
        end,
        limit,
        fromEnd ? 'true' : 'false'
      ];

      const child = spawn(pythonExec, args, { stdio: ['pipe', 'pipe', 'pipe'] });

      let stdout = '';
      let stderr = '';

      child.stdout.on('data', (d) => (stdout += d.toString()));
      child.stderr.on('data', (d) => (stderr += d.toString()));

      child.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`读取H5数据失败: ${stderr || '未知错误'}`));
          return;
        }
        try {
          const result = JSON.parse(stdout.trim());
          if (!result.success) {
            reject(new Error(result.error || '读取失败'));
            return;
          }
          resolve((result.data || []) as KlineData[]);
        } catch (e) {
          const errorMessage = e instanceof Error ? e.message : '未知错误';
          reject(new Error(`解析H5数据失败: ${errorMessage}`));
        }
      });

      child.on('error', (err) => {
        reject(new Error(`启动Python进程失败: ${err.message}`));
      });
    });
  }

  async getTimeRange(): Promise<TimeRange> {
    const filePath = this.validateH5File();

    const [firstRows, lastRows] = await Promise.all([
      this.runPython(filePath, 'null', 'null', '1', false),
      this.runPython(filePath, 'null', 'null', '1', true)
    ]);

    if (!firstRows.length || !lastRows.length) {
      throw new Error('H5文件中没有数据');
    }

    const minTs = firstRows[0].timestamp;
    const maxTs = lastRows[lastRows.length - 1].timestamp;
    return { minTs, maxTs };
  }

  async readData(startTime: number, endTime: number, limit = 1000): Promise<KlineData[]> {
    const filePath = this.validateH5File();
    const rows = await this.runPython(
      filePath,
      startTime?.toString?.() || 'null',
      endTime?.toString?.() || 'null',
      limit.toString(),
      false
    );
    return rows;
  }
}
