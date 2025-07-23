import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface StrategyLog {
  id: string;
  strategy: string;
  token: string;
  action: string;
  amount: number;
  price: number;
  timestamp: Date;
  status: 'success' | 'failed' | 'pending';
}

const mockLogs: StrategyLog[] = [
  {
    id: '1',
    strategy: 'TWAP',
    token: 'ETH',
    action: 'Buy Order',
    amount: 0.5,
    price: 2456.78,
    timestamp: new Date(Date.now() - 1800000),
    status: 'success'
  },
  {
    id: '2',
    strategy: 'DCA',
    token: 'UNI',
    action: 'Buy Order',
    amount: 100,
    price: 8.92,
    timestamp: new Date(Date.now() - 3600000),
    status: 'success'
  },
  {
    id: '3',
    strategy: 'Arbitrage',
    token: 'LINK',
    action: 'Arbitrage Trade',
    amount: 50,
    price: 15.67,
    timestamp: new Date(Date.now() - 7200000),
    status: 'failed'
  }
];

export function StrategyLogTable() {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Strategy Execution Log</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Strategy</TableHead>
              <TableHead>Token</TableHead>
              <TableHead>Action</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Price</TableHead>
              <TableHead>Time</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {mockLogs.map((log) => (
              <TableRow key={log.id}>
                <TableCell>
                  <Badge variant="outline">{log.strategy}</Badge>
                </TableCell>
                <TableCell className="font-medium">{log.token}</TableCell>
                <TableCell>{log.action}</TableCell>
                <TableCell>{log.amount}</TableCell>
                <TableCell>${log.price.toFixed(2)}</TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {log.timestamp.toLocaleString()}
                </TableCell>
                <TableCell>
                  <Badge className={getStatusColor(log.status)}>
                    {log.status}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}