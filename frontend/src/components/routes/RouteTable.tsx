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

interface Route {
  id: number;
  from_token: string;
  to_token: string;
  amount: number;
  best_dex: string;
  expected_output: number;
  slippage: number;
  gas_cost_usd: number;
  efficiency: number;
  route_hops: number;
  execution_time: number;
  price_impact: number;
}

export function RouteTable() {
  const [routes, setRoutes] = useState<Route[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRoutes();
  }, []);

  const fetchRoutes = () => {
    setLoading(true);
    fetch("http://localhost:8000/api/routes")
      .then((res) => res.json())
      .then((data) => {
        setRoutes(data.routes);
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
        <Button
          size="sm"
          onClick={fetchRoutes}
          className="bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70"
        >
          Refresh Routes
        </Button>
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
            {routes.map((route) => (
              <TableRow key={route.id}>
                <TableCell className="font-medium">
                  {route.from_token} → {route.to_token}
                </TableCell>
                <TableCell>
                  <Badge variant="outline" className="text-xs">
                    {route.best_dex}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="font-medium">
                    ${route.amount.toLocaleString()}
                  </div>
                </TableCell>
                <TableCell>
                  <div className="font-medium">
                    {route.expected_output.toFixed(6)} {route.to_token}
                  </div>
                </TableCell>
                <TableCell>
                  <GasCostIndicator cost={route.gas_cost_usd} />
                </TableCell>
                <TableCell>
                  <div className="flex items-center space-x-2">
                    <span>{route.slippage.toFixed(1)}%</span>
                    {route.slippage > 1.5 && <SlippageWarning />}
                  </div>
                </TableCell>
                <TableCell>
                  <Badge
                    variant={
                      route.efficiency > 95
                        ? "default"
                        : route.efficiency > 90
                        ? "secondary"
                        : "destructive"
                    }
                  >
                    {route.efficiency}%
                  </Badge>
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {route.execution_time.toFixed(1)}s
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
