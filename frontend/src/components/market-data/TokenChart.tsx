import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, BarChart3, Activity, DollarSign } from 'lucide-react';

const shineStyles = `
  @keyframes shine {
    0% { transform: translateX(-100%) skewX(-12deg); }
    100% { transform: translateX(200%) skewX(-12deg); }
  }
`;

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

interface TokenData {
  symbol: string;
  price: number | null;
  change_24h: number | null;
  volume_24h: number | null;
  liquidity: number | null;
}

const SimpleLineChart: React.FC<{ data: ChartDataPoint[]; dataKey: keyof ChartDataPoint; color: string; height?: number }> = ({ 
  data, 
  dataKey, 
  color, 
  height = 300 
}) => {
  const values = data
  .map(d => Number(d[dataKey]))
  .filter(v => isFinite(v));

  const maxValue = values.length ? Math.max(...values) : 0;
  const minValue = values.length ? Math.min(...values) : 0;
  const range = maxValue - minValue;

  const formatValue = (value?: number) => {
    if (value === undefined || value === null || !isFinite(value)) return "N/A";

    if (dataKey === "price") {
      return `$${value.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}`;
    }
    if (dataKey === "volume") return `$${(value / 1e9).toFixed(2)}B`;
    if (dataKey === "liquidity") return `$${(value / 1e6).toFixed(1)}M`;
    return value.toString();
  };

  const getGradientId = () => `gradient-${dataKey}-${Math.random().toString(36).substring(2, 11)}`;
  const gradientId = getGradientId();

  return (
    <div className="w-full" style={{ height }}>
      <div className="relative w-full h-full bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 rounded-xl border border-border/50 p-6 shadow-sm">
        <svg className="w-full h-full" viewBox="0 0 500 200" preserveAspectRatio="none">
          <defs>
            <linearGradient id={gradientId} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={color} stopOpacity="0.4" />
              <stop offset="50%" stopColor={color} stopOpacity="0.2" />
              <stop offset="100%" stopColor={color} stopOpacity="0.05" />
            </linearGradient>

            <pattern id={`grid-${dataKey}`} width="40" height="25" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 25" fill="none" stroke="currentColor" strokeWidth="0.5" opacity="0.1"/>
            </pattern>

            <filter id={`glow-${dataKey}`}>
              <feGaussianBlur stdDeviation="1.5" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          <rect x="45" y="0" width="455" height="200" fill={`url(#grid-${dataKey})`} />

          {[0.25, 0.5, 0.75].map((ratio, i) => {
            const yValue = minValue + (maxValue - minValue) * (1 - ratio);
            const formatYAxisLabel = (value: number) => {
              if (dataKey === 'price') {
                if (value >= 10000) {
                  return `$${(value / 1000).toFixed(0)}K`;
                } else if (value >= 1000) {
                  return `$${(value / 1000).toFixed(1)}K`;
                } else {
                  return `$${Math.round(value)}`;
                }
              }
              if (dataKey === 'volume') {
                if (value >= 1e12) {
                  return `$${(value / 1e12).toFixed(1)}T`;
                } else if (value >= 1e9) {
                  return `$${(value / 1e9).toFixed(1)}B`;
                } else if (value >= 1e6) {
                  return `$${(value / 1e6).toFixed(0)}M`;
                } else {
                  return `$${(value / 1e3).toFixed(0)}K`;
                }
              }
              if (dataKey === 'liquidity') {
                if (value >= 1e9) {
                  return `$${(value / 1e9).toFixed(1)}B`;
                } else if (value >= 1e6) {
                  return `$${(value / 1e6).toFixed(0)}M`;
                } else {
                  return `$${(value / 1e3).toFixed(0)}K`;
                }
              }
              return value.toFixed(0);
            };

            return (
              <g key={i}>
                <line
                  x1="45"
                  y1={200 * ratio}
                  x2="500"
                  y2={200 * ratio}
                  stroke="currentColor"
                  strokeWidth="0.5"
                  opacity="0.15"
                  strokeDasharray="3,3"
                />
                <text
                  x="15"
                  y={200 * ratio + 3}
                  textAnchor="start"
                  fill="currentColor"
                  fontSize="9"
                  opacity="0.8"
                  fontWeight="600"
                  fontFamily="system-ui, -apple-system, sans-serif"
                >
                  {formatYAxisLabel(yValue)}
                </text>
              </g>
            );
          })}

          {(() => {
            const chartPoints = data.map((d, index) => ({
              x: 50 + (index / (data.length - 1)) * 445,
              y: 200 - ((Number(d[dataKey]) - minValue) / (range || 1)) * 170 - 15
            }));

            const pathData = chartPoints.map((point, i) =>
              i === 0 ? `M ${point.x} ${point.y}` : `L ${point.x} ${point.y}`
            ).join(' ');

            return (
              <>
                <path
                  d={`${pathData} L 495 200 L 50 200 Z`}
                  fill={`url(#${gradientId})`}
                />

                <path
                  d={pathData}
                  fill="none"
                  stroke={color}
                  strokeWidth="1.5"
                  filter={`url(#glow-${dataKey})`}
                  className="drop-shadow-sm"
                />

                {chartPoints.map((point, index) => (
                  <g key={index} className="group">
                    <circle
                      cx={point.x}
                      cy={point.y}
                      r="3"
                      fill="white"
                      stroke={color}
                      strokeWidth="2"
                      className="opacity-0 group-hover:opacity-100 transition-all duration-200 cursor-pointer"
                    />
                    <g className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
                      <rect
                        x={point.x - 35}
                        y={point.y - 40}
                        width="70"
                        height="28"
                        rx="6"
                        fill="rgba(0,0,0,0.85)"
                        stroke="rgba(255,255,255,0.1)"
                        strokeWidth="1"
                      />
                      <text
                        x={point.x}
                        y={point.y - 25}
                        textAnchor="middle"
                        fill="white"
                        fontSize="11"
                        fontWeight="600"
                      >
                        {formatValue(values[index])}
                      </text>
                      <text
                        x={point.x}
                        y={point.y - 15}
                        textAnchor="middle"
                        fill="rgba(255,255,255,0.7)"
                        fontSize="9"
                      >
                        {data[index].time}
                      </text>
                    </g>
                  </g>
                ))}
              </>
            );
          })()}
        </svg>

        <div className="absolute top-3 left-3">
          <div className="text-xs text-muted-foreground mb-1 font-medium">Max</div>
          <div className="text-sm font-bold text-foreground">{formatValue(maxValue)}</div>
        </div>
        <div className="absolute bottom-3 left-3">
          <div className="text-xs text-muted-foreground mb-1 font-medium">Min</div>
          <div className="text-sm font-bold text-foreground">{formatValue(minValue)}</div>
        </div>
        <div className="absolute bottom-3 right-3">
          <div className="text-xs text-muted-foreground mb-1 font-medium">Current</div>
          <div className="text-sm font-bold" style={{ color }}>
            {formatValue(values[values.length - 1])}
          </div>
        </div>

        <div className="absolute top-3 right-3">
          <div className={`flex items-center space-x-1 px-3 py-1.5 rounded-full text-xs font-semibold shadow-sm ${
            values[values.length - 1] > values[0]
              ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
              : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
          }`}>
            {values[values.length - 1] > values[0] ? (
              <TrendingUp className="h-3 w-3" />
            ) : (
              <TrendingUp className="h-3 w-3 rotate-180" />
            )}
            <span>
              {((values[values.length - 1] - values[0]) / values[0] * 100).toFixed(1)}%
            </span>
          </div>
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
    if (dataKey === 'volume') return `$${(value / 1e9).toFixed(2)}B`;
    if (dataKey === 'liquidity') return `$${(value / 1e6).toFixed(1)}M`;
    return value.toString();
  };

  return (
    <div className="w-full" style={{ height }}>
      <style>{shineStyles}</style>
      <div className="relative w-full h-full bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 rounded-xl border border-border/50 p-6 shadow-sm">
        <div className="absolute left-2 top-6 bottom-16 flex flex-col justify-between text-xs text-muted-foreground">
          {[0.75, 0.5, 0.25, 0].map((ratio, i) => {
            const yValue = maxValue * (1 - ratio);
            return (
              <div key={i} className="text-right pr-2 font-medium">
                {formatValue(yValue)}
              </div>
            );
          })}
        </div>

        <div className="absolute left-8 right-6 top-6 bottom-16">
          {[0.25, 0.5, 0.75].map((ratio, i) => (
            <div
              key={i}
              className="absolute w-full border-t border-dashed border-border/30"
              style={{ top: `${ratio * 100}%` }}
            />
          ))}
        </div>

        <div className="flex items-end justify-between h-full space-x-1 pl-8 pr-2 pb-4">
          {data.map((d, index) => {
            const value = Number(d[dataKey]);
            const heightPercent = Math.max((value / maxValue) * 85, 3); 
            const isHighValue = value > maxValue * 0.7;

            return (
              <div
                key={index}
                className="flex-1 flex flex-col items-center group relative max-w-[40px]"
              >
                <div
                  className="w-full rounded-t-xl transition-all duration-300 hover:scale-110 hover:shadow-xl relative overflow-hidden border-b-2"
                  style={{
                    height: `${heightPercent}%`,
                    background: `linear-gradient(180deg, ${color} 0%, ${color}CC 50%, ${color}80 100%)`,
                    minHeight: '8px',
                    boxShadow: `0 4px 15px ${color}30, inset 0 1px 0 rgba(255,255,255,0.2)`,
                    borderBottomColor: color,
                    borderRadius: '8px 8px 4px 4px'
                  }}
                >
                  <div
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent transform -skew-x-12 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                    style={{ animation: 'shine 2s ease-in-out infinite' }}
                  />

                  <div
                    className="absolute top-0 left-1 right-1 h-1 rounded-t-lg"
                    style={{ background: `linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)` }}
                  />

                  {isHighValue && (
                    <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 w-2 h-2 rounded-full bg-yellow-400 animate-pulse" />
                  )}
                </div>

                <div className="text-xs text-muted-foreground mt-3 font-medium text-center">
                  <div className="group-hover:text-foreground transition-colors duration-200">
                    {d.time.split(':')[0]}h
                  </div>
                </div>

                <div className="absolute bottom-full mb-4 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-all duration-300 z-30">
                  <div className="bg-gray-900/95 backdrop-blur-sm text-white text-xs px-4 py-3 rounded-xl shadow-2xl border border-gray-700/50">
                    <div className="font-bold text-sm" style={{ color }}>{formatValue(value)}</div>
                    <div className="text-gray-300 text-xs mt-1">{d.time}</div>
                    <div className="text-gray-400 text-xs">
                      {((value / maxValue) * 100).toFixed(1)}% of peak
                    </div>
                    <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-6 border-r-6 border-t-6 border-transparent border-t-gray-900/95"></div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        <div className="absolute top-3 left-3">
          <div className="text-xs text-muted-foreground mb-1 font-medium">Peak</div>
          <div className="text-sm font-bold text-foreground">{formatValue(maxValue)}</div>
        </div>

        <div className="absolute top-3 right-3">
          <div className="text-xs text-muted-foreground mb-1 font-medium">Average</div>
          <div className="text-sm font-bold" style={{ color }}>
            {formatValue(values.reduce((a, b) => a + b, 0) / values.length)}
          </div>
        </div>
      </div>
    </div>
  );
};

export function TokenChart({ tokenSymbol }: TokenChartProps): JSX.Element {
  const [activeTab, setActiveTab] = useState('price');
  const [tokenData, setTokenData] = useState<TokenData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/market_data")
      .then((res) => res.json())
      .then((data) => {
        const ethToken = data.tokens?.find((token: any) =>
          token.symbol.toLowerCase() === tokenSymbol.toLowerCase()
        );
        if (ethToken) {
          setTokenData({
            symbol: ethToken.symbol,
            price: ethToken.price,
            change_24h: ethToken.change_24h,
            volume_24h: ethToken.volume_24h,
            liquidity: ethToken.liquidity
          });
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch token data:", err);
        setLoading(false);
      });
  }, [tokenSymbol]);

  const generateChartData = (): ChartDataPoint[] => {
    if (!tokenData) return [];

    const dataPoints: ChartDataPoint[] = [];
    const now = new Date();
    const basePrice = tokenData.price || 4200;
    const baseVolume = tokenData.volume_24h || 15000000000;
    const baseLiquidity = tokenData.liquidity || 5000000000; 

    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 60 * 1000);
      const hourlyVariation = (Math.random() - 0.5) * 0.1;

      dataPoints.push({
        time: time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        price: basePrice * (1 + hourlyVariation),
        volume: baseVolume / 24 * (1 + hourlyVariation * 2), 
        liquidity: baseLiquidity * (1 + hourlyVariation * 0.5),
        trades: Math.floor(Math.random() * 1000) + 100
      });
    }

    return dataPoints;
  };

  const chartData = generateChartData();

  const tabConfigs = [
    { value: 'price', label: 'Price', icon: TrendingUp, color: '#3b82f6' },
    { value: 'volume', label: 'Volume', icon: BarChart3, color: '#10b981' },
    { value: 'liquidity', label: 'Liquidity', icon: DollarSign, color: '#8b5cf6' },
    { value: 'combined', label: 'Combined', icon: Activity, color: '#f59e0b' },
  ];

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-3">
            <div className="h-8 w-8 sm:h-10 sm:w-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
              {tokenSymbol.slice(0, 2)}
            </div>
            <div>
              <CardTitle className="flex items-center space-x-2 text-lg sm:text-xl">
                <span>{tokenSymbol} Market Analysis</span>
                <Badge variant="secondary" className="text-xs">Loading...</Badge>
              </CardTitle>
              <p className="text-xs sm:text-sm text-muted-foreground">
                Loading real-time data...
              </p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-200 rounded w-full"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

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
                {tokenData ? (
                  <>
                    Volume: ${tokenData.volume_24h ? (tokenData.volume_24h / 1e9).toFixed(2) + 'B' : 'N/A'} •
                    Liquidity: ${tokenData.liquidity ? (tokenData.liquidity / 1e6).toFixed(1) + 'M' : 'N/A'}
                  </>
                ) : (
                  'Real-time price, volume, and liquidity data'
                )}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {tokenData && (
              <>
                <Badge variant="outline" className={`${
                  (tokenData.change_24h || 0) >= 0
                    ? 'text-green-600 border-green-200'
                    : 'text-red-600 border-red-200'
                }`}>
                  {(tokenData.change_24h || 0) >= 0 ? (
                    <TrendingUp className="h-3 w-3 mr-1" />
                  ) : (
                    <TrendingUp className="h-3 w-3 mr-1 rotate-180" />
                  )}
                  {tokenData.change_24h ? `${tokenData.change_24h > 0 ? '+' : ''}${tokenData.change_24h.toFixed(2)}%` : 'N/A'}
                </Badge>
                <Badge variant="secondary" className="text-xs">
                  ${tokenData.price ? tokenData.price.toFixed(2) : 'N/A'}
                </Badge>
              </>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-12">
          <TabsList className="grid w-full grid-cols-2 sm:grid-cols-4 gap-3">
            {tabConfigs.map(({ value, label, icon: Icon }) => (
              <TabsTrigger
                key={value}
                value={value}
                className={`
                  flex items-center space-x-1 sm:space-x-2 text-xs sm:text-sm font-medium
                  transition-all duration-300 ease-in-out
                  rounded-lg px-4 py-2.5 sm:px-6 sm:py-3 min-w-[80px] sm:min-w-[100px]
                  hover:shadow-md hover:scale-102
                  data-[state=active]:shadow-lg data-[state=active]:scale-102
                  data-[state=active]:text-white data-[state=active]:font-semibold
                  ${activeTab === value
                    ? `bg-gradient-to-r shadow-lg border-0 text-white` +
                      (value === 'price' ? ' from-blue-500 to-blue-600' :
                       value === 'volume' ? ' from-green-500 to-green-600' :
                       value === 'liquidity' ? ' from-purple-500 to-purple-600' :
                       ' from-amber-500 to-amber-600')
                    : 'hover:bg-background/80 text-white hover:text-white'
                  }
                `}
              >
                <Icon className={`h-3 w-3 sm:h-4 sm:w-4 transition-all duration-300 ${
                  activeTab === value ? 'drop-shadow-sm' : ''
                }`} />
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
