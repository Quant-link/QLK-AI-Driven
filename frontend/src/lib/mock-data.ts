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

export const mockTokens: Token[] = [
  {
    id: '1',
    symbol: 'ETH',
    name: 'Ethereum',
    price: 2456.78,
    change24h: 3.45,
    change7d: 12.8,
    volume24h: 15678900000,
    liquidity: 456000000,
    volatility: 12.3,
    marketCap: 295000000000,
    circulatingSupply: 120280000,
    maxSupply: 0,
    fdv: 295000000000,
    ath: 4891.70,
    atl: 0.43,
    lastUpdated: new Date()
  },
  {
    id: '2',
    symbol: 'USDC',
    name: 'USD Coin',
    price: 1.001,
    change24h: 0.01,
    change7d: -0.05,
    volume24h: 8900000000,
    liquidity: 890000000,
    volatility: 0.5,
    marketCap: 33000000000,
    circulatingSupply: 32967000000,
    maxSupply: 0,
    fdv: 33000000000,
    ath: 1.17,
    atl: 0.877,
    lastUpdated: new Date()
  },
  {
    id: '3',
    symbol: 'UNI',
    name: 'Uniswap',
    price: 8.92,
    change24h: -2.1,
    change7d: 8.4,
    volume24h: 230000000,
    liquidity: 120000000,
    volatility: 18.7,
    marketCap: 6700000000,
    circulatingSupply: 751000000,
    maxSupply: 1000000000,
    fdv: 8920000000,
    ath: 44.97,
    atl: 1.03,
    lastUpdated: new Date()
  },
  {
    id: '4',
    symbol: 'LINK',
    name: 'Chainlink',
    price: 15.67,
    change24h: 5.8,
    change7d: -3.2,
    volume24h: 180000000,
    liquidity: 89000000,
    volatility: 15.2,
    marketCap: 9200000000,
    circulatingSupply: 587000000,
    maxSupply: 1000000000,
    fdv: 15670000000,
    ath: 52.70,
    atl: 0.148,
    lastUpdated: new Date()
  },
  {
    id: '5',
    symbol: 'AAVE',
    name: 'Aave',
    price: 87.45,
    change24h: -1.2,
    change7d: 15.6,
    volume24h: 120000000,
    liquidity: 56000000,
    volatility: 22.1,
    marketCap: 1300000000,
    circulatingSupply: 14870000,
    maxSupply: 16000000,
    fdv: 1399200000,
    ath: 666.86,
    atl: 26.02,
    lastUpdated: new Date()
  },
  {
    id: '6',
    symbol: 'MATIC',
    name: 'Polygon',
    price: 0.89,
    change24h: 7.2,
    change7d: -5.1,
    volume24h: 340000000,
    liquidity: 78000000,
    volatility: 19.8,
    marketCap: 8900000000,
    circulatingSupply: 10000000000,
    maxSupply: 10000000000,
    fdv: 8900000000,
    ath: 2.92,
    atl: 0.00314,
    lastUpdated: new Date()
  }
];

export const mockArbitrageOpportunities: ArbitrageOpportunity[] = [
  {
    id: '1',
    tokenA: 'ETH',
    tokenB: 'USDC',
    dexA: 'Uniswap V3',
    dexB: 'SushiSwap',
    profit: 145.67,
    profitPercentage: 0.89,
    volume: 50000,
    timestamp: new Date(Date.now() - 300000),
    status: 'executed',
    executionTime: 12,
    gasUsed: 180000
  },
  {
    id: '2',
    tokenA: 'UNI',
    tokenB: 'ETH',
    dexA: 'Balancer',
    dexB: 'Curve',
    profit: 89.23,
    profitPercentage: 1.24,
    volume: 25000,
    timestamp: new Date(Date.now() - 600000),
    status: 'detected'
  },
  {
    id: '3',
    tokenA: 'LINK',
    tokenB: 'USDC',
    dexA: 'Uniswap V2',
    dexB: 'PancakeSwap',
    profit: 234.12,
    profitPercentage: 0.67,
    volume: 75000,
    timestamp: new Date(Date.now() - 900000),
    status: 'executed',
    executionTime: 8,
    gasUsed: 220000
  },
  {
    id: '4',
    tokenA: 'AAVE',
    tokenB: 'ETH',
    dexA: '1inch',
    dexB: 'Kyber',
    profit: 67.89,
    profitPercentage: 2.1,
    volume: 15000,
    timestamp: new Date(Date.now() - 1200000),
    status: 'failed'
  },
  {
    id: '5',
    tokenA: 'MATIC',
    tokenB: 'USDC',
    dexA: 'QuickSwap',
    dexB: 'SushiSwap',
    profit: 156.34,
    profitPercentage: 1.45,
    volume: 40000,
    timestamp: new Date(Date.now() - 1500000),
    status: 'expired'
  }
];

