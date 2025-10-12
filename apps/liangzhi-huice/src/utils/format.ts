/**
 * 格式化工具模块
 * 提供价格、时间、成交量、强度等数据的格式化函数
 * 所有函数均采用防御式编程，确保健壮性
 */

/**
 * 格式化价格
 * @param value 价格数值
 * @returns 格式化后的价格字符串
 */
export const formatPrice = (value: number | string | undefined | null): string => {
  try {
    // 转换为有效数字
    let num: number;
    
    if (typeof value === 'number') {
      num = value;
    } else if (typeof value === 'string') {
      num = parseFloat(value);
    } else {
      return '0.0000';
    }
    
    // 检查有效性
    if (!Number.isFinite(num) || num < 0) {
      return '0.0000';
    }
    
    // 根据价格大小决定精度
    if (num >= 1000) {
      return num.toFixed(2);
    } else if (num >= 1) {
      return num.toFixed(4);
    } else {
      return num.toFixed(6);
    }
  } catch (error) {
    console.warn('formatPrice error:', error, 'value:', value);
    return '0.0000';
  }
};

/**
 * 格式化时间戳
 * @param timestamp 时间戳（毫秒）
 * @param format 格式类型：'datetime' | 'time' | 'date'
 * @returns 格式化后的时间字符串
 */
export const formatTime = (
  timestamp: number | string | undefined | null,
  format: 'datetime' | 'time' | 'date' = 'datetime'
): string => {
  try {
    let num: number;
    
    if (typeof timestamp === 'number') {
      num = timestamp;
    } else if (typeof timestamp === 'string') {
      num = parseInt(timestamp, 10);
    } else {
      return '--:--';
    }
    
    if (!Number.isFinite(num) || num <= 0) {
      return '--:--';
    }
    
    const date = new Date(num);
    
    if (isNaN(date.getTime())) {
      return '--:--';
    }
    
    switch (format) {
      case 'time':
        return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
      case 'date':
        return `${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')}`;
      case 'datetime':
      default:
        return `${String(date.getMonth() + 1).padStart(2, '0')}/${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    }
  } catch (error) {
    console.warn('formatTime error:', error, 'timestamp:', timestamp);
    return '--:--';
  }
};

/**
 * 格式化时间戳为本地化字符串
 * @param timestamp 时间戳（毫秒）
 * @param locale 本地化设置，默认为 'zh-CN'
 * @returns 格式化后的本地化时间字符串
 */
export const formatTimeLocale = (
  timestamp: number | string | undefined | null,
  locale: string = 'zh-CN'
): string => {
  try {
    let num: number;
    
    if (typeof timestamp === 'number') {
      num = timestamp;
    } else if (typeof timestamp === 'string') {
      num = parseInt(timestamp, 10);
    } else {
      return '--:--';
    }
    
    if (!Number.isFinite(num) || num <= 0) {
      return '--:--';
    }
    
    const date = new Date(num);
    
    if (isNaN(date.getTime())) {
      return '--:--';
    }
    
    return date.toLocaleString(locale);
  } catch (error) {
    console.warn('formatTimeLocale error:', error, 'timestamp:', timestamp);
    return '--:--';
  }
};

/**
 * 格式化成交量
 * @param value 成交量数值
 * @returns 格式化后的成交量字符串
 */
export const formatVolume = (value: number | string | undefined | null): string => {
  try {
    let num: number;
    
    if (typeof value === 'number') {
      num = value;
    } else if (typeof value === 'string') {
      num = parseFloat(value);
    } else {
      return '0';
    }
    
    if (!Number.isFinite(num) || num < 0) {
      return '0';
    }
    
    if (num >= 1000000000) {
      return `${(num / 1000000000).toFixed(1)}B`;
    } else if (num >= 1000000) {
      return `${(num / 1000000).toFixed(1)}M`;
    } else if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`;
    } else {
      return num.toFixed(0);
    }
  } catch (error) {
    console.warn('formatVolume error:', error, 'value:', value);
    return '0';
  }
};

/**
 * 格式化信号强度（百分比）
 * @param strength 强度数值（0-1）
 * @returns 格式化后的百分比字符串
 */
export const formatStrength = (strength: number | string | undefined | null): string => {
  try {
    let num: number;
    
    if (typeof strength === 'number') {
      num = strength;
    } else if (typeof strength === 'string') {
      num = parseFloat(strength);
    } else {
      return '0.0%';
    }
    
    if (!Number.isFinite(num)) {
      return '0.0%';
    }
    
    // 限制在合理范围内
    const percentage = Math.max(0, Math.min(1, Math.abs(num))) * 100;
    
    return `${percentage.toFixed(1)}%`;
  } catch (error) {
    console.warn('formatStrength error:', error, 'strength:', strength);
    return '0.0%';
  }
};

/**
 * 格式化百分比变化
 * @param change 变化值
 * @param base 基础值
 * @returns 格式化后的百分比变化字符串
 */
export const formatPercentageChange = (
  change: number | string | undefined | null,
  base: number | string | undefined | null
): string => {
  try {
    let changeNum: number;
    let baseNum: number;
    
    if (typeof change === 'number') {
      changeNum = change;
    } else if (typeof change === 'string') {
      changeNum = parseFloat(change);
    } else {
      return '0.00%';
    }
    
    if (typeof base === 'number') {
      baseNum = base;
    } else if (typeof base === 'string') {
      baseNum = parseFloat(base);
    } else {
      return '0.00%';
    }
    
    if (!Number.isFinite(changeNum) || !Number.isFinite(baseNum) || baseNum === 0) {
      return '0.00%';
    }
    
    const percentage = (changeNum / baseNum) * 100;
    const sign = percentage >= 0 ? '+' : '';
    
    return `${sign}${percentage.toFixed(2)}%`;
  } catch (error) {
    console.warn('formatPercentageChange error:', error, 'change:', change, 'base:', base);
    return '0.00%';
  }
};

/**
 * 格式化数字为千分位格式
 * @param value 数值
 * @param decimals 小数位数，默认为2
 * @returns 格式化后的千分位字符串
 */
export const formatNumberWithCommas = (
  value: number | string | undefined | null,
  decimals: number = 2
): string => {
  try {
    let num: number;
    
    if (typeof value === 'number') {
      num = value;
    } else if (typeof value === 'string') {
      num = parseFloat(value);
    } else {
      return '0';
    }
    
    if (!Number.isFinite(num)) {
      return '0';
    }
    
    const validDecimals = Math.max(0, Math.min(10, Math.floor(decimals)));
    
    return num.toLocaleString('en-US', {
      minimumFractionDigits: validDecimals,
      maximumFractionDigits: validDecimals,
    });
  } catch (error) {
    console.warn('formatNumberWithCommas error:', error, 'value:', value);
    return '0';
  }
};

/**
 * 安全数值转换
 * @param value 待转换的值
 * @param defaultValue 默认值
 * @returns 转换后的数值
 */
export const safeNumber = (
  value: number | string | undefined | null,
  defaultValue: number = 0
): number => {
  try {
    if (typeof value === 'number' && Number.isFinite(value)) {
      return value;
    }
    
    if (typeof value === 'string') {
      const num = parseFloat(value);
      if (Number.isFinite(num)) {
        return num;
      }
    }
    
    return defaultValue;
  } catch (error) {
    console.warn('safeNumber error:', error, 'value:', value);
    return defaultValue;
  }
};