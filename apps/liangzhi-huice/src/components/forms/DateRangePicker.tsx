// DateRangePicker 日期范围选择组件

import React, { useCallback, useEffect, useState } from 'react';
import {
  DatePicker,
  Select,
  Button,
  Space,
  Card,
  Row,
  Col,
  Tooltip,
  message,
  Radio,
  InputNumber,
} from 'antd';
import {
  CalendarOutlined,
  ClockCircleOutlined,
  ReloadOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import { useKlineStore } from '../../stores/klineStore';

const { RangePicker } = DatePicker;
const { Option } = Select;

// 日期范围选择器属性
interface DateRangePickerProps {
  // 初始日期范围
  initialRange?: [Dayjs, Dayjs];
  // 是否显示快速选择
  showQuickSelect?: boolean;
  // 是否显示时间选择
  showTime?: boolean;
  // 是否显示预设范围
  showPresets?: boolean;
  // 最小日期
  minDate?: Dayjs;
  // 最大日期
  maxDate?: Dayjs;
  // 日期变化回调
  onChange?: (range: [Dayjs, Dayjs] | null) => void;
  // 自定义样式
  style?: React.CSSProperties;
  // 是否禁用
  disabled?: boolean;
}

// 快速选择选项
const quickSelectOptions = [
  { label: '最近1小时', value: 'last_1h', hours: 1 },
  { label: '最近6小时', value: 'last_6h', hours: 6 },
  { label: '最近12小时', value: 'last_12h', hours: 12 },
  { label: '最近1天', value: 'last_1d', days: 1 },
  { label: '最近3天', value: 'last_3d', days: 3 },
  { label: '最近7天', value: 'last_7d', days: 7 },
  { label: '最近15天', value: 'last_15d', days: 15 },
  { label: '最近30天', value: 'last_30d', days: 30 },
  { label: '最近90天', value: 'last_90d', days: 90 },
  { label: '最近180天', value: 'last_180d', days: 180 },
  { label: '最近1年', value: 'last_1y', days: 365 },
];

// 预设范围选项
const presetRanges = {
  '今天': [dayjs().startOf('day'), dayjs().endOf('day')] as [Dayjs, Dayjs],
  '昨天': [dayjs().subtract(1, 'day').startOf('day'), dayjs().subtract(1, 'day').endOf('day')] as [Dayjs, Dayjs],
  '本周': [dayjs().startOf('week'), dayjs().endOf('week')] as [Dayjs, Dayjs],
  '上周': [dayjs().subtract(1, 'week').startOf('week'), dayjs().subtract(1, 'week').endOf('week')] as [Dayjs, Dayjs],
  '本月': [dayjs().startOf('month'), dayjs().endOf('month')] as [Dayjs, Dayjs],
  '上月': [dayjs().subtract(1, 'month').startOf('month'), dayjs().subtract(1, 'month').endOf('month')] as [Dayjs, Dayjs],
  '本季度': [dayjs().startOf('month'), dayjs().endOf('month')] as [Dayjs, Dayjs],
  '上季度': [dayjs().subtract(3, 'month').startOf('month'), dayjs().subtract(1, 'month').endOf('month')] as [Dayjs, Dayjs],
  '本年': [dayjs().startOf('year'), dayjs().endOf('year')] as [Dayjs, Dayjs],
  '去年': [dayjs().subtract(1, 'year').startOf('year'), dayjs().subtract(1, 'year').endOf('year')] as [Dayjs, Dayjs],
};

// 自定义范围组件
const CustomRangeSelector: React.FC<{
  value: [Dayjs, Dayjs] | null;
  onChange: (range: [Dayjs, Dayjs] | null) => void;
}> = ({ onChange }) => {
  const [rangeType, setRangeType] = useState<'days' | 'hours'>('days');
  const [rangeValue, setRangeValue] = useState<number>(7);

  const handleCustomRangeChange = useCallback(() => {
    const now = dayjs();
    let startTime: Dayjs;

    if (rangeType === 'hours') {
      startTime = now.subtract(rangeValue, 'hour');
    } else {
      startTime = now.subtract(rangeValue, 'day').startOf('day');
    }

    onChange([startTime, now]);
  }, [rangeType, rangeValue, onChange]);

  return (
    <Space.Compact style={{ width: '100%' }}>
      <Radio.Group
        value={rangeType}
        onChange={(e) => setRangeType(e.target.value)}
        size="small"
      >
        <Radio.Button value="hours">小时</Radio.Button>
        <Radio.Button value="days">天</Radio.Button>
      </Radio.Group>
      
      <InputNumber
        value={rangeValue}
        onChange={(val) => setRangeValue(val || 1)}
        min={1}
        max={rangeType === 'hours' ? 24 * 30 : 365}
        size="small"
        style={{ width: 80 }}
      />
      
      <Button
        size="small"
        onClick={handleCustomRangeChange}
        type="primary"
      >
        应用
      </Button>
    </Space.Compact>
  );
};

// 导出类型
export type { DateRangePickerProps };

// DateRangePicker主组件
export const DateRangePicker: React.FC<DateRangePickerProps> = ({
  initialRange,
  showQuickSelect = true,
  showTime = false,
  showPresets = true,
  minDate,
  maxDate,
  onChange,
  style,
  disabled = false,
}) => {
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs] | null>(initialRange || null);
  const [quickSelectValue, setQuickSelectValue] = useState<string>('');
  
  const { dateRange: storeDateRange, updateDateRange } = useKlineStore();

  // 同步store中的日期范围
  useEffect(() => {
    if (storeDateRange && storeDateRange.start && storeDateRange.end) {
      const range: [Dayjs, Dayjs] = [dayjs(storeDateRange.start), dayjs(storeDateRange.end)];
      setDateRange(range);
    }
  }, [storeDateRange]);

  // 处理日期范围变化
  const handleDateRangeChange = useCallback((dates: [Dayjs, Dayjs] | null) => {
    if (dates && dates[0] && dates[1]) {
      setDateRange([dates[0], dates[1]]);
      setQuickSelectValue('');
      updateDateRange(dates[0].format('YYYY-MM-DD'), dates[1].format('YYYY-MM-DD'));
      onChange?.([dates[0], dates[1]]);
    } else {
      setDateRange(null);
      setQuickSelectValue('');
      updateDateRange('', '');
      onChange?.(null);
    }
  }, [onChange, updateDateRange]);

  // 处理快速选择
  const handleQuickSelect = useCallback((value: string) => {
    const option = quickSelectOptions.find(opt => opt.value === value);
    if (!option) return;

    const now = dayjs();
    let startTime: Dayjs;

    if (option.hours) {
      startTime = now.subtract(option.hours, 'hour');
    } else if (option.days) {
      startTime = now.subtract(option.days, 'day').startOf('day');
    } else {
      return;
    }

    const range: [Dayjs, Dayjs] = [startTime, now];
    setDateRange(range);
    setQuickSelectValue(value);
    
    // 更新store
    updateDateRange(range[0].format('YYYY-MM-DD'), range[1].format('YYYY-MM-DD'));
    onChange?.(range);
    
    message.success(`已选择${option.label}`);
  }, [onChange, updateDateRange]);

  // 处理预设范围选择
  const handlePresetSelect = useCallback((key: string) => {
    const range = presetRanges[key as keyof typeof presetRanges];
    if (range) {
      setDateRange(range);
      setQuickSelectValue('');
      
      // 更新store
      updateDateRange(range[0].format('YYYY-MM-DD'), range[1].format('YYYY-MM-DD'));
      onChange?.(range);
      
      message.success(`已选择${key}`);
    }
  }, [onChange, updateDateRange]);

  // 处理重置
  const handleReset = useCallback(() => {
    setDateRange(null);
    setQuickSelectValue('');
    updateDateRange('', '');
    onChange?.(null);
    message.info('日期范围已重置');
  }, [onChange, updateDateRange]);

  // 获取当前范围描述
  const getRangeDescription = useCallback(() => {
    if (!dateRange) return '未选择日期范围';
    
    const [start, end] = dateRange;
    const duration = end.diff(start, 'day', true);
    
    if (duration < 1) {
      const hours = end.diff(start, 'hour', true);
      return `${hours.toFixed(1)}小时`;
    } else if (duration < 30) {
      return `${Math.ceil(duration)}天`;
    } else if (duration < 365) {
      const months = duration / 30;
      return `${months.toFixed(1)}个月`;
    } else {
      const years = duration / 365;
      return `${years.toFixed(1)}年`;
    }
  }, [dateRange]);

  // 验证日期范围
  const validateDateRange = useCallback((dates: [Dayjs, Dayjs] | null): boolean => {
    if (!dates) return true;
    
    const [start, end] = dates;
    
    // 检查开始时间不能晚于结束时间
    if (start.isAfter(end)) {
      message.error('开始时间不能晚于结束时间');
      return false;
    }
    
    // 检查最小日期限制
    if (minDate && start.isBefore(minDate)) {
      message.error(`开始时间不能早于${minDate.format('YYYY-MM-DD')}`);
      return false;
    }
    
    // 检查最大日期限制
    if (maxDate && end.isAfter(maxDate)) {
      message.error(`结束时间不能晚于${maxDate.format('YYYY-MM-DD')}`);
      return false;
    }
    
    // 检查范围不能超过1年
    const duration = end.diff(start, 'day');
    if (duration > 365) {
      message.error('日期范围不能超过1年');
      return false;
    }
    
    return true;
  }, [minDate, maxDate]);

  // 处理日期选择器变化（带验证）
  const handleRangePickerChange = useCallback((dates: [Dayjs | null, Dayjs | null] | null, _dateStrings: [string, string]) => {
    const validDates = dates && dates[0] && dates[1] ? [dates[0], dates[1]] as [Dayjs, Dayjs] : null;
    if (validateDateRange(validDates)) {
      handleDateRangeChange(validDates);
    }
  }, [validateDateRange, handleDateRangeChange]);

  return (
    <Card
      title={
        <Space>
          <CalendarOutlined />
          <span>日期范围选择</span>
          <Tooltip title="选择数据的时间范围">
            <QuestionCircleOutlined style={{ color: '#999' }} />
          </Tooltip>
        </Space>
      }
      extra={
        <Space>
          <span style={{ fontSize: '12px', color: '#666' }}>
            {getRangeDescription()}
          </span>
          <Tooltip title="重置日期范围">
            <Button
              icon={<ReloadOutlined />}
              size="small"
              onClick={handleReset}
              disabled={disabled}
            />
          </Tooltip>
        </Space>
      }
      size="small"
      style={style}
    >
      <Space direction="vertical" style={{ width: '100%' }}>
        {/* 主要日期选择器 */}
        <RangePicker
          value={dateRange}
          onChange={handleRangePickerChange}
          showTime={showTime ? {
            format: 'HH:mm:ss',
            defaultValue: [dayjs('00:00:00', 'HH:mm:ss'), dayjs('23:59:59', 'HH:mm:ss')],
          } : false}
          format={showTime ? 'YYYY-MM-DD HH:mm:ss' : 'YYYY-MM-DD'}
          placeholder={['开始日期', '结束日期']}
          style={{ width: '100%' }}
          disabled={disabled}
          disabledDate={(current) => {
            if (minDate && current.isBefore(minDate, 'day')) return true;
            if (maxDate && current.isAfter(maxDate, 'day')) return true;
            return false;
          }}
          presets={showPresets ? Object.entries(presetRanges).map(([label, range]) => ({
            label,
            value: range,
          })) : undefined}
        />

        {/* 快速选择 */}
        {showQuickSelect && (
          <Row gutter={[8, 8]}>
            <Col span={12}>
              <Select
                placeholder="快速选择"
                value={quickSelectValue}
                onChange={handleQuickSelect}
                style={{ width: '100%' }}
                allowClear
                disabled={disabled}
              >
                {quickSelectOptions.map(option => (
                  <Option key={option.value} value={option.value}>
                    {option.label}
                  </Option>
                ))}
              </Select>
            </Col>
            <Col span={12}>
              <CustomRangeSelector
                value={dateRange}
                onChange={handleDateRangeChange}
              />
            </Col>
          </Row>
        )}

        {/* 预设范围按钮 */}
        {showPresets && (
          <Row gutter={[4, 4]}>
            {Object.keys(presetRanges).map(key => (
              <Col key={key}>
                <Button
                  size="small"
                  onClick={() => handlePresetSelect(key)}
                  disabled={disabled}
                  type={dateRange && 
                    dateRange[0].isSame(presetRanges[key as keyof typeof presetRanges][0], 'day') &&
                    dateRange[1].isSame(presetRanges[key as keyof typeof presetRanges][1], 'day') 
                    ? 'primary' : 'default'
                  }
                >
                  {key}
                </Button>
              </Col>
            ))}
          </Row>
        )}

        {/* 当前选择信息 */}
        {dateRange && (
          <div style={{ 
            padding: '8px 12px', 
            background: '#f5f5f5', 
            borderRadius: '4px',
            fontSize: '12px',
            color: '#666'
          }}>
            <Space>
              <ClockCircleOutlined />
              <span>
                从 {dateRange[0].format(showTime ? 'YYYY-MM-DD HH:mm:ss' : 'YYYY-MM-DD')} 
                到 {dateRange[1].format(showTime ? 'YYYY-MM-DD HH:mm:ss' : 'YYYY-MM-DD')}
              </span>
              <span>({getRangeDescription()})</span>
            </Space>
          </div>
        )}
      </Space>
    </Card>
  );
};

