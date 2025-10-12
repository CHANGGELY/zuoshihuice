#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
H5文件读取脚本
用于从H5文件中读取K线数据
"""

import sys
import json
import h5py
import numpy as np
from datetime import datetime
import os

def read_h5_data(file_path, start_time=None, end_time=None, limit=1000, from_end=False):
    """
    从H5文件读取K线数据
    
    Args:
        file_path: H5文件路径
        start_time: 开始时间戳（毫秒）
        end_time: 结束时间戳（毫秒）
        limit: 最大返回记录数
    
    Returns:
        dict: 包含success和data字段的结果
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"H5文件不存在: {file_path}"
            }
        
        # 打开H5文件
        with h5py.File(file_path, 'r') as f:
            # 获取kline_data数据集
            kline_data = f['kline_data'][:]
            
            # 解析数据列：[open_time_ms, open, high, low, close, volume, close_time_ms, quote_asset_volume]
            timestamps_ms = kline_data[:, 0]  # open_time_ms，已经是毫秒时间戳
            open_data = kline_data[:, 1]      # open
            high_data = kline_data[:, 2]      # high
            low_data = kline_data[:, 3]       # low
            close_data = kline_data[:, 4]     # close
            volume_data = kline_data[:, 5]    # volume
            
            # 应用时间过滤
            mask = np.ones(len(timestamps_ms), dtype=bool)
            
            if start_time is not None and start_time != 'null':
                start_time = int(start_time)
                mask &= (timestamps_ms >= start_time)
            
            if end_time is not None and end_time != 'null':
                end_time = int(end_time)
                mask &= (timestamps_ms <= end_time)
            
            # 应用过滤
            filtered_timestamps = timestamps_ms[mask]
            filtered_open = open_data[mask]
            filtered_high = high_data[mask]
            filtered_low = low_data[mask]
            filtered_close = close_data[mask]
            filtered_volume = volume_data[mask]
            
            # 应用限制
            if len(filtered_timestamps) > limit:
                if from_end:
                    # 从末尾取数据
                    filtered_timestamps = filtered_timestamps[-limit:]
                    filtered_open = filtered_open[-limit:]
                    filtered_high = filtered_high[-limit:]
                    filtered_low = filtered_low[-limit:]
                    filtered_close = filtered_close[-limit:]
                    filtered_volume = filtered_volume[-limit:]
                else:
                    # 从开头取数据
                    filtered_timestamps = filtered_timestamps[:limit]
                    filtered_open = filtered_open[:limit]
                    filtered_high = filtered_high[:limit]
                    filtered_low = filtered_low[:limit]
                    filtered_close = filtered_close[:limit]
                    filtered_volume = filtered_volume[:limit]
            
            # 构建结果数据
            data = []
            for i in range(len(filtered_timestamps)):
                data.append({
                    "timestamp": int(filtered_timestamps[i]),
                    "open": float(filtered_open[i]),
                    "high": float(filtered_high[i]),
                    "low": float(filtered_low[i]),
                    "close": float(filtered_close[i]),
                    "volume": float(filtered_volume[i])
                })
            
            return {
                "success": True,
                "data": data
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"读取H5文件失败: {str(e)}"
        }

def main():
    """
    主函数，处理命令行参数
    """
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "缺少必要参数: file_path"
        }))
        sys.exit(1)
    
    file_path = sys.argv[1]
    start_time = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != 'null' else None
    end_time = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != 'null' else None
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 1000
    from_end = sys.argv[5] == 'true' if len(sys.argv) > 5 else False
    
    result = read_h5_data(file_path, start_time, end_time, limit, from_end)
    print(json.dumps(result))

if __name__ == "__main__":
    main()