import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { VolatilityBadge } from "./VolatilityBadge";
import { LiquidityBar } from "./LiquidityBar";
import { useState, useEffect } from "react";
import { Search, Filter, TrendingUp, TrendingDown } from "lucide-react";

interface Token {
  id: string;
  symbol: string;
  name: string;
  price: number;
  change_24h: number;
  change_7d: number;
  volume_24h: number;
  market_cap: number;
  liquidity: number;
  circulating_supply: number;
  total_supply: number;
  ath: number;
  atl: number;
}

export function TokenListTable() {
  const [tokens, setTokens] = useState<Token[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/market_data")
      .then((res) => res.json())
      .then((data) => {
        setTokens(data.tokens);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Market data API fetch failed", err);
        setLoading(false);
      });
  }, []);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState<
    "price" | "change_24h" | "volume_24h" | "market_cap"
  >("market_cap");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const formatNumber = (num: number) => {
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    if (num >= 1e3) return `$${(num / 1e3).toFixed(2)}K`;
    return `$${num.toFixed(2)}`;
  };

  const formatSupply = (supply: number | undefined) => {
    if (!supply || supply === 0) return "0";
    if (supply >= 1e9) return `${(supply / 1e9).toFixed(2)}B`;
    if (supply >= 1e6) return `${(supply / 1e6).toFixed(2)}M`;
    if (supply >= 1e3) return `${(supply / 1e3).toFixed(2)}K`;
    return supply.toFixed(0);
  };

  const filteredTokens = tokens.filter(
    (token) =>
      token.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      token.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const sortedTokens = [...filteredTokens].sort((a, b) => {
    const aValue = a[sortBy as keyof Token];
    const bValue = b[sortBy as keyof Token];
    return sortOrder === "desc"
      ? (bValue as number) - (aValue as number)
      : (aValue as number) - (bValue as number);
  });

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Token Overview</CardTitle>
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

  const handleSort = (column: typeof sortBy) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === "desc" ? "asc" : "desc");
    } else {
      setSortBy(column);
      setSortOrder("desc");
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col space-y-4 lg:flex-row lg:items-center lg:justify-between lg:space-y-0">
          <div>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>Token Overview</span>
            </CardTitle>
            <p className="text-xs sm:text-sm text-muted-foreground mt-1">
              Comprehensive market data for all monitored tokens
            </p>
          </div>
          <div className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:space-y-0 sm:space-x-2">
            <div className="relative">
              <Search className="absolute left-2 sm:left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search tokens..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 sm:pl-9 w-full sm:w-48 lg:w-64"
              />
            </div>
            <Button
              variant="outline"
              size="sm"
              className="border-primary/20 text-primary hover:bg-primary hover:text-white"
            >
              <Filter className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline text-white">Filter</span>
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Desktop Table */}
        <div className="hidden xl:block">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Token</TableHead>
                <TableHead
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => handleSort("price")}
                >
                  <div className="flex items-center space-x-1">
                    <span className="text-white">Price</span>
                    {sortBy === "price" &&
                      (sortOrder === "desc" ? (
                        <TrendingDown className="h-3 w-3" />
                      ) : (
                        <TrendingUp className="h-3 w-3" />
                      ))}
                  </div>
                </TableHead>
                <TableHead
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => handleSort("change_24h")}
                >
                  <div className="flex items-center space-x-1">
                    <span>24h Change</span>
                    {sortBy === "change_24h" &&
                      (sortOrder === "desc" ? (
                        <TrendingDown className="h-3 w-3" />
                      ) : (
                        <TrendingUp className="h-3 w-3" />
                      ))}
                  </div>
                </TableHead>
                <TableHead>7d Change</TableHead>
                <TableHead
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => handleSort("volume_24h")}
                >
                  <div className="flex items-center space-x-1">
                    <span>Volume</span>
                    {sortBy === "volume_24h" &&
                      (sortOrder === "desc" ? (
                        <TrendingDown className="h-3 w-3" />
                      ) : (
                        <TrendingUp className="h-3 w-3" />
                      ))}
                  </div>
                </TableHead>
                <TableHead>Liquidity</TableHead>
                <TableHead>Volatility</TableHead>
                <TableHead
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => handleSort("market_cap")}
                >
                  <div className="flex items-center space-x-1">
                    <span>Market Cap</span>
                    {sortBy === "market_cap" &&
                      (sortOrder === "desc" ? (
                        <TrendingDown className="h-3 w-3" />
                      ) : (
                        <TrendingUp className="h-3 w-3" />
                      ))}
                  </div>
                </TableHead>
                <TableHead>Supply</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedTokens.map((token) => (
                <TableRow key={token.id} className="hover:bg-muted/50">
                  <TableCell>
                    <div className="flex items-center space-x-3">
                      <div className="h-8 w-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
                        {token.symbol.slice(0, 2)}
                      </div>
                      <div>
                        <div className="font-medium">{token.symbol}</div>
                        <div className="text-sm text-muted-foreground">
                          {token.name}
                        </div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="font-medium">
                      ${token.price.toFixed(token.price < 1 ? 4 : 2)}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      ATH: ${token.ath.toFixed(2)}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <span
                        className={
                          token.change_24h >= 0
                            ? "text-green-600 dark:text-green-400"
                            : "text-red-600 dark:text-red-400"
                        }
                      >
                        {token.change_24h >= 0 ? "+" : ""}
                        {token.change_24h.toFixed(2)}%
                      </span>
                      {token.change_24h >= 0 ? (
                        <TrendingUp className="h-3 w-3 text-green-600" />
                      ) : (
                        <TrendingDown className="h-3 w-3 text-red-600" />
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <span
                      className={
                        token.change_7d >= 0
                          ? "text-green-600 dark:text-green-400"
                          : "text-red-600 dark:text-red-400"
                      }
                    >
                      {token.change_7d >= 0 ? "+" : ""}
                      {token.change_7d.toFixed(2)}%
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="font-medium">
                      {formatNumber(token.volume_24h)}
                    </div>
                    <div className="text-xs text-muted-foreground">24h</div>
                  </TableCell>
                  <TableCell>
                    <LiquidityBar
                      value={token.liquidity}
                      maxValue={1000000000}
                    />
                  </TableCell>
                  <TableCell>
                    <VolatilityBadge volatility={token.volatility} />
                  </TableCell>
                  <TableCell>
                    <div className="font-medium">
                      {formatNumber(token.market_cap)}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      FDV: {formatNumber(token.fdv)}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <div>{formatSupply(token.circulating_supply)}</div>
                      {token.total_supply && token.total_supply > 0 && (
                        <div className="text-xs text-muted-foreground">
                          Total: {formatSupply(token.total_supply)}
                        </div>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Tablet Table */}
        <div className="hidden md:block xl:hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Token</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>24h</TableHead>
                <TableHead>Volume</TableHead>
                <TableHead>Market Cap</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedTokens.map((token) => (
                <TableRow key={token.id} className="hover:bg-muted/50">
                  <TableCell>
                    <div className="flex items-center space-x-3">
                      <div className="h-7 w-7 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
                        {token.symbol.slice(0, 2)}
                      </div>
                      <div>
                        <div className="font-medium text-sm">
                          {token.symbol}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {token.name}
                        </div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="font-medium text-sm">
                      ${token.price.toFixed(token.price < 1 ? 4 : 2)}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-1">
                      <span
                        className={`text-sm ${
                          token.change_24h >= 0
                            ? "text-green-600"
                            : "text-red-600"
                        }`}
                      >
                        {token.change_24h >= 0 ? "+" : ""}
                        {token.change_24h.toFixed(1)}%
                      </span>
                      {token.change_24h >= 0 ? (
                        <TrendingUp className="h-3 w-3 text-green-600" />
                      ) : (
                        <TrendingDown className="h-3 w-3 text-red-600" />
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm font-medium">
                      {formatNumber(token.volume_24h)}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm font-medium">
                      {formatNumber(token.market_cap)}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Mobile Cards */}
        <div className="md:hidden space-y-3">
          {sortedTokens.map((token) => (
            <Card key={token.id} className="p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className="h-8 w-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
                    {token.symbol.slice(0, 2)}
                  </div>
                  <div>
                    <div className="font-medium">{token.symbol}</div>
                    <div className="text-xs text-muted-foreground">
                      {token.name}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-medium">
                    ${token.price.toFixed(token.price < 1 ? 4 : 2)}
                  </div>
                  <div
                    className={`text-sm ${
                      token.change_24h >= 0 ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    {token.change_24h >= 0 ? "+" : ""}
                    {token.change_24h.toFixed(2)}%
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <div className="text-muted-foreground text-xs">
                    Volume 24h
                  </div>
                  <div className="font-medium">
                    {formatNumber(token.volume_24h)}
                  </div>
                </div>
                <div>
                  <div className="text-muted-foreground text-xs">
                    Market Cap
                  </div>
                  <div className="font-medium">
                    {formatNumber(token.market_cap)}
                  </div>
                </div>
                <div>
                  <div className="text-muted-foreground text-xs">7d Change</div>
                  <div
                    className={
                      token.change_7d >= 0 ? "text-green-600" : "text-red-600"
                    }
                  >
                    {token.change_7d >= 0 ? "+" : ""}
                    {token.change_7d.toFixed(1)}%
                  </div>
                </div>
                <div>
                  <div className="text-muted-foreground text-xs">
                    Volatility
                  </div>
                  <div className="font-medium">
                    {token.volatility.toFixed(1)}%
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