// 简化版日期范围选择器
export const SimpleDateRangePicker: React.FC<{
  value?: [Dayjs, Dayjs] | null;
  onChange?: (range: [Dayjs, Dayjs] | null) => void;
  placeholder?: [string, string];
  style?: React.CSSProperties;
  disabled?: boolean;
}> = ({ value, onChange, placeholder = ['开始日期', '结束日期'], style, disabled }) => {
  const handleChange = useCallback((dates: [Dayjs | null, Dayjs | null] | null, _dateStrings: [string, string]) => {
    const validDates = dates && dates[0] && dates[1] ? [dates[0], dates[1]] as [Dayjs, Dayjs] : null;
    onChange?.(validDates);
  }, [onChange]);

  return (
    <RangePicker
      value={value}
      onChange={handleChange}
      placeholder={placeholder}
      style={style}
      disabled={disabled}
      format="YYYY-MM-DD"
    />
  );
};

// 时间范围选择器（包含时间）
export const DateTimeRangePicker: React.FC<{
  value?: [Dayjs, Dayjs] | null;
  onChange?: (range: [Dayjs, Dayjs] | null) => void;
  placeholder?: [string, string];
  style?: React.CSSProperties;
  disabled?: boolean;
}> = ({ value, onChange, placeholder = ['开始时间', '结束时间'], style, disabled }) => {
  const handleChange = useCallback((dates: [Dayjs | null, Dayjs | null] | null, _dateStrings: [string, string]) => {
    const validDates = dates && dates[0] && dates[1] ? [dates[0], dates[1]] as [Dayjs, Dayjs] : null;
    onChange?.(validDates);
  }, [onChange]);

  return (
    <RangePicker
      value={value}
      onChange={handleChange}
      placeholder={placeholder}
      style={style}
      disabled={disabled}
      showTime={{
        format: 'HH:mm:ss',
        defaultValue: [dayjs('00:00:00', 'HH:mm:ss'), dayjs('23:59:59', 'HH:mm:ss')],
      }}
      format="YYYY-MM-DD HH:mm:ss"
    />
  );
};

export default DateRangePicker;