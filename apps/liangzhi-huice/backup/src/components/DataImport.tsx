import React, { useState, useEffect } from 'react';
import {
  Card,
  Upload,
  Button,
  Progress,
  Table,
  Tag,
  Space,
  message,
  Modal,
  Descriptions,
  Alert,
  Statistic,
  Row,
  Col,
  Typography
} from 'antd';
import {
  UploadOutlined,
  ReloadOutlined,
  DeleteOutlined,
  EyeOutlined,
  CloudUploadOutlined,
  DatabaseOutlined
} from '@ant-design/icons';
import type { UploadProps } from 'antd';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

interface ImportTask {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  message: string;
  result?: {
    success: boolean;
    total_rows: number;
    imported_rows: number;
    error_rows: number;
    processing_time: number;
    timeframes_generated: string[];
    file_info?: {
      file_name: string;
      file_size: number;
      file_format: string;
    };
    error_message?: string;
  };
  start_time?: string;
  end_time?: string;
}

interface DataSummary {
  total_records: number;
  symbols: string[];
  timeframes: string[];
  date_range: {
    start: string;
    end: string;
  };
  storage_size: string;
}

const DataImport: React.FC = () => {
  const [tasks, setTasks] = useState<ImportTask[]>([]);
  const [loading, setLoading] = useState(false);
  const [dataSummary, setDataSummary] = useState<DataSummary | null>(null);
  const [selectedTask, setSelectedTask] = useState<ImportTask | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);

  // 获取导入任务列表
  const fetchTasks = async () => {
    try {
      const response = await fetch('/api/data/import/tasks');
      if (response.ok) {
        const data = await response.json();
        setTasks(data);
      }
    } catch (error) {
      console.error('获取任务列表失败:', error);
    }
  };

  // 获取数据摘要
  const fetchDataSummary = async () => {
    try {
      const response = await fetch('/api/data/summary');
      if (response.ok) {
        const data = await response.json();
        setDataSummary(data);
      }
    } catch (error) {
      console.error('获取数据摘要失败:', error);
    }
  };

  // 导入ETHUSDT示例数据
  const importSampleData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/data/import/ethusdt-sample', {
        method: 'POST'
      });
      
      if (response.ok) {
        const result = await response.json();
        message.success('示例数据导入任务已启动');
        fetchTasks();
        
        // 开始轮询任务状态
        pollTaskStatus(result.task_id);
      } else {
        const error = await response.json();
        message.error(error.detail || '导入失败');
      }
    } catch (error) {
      console.error('导入示例数据失败:', error);
      message.error('导入失败，请检查网络连接');
    } finally {
      setLoading(false);
    }
  };

  // 轮询任务状态
  const pollTaskStatus = (taskId: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/api/data/import/status/${taskId}`);
        if (response.ok) {
          const task = await response.json();
          
          // 更新任务列表中的对应任务
          setTasks(prev => prev.map(t => 
            t.task_id === taskId ? task : t
          ));
          
          // 如果任务完成或失败，停止轮询
          if (task.status === 'completed' || task.status === 'failed') {
            clearInterval(interval);
            fetchDataSummary(); // 刷新数据摘要
            
            if (task.status === 'completed') {
              message.success('数据导入完成');
            } else {
              message.error('数据导入失败');
            }
          }
        }
      } catch (error) {
        console.error('轮询任务状态失败:', error);
        clearInterval(interval);
      }
    }, 2000);

    // 30秒后停止轮询
    setTimeout(() => clearInterval(interval), 30000);
  };

  // 删除任务
  const deleteTask = async (taskId: string) => {
    try {
      const response = await fetch(`/api/data/import/tasks/${taskId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        message.success('任务已删除');
        fetchTasks();
      } else {
        message.error('删除任务失败');
      }
    } catch (error) {
      console.error('删除任务失败:', error);
      message.error('删除任务失败');
    }
  };

  // 查看任务详情
  const viewTaskDetail = (task: ImportTask) => {
    setSelectedTask(task);
    setDetailModalVisible(true);
  };

  // 获取状态标签
  const getStatusTag = (status: string) => {
    const statusConfig = {
      pending: { color: 'blue', text: '等待中' },
      running: { color: 'orange', text: '运行中' },
      completed: { color: 'green', text: '已完成' },
      failed: { color: 'red', text: '失败' }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || 
                   { color: 'default', text: status };
    
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // 表格列定义
  const columns = [
    {
      title: '任务ID',
      dataIndex: 'task_id',
      key: 'task_id',
      width: 200,
      render: (text: string) => (
        <Text code style={{ fontSize: '12px' }}>
          {text.substring(0, 20)}...
        </Text>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => getStatusTag(status)
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      width: 150,
      render: (progress: number, record: ImportTask) => (
        <Progress 
          percent={progress} 
          size="small" 
          status={record.status === 'failed' ? 'exception' : 'active'}
        />
      )
    },
    {
      title: '消息',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
      width: 150,
      render: (time: string) => time ? dayjs(time).format('MM-DD HH:mm:ss') : '-'
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_, record: ImportTask) => (
        <Space>
          <Button
            icon={<EyeOutlined />}
            size="small"
            onClick={() => viewTaskDetail(record)}
          >
            详情
          </Button>
          <Button
            icon={<DeleteOutlined />}
            size="small"
            danger
            onClick={() => deleteTask(record.task_id)}
          >
            删除
          </Button>
        </Space>
      )
    }
  ];

  useEffect(() => {
    fetchTasks();
    fetchDataSummary();
  }, []);

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>数据导入管理</Title>
      
      {/* 数据摘要 */}
      {dataSummary && (
        <Card title="数据库概览" style={{ marginBottom: '24px' }}>
          <Row gutter={16}>
            <Col span={6}>
              <Statistic
                title="总记录数"
                value={dataSummary.total_records}
                prefix={<DatabaseOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="交易对数量"
                value={dataSummary.symbols.length}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="时间周期数量"
                value={dataSummary.timeframes.length}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="存储大小"
                value={dataSummary.storage_size}
              />
            </Col>
          </Row>
          
          {dataSummary.date_range.start && (
            <div style={{ marginTop: '16px' }}>
              <Text strong>数据时间范围: </Text>
              <Text>
                {dayjs(dataSummary.date_range.start).format('YYYY-MM-DD HH:mm')} ~ 
                {dayjs(dataSummary.date_range.end).format('YYYY-MM-DD HH:mm')}
              </Text>
            </div>
          )}
          
          <div style={{ marginTop: '8px' }}>
            <Text strong>支持的交易对: </Text>
            {dataSummary.symbols.map(symbol => (
              <Tag key={symbol} color="blue">{symbol}</Tag>
            ))}
          </div>
          
          <div style={{ marginTop: '8px' }}>
            <Text strong>支持的时间周期: </Text>
            {dataSummary.timeframes.map(timeframe => (
              <Tag key={timeframe} color="green">{timeframe}</Tag>
            ))}
          </div>
        </Card>
      )}
      
      {/* 导入操作 */}
      <Card title="数据导入" style={{ marginBottom: '24px' }}>
        <Alert
          message="导入说明"
          description="支持导入H5格式的历史K线数据文件。导入后系统会自动生成多个时间周期的数据，并可在K线图表中查看。"
          type="info"
          showIcon
          style={{ marginBottom: '16px' }}
        />
        
        <Space>
          <Button
            type="primary"
            icon={<CloudUploadOutlined />}
            loading={loading}
            onClick={importSampleData}
          >
            导入ETHUSDT示例数据
          </Button>
          
          <Button
            icon={<ReloadOutlined />}
            onClick={() => {
              fetchTasks();
              fetchDataSummary();
            }}
          >
            刷新状态
          </Button>
        </Space>
      </Card>
      
      {/* 任务列表 */}
      <Card 
        title="导入任务" 
        extra={
          <Button 
            icon={<ReloadOutlined />} 
            onClick={fetchTasks}
            size="small"
          >
            刷新
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={tasks}
          rowKey="task_id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个任务`
          }}
        />
      </Card>
      
      {/* 任务详情弹窗 */}
      <Modal
        title="任务详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        {selectedTask && (
          <Descriptions column={2} bordered>
            <Descriptions.Item label="任务ID" span={2}>
              <Text code>{selectedTask.task_id}</Text>
            </Descriptions.Item>
            <Descriptions.Item label="状态">
              {getStatusTag(selectedTask.status)}
            </Descriptions.Item>
            <Descriptions.Item label="进度">
              <Progress percent={selectedTask.progress} size="small" />
            </Descriptions.Item>
            <Descriptions.Item label="消息" span={2}>
              {selectedTask.message}
            </Descriptions.Item>
            <Descriptions.Item label="开始时间">
              {selectedTask.start_time ? 
                dayjs(selectedTask.start_time).format('YYYY-MM-DD HH:mm:ss') : '-'
              }
            </Descriptions.Item>
            <Descriptions.Item label="结束时间">
              {selectedTask.end_time ? 
                dayjs(selectedTask.end_time).format('YYYY-MM-DD HH:mm:ss') : '-'
              }
            </Descriptions.Item>
            
            {selectedTask.result && (
              <>
                <Descriptions.Item label="导入结果" span={2}>
                  <Tag color={selectedTask.result.success ? 'green' : 'red'}>
                    {selectedTask.result.success ? '成功' : '失败'}
                  </Tag>
                </Descriptions.Item>
                
                {selectedTask.result.success && (
                  <>
                    <Descriptions.Item label="总行数">
                      {selectedTask.result.total_rows?.toLocaleString()}
                    </Descriptions.Item>
                    <Descriptions.Item label="导入行数">
                      {selectedTask.result.imported_rows?.toLocaleString()}
                    </Descriptions.Item>
                    <Descriptions.Item label="错误行数">
                      {selectedTask.result.error_rows?.toLocaleString()}
                    </Descriptions.Item>
                    <Descriptions.Item label="处理时间">
                      {selectedTask.result.processing_time?.toFixed(2)} 秒
                    </Descriptions.Item>
                    <Descriptions.Item label="生成的时间周期" span={2}>
                      {selectedTask.result.timeframes_generated?.map(tf => (
                        <Tag key={tf} color="blue">{tf}</Tag>
                      ))}
                    </Descriptions.Item>
                    
                    {selectedTask.result.file_info && (
                      <>
                        <Descriptions.Item label="文件名">
                          {selectedTask.result.file_info.file_name}
                        </Descriptions.Item>
                        <Descriptions.Item label="文件大小">
                          {(selectedTask.result.file_info.file_size / 1024 / 1024).toFixed(2)} MB
                        </Descriptions.Item>
                      </>
                    )}
                  </>
                )}
                
                {selectedTask.result.error_message && (
                  <Descriptions.Item label="错误信息" span={2}>
                    <Text type="danger">{selectedTask.result.error_message}</Text>
                  </Descriptions.Item>
                )}
              </>
            )}
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default DataImport;