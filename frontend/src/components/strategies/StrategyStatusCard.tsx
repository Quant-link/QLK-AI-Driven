import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Strategy } from '@/lib/mock-data';
import { Play, Pause, CheckCircle } from 'lucide-react';

interface StrategyStatusCardProps {
  strategy: Strategy;
}

export function StrategyStatusCard({ strategy }: StrategyStatusCardProps) {
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

  return (
    <Card className="h-full">
      <CardHeader className="pb-3 sm:pb-4">
        <div className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
          <CardTitle className="text-base sm:text-lg">{strategy.type} Strategy</CardTitle>
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
            <span className="text-muted-foreground">Target Token</span>
            <span className="font-medium">{strategy.token}</span>
          </div>
          <div className="flex justify-between text-xs sm:text-sm mb-2">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-medium">{strategy.progress}%</span>
          </div>
          <Progress value={strategy.progress} className="w-full h-2" />
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 text-xs sm:text-sm">
          <div>
            <span className="text-muted-foreground">Total Executions</span>
            <div className="font-medium">{strategy.totalExecutions}</div>
          </div>
          <div>
            <span className="text-muted-foreground">Last Execution</span>
            <div className="font-medium">
              {strategy.lastExecution.toLocaleTimeString()}
            </div>
          </div>
        </div>
        
        <div className="text-xs text-muted-foreground pt-2 sm:pt-3 border-t">
          <div className="sm:hidden">
            Started: {strategy.startTime.toLocaleDateString()}
          </div>
          <div className="hidden sm:block">
            Started: {strategy.startTime.toLocaleDateString()} {strategy.startTime.toLocaleTimeString()}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}