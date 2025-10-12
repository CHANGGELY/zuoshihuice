import * as h5wasm from 'h5wasm';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const backtestDataDir = path.resolve(__dirname, '..', '..', 'services', 'backtest-engine');
const defaultH5Path = path.resolve(backtestDataDir, 'ethusdt_1m_2019-11-01_to_2025-06-15.h5');

const H5_FILE_PATH = process.env.H5_FILE_PATH || defaultH5Path;

async function exploreH5File() {
  try {
    await h5wasm.ready;
    const fileBuffer = fs.readFileSync(H5_FILE_PATH);
    const f = new h5wasm.File(fileBuffer, 'r');

    const required = ['timestamp', 'open', 'high', 'low', 'close', 'volume'];
    const optional = ['turnover', 'amount', 'quote_volume', 'quoteVolume', 'quote_asset_volume'];

    // 检查必需字段
    console.log('Required datasets presence:');
    const present = new Map();
    for (const k of required) {
      try {
        const item = f.get(k);
        const len = item?.value?.length ?? 0;
        present.set(k, len > 0);
      } catch {
        present.set(k, false);
      }
      console.log(` - ${k}: ${present.get(k) ? 'YES' : 'NO'}`);
    }

    // 检查可选字段（成交额）
    console.log('Optional datasets presence:');
    const foundOptionals = [];
    for (const k of optional) {
      try {
        const item = f.get(k);
        const len = item?.value?.length ?? 0;
        if (len > 0) {
          foundOptionals.push(k);
          console.log(` - ${k}: YES (len=${len})`);
        } else {
          console.log(` - ${k}: NO`);
        }
      } catch {
        console.log(` - ${k}: NO`);
      }
    }

    // 预览
    const previewKeys = [...required, ...foundOptionals];
    for (const key of previewKeys) {
      try {
        const item = f.get(key);
        const shape = item?.shape ?? [];
        const dtype = item?.dtype ?? 'unknown';
        console.log(`\n[${key}] shape=${shape} dtype=${dtype}`);
        const values = item?.value;
        const max = Math.min(5, (values?.length ?? 0));
        for (let i = 0; i < max; i++) {
          console.log(values[i]);
        }
      } catch (e) {
        console.warn(`读取数据集失败: ${key}`, e);
      }
    }

    // 选择成交额键名
    const turnoverKey = ['turnover', 'amount', 'quote_volume', 'quoteVolume', 'quote_asset_volume'].find(k => foundOptionals.includes(k)) || 'N/A';
    console.log(`\nDetected turnover key: ${turnoverKey}`);

    f.close();
  } catch (error) {
    console.error('探索H5文件失败:', error);
  }
}

exploreH5File();
