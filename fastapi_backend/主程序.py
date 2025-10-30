from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Literal
import asyncio
import json
import os
import sys
import tempfile
import subprocess
from pathlib import Path
import uvicorn

from .设置 import 配置

# =============================
# 数据模型（类名中文，字段保持英文，避免前端破坏）
# =============================
class K线(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    quote_volume: float

class K线响应(BaseModel):
    success: bool
    symbol: str
    start_date: str
    end_date: str
    timeframe: Literal['1m','1h','1d','1M']
    count: int
    klines: List[K线]
    source: str

class 回测参数(BaseModel):
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

class 进度响应(BaseModel):
    progress: float
    message: str

# =============================
# 应用与静态资源
# =============================
应用 = FastAPI(title="回测接口", version="0.2.0")
静态目录 = Path(__file__).parent / "static"
try:
    应用.mount("/static", StaticFiles(directory=str(静态目录)), name="static")
except Exception:
    pass

@应用.get("/")
def 首页():
    首页文件 = 静态目录 / "index.html"
    if 首页文件.exists():
        return FileResponse(首页文件)
    return JSONResponse({"status": "ok", "message": "index.html not found"})

# =============================
# 运行态对象
# =============================
正在运行的回测任务: Optional[asyncio.Task] = None

# =============================
# 健康与进度
# =============================
@应用.get("/health")
def 健康():
    return {"status": "ok"}

@应用.get("/progress", response_model=进度响应)
def 获取进度():
    try:
        进度文件 = 配置.缓存目录 / "progress.json"
        if 进度文件.exists():
            with open(进度文件, 'r', encoding='utf-8') as f:
                数据 = json.load(f)
            return 进度响应(
                progress=float(数据.get('progress', 0)),
                message=str(数据.get('message', '等待中...'))
            )
        else:
            return 进度响应(progress=0, message='等待中...')
    except Exception as e:
        return 进度响应(progress=0, message=f'获取进度失败: {str(e)}')

# =============================
# K线数据（参数化 + 缓存）
# =============================
@应用.get("/klines", response_model=K线响应)
def 获取K线(symbol: str, start_date: str, end_date: str, timeframe: Literal['1m','1h','1d','1M'] = '1m'):
    try:
        import pandas as pd
        import pickle

        数据目录 = 配置.数据目录
        候选文件 = list(数据目录.glob(f"{symbol}_1m_*.h5"))
        if 候选文件:
            数据文件 = 候选文件[0]
        else:
            数据文件 = 数据目录 / "ETHUSDT_1m_2019-11-01_to_2025-06-15.h5"

        缓存目录 = 配置.缓存目录 / "klines" / symbol
        缓存目录.mkdir(parents=True, exist_ok=True)
        周期缓存名 = {
            '1m': f'{symbol}_1m_processed.pkl',
            '1h': f'{symbol}_1h_processed.pkl',
            '1d': f'{symbol}_1d_processed.pkl',
            '1M': f'{symbol}_1M_processed.pkl'
        }

        # 先用周期缓存（再按时间过滤）
        缓存文件 = 缓存目录 / 周期缓存名.get(timeframe, '')
        if 缓存文件.exists():
            with open(缓存文件, 'rb') as f:
                缓存数据 = pickle.load(f)
            起始 = int(pd.to_datetime(start_date).timestamp())
            结束 = int(pd.to_datetime(end_date).timestamp())
            过滤后 = [k for k in 缓存数据 if 起始 <= k['time'] <= 结束]
            for k in 过滤后:
                k['timestamp'] = k['time']
                k['quote_volume'] = k['volume'] * k['close']
            return K线响应(
                success=True,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                timeframe=timeframe,
                count=len(过滤后),
                klines=[K线(**{
                    'timestamp': k['timestamp'],
                    'open': k['open'],
                    'high': k['high'],
                    'low': k['low'],
                    'close': k['close'],
                    'volume': k['volume'],
                    'quote_volume': k['quote_volume'],
                }) for k in 过滤后],
                source='cache'
            )

        # 缓存不存在，读取源数据
        if not 数据文件.exists():
            raise HTTPException(status_code=404, detail=f"数据文件不存在: {数据文件}")
        df = pd.read_hdf(数据文件, key='klines')
        起始 = int(pd.to_datetime(start_date).timestamp())
        结束 = int(pd.to_datetime(end_date).timestamp())
        if df['timestamp'].dtype == 'datetime64[ns]':
            df['timestamp'] = df['timestamp'].astype('int64') // 10**9
        掩码 = (df['timestamp'] >= 起始) & (df['timestamp'] <= 结束)
        子集 = df[掩码].copy()
        if len(子集) == 0:
            raise HTTPException(status_code=400, detail=f"指定时间范围内没有数据: {start_date} 到 {end_date}")
        if timeframe != '1m':
            规则映射 = {'1h': '1h', '1d': '1D', '1M': '1M'}
            子集['datetime'] = pd.to_datetime(子集['timestamp'], unit='s')
            子集.set_index('datetime', inplace=True)
            重采样 = 子集.resample(规则映射[timeframe]).agg({
                'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'
            }).dropna().reset_index()
            重采样['timestamp'] = 重采样['datetime'].astype('int64') // 10**9
            子集 = 重采样
        序列 = []
        for _, 行 in 子集.iterrows():
            成交额 = 行.get('quote_volume', 行['volume'] * 行['close'])
            序列.append(K线(
                timestamp=int(行['timestamp']),
                open=float(行['open']),
                high=float(行['high']),
                low=float(行['low']),
                close=float(行['close']),
                volume=float(行['volume']),
                quote_volume=float(成交额)
            ))
        return K线响应(
            success=True,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            timeframe=timeframe,
            count=len(序列),
            klines=序列,
            source='realtime'
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================
# 回测（异步子进程 + 进度文件）
# =============================
@应用.post("/backtest")
async def 启动回测(参数: 回测参数, 后台任务: BackgroundTasks):
    global 正在运行的回测任务
    if 正在运行的回测任务 and not 正在运行的回测任务.done():
        raise HTTPException(status_code=409, detail="已有回测正在运行，请等待完成")

    # 临时参数文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        回测参数字典 = {
            'symbol': 参数.symbol,
            'startDate': 参数.startDate,
            'endDate': 参数.endDate,
            'initialCapital': 参数.initialCapital,
            'leverage': 参数.leverage,
            'bidSpread': 参数.bidSpread,
            'askSpread': 参数.askSpread,
            'positionSizeRatio': 参数.positionSizeRatio,
            'maxPositionRatio': 参数.maxPositionRatio,
            'orderRefreshTime': 参数.orderRefreshTime,
            'useDynamicOrderSize': 参数.useDynamicOrderSize,
            'minOrderAmount': 参数.minOrderAmount,
            'maxOrderAmount': 参数.maxOrderAmount,
            'positionStopLoss': 参数.positionStopLoss,
            'enablePositionStopLoss': 参数.enablePositionStopLoss,
            'positionMode': 参数.positionMode,
            'makerFee': 参数.makerFee,
            'takerFee': 参数.takerFee,
            'useFeeRebate': 参数.useFeeRebate,
            'rebateRate': 参数.rebateRate,
        }
        json.dump(回测参数字典, f, ensure_ascii=False, indent=2)
        参数文件路径 = f.name

    # 初始化进度
    进度文件 = 配置.缓存目录 / "progress.json"
    with open(进度文件, 'w', encoding='utf-8') as f:
        json.dump({'progress': 0, 'message': '准备回测参数...'}, f, ensure_ascii=False)

    # 启动异步任务
    正在运行的回测任务 = asyncio.create_task(
        _执行回测子进程(参数文件路径, 后台任务)
    )
    return {"status": "accepted", "message": "回测已启动，请通过/progress查询进度"}

async def _执行回测子进程(参数文件路径: str, 后台任务: BackgroundTasks):
    try:
        项目根 = Path(__file__).parent.parent
        命令 = [
            sys.executable, '-X', 'utf8',
            str(项目根 / "进度回测执行器.py"),
            "--params-file", 参数文件路径,
        ]
        进程 = await asyncio.create_subprocess_exec(
            *命令,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(项目根)
        )
        asyncio.create_task(_监控进度(进程.stderr))
        标准输出, 标准错误 = await 进程.communicate()

        if 进程.returncode == 0:
            try:
                结果 = json.loads(标准输出.decode('utf-8'))
                进度数据 = {'progress': 100, 'message': '回测完成', 'result': 结果}
            except json.JSONDecodeError:
                进度数据 = {'progress': 100, 'message': '回测完成但结果解析失败', 'error': '结果格式错误'}
        else:
            错误文本 = 标准错误.decode('utf-8', errors='ignore')
            进度数据 = {'progress': 0, 'message': f'回测失败: {错误文本}', 'error': 错误文本}

        进度文件 = 配置.缓存目录 / "progress.json"
        with open(进度文件, 'w', encoding='utf-8') as f:
            json.dump(进度数据, f, ensure_ascii=False, indent=2)
    except Exception as e:
        进度数据 = {'progress': 0, 'message': f'执行回测时发生错误: {str(e)}', 'error': str(e)}
        进度文件 = 配置.缓存目录 / "progress.json"
        with open(进度文件, 'w', encoding='utf-8') as f:
            json.dump(进度数据, f, ensure_ascii=False, indent=2)
    finally:
        后台任务.add_task(_清理临时文件, 参数文件路径)

async def _监控进度(标准错误管道):
    try:
        while True:
            行 = await 标准错误管道.readline()
            if not 行:
                break
            文本 = 行.decode('utf-8', errors='ignore').strip()
            if 文本.startswith('PROGRESS:'):
                部分 = 文本.split(':')
                if len(部分) >= 4:
                    try:
                        百分比 = float(部分[2].replace('%', ''))
                        状态 = 部分[3] if len(部分) > 3 else '处理中...'
                        进度文件 = 配置.缓存目录 / "progress.json"
                        with open(进度文件, 'w', encoding='utf-8') as f:
                            json.dump({'progress': 百分比, 'message': 状态}, f, ensure_ascii=False, indent=2)
                    except (ValueError, IndexError):
                        pass
    except Exception:
        pass

def _清理临时文件(文件路径: str):
    try:
        os.unlink(文件路径)
    except Exception:
        pass

if __name__ == "__main__":
    uvicorn.run("fastapi_backend.主程序:应用", host="0.0.0.0", port=8000, reload=False)
