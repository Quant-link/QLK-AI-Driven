import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { mockChartData } from '@/lib/mock-data';
import { TrendingUp, BarChart3, Activity, DollarSign } from 'lucide-react';

interface TokenChartProps {
  tokenSymbol: string;
}

interface ChartDataPoint {
  time: string;
  price: number;
  volume: number;
  liquidity: number;
  trades: number;
}

const SimpleLineChart: React.FC<{ data: ChartDataPoint[]; dataKey: keyof ChartDataPoint; color: string; height?: number }> = ({ 
  data, 
  dataKey, 
  color, 
  height = 300 
}) => {
  const values = data.map(d => Number(d[dataKey]));
  const maxValue = Math.max(...values);
  const minValue = Math.min(...values);
  const range = maxValue - minValue;

  const points = data.map((d, index) => {
    const x = (index / (data.length - 1)) * 100;
    const y = 100 - ((Number(d[dataKey]) - minValue) / range) * 100;
    return `${x},${y}`;
  }).join(' ');

  const formatValue = (value: number) => {
    if (dataKey === 'price') return `$${value.toFixed(2)}`;
    if (dataKey === 'volume' || dataKey === 'liquidity') return `$${(value / 1e6).toFixed(1)}M`;
    return value.toString();
  };

  return (
    <div className="w-full" style={{ height }}>
      <div className="relative w-full h-full bg-gradient-to-b from-muted/20 to-muted/5 rounded-lg p-4">
        <svg
          width="100%"
          height="100%"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          className="absolute inset-0"
        >
          <defs>
            <linearGradient id={`gradient-${dataKey}`} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={color} stopOpacity="0.3" />
              <stop offset="100%" stopColor={color} stopOpacity="0.05" />
            </linearGradient>
          </defs>
          <polyline
            fill="none"
            stroke={color}
            strokeWidth="0.5"
            points={points}
            vectorEffect="non-scaling-stroke"
          />
          <polygon
            fill={`url(#gradient-${dataKey})`}
            points={`0,100 ${points} 100,100`}
          />
        </svg>
        
        <div className="absolute top-2 left-2 text-xs text-muted-foreground">
          Max: {formatValue(maxValue)}
        </div>
        <div className="absolute bottom-2 left-2 text-xs text-muted-foreground">
          Min: {formatValue(minValue)}
        </div>
        <div className="absolute bottom-2 right-2 text-xs text-muted-foreground">
          Current: {formatValue(values[values.length - 1])}
        </div>
      </div>
    </div>
  );
};

const SimpleBarChart: React.FC<{ data: ChartDataPoint[]; dataKey: keyof ChartDataPoint; color: string; height?: number }> = ({ 
  data, 
  dataKey, 
  color, 
  height = 300 
}) => {
  const values = data.map(d => Number(d[dataKey]));
  const maxValue = Math.max(...values);

  const formatValue = (value: number) => {
    if (dataKey === 'volume' || dataKey === 'liquidity') return `$${(value / 1e6).toFixed(1)}M`;
    return value.toString();
  };

  return (
    <div className="w-full" style={{ height }}>
      <div className="relative w-full h-full bg-gradient-to-b from-muted/20 to-muted/5 rounded-lg p-4">
        <div className="flex items-end justify-between h-full space-x-1">
          {data.map((d, index) => {
            const value = Number(d[dataKey]);
            const heightPercent = (value / maxValue) * 100;
            
            return (
              <div
                key={index}
                className="flex-1 flex flex-col items-center group relative"
              >
                <div
                  className="w-full rounded-t transition-all duration-300 hover:opacity-80"
                  style={{
                    height: `${heightPercent}%`,
                    backgroundColor: color,
                    minHeight: '2px'
                  }}
                />
                <div className="text-xs text-muted-foreground mt-1 transform -rotate-45 origin-left">
                  {d.time}
                </div>
                
                {/* Tooltip */}
                <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-black text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                  {formatValue(value)}
                </div>
              </div>
            );
          })}
        </div>
        
        <div className="absolute top-2 left-2 text-xs text-muted-foreground">
          Max: {formatValue(maxValue)}
        </div>
      </div>
    </div>
  );
};

export function TokenChart({ tokenSymbol }: TokenChartProps): JSX.Element {
  const [activeTab, setActiveTab] = useState('price');
  const chartData = mockChartData;

  const tabConfigs = [
    { value: 'price', label: 'Price', icon: TrendingUp, color: '#3b82f6' },
    { value: 'volume', label: 'Volume', icon: BarChart3, color: '#10b981' },
    { value: 'liquidity', label: 'Liquidity', icon: DollarSign, color: '#8b5cf6' },
    { value: 'combined', label: 'Combined', icon: Activity, color: '#f59e0b' },
  ];

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col space-y-3 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
          <div className="flex items-center space-x-3">
            <div className="h-8 w-8 sm:h-10 sm:w-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
              {tokenSymbol.slice(0, 2)}
            </div>
            <div>
              <CardTitle className="flex items-center space-x-2 text-lg sm:text-xl">
                <span>{tokenSymbol} Market Analysis</span>
                <Badge variant="secondary" className="text-xs">Live</Badge>
              </CardTitle>
              <p className="text-xs sm:text-sm text-muted-foreground">
                Real-time price, volume, and liquidity data
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="text-green-600 border-green-200">
              <TrendingUp className="h-3 w-3 mr-1" />
              +3.45%
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-2 sm:grid-cols-4">
            {tabConfigs.map(({ value, label, icon: Icon }) => (
              <TabsTrigger 
                key={value}
                value={value} 
                className="flex items-center space-x-1 sm:space-x-2 text-xs sm:text-sm"
              >
                <Icon className="h-3 w-3 sm:h-4 sm:w-4" />
                <span className="hidden sm:inline">{label}</span>
                <span className="sm:hidden">{label.slice(0, 3)}</span>
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent value="price" className="space-y-4">
            <SimpleLineChart 
              data={chartData} 
              dataKey="price" 
              color="#3b82f6"
              height={350}
            />
          </TabsContent>

          <TabsContent value="volume" className="space-y-4">
            <SimpleBarChart 
              data={chartData} 
              dataKey="volume" 
              color="#10b981"
              height={350}
            />
          </TabsContent>

          <TabsContent value="liquidity" className="space-y-4">
            <SimpleLineChart 
              data={chartData} 
              dataKey="liquidity" 
              color="#8b5cf6"
              height={350}
            />
          </TabsContent>

          <TabsContent value="combined" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div>
                <h4 className="text-sm font-medium mb-2 flex items-center">
                  <TrendingUp className="h-4 w-4 mr-1" />
                  Price Trend
                </h4>
                <SimpleLineChart 
                  data={chartData} 
                  dataKey="price" 
                  color="#3b82f6"
                  height={200}
                />
              </div>
              <div>
                <h4 className="text-sm font-medium mb-2 flex items-center">
                  <BarChart3 className="h-4 w-4 mr-1" />
                  Volume
                </h4>
                <SimpleBarChart 
                  data={chartData} 
                  dataKey="volume" 
                  color="#10b981"
                  height={200}
                />
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}