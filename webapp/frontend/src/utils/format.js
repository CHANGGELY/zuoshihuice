import numeral from 'numeral'

/**
 * 格式化价格
 * @param {number|string} price 价格
 * @param {number} decimals 小数位数
 * @returns {string} 格式化后的价格
 */
export function formatPrice(price, decimals = 2) {
  if (price === null || price === undefined || price === '') {
    return '--'
  }
  
  const num = parseFloat(price)
  if (isNaN(num)) {
    return '--'
  }
  
  return num.toFixed(decimals)
}

/**
 * 格式化百分比
 * @param {number|string} percent 百分比
 * @param {number} decimals 小数位数
 * @returns {string} 格式化后的百分比
 */
export function formatPercent(percent, decimals = 2) {
  if (percent === null || percent === undefined || percent === '') {
    return '--'
  }
  
  const num = parseFloat(percent)
  if (isNaN(num)) {
    return '--'
  }
  
  const sign = num >= 0 ? '+' : ''
  return `${sign}${num.toFixed(decimals)}%`
}

/**
 * 格式化成交量
 * @param {number|string} volume 成交量
 * @returns {string} 格式化后的成交量
 */
export function formatVolume(volume) {
  if (volume === null || volume === undefined || volume === '') {
    return '--'
  }
  
  const num = parseFloat(volume)
  if (isNaN(num)) {
    return '--'
  }
  
  if (num >= 1000000) {
    return numeral(num).format('0.00a').toUpperCase()
  } else if (num >= 1000) {
    return numeral(num).format('0.0a').toUpperCase()
  } else {
    return num.toFixed(2)
  }
}

/**
 * 格式化数字
 * @param {number|string} number 数字
 * @param {string} format 格式
 * @returns {string} 格式化后的数字
 */
export function formatNumber(number, format = '0,0.00') {
  if (number === null || number === undefined || number === '') {
    return '--'
  }
  
  const num = parseFloat(number)
  if (isNaN(num)) {
    return '--'
  }
  
  return numeral(num).format(format)
}

/**
 * 格式化时间
 * @param {string|Date} time 时间
 * @param {string} format 格式
 * @returns {string} 格式化后的时间
 */
export function formatTime(time, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!time) {
    return '--'
  }
  
  try {
    const date = new Date(time)
    if (isNaN(date.getTime())) {
      return '--'
    }
    
    // 简单的时间格式化
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    
    if (format === 'YYYY-MM-DD') {
      return `${year}-${month}-${day}`
    } else if (format === 'HH:mm:ss') {
      return `${hours}:${minutes}:${seconds}`
    } else {
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    }
  } catch (error) {
    return '--'
  }
}

/**
 * 格式化文件大小
 * @param {number} bytes 字节数
 * @returns {string} 格式化后的文件大小
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 获取价格变化的CSS类名
 * @param {number} change 价格变化
 * @returns {string} CSS类名
 */
export function getPriceChangeClass(change) {
  if (change > 0) return 'text-green'
  if (change < 0) return 'text-red'
  return ''
}
