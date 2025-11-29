"""
该文件用于基础环境健康检查，确保仓库结构与 Python 环境正常。
"""

import pathlib


def test_repo_layout_exists():
    root = pathlib.Path(__file__).resolve().parents[2]
    assert (root / 'services' / 'backtest-engine' / 'backtest_kline_trajectory.py').exists()


def test_python_runtime_basic():
    import sys
    from decimal import Decimal

    assert sys.version_info.major >= 3
    # 基础 Decimal 运算精度检查
    x = Decimal('0.1') + Decimal('0.2')
    assert x == Decimal('0.3')
