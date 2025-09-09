import { PageLayout } from "@/components/layout/PageLayout";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { RecentOpportunitiesTable } from "@/components/dashboard/RecentOpportunitiesTable";
import { VolatilityAlert } from "@/components/dashboard/VolatilityAlert";
import { RiskManagementTable } from "@/components/dashboard/RiskManagementTable";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  mockArbitrageOpportunities,
  mockMarketMetrics,
  mockPerformanceData,
} from "@/lib/mock-data";
import {
  TrendingUp,
  Zap,
  Target,
  DollarSign,
  Clock,
  Activity,
  RefreshCw,
} from "lucide-react";
import { useEffect, useState } from "react";

const toNum = (v: unknown): number | null => {
  const n = typeof v === "number" ? v : Number(v);
  return Number.isFinite(n) ? n : null;
};

const fmt = (v: unknown, digits = 2): string => {
  const n = toNum(v);
  return n === null ? "—" : n.toFixed(digits);
};

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

export function Dashboard() {
  const [strategies, setStrategies] = useState<DCAStrategy[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/api/dca_data")
      .then((res) => res.json())
      .then((data) => {
        setStrategies(data?.strategies || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error("DCA API fetch failed", err);
        setLoading(false);
      });
  }, []);

  const activeStrategies = strategies?.filter(
    (s) => s.status === "active"
  ).length;

  const detectedArbitrages = mockArbitrageOpportunities.filter(
    (o) => o.status === "detected"
  ).length;
  const totalProfit = mockArbitrageOpportunities
    .filter((o) => o.status === "executed")
    .reduce((sum, o) => sum + o.profit, 0);

  const actions = (
    <div className="flex items-center space-x-2 w-full sm:w-auto">
      <Button
        variant="outline"
        size="sm"
        className="border-primary/20 text-white hover:bg-primary hover:text-white"
      >
        <RefreshCw className="h-4 w-4 sm:mr-2" />
        <span className="hidden sm:inline">Refresh</span>
      </Button>
      <Button
        size="sm"
        className="bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 shadow-lg"
      >
        <Activity className="h-4 w-4 sm:mr-2" />
        <span className="hidden sm:inline">Live View</span>
      </Button>
    </div>
  );

  return (
    <PageLayout
      title="Trading Dashboard"
      description="Real-time overview of AI trading strategies, market opportunities, and performance metrics"
      actions={actions}
    >
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6">
        <MetricCard
          title="Total Value Locked"
          value={`$${fmt(mockMarketMetrics.totalValueLocked / 1e9, 2)}B`}
          change={5.2}
          icon={DollarSign}
          description="Assets under management"
          trend="up"
        />
        <MetricCard
          title="Active Strategies"
          value={loading ? "..." : activeStrategies}
          change={0}
          icon={Target}
          description="Currently running strategies"
          progress={
            loading || strategies.length === 0
              ? 0
              : (activeStrategies / strategies.length) * 100
          }
          target={loading ? 0 : strategies.length}
        />
        <MetricCard
          title="Success Rate"
          value={`${mockMarketMetrics.successRate}%`}
          change={2.1}
          icon={TrendingUp}
          description="Strategy execution success"
          trend="up"
        />
        <MetricCard
          title="Avg Execution Time"
          value={`${mockMarketMetrics.avgExecutionTime}s`}
          change={-8.5}
          icon={Clock}
          description="Average trade execution"
          trend="up"
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 sm:gap-6">
        <Card className="xl:col-span-2">
          <CardHeader>
            <div className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
              <div>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5" />
                  <span>Performance Overview</span>
                </CardTitle>
                <p className="text-xs sm:text-sm text-muted-foreground mt-1">
                  7-day P&L and trading volume
                </p>
              </div>
              <Badge variant="secondary" className="text-green-600">
                +{fmt(mockMarketMetrics.totalPnL, 2)} USD
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-[250px] sm:h-[300px] relative bg-gradient-to-b from-muted/20 to-muted/5 rounded-lg p-4">
              <svg
                width="100%"
                height="100%"
                viewBox="0 0 100 100"
                preserveAspectRatio="none"
                className="absolute inset-0"
              >
                <defs>
                  <linearGradient
                    id="pnl-gradient"
                    x1="0%"
                    y1="0%"
                    x2="0%"
                    y2="100%"
                  >
                    <stop offset="0%" stopColor="#10b981" stopOpacity="0.3" />
                    <stop
                      offset="100%"
                      stopColor="#10b981"
                      stopOpacity="0.05"
                    />
                  </linearGradient>
                </defs>
                <polyline
                  fill="none"
                  stroke="#10b981"
                  strokeWidth="0.8"
                  points={mockPerformanceData
                    .map((d, index) => {
                      const maxPnL = Math.max(
                        ...mockPerformanceData.map((p) => p.pnl)
                      );
                      const minPnL = Math.min(
                        ...mockPerformanceData.map((p) => p.pnl)
                      );
                      const x =
                        (index / (mockPerformanceData.length - 1)) * 100;
                      const y =
                        100 - ((d.pnl - minPnL) / (maxPnL - minPnL)) * 100;
                      return `${x},${y}`;
                    })
                    .join(" ")}
                  vectorEffect="non-scaling-stroke"
                />
                <polygon
                  fill="url(#pnl-gradient)"
                  points={`0,100 ${mockPerformanceData
                    .map((d, index) => {
                      const maxPnL = Math.max(
                        ...mockPerformanceData.map((p) => p.pnl)
                      );
                      const minPnL = Math.min(
                        ...mockPerformanceData.map((p) => p.pnl)
                      );
                      const x =
                        (index / (mockPerformanceData.length - 1)) * 100;
                      const y =
                        100 - ((d.pnl - minPnL) / (maxPnL - minPnL)) * 100;
                      return `${x},${y}`;
                    })
                    .join(" ")} 100,100`}
                />
              </svg>

              <div className="absolute top-2 left-2 text-xs text-muted-foreground">
                Max: ${Math.max(...mockPerformanceData.map((d) => d.pnl))}
              </div>
              <div className="absolute bottom-2 left-2 text-xs text-muted-foreground">
                Min: ${Math.min(...mockPerformanceData.map((d) => d.pnl))}
              </div>
              <div className="absolute bottom-2 right-2 text-xs text-muted-foreground">
                Current: $
                {mockPerformanceData[mockPerformanceData.length - 1].pnl}
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-4 sm:space-y-6">
          <VolatilityAlert />

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center space-x-2 text-sm sm:text-base">
                <Zap className="h-4 w-4" />
                <span>Quick Stats</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 sm:space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-xs sm:text-sm text-muted-foreground">
                  Detected Arbitrages
                </span>
                <Badge
                  variant="outline"
                  className="text-blue-600 border-blue-200"
                >
                  {detectedArbitrages}
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs sm:text-sm text-muted-foreground">
                  Total Profit Today
                </span>
                <Badge
                  variant="outline"
                  className="text-green-600 border-green-200"
                >
                  ${fmt(totalProfit, 2)}
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs sm:text-sm text-muted-foreground">
                  Monitored Tokens
                </span>
                <Badge variant="outline">Dynamic</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs sm:text-sm text-muted-foreground">
                  24h Volume
                </span>
                <Badge variant="outline">
                  ${fmt(mockMarketMetrics.totalVolume24h / 1e9, 1)}B
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <RecentOpportunitiesTable />
        <RiskManagementTable />
      </div>
    </PageLayout>
  );
}
