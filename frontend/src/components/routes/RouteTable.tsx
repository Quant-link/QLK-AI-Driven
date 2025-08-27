import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { GasCostIndicator } from "./GasCostIndicator";
import { SlippageWarning } from "./SlippageWarning";
import { useEffect, useState } from "react";

/* ---------------------- DEX label mapping ---------------------- */
const DEX_LABEL: Record<string, string> = {
  uniswap: "Uniswap",
  uniswap_v2: "Uniswap V2",
  uniswap_v3: "Uniswap V3",
  sushiswap: "SushiSwap",
  curve: "Curve",
  balancer: "Balancer",
  raydium: "Raydium",
  pancakeswap: "PancakeSwap",
  osmosis: "Osmosis",
  pulsex: "PulseX",
  pumpswap: "PumpSwap",
  swappi: "Swappi",
  // aggregators (fallback)
  "1inch": "1inch",
  openocean: "OpenOcean",
};

const DEX_ALIASES: Record<string, string> = {
  uniswap: "uniswap",
  "uniswap v2": "uniswap_v2",
  "uniswap_v2": "uniswap_v2",
  "uniswap-v2": "uniswap_v2",
  v2: "uniswap_v2",
  "uniswap v3": "uniswap_v3",
  "uniswap_v3": "uniswap_v3",
  "uniswap-v3": "uniswap_v3",
  v3: "uniswap_v3",
  sushi: "sushiswap",
  sushiswap: "sushiswap",
  curve: "curve",
  balancer: "balancer",
  raydium: "raydium",
  pancakeswap: "pancakeswap",
  osmosis: "osmosis",
  pulsex: "pulsex",
  pumpswap: "pumpswap",
  swappi: "swappi",
  "1inch": "1inch",
  openocean: "openocean",
};

function normalizeDex(raw: string | null | undefined): string {
  if (!raw) return "N/A";
  const s = String(raw).trim();

  const pretty = Object.values(DEX_LABEL).find(
    (label) => label.toLowerCase() === s.toLowerCase()
  );
  if (pretty) return pretty;

  const cleaned = s.replace(/[^a-zA-Z0-9]+/g, " ").trim().toLowerCase();
  if (DEX_ALIASES[cleaned]) {
    const canonical = DEX_ALIASES[cleaned];
    return DEX_LABEL[canonical] ?? canonical;
  }

  const compact = cleaned.replace(/\s+/g, " ");
  if (DEX_ALIASES[compact]) {
    const canonical = DEX_ALIASES[compact];
    return DEX_LABEL[canonical] ?? canonical;
  }

  const snakeUpper = s.toUpperCase().replace(/[^A-Z0-9]+/g, "_").toLowerCase();
  if (DEX_ALIASES[snakeUpper]) {
    const canonical = DEX_ALIASES[snakeUpper];
    return DEX_LABEL[canonical] ?? canonical;
  }

  return s;
}

/* --------------------------- types ---------------------------- */
interface Route {
  id: number;
  from_token: string;
  to_token: string;
  amount: number;
  best_dex?: string;
  expected_output?: number;
  slippage?: number;
  gas_cost_usd?: number;
  efficiency?: number;
  route_hops?: number;
  execution_time?: number;
  price_impact?: number;
  path?: string[];
  source?: string;
}

export function RouteTable() {
  const [routes, setRoutes] = useState<Route[]>([]);
  const [loading, setLoading] = useState(true);
  const [amount, setAmount] = useState<number>(500);

  useEffect(() => {
    fetchRoutes(amount);
  }, []);

  const fetchRoutes = (amt: number) => {
    setLoading(true);
    fetch(`http://localhost:8000/api/routes?amount=${amt}`)
      .then((res) => res.json())
      .then((data) => {
        setRoutes(Array.isArray(data?.routes) ? data.routes : []);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Routes API fetch failed", err);
        setLoading(false);
      });
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Optimal Swap Routes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-12 bg-gray-200 rounded"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Optimal Swap Routes</CardTitle>
        <div className="flex items-center space-x-2">
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(Number(e.target.value))}
            className="w-24 border px-2 py-1 rounded text-sm"
          />
          <Button
            size="sm"
            onClick={() => fetchRoutes(amount)}
            className="bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70"
          >
            Refresh Routes
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Pair</TableHead>
              <TableHead>Best DEX</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Expected Output</TableHead>
              <TableHead>Gas Cost</TableHead>
              <TableHead>Slippage</TableHead>
              <TableHead>Efficiency</TableHead>
              <TableHead>Est. Time</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {routes.map((route) => {
              const rawDex =
                (route.best_dex && route.best_dex !== "Unknown"
                  ? route.best_dex
                  : route.source) || route.best_dex || "N/A";
              const prettyDex = normalizeDex(rawDex);

              const amountStr = route.amount
                ? `$${Number(route.amount).toLocaleString()}`
                : "-";

              const expected =
                route.expected_output !== null &&
                route.expected_output !== undefined
                  ? `${Number(route.expected_output).toFixed(6)} ${route.to_token}`
                  : "-";

              const gasUsd = Number(route.gas_cost_usd ?? 0);

              const slip =
                route.slippage !== null && route.slippage !== undefined
                  ? `${Number(route.slippage).toFixed(1)}%`
                  : "-";

              const eff =
                route.efficiency !== null && route.efficiency !== undefined
                  ? `${Number(route.efficiency).toFixed(1)}%`
                  : "-";

              const exec =
                route.execution_time !== null && route.execution_time !== undefined
                  ? `${Number(route.execution_time).toFixed(1)}s`
                  : "-";

              return (
                <TableRow key={route.id}>
                  {/* Pair */}
                  <TableCell className="font-medium">
                    {route.from_token} → {route.to_token}
                  </TableCell>

                  {/* Best DEX (normalized with source fallback) */}
                  <TableCell>
                    <Badge variant="outline" className="text-xs">
                      {prettyDex}
                    </Badge>
                  </TableCell>

                  {/* Amount */}
                  <TableCell>
                    <div className="font-medium">{amountStr}</div>
                  </TableCell>

                  {/* Expected Output */}
                  <TableCell>
                    <div className="font-medium">{expected}</div>
                  </TableCell>

                  {/* Gas Cost */}
                  <TableCell>
                    <GasCostIndicator cost={isFinite(gasUsd) ? gasUsd : 0} />
                  </TableCell>

                  {/* Slippage */}
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <span>{slip}</span>
                      {route.slippage !== null &&
                        route.slippage !== undefined &&
                        Number(route.slippage) > 1.5 && <SlippageWarning />}
                    </div>
                  </TableCell>

                  {/* Efficiency */}
                  <TableCell>
                    <Badge
                      variant={
                        Number(route.efficiency) > 95
                          ? "default"
                          : Number(route.efficiency) > 90
                          ? "secondary"
                          : "destructive"
                      }
                    >
                      {eff}
                    </Badge>
                  </TableCell>

                  {/* Est. Time */}
                  <TableCell className="text-muted-foreground">{exec}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
