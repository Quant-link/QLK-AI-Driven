import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Play, Pause, CheckCircle, TrendingUp, TrendingDown } from 'lucide-react';
import { useEffect, useState } from 'react';

interface DCAStrategy {
  id: number;
  token: string;
  status: string;
  total_investment: number;
  intervals_completed: number;
  total_intervals: number;
  avg_buy_price: number;
  current_price: number;
  total_tokens: number;
  current_value: number;
  pnl: number;
  pnl_percentage: number;
  next_buy_in: number | null;
  frequency: string;
}

export function DCAStatusCard() {
  const [strategies, setStrategies] = useState<DCAStrategy[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/dca_data")
      .then((res) => res.json())
      .then((data) => {
        setStrategies(data.strategies);
        setLoading(false);
      })
      .catch((err) => {
        console.error("DCA API fetch failed", err);
        setLoading(false);
      });
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <Play className="h-4 w-4" />;
      case 'paused':
        return <Pause className="h-4 w-4" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'completed':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="h-full animate-pulse">
            <CardHeader className="pb-3 sm:pb-4">
              <div className="h-6 bg-gray-200 rounded w-3/4"></div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="h-4 bg-gray-200 rounded w-full"></div>
              <div className="h-4 bg-gray-200 rounded w-2/3"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6">
      {strategies.map((strategy) => {
        const progress = (strategy.intervals_completed / strategy.total_intervals) * 100;
        const isProfitable = strategy.pnl > 0;
        
        return (
          <Card key={strategy.id} className="h-full">
            <CardHeader className="pb-3 sm:pb-4">
              <div className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
                <CardTitle className="text-base sm:text-lg">DCA - {strategy.token}</CardTitle>
                <Badge className={getStatusColor(strategy.status)}>
                  <div className="flex items-center space-x-1">
                    {getStatusIcon(strategy.status)}
                    <span className="capitalize">{strategy.status}</span>
                  </div>
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3 sm:space-y-4">
              <div>
                <div className="flex justify-between text-xs sm:text-sm mb-2">
                  <span className="text-muted-foreground">Progress</span>
                  <span className="font-medium">{strategy.intervals_completed}/{strategy.total_intervals}</span>
                </div>
                <Progress value={progress} className="w-full h-2" />
              </div>
              
              <div className="grid grid-cols-2 gap-3 text-xs sm:text-sm">
                <div>
                  <span className="text-muted-foreground">Invested</span>
                  <div className="font-medium">{formatCurrency(strategy.total_investment)}</div>
                </div>
                <div>
                  <span className="text-muted-foreground">Current Value</span>
                  <div className="font-medium">{formatCurrency(strategy.current_value)}</div>
                </div>
                <div>
                  <span className="text-muted-foreground">Avg Price</span>
                  <div className="font-medium">${strategy.avg_buy_price.toFixed(4)}</div>
                </div>
                <div>
                  <span className="text-muted-foreground">Current Price</span>
                  <div className="font-medium">${strategy.current_price.toFixed(4)}</div>
                </div>
              </div>

              <div className="pt-2 border-t">
                <div className="flex items-center justify-between">
                  <span className="text-xs sm:text-sm text-muted-foreground">P&L</span>
                  <div className={`flex items-center space-x-1 ${isProfitable ? 'text-green-600' : 'text-red-600'}`}>
                    {isProfitable ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                    <span className="font-medium text-xs sm:text-sm">
                      {formatCurrency(strategy.pnl)} ({strategy.pnl_percentage.toFixed(2)}%)
                    </span>
                  </div>
                </div>
                
                {strategy.next_buy_in && (
                  <div className="flex justify-between text-xs text-muted-foreground mt-2">
                    <span>Next buy in:</span>
                    <span>{strategy.next_buy_in}h</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
