// 登录页面

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, message, Typography, Space } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { authService } from '../services/authService';

const { Title, Text } = Typography;

interface LoginForm {
  username: string;
  password: string;
}

export const LoginPage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (values: LoginForm) => {
    setLoading(true);
    try {
      const response = await authService.login(values);
      
      if (response.success) {
        message.success('登录成功！');
        navigate('/kline'); // 登录成功后跳转到K线页面
      } else {
        message.error(response.message || '登录失败');
      }
    } catch (error) {
      message.error('登录过程中发生错误');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = async () => {
    // 提供一个快速登录选项，使用默认凭据
    setLoading(true);
    try {
      const response = await authService.login({
        username: 'demo',
        password: 'demo123'
      });
      
      if (response.success) {
        message.success('快速登录成功！');
        navigate('/kline');
      } else {
        // 如果demo用户不存在，尝试注册
        const registerResponse = await authService.register({
          username: 'demo',
          email: 'demo@example.com',
          password: 'demo123',
          full_name: 'Demo User'
        });
        
        if (registerResponse.success) {
          message.success('Demo用户创建成功，请重新登录');
          // 注册成功后自动登录
          const loginResponse = await authService.login({
            username: 'demo',
            password: 'demo123'
          });
          
          if (loginResponse.success) {
            message.success('登录成功！');
            navigate('/kline');
          }
        } else {
          message.error('快速登录失败，请手动输入凭据');
        }
      }
    } catch (error) {
      message.error('快速登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-lg">
        <div className="text-center mb-8">
          <Title level={2} className="mb-2">左势慧策</Title>
          <Text type="secondary">量化交易分析平台</Text>
        </div>

        <Form
          form={form}
          name="login"
          onFinish={handleLogin}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="username"
            label="用户名"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' }
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="请输入用户名"
              autoComplete="username"
            />
          </Form.Item>

          <Form.Item
            name="password"
            label="密码"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码至少6个字符' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="请输入密码"
              autoComplete="current-password"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              className="w-full"
            >
              登录
            </Button>
          </Form.Item>
        </Form>

        <div className="text-center">
          <Space direction="vertical" className="w-full">
            <Button
              type="link"
              onClick={handleQuickLogin}
              loading={loading}
              className="text-sm"
            >
              快速登录 (demo/demo123)
            </Button>
            
            <Text type="secondary" className="text-xs">
              提示：首次使用快速登录会自动创建demo账户
            </Text>
          </Space>
        </div>
      </Card>
    </div>
  );
};

export default LoginPage;