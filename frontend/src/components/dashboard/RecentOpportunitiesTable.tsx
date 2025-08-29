import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { formatDistanceToNow } from "date-fns";
import { TrendingUp, Clock, Zap, CheckCircle, XCircle, Timer } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

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
      return { color: "bg-gray-100 text-gray-800 border-gray-200", icon: Clock };
  }
}

function formatQLK(qlk: number, usd?: number) {
  const qlkStr = `${qlk.toLocaleString("en-US", {
    minimumFractionDigits: 4,
    maximumFractionDigits: 6,
  })} QLK`;
  return usd !== undefined ? `${qlkStr} (~$${usd.toFixed(2)})` : qlkStr;
}

const DEX_LABEL: Record<string, string> = {
  uniswap_v2: "Uniswap V2",
  uniswap_v3: "Uniswap V3",
  sushiswap: "SushiSwap",
  curve: "Curve",
  balancer: "Balancer",
  swappi: "Swappi",
  pumpswap: "PumpSwap",
  raydium: "Raydium",
  pancakeswap: "PancakeSwap",
  osmosis: "Osmosis",
  oneinch: "1inch",
  openocean: "OpenOcean",
};
function shortenAddress(addr: string, chars = 6): string {
  if (!addr) return "";
  return addr.slice(0, chars) + "..." + addr.slice(-chars);
}

export function RecentOpportunitiesTable() {
  interface Opportunity {
    id: number;
    tokenA: string;
    tokenB: string;
    dexA: string;
    dexB: string;
    profitQLK: number;
    profitUSD: number;
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
        if (!data || !Array.isArray(data.opportunities)) {
          console.error("Invalid arbitrage payload", data);
          return;
        }

        const formatted = data.opportunities
        .map((item: any, idx: number) => {
          return {
            id: idx + 1,
            tokenA: item.symbol || "UNKNOWN",
            tokenB: "QLK",
            dexA: (item.buy_from || "").toLowerCase(),
            dexB: (item.sell_to || "").toLowerCase(),
            profitQLK: Number(item.net_profit_qlk ?? 0),
            profitUSD: Number(item.net_profit_usd ?? 0),
            profitPercentage: Number(item.spread_pct ?? 0), 
            volume: Number(item.volume ?? 0), 
            gasUsed: Number(item.gas_cost_usd ?? 0),
            timestamp: item.timestamp ? new Date(item.timestamp * 1000) : new Date(),
            executionTime: item.execution_time_sec ?? null,
            status: "detected", 
          } as Opportunity;
        })
        setOpportunities(formatted);
      })
      .catch((err) => console.error("Arbitrage API error", err));
  }, []);

  const formatVolume = (volume: number) => {
    if (volume >= 1_000_000) return `$${(volume / 1_000_000).toFixed(1)}M`;
    if (volume >= 1_000) return `$${(volume / 1_000).toFixed(1)}K`;
    return `$${volume.toFixed(0)}`;
  };

  const rows = useMemo(() => opportunities, [opportunities]);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5" />
            <span>Recent Arbitrage Opportunities</span>
          </CardTitle>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            Latest detected and executed arbitrage trades (in QLK)
          </p>
        </div>
        <Button variant="outline" size="sm" className="hidden sm:flex">
          <span className="hidden lg:inline">View All</span>
          <span className="lg:hidden">All</span>
        </Button>
      </CardHeader>
      <CardContent>
        {/* Desktop */}
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
              {rows.map((o) => {
                const s = getStatusConfig(o.status);
                const Icon = s.icon as any;
                return (
                  <TableRow key={o.id} className="hover:bg-muted/50">
                    <TableCell>
                      <div className="font-medium">
                        {o.tokenA}/{o.tokenB}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {o.profitPercentage.toFixed(2)}% spread
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                      <div className="text-sm font-medium">
                        {DEX_LABEL[o.dexA] ? DEX_LABEL[o.dexA] : shortenAddress(o.dexA)}
                      </div>
                      <div className="text-xs text-muted-foreground flex items-center">
                        <span>→</span>
                        <span className="ml-1">
                          {DEX_LABEL[o.dexB] ? DEX_LABEL[o.dexB] : shortenAddress(o.dexB)}
                        </span>
                      </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="font-medium text-green-600">
                        {formatQLK(o.profitQLK, o.profitUSD)}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {o.profitPercentage.toFixed(2)}%
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="font-medium">{formatVolume(o.volume)}</div>
                      {o.gasUsed && (
                        <div className="text-xs text-muted-foreground">
                          Gas: {o.gasUsed.toLocaleString()}
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {formatDistanceToNow(o.timestamp, { addSuffix: true })}
                      </div>
                      {o.executionTime && (
                        <div className="text-xs text-muted-foreground">
                          Exec: {o.executionTime}s
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge className={s.color}>
                        <Icon className="h-3 w-3 mr-1" />
                        {o.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm" onClick={() => console.log("Details", o)}>
                        Details
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>

        {/* Mobile */}
        <div className="lg:hidden space-y-4">
          {rows.map((o) => {
            const s = getStatusConfig(o.status);
            const Icon = s.icon as any;
            return (
              <Card key={o.id} className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="font-medium text-base">
                      {o.tokenA}/{o.tokenB}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {DEX_LABEL[o.dexA] ?? o.dexA} → {DEX_LABEL[o.dexB] ?? o.dexB}
                    </div>
                  </div>
                  <Badge className={s.color}>
                    <Icon className="h-3 w-3 mr-1" />
                    <span className="hidden sm:inline">{o.status}</span>
                  </Badge>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-muted-foreground">Profit</div>
                    <div className="font-medium text-green-600">
                      {formatQLK(o.profitQLK, o.profitUSD)}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {o.profitPercentage.toFixed(2)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">Volume</div>
                    <div className="font-medium">{formatVolume(o.volume)}</div>
                    {o.gasUsed && (
                      <div className="text-xs text-muted-foreground">
                        Gas: {o.gasUsed.toLocaleString()}
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between mt-3 pt-3 border-t">
                  <div className="text-xs text-muted-foreground">
                    {formatDistanceToNow(o.timestamp, { addSuffix: true })}
                    {o.executionTime && <span className="ml-2">• Exec: {o.executionTime}s</span>}
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 px-3"
                    onClick={() => console.log("Details", o)}
                  >
                    Details
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Tablet */}
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
              {rows.map((o) => {
                const s = getStatusConfig(o.status);
                const Icon = s.icon as any;
                return (
                  <TableRow key={o.id} className="hover:bg-muted/50">
                    <TableCell>
                      <div className="font-medium">
                        {o.tokenA}/{o.tokenB}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {o.profitPercentage.toFixed(2)}%
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">{DEX_LABEL[o.dexA] ?? o.dexA}</div>
                      <div className="text-xs text-muted-foreground">→ {DEX_LABEL[o.dexB] ?? o.dexB}</div>
                    </TableCell>
                    <TableCell>
                      <div className="font-medium text-green-600">
                        {formatQLK(o.profitQLK, o.profitUSD)}
                      </div>
                      <div className="text-xs text-muted-foreground">{formatVolume(o.volume)}</div>
                    </TableCell>
                    <TableCell>
                      <Badge className={s.color}>
                        <Icon className="h-3 w-3 mr-1" />
                        {o.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm" onClick={() => console.log("Details", o)}>
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
