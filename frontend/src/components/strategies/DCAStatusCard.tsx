import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Play, Pause, CheckCircle, TrendingUp, TrendingDown } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

interface DCAStrategy {
  id: number;
  token: string;
  status: 'active' | 'paused' | 'completed' | string;
  plan?: string;
  total_investment: number;
  invested_so_far?: number; 
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

type ExecStatus = 'success' | 'failed' | 'pending';

interface ExecutionLogItem {
  strategy: string;      
  plan?: string;         
  token: string;        
  action: string;        
  amount?: number;
  price?: number | null; 
  tokens?: number;       
  dex?: string;
  status: ExecStatus;
  error?: string;
  time: string;         
}

const API_BASE = 'http://localhost:8000';
const POLL_MS = 2500;

const formatCurrency = (amount: number) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: Math.abs(amount) < 0.01 ? 4 : 2,
    maximumFractionDigits: Math.abs(amount) < 0.01 ? 4 : 2,
  }).format(Number.isFinite(amount) ? amount : 0);

const formatNumber = (n: number, digits = 6) =>
  (Number.isFinite(n) ? n : 0).toLocaleString('en-US', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });

const formatDateTime = (iso: string) =>
  new Date(iso).toLocaleString('en-GB', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });

const statusPill = (s: ExecStatus) =>
  s === 'success'
    ? 'bg-emerald-100 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded'
    : s === 'failed'
    ? 'bg-rose-100 text-rose-800 border border-rose-200 px-2 py-0.5 rounded'
    : 'bg-slate-100 text-slate-800 border border-slate-200 px-2 py-0.5 rounded';

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'active':
      return <Play className="h-4 w-4" />;
    case 'paused':
      return <Pause className="h-4 w-4" />;
    case 'completed':
      return <CheckCircle className="h-4 w-4" />;
    default:
      return null;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active':
      return 'bg-green-100 text-green-800 border-green-200';
    case 'paused':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'completed':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

