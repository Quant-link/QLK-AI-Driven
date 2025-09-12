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
import { Shield, TrendingUp, TrendingDown } from 'lucide-react';
import { useEffect, useState } from 'react';

interface RiskData {
  id: string;
  symbol: string;
  current_price: number | null;
  stop_loss: number | null;
  position_size: number | null;
  risk_percentage: number | null;
  risk_score: number | null;
  max_drawdown: number | null;
  sharpe_ratio: number | null;
  status: string | null;
}

export const toNum = (v: unknown): number | null => {
  const n = typeof v === 'number' ? v : Number(v);
  return Number.isFinite(n) ? n : null;
};

export const fmt = (v: unknown, digits = 2): string => {
  const n = toNum(v);
  return n === null ? '—' : n.toFixed(digits);
};

export const fmtPct = (v: unknown, digits = 2): string => {
  const n = toNum(v);
  return n === null ? '—' : `${n.toFixed(digits)}%`;
};

export const fmtCurrency = (v: unknown): string => {
  const n = toNum(v);
  if (n === null) return '—';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 6,
  }).format(n);
};


const getRiskBadgeColor = (riskScore: number | null) => {
  const s = riskScore ?? 1; 
  if (s < 0.3) return 'bg-green-100 text-green-800 border-green-200';
  if (s < 0.7) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
  return 'bg-red-100 text-red-800 border-red-200';
};

const getRiskLabel = (riskScore: number | null) => {
  const s = riskScore ?? 1;
  if (s < 0.3) return 'Low';
  if (s < 0.7) return 'Medium';
  return 'High';
};

const getStatusColor = (status: string | null) => {
  switch (status) {
    case 'active':
      return 'bg-green-100 text-green-800 border-green-200';
    case 'high_risk':
      return 'bg-red-100 text-red-800 border-red-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

export function RiskManagementTable() {
  const [riskData, setRiskData] = useState<RiskData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/risk_management')
      .then((res) => res.json())
      .then((data) => {
        const rows = Array.isArray(data?.risk_data) ? data.risk_data : [];
        const normalized: RiskData[] = rows.map((r: any) => ({
          id: String(r.id ?? crypto.randomUUID()),
          symbol: String(r.symbol ?? '—'),
          current_price: toNum(r.current_price),
          stop_loss: toNum(r.stop_loss),
          position_size: toNum(r.position_size),
          risk_percentage: toNum(r.risk_percentage),
          risk_score: toNum(r.risk_score),
          max_drawdown: toNum(r.max_drawdown),
          sharpe_ratio: toNum(r.sharpe_ratio),
          status: r.status ?? null,
        }));
        setRiskData(normalized);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Risk management API fetch failed', err);
        setLoading(false);
      });
  }, []);

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

  if (!riskData?.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="h-5 w-5" />
            <span>Risk Management</span>
          </CardTitle>
        </CardHeader>
        <CardContent>No data</CardContent>
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
              {riskData.map((token) => (
                <TableRow key={token.id} className="hover:bg-muted/50">
                  <TableCell>
                    <div className="font-medium">{token.symbol}</div>
                  </TableCell>

                  <TableCell>
                    <div className="font-medium">{fmtCurrency(token.current_price)}</div>
                  </TableCell>

                  <TableCell>
                    <div className="font-medium">{fmtCurrency(token.stop_loss)}</div>
                    <div className="text-sm text-muted-foreground">
                      {fmtPct(token.risk_percentage)}
                    </div>
                  </TableCell>

                  <TableCell>
                    <div className="font-medium">{fmt(token.position_size, 2)}</div>
                    <div className="text-sm text-muted-foreground">
                      Max DD: {fmtPct(token.max_drawdown, 1)}
                    </div>
                  </TableCell>

                  <TableCell>
                    <Badge className={getRiskBadgeColor(token.risk_score)}>
                      {getRiskLabel(token.risk_score)} ({fmt(token.risk_score, 2)})
                    </Badge>
                  </TableCell>

                  <TableCell>
                    <div
                    className={`flex items-center space-x-1 ${
                      (token.sharpe_ratio ?? 0) > 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {(token.sharpe_ratio ?? 0) > 0 ? (
                      <TrendingUp className="h-3 w-3" />
                    ) : (
                      <TrendingDown className="h-3 w-3" />
                    )}
                    <span className="font-medium">{fmt(token.sharpe_ratio, 2)}</span>
                  </div>
                  </TableCell>

                  <TableCell>
                    <Badge className={getStatusColor(token.status)}>
                      {token.status === 'active' ? 'Active' : token.status === 'high_risk' ? 'High Risk' : '—'}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        <div className="lg:hidden space-y-4">
          {riskData.map((token) => (
            <Card key={token.id} className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="font-medium text-base">{token.symbol}</div>
                  <div className="text-sm text-muted-foreground">{fmtCurrency(token.current_price)}</div>
                </div>
                <Badge className={getStatusColor(token.status)}>
                  {token.status === 'active' ? 'Active' : token.status === 'high_risk' ? 'High Risk' : '—'}
                </Badge>
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-muted-foreground">Stop Loss</span>
                  <div className="font-medium">{fmtCurrency(token.stop_loss)}</div>
                </div>
                <div>
                  <span className="text-muted-foreground">Position Size</span>
                  <div className="font-medium">{fmt(token.position_size, 2)}</div>
                </div>
                <div>
                  <span className="text-muted-foreground">Risk Score</span>
                  <Badge className={getRiskBadgeColor(token.risk_score)}>{getRiskLabel(token.risk_score)}</Badge>
                </div>
                <div>
                  <span className="text-muted-foreground">Sharpe Ratio</span>
                  <div
                  className={`font-medium ${
                    (token.sharpe_ratio ?? 0) > 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {fmt(token.sharpe_ratio, 2)}
                </div>
                </div>
              </div>
            </Card>
          ))}
        </div>

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
              {riskData.map((token) => (
                <TableRow key={token.id} className="hover:bg-muted/50">
                  <TableCell>
                    <div className="font-medium">{token.symbol}</div>
                  </TableCell>
                  <TableCell>
                    <div className="font-medium">{fmtCurrency(token.current_price)}</div>
                  </TableCell>
                  <TableCell>
                    <div className="font-medium">{fmtCurrency(token.stop_loss)}</div>
                  </TableCell>
                  <TableCell>
                    <Badge className={getRiskBadgeColor(token.risk_score)}>{getRiskLabel(token.risk_score)}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(token.status)}>
                      {token.status === 'active' ? 'Active' : token.status === 'high_risk' ? 'High Risk' : '—'}
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
