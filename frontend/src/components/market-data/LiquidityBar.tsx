import { Progress } from '@/components/ui/progress';
import { Droplets } from 'lucide-react';

interface LiquidityBarProps {
  value: number;
  maxValue: number;
}

export function LiquidityBar({ value, maxValue }: LiquidityBarProps) {
  const percentage = (value / maxValue) * 100;
  
  const formatValue = (num: number) => {
    if (num >= 1e9) return `$${(num / 1e9).toFixed(1)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(1)}M`;
    if (num >= 1e3) return `$${(num / 1e3).toFixed(1)}K`;
    return `$${num.toFixed(0)}`;
  };

  const getLiquidityLevel = (percentage: number) => {
    if (percentage > 70) return { level: 'High', color: 'text-green-600' };
    if (percentage > 30) return { level: 'Medium', color: 'text-yellow-600' };
    return { level: 'Low', color: 'text-red-600' };
  };

  const { level, color } = getLiquidityLevel(percentage);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center space-x-1">
          <Droplets className="h-3 w-3 text-muted-foreground" />
          <span className="text-muted-foreground">Liquidity</span>
        </div>
        <span className={`font-medium ${color}`}>{level}</span>
      </div>
      <div className="space-y-1">
        <div className="flex justify-between text-xs">
          <span className="font-medium">{formatValue(value)}</span>
          <span className="text-muted-foreground">{percentage.toFixed(1)}%</span>
        </div>
        <Progress 
          value={Math.min(percentage, 100)} 
          className="h-2"
        />
      </div>
    </div>
  );
}