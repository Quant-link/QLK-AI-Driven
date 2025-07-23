// Core Types for Trading AI Dashboard

export interface Token {
  id: string;
  symbol: string;
  name: string;
  price: number;
  change24h: number;
  change7d: number;
  volume24h: number;
  liquidity: number;
  volatility: number;
  marketCap: number;
  circulatingSupply: number;
  maxSupply: number;
  fdv: number;
  ath: number;
  atl: number;
  lastUpdated: Date;
}

export interface ArbitrageOpportunity {
  id: string;
  tokenA: string;
  tokenB: string;
  dexA: string;
  dexB: string;
  profit: number;
  profitPercentage: number;
  volume: number;
  timestamp: Date;
  status: 'detected' | 'executed' | 'failed' | 'expired';
  executionTime?: number;
  gasUsed?: number;
}

export interface Strategy {
  id: string;
  type: 'TWAP' | 'DCA' | 'Arbitrage' | 'Grid' | 'Momentum';
  token: string;
  status: 'active' | 'paused' | 'completed' | 'error';
  progress: number;
  startTime: Date;
  lastExecution: Date;
  totalExecutions: number;
  totalVolume: number;
  pnl: number;
  roi: number;
  parameters: Record<string, any>;
}

export interface Route {
  id: string;
  tokenIn: string;
  tokenOut: string;
  path: string[];
  gasCost: number;
  gasLimit: number;
  slippage: number;
  priceImpact: number;
  estimatedTime: number;
  confidence: number;
  dexes: string[];
  amountIn: number;
  amountOut: number;
}

export interface MarketMetrics {
  totalValueLocked: number;
  totalVolume24h: number;
  activeStrategies: number;
  successRate: number;
  avgExecutionTime: number;
  totalPnL: number;
}

export interface ChartDataPoint {
  time: string;
  price: number;
  volume: number;
  liquidity: number;
  trades: number;
}

export interface PerformanceDataPoint {
  date: string;
  pnl: number;
  volume: number;
  trades: number;
}

// Component Props Types
export interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ComponentType<{ className?: string }>;
  description?: string;
  trend?: 'up' | 'down' | 'neutral';
  progress?: number;
  target?: number;
  className?: string;
}

export interface TokenChartProps {
  tokenSymbol: string;
}

export interface TokenListTableProps {
  tokens: Token[];
}

export interface RouteTableProps {
  routes: Route[];
}

export interface StrategyStatusCardProps {
  strategy: Strategy;
}

export interface RecentOpportunitiesTableProps {
  opportunities: ArbitrageOpportunity[];
}

export interface VolatilityAlertProps {
  tokens: Token[];
}

// Utility Types
export type SortDirection = 'asc' | 'desc';
export type TableSortKey = 'price' | 'change24h' | 'volume24h' | 'marketCap';
export type ChartTimeframe = '1h' | '4h' | '1d' | '7d' | '30d';
export type StrategyStatus = 'active' | 'paused' | 'completed' | 'error';
export type OpportunityStatus = 'detected' | 'executed' | 'failed' | 'expired';