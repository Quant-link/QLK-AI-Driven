import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { DivideIcon as LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: LucideIcon;
  description?: string;
  trend?: 'up' | 'down' | 'neutral';
  progress?: number;
  target?: number;
  className?: string;
}

interface TrendConfig {
  color: string;
  label: string;
}

interface ChangeConfig {
  color: string;
  prefix: string;
}

const getTrendConfig = (trend?: 'up' | 'down' | 'neutral'): TrendConfig => {
  switch (trend) {
    case 'up':
      return {
        color: 'text-green-600 dark:text-green-400 border-green-200',
        label: 'UP'
      };
    case 'down':
      return {
        color: 'text-red-600 dark:text-red-400 border-red-200',
        label: 'DOWN'
      };
    default:
      return {
        color: 'text-muted-foreground border-muted',
        label: 'STABLE'
      };
  }
};

const getChangeConfig = (change?: number): ChangeConfig => {
  if (change === undefined) {
    return {
      color: 'text-muted-foreground',
      prefix: ''
    };
  }
  
  return {
    color: change >= 0 
      ? 'text-green-600 dark:text-green-400' 
      : 'text-red-600 dark:text-red-400',
    prefix: change >= 0 ? '+' : ''
  };
};

const formatValue = (value: string | number): string => {
  if (typeof value === 'string') return value;
  
  if (value >= 1e12) return `${(value / 1e12).toFixed(2)}T`;
  if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
  if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
  if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`;
  
  return value.toString();
};

export function MetricCard({ 
  title, 
  value, 
  change, 
  icon: Icon, 
  description, 
  trend,
  progress,
  target,
  className 
}: MetricCardProps): JSX.Element {
  const trendConfig = getTrendConfig(trend);
  const changeConfig = getChangeConfig(change);
  const formattedValue = formatValue(value);

  return (
    <Card className={cn(
      'transition-all duration-200 hover:shadow-md h-full',
      'border-border/50 hover:border-border',
      className
    )}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 sm:pb-3">
        <CardTitle className="text-xs sm:text-sm font-medium text-muted-foreground truncate pr-2">
          {title}
        </CardTitle>
        <div className="flex items-center space-x-2">
          {trend && (
            <Badge 
              variant="outline" 
              className={cn('text-xs hidden sm:inline-flex', trendConfig.color)}
            >
              <span className="hidden lg:inline">{trendConfig.label}</span>
              <span className="lg:hidden">{trendConfig.label.charAt(0)}</span>
            </Badge>
          )}
          <Icon className="h-4 w-4 sm:h-5 sm:w-5 text-muted-foreground flex-shrink-0" />
        </div>
      </CardHeader>
      
      <CardContent className="space-y-2 sm:space-y-3">
        <div className="flex items-baseline space-x-2">
          <div className="text-xl sm:text-2xl lg:text-3xl font-bold truncate">
            {formattedValue}
          </div>
          {target && (
            <div className="text-xs sm:text-sm text-muted-foreground hidden sm:block">
              / {formatValue(target)}
            </div>
          )}
        </div>
        
        {change !== undefined && (
          <div className="flex items-center space-x-2">
            <span className={cn('text-xs font-medium', changeConfig.color)}>
              {changeConfig.prefix}{change.toFixed(2)}%
            </span>
            <span className="text-xs text-muted-foreground hidden sm:inline">
              from last hour
            </span>
            <span className="text-xs text-muted-foreground sm:hidden">1h</span>
          </div>
        )}
        
        {progress !== undefined && (
          <div className="space-y-1">
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Progress</span>
              <span>{progress.toFixed(1)}%</span>
            </div>
            <Progress 
              value={Math.min(Math.max(progress, 0), 100)} 
              className="h-1.5 sm:h-2" 
            />
          </div>
        )}
        
        {description && (
          <p className="text-xs text-muted-foreground leading-relaxed hidden sm:block">
            {description}
          </p>
        )}
      </CardContent>
    </Card>
  );
}