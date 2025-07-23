"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { AlertTriangle, TrendingUp, TrendingDown } from "lucide-react";

interface Token {
  id: string;
  symbol: string;
  name: string;
  price: number;
  volatility: number;
  change24h: number;
}

export function VolatilityAlert() {
  const [tokens, setTokens] = useState<Token[]>([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/risk_management")
      .then((res) => res.json())
      .then((data) => setTokens(data.risk_data || []))
      .catch((err) => console.error("Risk API fetch failed:", err));
  }, []);

  const highVolatilityTokens =
    tokens?.filter((token) => token.volatility > 15) || [];

  if (highVolatilityTokens.length === 0) {
    return (
      <Card className="border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center space-x-2 text-green-800 dark:text-green-100">
            <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Market Stability</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-green-700 dark:text-green-200">
            All monitored tokens are within normal volatility ranges. Market
            conditions are stable.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-yellow-800 dark:text-yellow-100">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5" />
            <span className="text-sm sm:text-base">High Volatility Alert</span>
          </div>
          <Badge
            variant="outline"
            className="border-yellow-400 text-yellow-800 dark:text-yellow-100 text-xs"
          >
            {highVolatilityTokens.length} Tokens
          </Badge>
        </CardTitle>
        <p className="text-xs sm:text-sm text-yellow-700 dark:text-yellow-200 mt-1">
          Increased market volatility detected. Monitor positions carefully.
        </p>
      </CardHeader>
      <CardContent className="space-y-3 sm:space-y-4">
        {highVolatilityTokens.map((token) => (
          <div key={token.id} className="space-y-2 sm:space-y-3">
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <div>
                  <div className="font-medium text-sm sm:text-base text-yellow-900 dark:text-yellow-100">
                    {token.symbol}
                  </div>
                  <div className="text-xs sm:text-sm text-yellow-700 dark:text-yellow-200">
                    {token.name}
                  </div>
                </div>
              </div>
              <div className="text-right space-y-1 flex-shrink-0">
                <div className="flex items-center space-x-2">
                  <Badge
                    variant="outline"
                    className="border-yellow-400 text-yellow-800 dark:text-yellow-100 text-xs"
                  >
                    {token.volatility.toFixed(1)}%
                  </Badge>
                  {token.change24h >= 0 ? (
                    <TrendingUp className="h-3 w-3 sm:h-4 sm:w-4 text-green-600" />
                  ) : (
                    <TrendingDown className="h-3 w-3 sm:h-4 sm:w-4 text-red-600" />
                  )}
                </div>
                <div className="text-xs sm:text-sm font-medium text-yellow-900 dark:text-yellow-100">
                  ${token.price.toFixed(token.price < 1 ? 4 : 2)}
                </div>
                <div
                  className={`text-xs ${
                    token.change24h >= 0
                      ? "text-green-600 dark:text-green-400"
                      : "text-red-600 dark:text-red-400"
                  }`}
                >
                  {token.change24h >= 0 ? "+" : ""}
                  {token.change24h.toFixed(2)}%
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-xs text-yellow-700 dark:text-yellow-200">
                <span>Risk Level</span>
                <span>{token.volatility > 20 ? "High" : "Medium"}</span>
              </div>
              <Progress
                value={Math.min(token.volatility * 2, 100)}
                className="h-2"
              />
            </div>
          </div>
        ))}

        <div className="pt-3 border-t border-yellow-200 dark:border-yellow-800">
          <Button
            variant="outline"
            size="sm"
            className="w-full border-primary/20 text-primary hover:bg-primary hover:text-white"
            onClick={(e) => {
              e.preventDefault();
              console.log("Opening risk management...");
            }}
          >
            View Risk Management
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
