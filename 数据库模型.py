#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测结果数据库模型
支持SQLite数据库，用于持久化回测结果
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import uuid

class 回测数据库:
    def __init__(self, db_path: str = "回测结果.db"):
        """初始化数据库连接"""
        self.db_path = db_path
        self.初始化数据库()
    
    def 初始化数据库(self):
        """创建数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建回测结果表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS 回测结果 (
                    id TEXT PRIMARY KEY,
                    策略名称 TEXT NOT NULL,
                    交易对 TEXT NOT NULL,
                    时间周期 TEXT NOT NULL,
                    开始日期 TEXT NOT NULL,
                    结束日期 TEXT NOT NULL,
                    初始资金 REAL NOT NULL,
                    杠杆倍数 INTEGER NOT NULL,
                    价差阈值 REAL NOT NULL,
                    总收益率 REAL NOT NULL,
                    最大回撤 REAL NOT NULL,
                    夏普比率 REAL NOT NULL,
                    交易次数 INTEGER NOT NULL,
                    胜率 REAL NOT NULL,
                    最终资金 REAL NOT NULL,
                    创建时间 TEXT NOT NULL,
                    参数配置 TEXT NOT NULL,
                    交易记录 TEXT NOT NULL,
                    权益曲线 TEXT NOT NULL
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_创建时间 ON 回测结果(创建时间)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_策略名称 ON 回测结果(策略名称)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_交易对 ON 回测结果(交易对)')
            
            conn.commit()
    
    def 保存回测结果(self, 回测参数: Dict, 回测结果: Dict) -> str:
        """保存回测结果到数据库"""
        try:
            回测id = str(uuid.uuid4())
            创建时间 = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO 回测结果 (
                        id, 策略名称, 交易对, 时间周期, 开始日期, 结束日期,
                        初始资金, 杠杆倍数, 价差阈值, 总收益率, 最大回撤, 夏普比率,
                        交易次数, 胜率, 最终资金, 创建时间, 参数配置, 交易记录, 权益曲线
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    回测id,
                    回测参数.get('strategy', '网格做市策略'),
                    回测参数.get('symbol', 'ETH/USDC'),
                    回测参数.get('timeframe', '1小时'),
                    回测参数.get('start_date', ''),
                    回测参数.get('end_date', ''),
                    回测参数.get('initial_capital', 10000),
                    回测参数.get('leverage', 5),
                    回测参数.get('spread_threshold', 0.002),
                    回测结果.get('total_return', 0),
                    回测结果.get('max_drawdown', 0),
                    回测结果.get('sharpe_ratio', 0),
                    回测结果.get('total_trades', 0),
                    回测结果.get('win_rate', 0),
                    回测结果.get('final_capital', 0),
                    创建时间,
                    json.dumps(回测参数, ensure_ascii=False),
                    json.dumps(回测结果.get('trades', []), ensure_ascii=False),
                    json.dumps(回测结果.get('equity_curve', []), ensure_ascii=False)
                ))
                
                conn.commit()
                print(f"✅ 回测结果已保存到数据库，ID: {回测id}")
                return 回测id
                
        except Exception as e:
            print(f"❌ 保存回测结果失败: {e}")
            return ""
    
    def 获取回测结果(self, 回测id: str) -> Optional[Dict]:
        """根据ID获取回测结果"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM 回测结果 WHERE id = ?', (回测id,))
                row = cursor.fetchone()
                
                if row:
                    return self._行转字典(cursor, row)
                return None
                
        except Exception as e:
            print(f"❌ 获取回测结果失败: {e}")
            return None
    
    def 获取回测历史(self, 限制数量: int = 50) -> List[Dict]:
        """获取回测历史记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM 回测结果 
                    ORDER BY 创建时间 DESC 
                    LIMIT ?
                ''', (限制数量,))
                
                rows = cursor.fetchall()
                return [self._行转字典(cursor, row) for row in rows]
                
        except Exception as e:
            print(f"❌ 获取回测历史失败: {e}")
            return []
    
    def 删除回测结果(self, 回测id: str) -> bool:
        """删除指定的回测结果"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM 回测结果 WHERE id = ?', (回测id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    print(f"✅ 回测结果已删除，ID: {回测id}")
                    return True
                else:
                    print(f"⚠️ 未找到回测结果，ID: {回测id}")
                    return False
                    
        except Exception as e:
            print(f"❌ 删除回测结果失败: {e}")
            return False
    
    def 搜索回测结果(self, 策略名称: str = None, 交易对: str = None, 
                    开始日期: str = None, 结束日期: str = None) -> List[Dict]:
        """搜索回测结果"""
        try:
            conditions = []
            params = []
            
            if 策略名称:
                conditions.append('策略名称 LIKE ?')
                params.append(f'%{策略名称}%')
            
            if 交易对:
                conditions.append('交易对 = ?')
                params.append(交易对)
            
            if 开始日期:
                conditions.append('创建时间 >= ?')
                params.append(开始日期)
            
            if 结束日期:
                conditions.append('创建时间 <= ?')
                params.append(结束日期)
            
            where_clause = ' AND '.join(conditions) if conditions else '1=1'
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    SELECT * FROM 回测结果 
                    WHERE {where_clause}
                    ORDER BY 创建时间 DESC
                ''', params)
                
                rows = cursor.fetchall()
                return [self._行转字典(cursor, row) for row in rows]
                
        except Exception as e:
            print(f"❌ 搜索回测结果失败: {e}")
            return []
    
    def _行转字典(self, cursor, row) -> Dict:
        """将数据库行转换为字典"""
        columns = [description[0] for description in cursor.description]
        result = dict(zip(columns, row))
        
        # 解析JSON字段
        try:
            result['参数配置'] = json.loads(result['参数配置'])
            result['交易记录'] = json.loads(result['交易记录'])
            result['权益曲线'] = json.loads(result['权益曲线'])
        except:
            pass
        
        return result
    
    def 获取统计信息(self) -> Dict:
        """获取数据库统计信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 总回测次数
                cursor.execute('SELECT COUNT(*) FROM 回测结果')
                总回测次数 = cursor.fetchone()[0]
                
                # 平均收益率
                cursor.execute('SELECT AVG(总收益率) FROM 回测结果')
                平均收益率 = cursor.fetchone()[0] or 0
                
                # 最佳收益率
                cursor.execute('SELECT MAX(总收益率) FROM 回测结果')
                最佳收益率 = cursor.fetchone()[0] or 0
                
                # 最差收益率
                cursor.execute('SELECT MIN(总收益率) FROM 回测结果')
                最差收益率 = cursor.fetchone()[0] or 0
                
                return {
                    '总回测次数': 总回测次数,
                    '平均收益率': 平均收益率,
                    '最佳收益率': 最佳收益率,
                    '最差收益率': 最差收益率,
                    '数据库大小': os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                }
                
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
            return {}

# 全局数据库实例
数据库 = 回测数据库()

if __name__ == '__main__':
    # 测试数据库功能
    print("🔧 测试数据库功能...")
    
    # 测试保存
    测试参数 = {
        'strategy': '网格做市策略',
        'symbol': 'ETH/USDC',
        'timeframe': '1小时',
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'initial_capital': 10000,
        'leverage': 5,
        'spread_threshold': 0.002
    }
    
    测试结果 = {
        'total_return': 1.5,
        'max_drawdown': 0.2,
        'sharpe_ratio': 1.8,
        'total_trades': 100,
        'win_rate': 0.6,
        'final_capital': 25000,
        'trades': [{'timestamp': 1234567890, 'side': 'buy', 'amount': 1.0, 'price': 2000}],
        'equity_curve': [{'timestamp': 1234567890, 'equity': 10000}]
    }
    
    回测id = 数据库.保存回测结果(测试参数, 测试结果)
    
    if 回测id:
        # 测试获取
        结果 = 数据库.获取回测结果(回测id)
        print(f"📊 获取结果: {结果['策略名称'] if 结果 else 'None'}")
        
        # 测试统计
        统计 = 数据库.获取统计信息()
        print(f"📈 统计信息: {统计}")
        
        print("✅ 数据库功能测试完成")
    else:
        print("❌ 数据库功能测试失败")
