import os
import h5py
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
API_DIR = SCRIPTS_DIR.parent
APP_DIR = API_DIR.parent
REPO_ROOT = APP_DIR.parent
BACKTEST_DATA_DIR = REPO_ROOT / 'services' / 'backtest-engine'
DEFAULT_H5_PATH = BACKTEST_DATA_DIR / 'ethusdt_1m_2019-11-01_to_2025-06-15.h5'


def probe_node(node, prefix="/"):
    if isinstance(node, h5py.Dataset):
        shape = node.shape
        dtype = node.dtype
        sample = node[0:5].tolist() if len(shape) > 0 and shape[0] > 0 else None
        print(f'DATASET {prefix}: shape={shape}, dtype={dtype}, sample={sample}')
        # 打印 columns 属性（若存在），兼容 bytes/str/ndarray
        try:
            cols_attr = node.attrs.get('columns')
            cols = None
            if cols_attr is not None:
                # 延迟导入，避免无numpy环境时报错
                try:
                    import numpy as np  # type: ignore
                except Exception:
                    np = None  # noqa: N816
                if isinstance(cols_attr, (list, tuple)):
                    cols = [c.decode('utf-8') if isinstance(c, (bytes, bytearray)) else str(c) for c in cols_attr]
                elif np is not None and hasattr(np, 'ndarray') and isinstance(cols_attr, np.ndarray):
                    cols = [c.decode('utf-8') if isinstance(c, (bytes, bytearray)) else str(c) for c in cols_attr.tolist()]
                elif isinstance(cols_attr, (bytes, bytearray)):
                    cols = [cols_attr.decode('utf-8')]
                else:
                    cols = [str(cols_attr)]
            if cols is not None:
                print(f'ATTR columns: {cols}')
        except Exception as e:
            print(f'WARN reading columns attr failed: {e}')
        return
    if isinstance(node, h5py.Group):
        print(f'GROUP {prefix} keys:', list(node.keys()))
        for name, child in node.items():
            probe_node(child, prefix=f'{prefix}{name}/')


def main():
    # 优先使用命令行参数，其次环境变量，最后回退默认路径（兼容旧逻辑）
    path = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else os.environ.get(
        'H5_FILE_PATH',
        str(DEFAULT_H5_PATH)
    )
    print('Inspecting H5 file:', path)
    if not os.path.exists(path):
        print('H5 file not found:', path)
        return
    with h5py.File(path, 'r') as f:
        probe_node(f, "/")


if __name__ == '__main__':
    main()
