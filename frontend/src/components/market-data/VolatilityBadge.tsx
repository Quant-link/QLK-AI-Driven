import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface VolatilityBadgeProps {
  volatility: number;
}

export function VolatilityBadge({ volatility }: VolatilityBadgeProps) {
  const getVolatilityConfig = (vol: number) => {
    if (vol < 5) return { 
      level: 'Low', 
      color: 'bg-green-100 text-green-800 border-green-200 dark:bg-green-950 dark:text-green-100',
      icon: Minus,
      progressColor: 'bg-green-500'
    };
    if (vol < 15) return { 
      level: 'Medium', 
      color: 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-950 dark:text-yellow-100',
      icon: TrendingUp,
      progressColor: 'bg-yellow-500'
    };
    return { 
      level: 'High', 
      color: 'bg-red-100 text-red-800 border-red-200 dark:bg-red-950 dark:text-red-100',
      icon: TrendingUp,
      progressColor: 'bg-red-500'
    };
  };

  const { level, color, icon: Icon, progressColor } = getVolatilityConfig(volatility);

  return (
    <div className="space-y-2">
      <div className="flex items-center space-x-2">
        <Badge className={color}>
          <Icon className="h-3 w-3 mr-1" />
          {level}
        </Badge>
      </div>
      <div className="space-y-1">
        <div className="flex justify-between text-xs">
          <span className="text-muted-foreground">Volatility</span>
          <span className="font-medium">{volatility.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-muted rounded-full h-1.5">
          <div 
            className={`h-1.5 rounded-full transition-all duration-300 ${progressColor}`}
            style={{ width: `${Math.min(volatility * 2, 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
}