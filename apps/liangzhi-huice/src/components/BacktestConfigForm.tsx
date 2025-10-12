import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import { Separator } from './ui/separator';
import { CalendarIcon, PlayIcon, SettingsIcon } from 'lucide-react';
import { toast } from 'sonner';

export interface BacktestConfig {
  symbol: string;
  startDate: string;
  endDate: string;
  initialBalance: number;
  leverage: number;
  bidSpread: number;
  askSpread: number;
  maxPositionValueRatio: number;
  useDynamicOrderSize: boolean;
  minOrderAmount: number;
  maxOrderAmount: number;
}

interface BacktestConfigFormProps {
  onSubmit: (config: BacktestConfig) => void;
  loading?: boolean;
}

export const BacktestConfigForm: React.FC<BacktestConfigFormProps> = ({
  onSubmit,
  loading = false
}) => {
  const [config, setConfig] = useState<BacktestConfig>({
    symbol: 'ETHUSDT',
    startDate: '2024-01-01',
    endDate: '2024-12-31',
    initialBalance: 10000,
    leverage: 10,
    bidSpread: 0.001,
    askSpread: 0.001,
    maxPositionValueRatio: 0.8,
    useDynamicOrderSize: true,
    minOrderAmount: 0.001,
    maxOrderAmount: 10.0
  });

  const handleInputChange = (field: keyof BacktestConfig, value: string | number | boolean) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // 验证表单
    if (!config.startDate || !config.endDate) {
      toast.error('请选择回测时间范围');
      return;
    }
    
    if (new Date(config.startDate) >= new Date(config.endDate)) {
      toast.error('开始时间必须早于结束时间');
      return;
    }
    
    if (config.initialBalance <= 0) {
      toast.error('初始资金必须大于0');
      return;
    }
    
    if (config.leverage <= 0 || config.leverage > 100) {
      toast.error('杠杆倍数必须在1-100之间');
      return;
    }
    
    onSubmit(config);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <SettingsIcon className="h-5 w-5" />
          回测配置
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 基础配置 */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">基础配置</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="symbol">交易对</Label>
                <Input
                  id="symbol"
                  value={config.symbol}
                  onChange={(e) => handleInputChange('symbol', e.target.value)}
                  placeholder="ETHUSDT"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="initialBalance">初始资金 (USDT)</Label>
                <Input
                  id="initialBalance"
                  type="number"
                  value={config.initialBalance}
                  onChange={(e) => handleInputChange('initialBalance', Number(e.target.value))}
                  min="100"
                  step="100"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="startDate" className="flex items-center gap-2">
                  <CalendarIcon className="h-4 w-4" />
                  开始时间
                </Label>
                <Input
                  id="startDate"
                  type="date"
                  value={config.startDate}
                  onChange={(e) => handleInputChange('startDate', e.target.value)}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="endDate" className="flex items-center gap-2">
                  <CalendarIcon className="h-4 w-4" />
                  结束时间
                </Label>
                <Input
                  id="endDate"
                  type="date"
                  value={config.endDate}
                  onChange={(e) => handleInputChange('endDate', e.target.value)}
                />
              </div>
            </div>
          </div>
          
          <Separator />
          
          {/* 策略参数 */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">策略参数</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="leverage">杠杆倍数</Label>
                <Input
                  id="leverage"
                  type="number"
                  value={config.leverage}
                  onChange={(e) => handleInputChange('leverage', Number(e.target.value))}
                  min="1"
                  max="100"
                  step="1"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="maxPositionValueRatio">最大仓位比例</Label>
                <Input
                  id="maxPositionValueRatio"
                  type="number"
                  value={config.maxPositionValueRatio}
                  onChange={(e) => handleInputChange('maxPositionValueRatio', Number(e.target.value))}
                  min="0.1"
                  max="1"
                  step="0.1"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="bidSpread">买单价差 (%)</Label>
                <Input
                  id="bidSpread"
                  type="number"
                  value={config.bidSpread * 100}
                  onChange={(e) => handleInputChange('bidSpread', Number(e.target.value) / 100)}
                  min="0.001"
                  max="1"
                  step="0.001"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="askSpread">卖单价差 (%)</Label>
                <Input
                  id="askSpread"
                  type="number"
                  value={config.askSpread * 100}
                  onChange={(e) => handleInputChange('askSpread', Number(e.target.value) / 100)}
                  min="0.001"
                  max="1"
                  step="0.001"
                />
              </div>
            </div>
          </div>
          
          <Separator />
          
          {/* 订单配置 */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">订单配置</h3>
            
            <div className="flex items-center space-x-2">
              <Switch
                id="useDynamicOrderSize"
                checked={config.useDynamicOrderSize}
                onCheckedChange={(checked) => handleInputChange('useDynamicOrderSize', checked)}
              />
              <Label htmlFor="useDynamicOrderSize">启用动态订单大小</Label>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="minOrderAmount">最小订单量 (ETH)</Label>
                <Input
                  id="minOrderAmount"
                  type="number"
                  value={config.minOrderAmount}
                  onChange={(e) => handleInputChange('minOrderAmount', Number(e.target.value))}
                  min="0.001"
                  step="0.001"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="maxOrderAmount">最大订单量 (ETH)</Label>
                <Input
                  id="maxOrderAmount"
                  type="number"
                  value={config.maxOrderAmount}
                  onChange={(e) => handleInputChange('maxOrderAmount', Number(e.target.value))}
                  min="0.001"
                  step="0.1"
                />
              </div>
            </div>
          </div>
          
          <Separator />
          
          {/* 提交按钮 */}
          <div className="flex justify-end">
            <Button 
              type="submit" 
              disabled={loading}
              className="flex items-center gap-2"
            >
              <PlayIcon className="h-4 w-4" />
              {loading ? '启动中...' : '开始回测'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default BacktestConfigForm;