export const mockStrategies: Strategy[] = [
  {
    id: '1',
    type: 'TWAP',
    token: 'ETH',
    status: 'active',
    progress: 67,
    startTime: new Date(Date.now() - 86400000),
    lastExecution: new Date(Date.now() - 3600000),
    totalExecutions: 24,
    totalVolume: 125000,
    pnl: 2340.56,
    roi: 4.8,
    parameters: {
      totalAmount: 50000,
      timeWindow: 24,
      intervalMinutes: 60
    }
  },
  {
    id: '2',
    type: 'DCA',
    token: 'UNI',
    status: 'active',
    progress: 45,
    startTime: new Date(Date.now() - 172800000),
    lastExecution: new Date(Date.now() - 7200000),
    totalExecutions: 12,
    totalVolume: 75000,
    pnl: 890.23,
    roi: 2.1,
    parameters: {
      buyAmount: 1000,
      frequency: 'daily',
      targetAmount: 50000
    }
  },
  {
    id: '3',
    type: 'Arbitrage',
    token: 'LINK',
    status: 'paused',
    progress: 12,
    startTime: new Date(Date.now() - 259200000),
    lastExecution: new Date(Date.now() - 14400000),
    totalExecutions: 8,
    totalVolume: 45000,
    pnl: -123.45,
    roi: -0.8,
    parameters: {
      minProfitThreshold: 0.5,
      maxSlippage: 1.0
    }
  },
  {
    id: '4',
    type: 'Grid',
    token: 'AAVE',
    status: 'active',
    progress: 89,
    startTime: new Date(Date.now() - 345600000),
    lastExecution: new Date(Date.now() - 1800000),
    totalExecutions: 156,
    totalVolume: 200000,
    pnl: 5670.89,
    roi: 12.4,
    parameters: {
      gridLevels: 20,
      priceRange: [80, 120],
      gridSpacing: 2
    }
  },
  {
    id: '5',
    type: 'Momentum',
    token: 'MATIC',
    status: 'error',
    progress: 23,
    startTime: new Date(Date.now() - 432000000),
    lastExecution: new Date(Date.now() - 21600000),
    totalExecutions: 34,
    totalVolume: 89000,
    pnl: 456.78,
    roi: 1.9,
    parameters: {
      momentumThreshold: 5,
      stopLoss: 2,
      takeProfit: 8
    }
  }
];

export const mockRoutes: Route[] = [
  {
    id: '1',
    tokenIn: 'ETH',
    tokenOut: 'USDC',
    path: ['ETH', 'WETH', 'USDC'],
    gasCost: 45.67,
    gasLimit: 250000,
    slippage: 0.5,
    priceImpact: 0.12,
    estimatedTime: 15,
    confidence: 98.5,
    dexes: ['Uniswap V3', 'Curve'],
    amountIn: 10,
    amountOut: 24567.8
  },
  {
    id: '2',
    tokenIn: 'UNI',
    tokenOut: 'ETH',
    path: ['UNI', 'WETH', 'ETH'],
    gasCost: 32.45,
    gasLimit: 180000,
    slippage: 1.2,
    priceImpact: 0.45,
    estimatedTime: 20,
    confidence: 94.2,
    dexes: ['SushiSwap', 'Balancer'],
    amountIn: 1000,
    amountOut: 3.63
  },
  {
    id: '3',
    tokenIn: 'LINK',
    tokenOut: 'USDC',
    path: ['LINK', 'ETH', 'WETH', 'USDC'],
    gasCost: 78.90,
    gasLimit: 320000,
    slippage: 2.1,
    priceImpact: 0.89,
    estimatedTime: 25,
    confidence: 89.7,
    dexes: ['1inch', 'Kyber', 'Curve'],
    amountIn: 500,
    amountOut: 7835
  },
  {
    id: '4',
    tokenIn: 'AAVE',
    tokenOut: 'ETH',
    path: ['AAVE', 'USDC', 'WETH', 'ETH'],
    gasCost: 56.23,
    gasLimit: 280000,
    slippage: 1.8,
    priceImpact: 0.67,
    estimatedTime: 18,
    confidence: 91.3,
    dexes: ['Uniswap V2', 'SushiSwap'],
    amountIn: 100,
    amountOut: 3.56
  }
];

export const mockMarketMetrics: MarketMetrics = {
  totalValueLocked: 1250000000,
  totalVolume24h: 45600000000,
  activeStrategies: 127,
  successRate: 94.7,
  avgExecutionTime: 14.2,
  totalPnL: 156789.45
};

export const mockChartData = [
  { time: '00:00', price: 2420, volume: 12000000, liquidity: 450000000, trades: 1250 },
  { time: '02:00', price: 2428, volume: 8500000, liquidity: 451000000, trades: 980 },
  { time: '04:00', price: 2435, volume: 13500000, liquidity: 452000000, trades: 1450 },
  { time: '06:00', price: 2442, volume: 9800000, liquidity: 451500000, trades: 1120 },
  { time: '08:00', price: 2445, volume: 11000000, liquidity: 451000000, trades: 1380 },
  { time: '10:00', price: 2451, volume: 16200000, liquidity: 453000000, trades: 1680 },
  { time: '12:00', price: 2460, volume: 15000000, liquidity: 454000000, trades: 1590 },
  { time: '14:00', price: 2455, volume: 10800000, liquidity: 453500000, trades: 1220 },
  { time: '16:00', price: 2450, volume: 12500000, liquidity: 453000000, trades: 1340 },
  { time: '18:00', price: 2448, volume: 9200000, liquidity: 452500000, trades: 1050 },
  { time: '20:00', price: 2457, volume: 14000000, liquidity: 456000000, trades: 1520 },
  { time: '22:00', price: 2461, volume: 11800000, liquidity: 456500000, trades: 1290 }
];

export const mockPerformanceData = [
  { date: '2024-01-01', pnl: 1250, volume: 45000, trades: 23 },
  { date: '2024-01-02', pnl: 2340, volume: 67000, trades: 34 },
  { date: '2024-01-03', pnl: 1890, volume: 52000, trades: 28 },
  { date: '2024-01-04', pnl: 3450, volume: 78000, trades: 41 },
  { date: '2024-01-05', pnl: 2780, volume: 61000, trades: 35 },
  { date: '2024-01-06', pnl: 4120, volume: 89000, trades: 47 },
  { date: '2024-01-07', pnl: 3680, volume: 72000, trades: 39 }
];