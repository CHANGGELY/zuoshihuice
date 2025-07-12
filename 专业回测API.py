#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业量化回测API服务
通过独立进程调用原始回测引擎，确保100%使用原始逻辑
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import tempfile
import os
import sys
import traceback
from pathlib import Path

app = Flask(__name__)
CORS(app)

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.absolute()
BACKTEST_SCRIPT = PROJECT_ROOT / "backtest_kline_trajectory.py"

print(f"🔍 项目根目录: {PROJECT_ROOT}")
print(f"🔍 回测脚本: {BACKTEST_SCRIPT}")
print(f"🔍 回测脚本存在: {BACKTEST_SCRIPT.exists()}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'backtest_script_exists': BACKTEST_SCRIPT.exists(),
        'project_root': str(PROJECT_ROOT)
    })

@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """运行回测 - 通过独立进程调用原始回测引擎"""
    try:
        # 获取请求参数
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '缺少请求参数'
            }), 400

        print(f"📋 收到回测请求: {data}")

        # 验证回测脚本存在
        if not BACKTEST_SCRIPT.exists():
            return jsonify({
                'success': False,
                'error': f'回测脚本不存在: {BACKTEST_SCRIPT}'
            }), 500

        # 创建独立的回测执行脚本
        backtest_runner_script = create_backtest_runner(data)
        
        try:
            # 在独立进程中运行回测
            print("🚀 启动独立回测进程...")
            result = subprocess.run([
                sys.executable, backtest_runner_script
            ], 
            capture_output=True, 
            text=True, 
            timeout=600,  # 10分钟超时
            cwd=str(PROJECT_ROOT),
            encoding='utf-8'
            )

            print(f"📊 回测进程返回码: {result.returncode}")
            
            if result.returncode == 0:
                # 解析回测结果
                output = result.stdout
                print(f"📄 回测输出长度: {len(output)} 字符")
                
                # 查找结果标记
                start_marker = "BACKTEST_RESULT_START"
                end_marker = "BACKTEST_RESULT_END"
                
                start_idx = output.find(start_marker)
                end_idx = output.find(end_marker)
                
                if start_idx != -1 and end_idx != -1:
                    json_str = output[start_idx + len(start_marker):end_idx].strip()
                    print(f"✅ 找到回测结果，JSON长度: {len(json_str)}")
                    
                    try:
                        backtest_result = json.loads(json_str)
                        print(f"📈 回测成功: 收益率={backtest_result.get('total_return', 0):.4f}")
                        
                        return jsonify({
                            'success': True,
                            'data': backtest_result
                        })
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON解析失败: {e}")
                        print(f"❌ JSON内容: {json_str[:500]}...")
                        return jsonify({
                            'success': False,
                            'error': f'回测结果解析失败: {e}'
                        }), 500
                else:
                    print("❌ 未找到回测结果标记")
                    print(f"❌ 完整输出: {output[:1000]}...")
                    return jsonify({
                        'success': False,
                        'error': '回测结果格式错误'
                    }), 500
            else:
                print(f"❌ 回测进程执行失败")
                print(f"❌ stdout: {result.stdout[:500]}...")
                print(f"❌ stderr: {result.stderr[:500]}...")
                return jsonify({
                    'success': False,
                    'error': f'回测执行失败: {result.stderr}'
                }), 500

        finally:
            # 清理临时文件
            try:
                os.unlink(backtest_runner_script)
            except:
                pass

    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': '回测执行超时'
        }), 500
    except Exception as e:
        print(f"❌ API执行失败: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'API执行失败: {str(e)}'
        }), 500

def create_backtest_runner(params):
    """创建独立的回测执行脚本"""
    script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立回测执行脚本
确保100%使用原始回测引擎逻辑
"""

import sys
import os
import json
from decimal import Decimal
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

try:
    # 导入原始回测引擎
    from backtest_kline_trajectory import run_backtest_with_params, BACKTEST_CONFIG, STRATEGY_CONFIG

    print("✅ 原始回测引擎导入成功")

    # 设置回测参数
    params = {json.dumps(params)}
    
    # 更新回测配置
    BACKTEST_CONFIG.update({{
        'start_date': params.get('start_date', '2024-06-15'),
        'end_date': params.get('end_date', '2024-12-31'),
        'initial_balance': params.get('initial_capital', 10000),
    }})

    # 设置策略参数
    strategy_params = {{
        "leverage": params.get('leverage', 5),
        "bid_spread": Decimal(str(params.get('bid_spread', 0.002))),
        "ask_spread": Decimal(str(params.get('ask_spread', 0.002))),
    }}

    print(f"📊 回测配置: {{BACKTEST_CONFIG['start_date']}} -> {{BACKTEST_CONFIG['end_date']}}")
    print(f"💰 初始资金: {{BACKTEST_CONFIG['initial_balance']}} USDT")
    print(f"⚡ 杠杆倍数: {{strategy_params['leverage']}}")

    # 调用原始回测引擎 - 100%原始逻辑
    print("🚀 执行原始回测引擎...")
    result = run_backtest_with_params(strategy_params=strategy_params, use_cache=False)

    print("✅ 回测完成，输出结果...")
    
    # 输出结果（使用标记便于解析）
    print("BACKTEST_RESULT_START")
    print(json.dumps(result, default=str, ensure_ascii=False))
    print("BACKTEST_RESULT_END")

except Exception as e:
    print(f"❌ 回测执行失败: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''

    # 创建临时脚本文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(script_content)
        return f.name

if __name__ == '__main__':
    print("🚀 启动专业量化回测API服务...")
    print(f"📍 服务地址: http://localhost:8001")
    print(f"🔧 回测脚本: {BACKTEST_SCRIPT}")
    app.run(host='0.0.0.0', port=8001, debug=False)  # 关闭debug避免重启问题
