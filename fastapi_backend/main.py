# 兼容层：保持原入口 fastapi_backend.main:app 可用
from .主程序 import 应用 as app

__all__ = ["app"]
