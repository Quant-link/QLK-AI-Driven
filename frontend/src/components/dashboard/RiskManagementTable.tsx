import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Shield, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';
import { useEffect, useState } from 'react';

interface RiskData {
  id: string;
  symbol: string;
  current_price: number;
  stop_loss: number;
  position_size: number;
  risk_percentage: number;
  volatility: number;
  risk_score: number;
  max_drawdown: number;
  sharpe_ratio: number;
  status: string;
}

export function RiskManagementTable() {
  const [riskData, setRiskData] = useState<RiskData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/risk_management")
      .then((res) => res.json())
      .then((data) => {
        setRiskData(data.risk_data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Risk management API fetch failed", err);
        setLoading(false);
      });
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 6,
    }).format(amount);
  };

  const getRiskBadgeColor = (riskScore: number) => {
    if (riskScore < 0.3) return 'bg-green-100 text-green-800 border-green-200';
    if (riskScore < 0.7) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  const getRiskLabel = (riskScore: number) => {
    if (riskScore < 0.3) return 'Low';
    if (riskScore < 0.7) return 'Medium';
    return 'High';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'high_risk':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="h-5 w-5" />
            <span>Risk Management</span>
          </CardTitle>
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
        <div>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="h-5 w-5" />
            <span>Risk Management</span>
          </CardTitle>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            Position sizing and risk metrics for monitored tokens
          </p>
        </div>
      </CardHeader>
      <CardContent>
        {/* Desktop Table */}
        <div className="hidden lg:block">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Token</TableHead>
                <TableHead>Current Price</TableHead>
                <TableHead>Stop Loss</TableHead>
                <TableHead>Position Size</TableHead>
                <TableHead>Risk Score</TableHead>
                <TableHead>Sharpe Ratio</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {riskData.slice(0, 10).map((token) => (
                <TableRow key={token.id} className="hover:bg-muted/50">
                  <TableCell>
                    <div className="font-medium">{token.symbol}</div>
                    <div className="text-sm text-muted-foreground">
                      Vol: {token.volatility.toFixed(1)}%
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="font-medium">{formatCurrency(token.current_price)}</div>
                  </TableCell>
                  <TableCell>
                    <div className="font-medium">{formatCurrency(token.stop_loss)}</div>
                    <div className="text-sm text-muted-foreground">
                      -{token.risk_percentage}%
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="font-medium">{token.position_size.toFixed(2)}</div>
                    <div className="text-sm text-muted-foreground">
                      Max DD: {token.max_drawdown.toFixed(1)}%
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className={getRiskBadgeColor(token.risk_score)}>
                      {getRiskLabel(token.risk_score)} ({token.risk_score})
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className={`flex items-center space-x-1 ${token.sharpe_ratio > 1 ? 'text-green-600' : 'text-red-600'}`}>
                      {token.sharpe_ratio > 1 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                      <span className="font-medium">{token.sharpe_ratio.toFixed(2)}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(token.status)}>
                      {token.status === 'active' ? 'Active' : 'High Risk'}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Mobile Cards */}
        <div className="lg:hidden space-y-4">
          {riskData.slice(0, 5).map((token) => (
            <Card key={token.id} className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="font-medium text-base">{token.symbol}</div>
                  <div className="text-sm text-muted-foreground">
                    {formatCurrency(token.current_price)}
                  </div>
                </div>
                <Badge className={getStatusColor(token.status)}>
                  {token.status === 'active' ? 'Active' : 'High Risk'}
                </Badge>
              </div>
              
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-muted-foreground">Stop Loss</span>
                  <div className="font-medium">{formatCurrency(token.stop_loss)}</div>
                </div>
                <div>
                  <span className="text-muted-foreground">Position Size</span>
                  <div className="font-medium">{token.position_size.toFixed(2)}</div>
                </div>
                <div>
                  <span className="text-muted-foreground">Risk Score</span>
                  <Badge className={getRiskBadgeColor(token.risk_score)}>
                    {getRiskLabel(token.risk_score)}
                  </Badge>
                </div>
                <div>
                  <span className="text-muted-foreground">Sharpe Ratio</span>
                  <div className={`font-medium ${token.sharpe_ratio > 1 ? 'text-green-600' : 'text-red-600'}`}>
                    {token.sharpe_ratio.toFixed(2)}
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Tablet Table */}
        <div className="hidden md:block lg:hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Token</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>Stop Loss</TableHead>
                <TableHead>Risk</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {riskData.slice(0, 8).map((token) => (
                <TableRow key={token.id} className="hover:bg-muted/50">
                  <TableCell>
                    <div className="font-medium">{token.symbol}</div>
                    <div className="text-xs text-muted-foreground">
                      Vol: {token.volatility.toFixed(1)}%
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="font-medium">{formatCurrency(token.current_price)}</div>
                  </TableCell>
                  <TableCell>
                    <div className="font-medium">{formatCurrency(token.stop_loss)}</div>
                  </TableCell>
                  <TableCell>
                    <Badge className={getRiskBadgeColor(token.risk_score)}>
                      {getRiskLabel(token.risk_score)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(token.status)}>
                      {token.status === 'active' ? 'Active' : 'High Risk'}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
