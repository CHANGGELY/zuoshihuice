"""
ASGI config for trading_platform project.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_platform.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # WebSocket支持（用于实时数据）
    # "websocket": AuthMiddlewareStack(
    #     URLRouter([
    #         # WebSocket路由将在这里添加
    #     ])
    # ),
})
