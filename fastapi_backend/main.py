from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any
import os
import json
import tempfile
import subprocess
import sys
import asyncio
import uvicorn
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .settings import settings

# Models
class Kline(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    quote_volume: float

class KlinesResponse(BaseModel):
    success: bool
    symbol: str
    start_date: str
    end_date: str
    timeframe: Literal['1m','1h','1d','1M']
    count: int
    klines: List[Kline]
    source: str

class BacktestParams(BaseModel):
    symbol: str
    startDate: str
    endDate: str
    initialCapital: float
    leverage: int
    bidSpread: Optional[float] = 0.002
    askSpread: Optional[float] = 0.002
    positionSizeRatio: Optional[float] = 0.02
    maxPositionRatio: Optional[float] = 0.8
    orderRefreshTime: Optional[float] = 30.0
    useDynamicOrderSize: Optional[bool] = True
    minOrderAmount: Optional[float] = 0.008
    maxOrderAmount: Optional[float] = 99.0
    positionStopLoss: Optional[float] = 0.05
    enablePositionStopLoss: Optional[bool] = False
    positionMode: Optional[str] = 'Hedge'
    makerFee: Optional[float] = 0.0002
    takerFee: Optional[float] = 0.0005
    useFeeRebate: Optional[bool] = True
    rebateRate: Optional[float] = 0.30

class BacktestResult(BaseModel):
    success: bool
    total_return: float
    final_equity: float
    max_drawdown: float
    liquidated: bool

class ProgressResponse(BaseModel):
    progress: float
    message: str

app = FastAPI(title="Backtest API", version="0.1.0")

# 静态资源目录与首页
STATIC_DIR = Path(__file__).parent / "static"
try:
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
except Exception:
    pass

@app.get("/")
def index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse({"status": "ok", "message": "index.html not found"})

# 存储运行中的回测任务
running_backtest_task: Optional[asyncio.Task] = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/progress", response_model=ProgressResponse)
def get_progress():
    """获取回测进度"""
    try:
        progress_file = settings.CACHE_DIR / "progress.json"
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
            return ProgressResponse(
                progress=float(progress_data.get('progress', 0)),
                message=str(progress_data.get('message', '等待中...'))
            )
        else:
            return ProgressResponse(progress=0, message='等待中...')
    except Exception as e:
        return ProgressResponse(progress=0, message=f'获取进度失败: {str(e)}')

@app.get("/klines", response_model=KlinesResponse)
def get_klines(symbol: str, start_date: str, end_date: str, timeframe: Literal['1m','1h','1d','1M'] = '1m'):
    try:
        # 调用现有后端脚本逻辑（直接复用文件结构与缓存格式）
        import types
        import pandas as pd

        # 直接复用其静态方法能力：构造query_params字典后调用其处理逻辑中的核心代码
        # 为隔离副作用，这里复制核心过滤与重采样流程（未来会重构为data模块公用函数）
        from pathlib import Path
        import pickle

        # 动态发现数据文件（匹配 {symbol}_1m_*.h5），找不到则回退到默认样例
        data_dir = settings.DATA_DIR
        candidates = list(data_dir.glob(f"{symbol}_1m_*.h5"))
        if candidates:
            data_file = candidates[0]
        else:
            data_file = data_dir / "ETHUSDT_1m_2019-11-01_to_2025-06-15.h5"

        # 缓存目录移动到 CACHE_DIR，按 symbol/timeframe 组织
        cache_dir = settings.CACHE_DIR / "klines" / symbol
        cache_dir.mkdir(parents=True, exist_ok=True)
        timeframe_cache = {
            '1m': f'{symbol}_1m_processed.pkl',
            '1h': f'{symbol}_1h_processed.pkl',
            '1d': f'{symbol}_1d_processed.pkl',
            '1M': f'{symbol}_1M_processed.pkl'
        }

        # 先尝试缓存
        cache_file = cache_dir / timeframe_cache.get(timeframe, '')
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
            start_ts = int(pd.to_datetime(start_date).timestamp())
            end_ts = int(pd.to_datetime(end_date).timestamp())
            filtered_klines = [k for k in cached_data if start_ts <= k['time'] <= end_ts]
            for k in filtered_klines:
                k['timestamp'] = k['time']
                k['quote_volume'] = k['volume'] * k['close']
            return KlinesResponse(
                success=True,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                timeframe=timeframe,
                count=len(filtered_klines),
                klines=[Kline(**{
                    'timestamp': k['timestamp'],
                    'open': k['open'],
                    'high': k['high'],
                    'low': k['low'],
                    'close': k['close'],
                    'volume': k['volume'],
                    'quote_volume': k['quote_volume'],
                }) for k in filtered_klines],
                source='cache'
            )

        # 回退到原始数据
        if not data_file.exists():
            raise HTTPException(status_code=404, detail=f"数据文件不存在: {data_file}")
        df = pd.read_hdf(data_file, key='klines')
        start_ts = int(pd.to_datetime(start_date).timestamp())
        end_ts = int(pd.to_datetime(end_date).timestamp())
        if df['timestamp'].dtype == 'datetime64[ns]':
            df['timestamp'] = df['timestamp'].astype('int64') // 10**9
        mask = (df['timestamp'] >= start_ts) & (df['timestamp'] <= end_ts)
        filtered_df = df[mask].copy()
        if len(filtered_df) == 0:
            raise HTTPException(status_code=400, detail=f"指定时间范围内没有数据: {start_date} 到 {end_date}")
        if timeframe != '1m':
            # 临时内联重采样（后续抽到 data.resample）
            resample_rules = {'1h': '1h', '1d': '1D', '1M': '1M'}
            filtered_df['datetime'] = pd.to_datetime(filtered_df['timestamp'], unit='s')
            filtered_df.set_index('datetime', inplace=True)
            resampled = filtered_df.resample(resample_rules[timeframe]).agg({
                'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
            }).dropna().reset_index()
            resampled['timestamp'] = resampled['datetime'].astype('int64') // 10**9
            filtered_df = resampled
        klines = []
        for _, row in filtered_df.iterrows():
            quote_volume = row.get('quote_volume', row['volume'] * row['close'])
            klines.append(Kline(
                timestamp=int(row['timestamp']),
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=float(row['volume']),
                quote_volume=float(quote_volume)
            ))
        return KlinesResponse(
            success=True,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            timeframe=timeframe,
            count=len(klines),
            klines=klines,
            source='realtime'
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backtest")
async def run_backtest(params: BacktestParams, background_tasks: BackgroundTasks):
    """异步执行回测，支持进度轮询"""
    global running_backtest_task
    
    # 检查是否有正在运行的回测
    if running_backtest_task and not running_backtest_task.done():
        raise HTTPException(status_code=409, detail="已有回测正在运行，请等待完成")
    
    # 创建临时参数文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        # 转换为旧后端期望的格式
        backtest_params = {
            'symbol': params.symbol,
            'startDate': params.startDate,
            'endDate': params.endDate,
            'initialCapital': params.initialCapital,
            'leverage': params.leverage,
            'bidSpread': params.bidSpread,
            'askSpread': params.askSpread,
            'positionSizeRatio': params.positionSizeRatio,
            'maxPositionRatio': params.maxPositionRatio,
            'orderRefreshTime': params.orderRefreshTime,
            'useDynamicOrderSize': params.useDynamicOrderSize,
            'minOrderAmount': params.minOrderAmount,
            'maxOrderAmount': params.maxOrderAmount,
            'positionStopLoss': params.positionStopLoss,
            'enablePositionStopLoss': params.enablePositionStopLoss,
            'positionMode': params.positionMode,
            'makerFee': params.makerFee,
            'takerFee': params.takerFee,
            'useFeeRebate': params.useFeeRebate,
            'rebateRate': params.rebateRate
        }
        json.dump(backtest_params, f, ensure_ascii=False, indent=2)
        params_file = f.name
    
    # 初始化进度文件
    progress_file = settings.CACHE_DIR / "progress.json"
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump({'progress': 0, 'message': '准备回测参数...'}, f, ensure_ascii=False)
    
    # 启动异步回测任务
    running_backtest_task = asyncio.create_task(
        _execute_backtest_subprocess(params_file, background_tasks)
    )
    
    return {"status": "accepted", "message": "回测已启动，请通过/progress查询进度"}

async def _execute_backtest_subprocess(params_file: str, background_tasks: BackgroundTasks):
    """在后台执行回测子进程"""
    try:
        # 构建命令
        project_root = Path(__file__).parent.parent
        cmd = [
            sys.executable, '-X', 'utf8',
            str(project_root / "进度回测执行器.py"),
            "--params-file", params_file
        ]
        
        # 执行子进程
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(project_root)
        )
        
        # 监控stderr输出并更新progress.json
        asyncio.create_task(_monitor_progress(process.stderr))
        
        # 等待子进程完成
        stdout, stderr = await process.communicate()
        
        # 解析结果并写入progress.json
        if process.returncode == 0:
            try:
                result = json.loads(stdout.decode('utf-8'))
                progress_data = {
                    'progress': 100,
                    'message': '回测完成',
                    'result': result
                }
            except json.JSONDecodeError:
                progress_data = {
                    'progress': 100,
                    'message': '回测完成但结果解析失败',
                    'error': '结果格式错误'
                }
        else:
            progress_data = {
                'progress': 0,
                'message': f'回测失败: {stderr.decode("utf-8", errors="ignore")}',
                'error': stderr.decode('utf-8', errors='ignore')
            }
        
        # 更新最终进度
        progress_file = settings.CACHE_DIR / "progress.json"
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        # 错误处理
        progress_data = {
            'progress': 0,
            'message': f'执行回测时发生错误: {str(e)}',
            'error': str(e)
        }
        progress_file = settings.CACHE_DIR / "progress.json"
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
    finally:
        # 清理临时文件
        background_tasks.add_task(_cleanup_temp_file, params_file)

async def _monitor_progress(stderr):
    """监控stderr输出并更新progress.json"""
    try:
        while True:
            line = await stderr.readline()
            if not line:
                break
            
            line_str = line.decode('utf-8', errors='ignore').strip()
            if line_str.startswith('PROGRESS:'):
                # 解析进度信息: PROGRESS:current/total:percentage%:status:ETA:eta_seconds
                parts = line_str.split(':')
                if len(parts) >= 4:
                    try:
                        # 提取进度百分比
                        percentage_part = parts[2]  # "percentage%"
                        percentage = float(percentage_part.replace('%', ''))
                        
                        # 提取状态消息
                        status = parts[3] if len(parts) > 3 else '处理中...'
                        
                        # 更新progress.json
                        progress_data = {
                            'progress': percentage,
                            'message': status
                        }
        progress_file = settings.CACHE_DIR / "progress.json"
        with open(progress_file, 'w', encoding='utf-8') as f:
                            json.dump(progress_data, f, ensure_ascii=False, indent=2)
                            
                    except (ValueError, IndexError):
                        pass  # 忽略格式错误的进度行
    except Exception:
        pass  # 忽略监控错误

def _cleanup_temp_file(file_path: str):
    """清理临时文件"""
    try:
        os.unlink(file_path)
    except Exception:
        pass

if __name__ == "__main__":
    uvicorn.run("fastapi_backend.main:app", host="0.0.0.0", port=8000, reload=False)