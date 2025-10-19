import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { formatDistanceToNow } from "date-fns";
import { TrendingUp, Clock, Zap, CheckCircle, XCircle, Timer } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

const toNum = (v: unknown): number | null => {
  const n = typeof v === "number" ? v : Number(v);
  return Number.isFinite(n) ? n : null;
};

const fmt = (v: unknown, digits = 2): string => {
  const n = toNum(v);
  return n === null ? "—" : n.toFixed(digits);
};

const fmtPct = (v: unknown, digits = 2): string => {
  const n = toNum(v);
  return n === null ? "—" : `${n.toFixed(digits)}%`;
};


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
    fetch("http://localhost:8000/api/api/arbitrage")
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
    if (volume >= 1_000_000) return `$${fmt(volume / 1_000_000, 1)}M`;
    if (volume >= 1_000) return `$${fmt(volume / 1_000, 1)}K`;
    return `$${fmt(volume, 0)}`;
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
        <Button variant="outline" size="sm" className="hidden sm:flex" disabled>
          <span className="hidden lg:inline">Coming Soon</span>
          <span className="lg:hidden">Soon</span>
        </Button>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <TrendingUp className="h-12 w-12 text-muted-foreground/50 mb-4" />
          <h3 className="text-lg font-semibold text-muted-foreground mb-2">Coming Soon</h3>
          <p className="text-sm text-muted-foreground max-w-sm">
            Arbitrage detection is currently under development. We're working on real-time arbitrage opportunities across multiple DEXs.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
