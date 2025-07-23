import { Badge } from '@/components/ui/badge';
import { Fuel } from 'lucide-react';

interface GasCostIndicatorProps {
  cost: number;
}

export function GasCostIndicator({ cost }: GasCostIndicatorProps) {
  const getCostLevel = (cost: number) => {
    if (cost < 30) return { level: 'Low', color: 'bg-green-100 text-green-800 border-green-200' };
    if (cost < 60) return { level: 'Medium', color: 'bg-yellow-100 text-yellow-800 border-yellow-200' };
    return { level: 'High', color: 'bg-red-100 text-red-800 border-red-200' };
  };

  const { level, color } = getCostLevel(cost);

  return (
    <div className="flex items-center space-x-2">
      <Fuel className="h-3 w-3 text-muted-foreground" />
      <div className="space-y-1">
        <Badge className={color}>
          {level}
        </Badge>
        <div className="text-xs text-muted-foreground">
          ${cost.toFixed(2)}
        </div>
      </div>
    </div>
  );
}