export function DCAStatusCard() {
  const [strategies, setStrategies] = useState<DCAStrategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [execLog, setExecLog] = useState<ExecutionLogItem[]>([]);

  useEffect(() => {
    let live = true;
    const fetchOnce = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/dca_data`);
        const data = await res.json();
        if (live) {
          const list: DCAStrategy[] = Array.isArray(data?.strategies) ? data.strategies : [];
          setStrategies(list);
          setLoading(false);
        }
      } catch (err) {
        console.error('DCA API fetch failed', err);
        if (live) setLoading(false);
      }
    };
    fetchOnce();
    const t = setInterval(fetchOnce, POLL_MS);
    return () => {
      live = false;
      clearInterval(t);
    };
  }, []);

  useEffect(() => {
    let live = true;
    const fetchLog = async () => {
      try {
        const r = await fetch(`${API_BASE}/api/execution_log?limit=50`);
        const j = await r.json();
        if (live) setExecLog(Array.isArray(j?.items) ? j.items : []);
      } catch (e) {
        console.error('execution_log fetch failed', e);
      }
    };
    fetchLog();
    const t = setInterval(fetchLog, POLL_MS);
    return () => {
      live = false;
      clearInterval(t);
    };
  }, []);

  const sorted = useMemo(() => {
    const stepOf = (p?: string) => {
      if (!p) return 9999;
      const parts = String(p).split('-');
      const n = Number(parts[1]);
      return Number.isFinite(n) ? n : 9999;
    };
    return [...strategies].sort((a, b) => stepOf(a.plan) - stepOf(b.plan));
  }, [strategies]);

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="h-full animate-pulse">
            <CardHeader className="pb-3 sm:pb-4">
              <div className="h-6 bg-gray-200 rounded w-3/4" />
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="h-4 bg-gray-200 rounded w-full" />
              <div className="h-4 bg-gray-200 rounded w-2/3" />
              <div className="h-4 bg-gray-200 rounded w-1/2" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6">
        {sorted.map((strategy) => {
          const progress = (strategy.intervals_completed / strategy.total_intervals) * 100;
          const isProfitable = strategy.pnl >= 0;

          const invested =
            typeof strategy.invested_so_far === 'number'
              ? strategy.invested_so_far
              : (strategy.total_investment || 0) *
                (strategy.intervals_completed / Math.max(1, strategy.total_intervals));

          return (
            <Card key={strategy.id} className="h-full">
              <CardHeader className="pb-3 sm:pb-4">
                <div className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
                  <CardTitle className="text-base sm:text-lg">
                    DCA - {strategy.token}
                    {strategy.plan ? (
                      <span className="ml-2 text-sm text-muted-foreground">({strategy.plan})</span>
                    ) : null}
                  </CardTitle>
                  <Badge className={getStatusColor(strategy.status)}>
                    <div className="flex items-center space-x-1">
                      {getStatusIcon(strategy.status)}
                      <span className="capitalize">{strategy.status}</span>
                    </div>
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="space-y-3 sm:space-y-4">
                <div>
                  <div className="flex justify-between text-xs sm:text-sm mb-2">
                    <span className="text-muted-foreground">Progress</span>
                    <span className="font-medium">
                      {strategy.intervals_completed}/{strategy.total_intervals}
                    </span>
                  </div>
                  <Progress value={progress} className="w-full h-2" />
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs sm:text-sm">
                  <div>
                    <span className="text-muted-foreground">Invested so far</span>
                    <div className="font-medium">{formatCurrency(invested)}</div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Current Value</span>
                    <div className="font-medium">{formatCurrency(strategy.current_value)}</div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Avg Price</span>
                    <div className="font-medium">${formatNumber(strategy.avg_buy_price, 8)}</div>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Current Price</span>
                    <div className="font-medium">${formatNumber(strategy.current_price, 8)}</div>
                  </div>
                </div>

                <div className="pt-2 border-t">
                  <div className="flex items-center justify-between">
                    <span className="text-xs sm:text-sm text-muted-foreground">P&L</span>
                    <div
                      className={`flex items-center space-x-1 ${
                        isProfitable ? 'text-emerald-600' : 'text-rose-600'
                      }`}
                    >
                      {isProfitable ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                      <span className="font-medium text-xs sm:text-sm">
                        {formatCurrency(strategy.pnl)} ({strategy.pnl_percentage.toFixed(2)}%)
                      </span>
                    </div>
                  </div>

                  {strategy.status === 'active' && !!strategy.next_buy_in && strategy.next_buy_in > 0 && (
                    <div className="flex justify-between text-xs text-muted-foreground mt-2">
                      <span>Next buy in:</span>
                      <span>{strategy.next_buy_in} min</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Strategy Execution Log */}
      <div className="mt-8">
        <div className="text-lg font-semibold mb-3">DCA Execution Log</div>

        <div className="overflow-x-auto rounded border border-slate-200">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="text-left font-medium px-4 py-2">Strategy</th>
                <th className="text-left font-medium px-4 py-2">Token</th>
                <th className="text-left font-medium px-4 py-2">Action</th>
                <th className="text-right font-medium px-4 py-2">Amount</th>
                <th className="text-right font-medium px-4 py-2">Price</th>
                <th className="text-right font-medium px-4 py-2">Tokens</th>
                <th className="text-left font-medium px-4 py-2">DEX</th>
                <th className="text-left font-medium px-4 py-2">Time</th>
                <th className="text-left font-medium px-4 py-2">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {execLog.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-4 py-6 text-center text-slate-500">
                    No executions yet.
                  </td>
                </tr>
              ) : (
                execLog.map((row, i) => (
                  <tr key={i} className="odd:bg-white even:bg-slate-50">
                    <td className="px-4 py-2">
                      <span className="inline-flex items-center gap-2">
                        <span className="text-slate-800 font-medium">{row.strategy}</span>
                        {row.plan ? <span className="text-xs text-slate-500">({row.plan})</span> : null}
                      </span>
                    </td>
                    <td className="px-4 py-2">{row.token}</td>
                    <td className="px-4 py-2">{row.action}</td>
                    <td className="px-4 py-2 text-right">
                      {row.amount != null ? formatNumber(row.amount, 4) : '—'}
                    </td>
                    <td className="px-4 py-2 text-right">
                      {row.price != null ? formatCurrency(row.price) : '—'}
                    </td>
                    <td className="px-4 py-2 text-right">
                      {row.tokens != null ? formatNumber(row.tokens, 4) : '—'}
                    </td>
                    <td className="px-4 py-2">{row.dex || '—'}</td>
                    <td className="px-4 py-2">{formatDateTime(row.time)}</td>
                    <td className="px-4 py-2">
                      <span className={statusPill(row.status as ExecStatus)}>{row.status}</span>
                      {row.status === 'failed' && row.error ? (
                        <span className="ml-2 text-xs text-rose-600" title={row.error}>
                          (err)
                        </span>
                      ) : null}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
