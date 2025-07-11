"""
用户认证视图
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from datetime import datetime
import json


class RegisterView(APIView):
    """用户注册接口"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """用户注册"""
        try:
            data = request.data
            
            # 获取参数
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
            
            # 验证参数
            if not username:
                return Response({
                    'success': False,
                    'error': '用户名不能为空',
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not email:
                return Response({
                    'success': False,
                    'error': '邮箱不能为空',
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not password:
                return Response({
                    'success': False,
                    'error': '密码不能为空',
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if password != confirm_password:
                return Response({
                    'success': False,
                    'error': '两次输入的密码不一致',
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查用户名是否已存在
            if User.objects.filter(username=username).exists():
                return Response({
                    'success': False,
                    'error': '用户名已存在',
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查邮箱是否已存在
            if User.objects.filter(email=email).exists():
                return Response({
                    'success': False,
                    'error': '邮箱已被注册',
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 验证密码强度
            try:
                validate_password(password)
            except ValidationError as e:
                return Response({
                    'success': False,
                    'error': '密码强度不够：' + ', '.join(e.messages),
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 创建用户
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # 创建Token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'success': True,
                'data': {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'date_joined': user.date_joined.isoformat()
                    },
                    'token': token.key
                },
                'message': '注册成功',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    """用户登录接口"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """用户登录"""
        try:
            data = request.data
            
            # 获取参数
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            # 验证参数
            if not username:
                return Response({
                    'success': False,
                    'error': '用户名不能为空',
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not password:
                return Response({
                    'success': False,
                    'error': '密码不能为空',
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 认证用户
            user = authenticate(username=username, password=password)
            
            if user is None:
                return Response({
                    'success': False,
                    'error': '用户名或密码错误',
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if not user.is_active:
                return Response({
                    'success': False,
                    'error': '账户已被禁用',
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 获取或创建Token
            token, created = Token.objects.get_or_create(user=user)
            
            # 更新最后登录时间
            user.last_login = datetime.now()
            user.save()
            
            return Response({
                'success': True,
                'data': {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'last_login': user.last_login.isoformat(),
                        'date_joined': user.date_joined.isoformat()
                    },
                    'token': token.key
                },
                'message': '登录成功',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    """用户登出接口"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """用户登出"""
        try:
            # 删除Token
            try:
                token = Token.objects.get(user=request.user)
                token.delete()
            except Token.DoesNotExist:
                pass
            
            return Response({
                'success': True,
                'message': '登出成功',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(APIView):
    """用户信息接口"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取用户信息"""
        try:
            user = request.user
            
            return Response({
                'success': True,
                'data': {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'last_login': user.last_login.isoformat() if user.last_login else None,
                        'date_joined': user.date_joined.isoformat(),
                        'is_active': user.is_active,
                        'is_staff': user.is_staff
                    }
                },
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """更新用户信息"""
        try:
            user = request.user
            data = request.data
            
            # 更新允许的字段
            if 'email' in data:
                email = data['email'].strip()
                if email and email != user.email:
                    # 检查邮箱是否已被其他用户使用
                    if User.objects.filter(email=email).exclude(id=user.id).exists():
                        return Response({
                            'success': False,
                            'error': '邮箱已被其他用户使用',
                            'timestamp': datetime.now().isoformat()
                        }, status=status.HTTP_400_BAD_REQUEST)
                    user.email = email
            
            if 'first_name' in data:
                user.first_name = data['first_name'].strip()
            
            if 'last_name' in data:
                user.last_name = data['last_name'].strip()
            
            user.save()
            
            return Response({
                'success': True,
                'data': {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'last_login': user.last_login.isoformat() if user.last_login else None,
                        'date_joined': user.date_joined.isoformat(),
                        'is_active': user.is_active,
                        'is_staff': user.is_staff
                    }
                },
                'message': '用户信息更新成功',
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
