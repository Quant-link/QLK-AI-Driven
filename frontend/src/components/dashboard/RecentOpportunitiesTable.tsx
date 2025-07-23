import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { formatDistanceToNow } from "date-fns";
import {
  TrendingUp,
  Clock,
  Zap,
  CheckCircle,
  XCircle,
  Timer,
} from "lucide-react";
import { useEffect, useState } from "react";

function getStatusConfig(status: string) {
  switch (status) {
    case "executed":
      return {
        color:
          "bg-green-100 text-green-800 border-green-200 dark:bg-green-950 dark:text-green-100",
        icon: CheckCircle,
      };
    case "detected":
      return {
        color:
          "bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-950 dark:text-blue-100",
        icon: Zap,
      };
    case "failed":
      return {
        color:
          "bg-red-100 text-red-800 border-red-200 dark:bg-red-950 dark:text-red-100",
        icon: XCircle,
      };
    case "expired":
      return {
        color:
          "bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-950 dark:text-gray-100",
        icon: Timer,
      };
    default:
      return {
        color: "bg-gray-100 text-gray-800 border-gray-200",
        icon: Clock,
      };
  }
}

export function RecentOpportunitiesTable() {
  interface Opportunity {
    id: number;
    tokenA: string;
    tokenB: string;
    dexA: string;
    dexB: string;
    profit: number;
    profitPercentage: number;
    volume: number;
    gasUsed?: number;
    timestamp: Date;
    executionTime?: number;
    status: string;
  }

  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/arbitrage")
      .then((res) => res.json())
      .then((data) => {
        console.log("Arbitrage API response:", data); // Debug log
        if (data.opportunities && Array.isArray(data.opportunities)) {
          const formatted = data.opportunities.map(
            (item: any, idx: number) => ({
              id: idx + 1,
              tokenA: item.token,
              tokenB: "USDT",
              dexA: item.buy_exchange,
              dexB: item.sell_exchange,
              profit: item.profit_usd,
              profitPercentage: item.profit_percentage,
              volume: item.volume_24h || Math.random() * 10000 + 1000,
              gasUsed: Math.floor(Math.random() * 50000),
              timestamp: new Date(item.timestamp || Date.now()),
              executionTime: Math.floor(Math.random() * 5),
              status: "detected",
            })
          );
          setOpportunities(formatted);
          console.log("Formatted opportunities:", formatted); // Debug log
        } else {
          console.error("No opportunities found in response:", data);
        }
      })
      .catch((err) => console.error("API fetch failed", err));
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1000000) return `$${(volume / 1000000).toFixed(1)}M`;
    if (volume >= 1000) return `$${(volume / 1000).toFixed(1)}K`;
    return `$${volume.toFixed(0)}`;
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5" />
            <span>Recent Arbitrage Opportunities</span>
          </CardTitle>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            Latest detected and executed arbitrage trades
          </p>
        </div>
        <Button variant="outline" size="sm" className="hidden sm:flex">
          <span className="hidden lg:inline">View All</span>
          <span className="lg:hidden">All</span>
        </Button>
      </CardHeader>
      <CardContent>
        {/* Desktop Table */}
        <div className="hidden lg:block">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Trading Pair</TableHead>
                <TableHead>DEX Route</TableHead>
                <TableHead>Profit</TableHead>
                <TableHead>Volume</TableHead>
                <TableHead>Time</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {opportunities.map((opportunity) => {
                const statusConfig = getStatusConfig(opportunity.status);
                const StatusIcon = statusConfig.icon;

                return (
                  <TableRow key={opportunity.id} className="hover:bg-muted/50">
                    <TableCell>
                      <div className="font-medium">
                        {opportunity.tokenA}/{opportunity.tokenB}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {opportunity.profitPercentage.toFixed(2)}% spread
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="text-sm font-medium">
                          {opportunity.dexA}
                        </div>
                        <div className="text-xs text-muted-foreground flex items-center">
                          <span>→</span>
                          <span className="ml-1">{opportunity.dexB}</span>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="font-medium text-green-600">
                        {formatCurrency(opportunity.profit)}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {opportunity.profitPercentage.toFixed(2)}%
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="font-medium">
                        {formatVolume(opportunity.volume)}
                      </div>
                      {opportunity.gasUsed && (
                        <div className="text-xs text-muted-foreground">
                          Gas: {opportunity.gasUsed.toLocaleString()}
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {formatDistanceToNow(opportunity.timestamp, {
                          addSuffix: true,
                        })}
                      </div>
                      {opportunity.executionTime && (
                        <div className="text-xs text-muted-foreground">
                          Exec: {opportunity.executionTime}s
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge className={statusConfig.color}>
                        <StatusIcon className="h-3 w-3 mr-1" />
                        {opportunity.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.preventDefault();
                          console.log("View details for:", opportunity.id);
                        }}
                      >
                        Details
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>

        {/* Mobile Cards */}
        <div className="lg:hidden space-y-4">
          {opportunities.map((opportunity) => {
            const statusConfig = getStatusConfig(opportunity.status);
            const StatusIcon = statusConfig.icon;

            return (
              <Card key={opportunity.id} className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="font-medium text-base">
                      {opportunity.tokenA}/{opportunity.tokenB}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {opportunity.dexA} → {opportunity.dexB}
                    </div>
                  </div>
                  <Badge className={statusConfig.color}>
                    <StatusIcon className="h-3 w-3 mr-1" />
                    <span className="hidden sm:inline">
                      {opportunity.status}
                    </span>
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-muted-foreground">Profit</div>
                    <div className="font-medium text-green-600">
                      {formatCurrency(opportunity.profit)}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {opportunity.profitPercentage.toFixed(2)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">Volume</div>
                    <div className="font-medium">
                      {formatVolume(opportunity.volume)}
                    </div>
                    {opportunity.gasUsed && (
                      <div className="text-xs text-muted-foreground">
                        Gas: {opportunity.gasUsed.toLocaleString()}
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between mt-3 pt-3 border-t">
                  <div className="text-xs text-muted-foreground">
                    {formatDistanceToNow(opportunity.timestamp, {
                      addSuffix: true,
                    })}
                    {opportunity.executionTime && (
                      <span className="ml-2">
                        • Exec: {opportunity.executionTime}s
                      </span>
                    )}
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 px-3"
                    onClick={(e) => {
                      e.preventDefault();
                      console.log("View details for:", opportunity.id);
                    }}
                  >
                    Details
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Tablet Table */}
        <div className="hidden md:block lg:hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Pair</TableHead>
                <TableHead>Route</TableHead>
                <TableHead>Profit</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {opportunities.map((opportunity) => {
                const statusConfig = getStatusConfig(opportunity.status);
                const StatusIcon = statusConfig.icon;

                return (
                  <TableRow key={opportunity.id} className="hover:bg-muted/50">
                    <TableCell>
                      <div className="font-medium">
                        {opportunity.tokenA}/{opportunity.tokenB}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {opportunity.profitPercentage.toFixed(2)}%
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">{opportunity.dexA}</div>
                      <div className="text-xs text-muted-foreground">
                        → {opportunity.dexB}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="font-medium text-green-600">
                        {formatCurrency(opportunity.profit)}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {formatVolume(opportunity.volume)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={statusConfig.color}>
                        <StatusIcon className="h-3 w-3 mr-1" />
                        {opportunity.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.preventDefault();
                          console.log("View details for:", opportunity.id);
                        }}
                      >
                        Details
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
