import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { RefreshCw, Coins } from 'lucide-react';
import { useSimpleWallet } from '@/hooks/useSimpleWallet';
import { formatTokenDisplay } from '@/utils/tokenBalance';

interface TokenBalancesProps {
  className?: string;
}

export function TokenBalances({ className }: TokenBalancesProps) {
  const { 
    tokenBalances, 
    isLoadingBalances, 
    balance, 
    refreshBalances,
    isConnected 
  } = useSimpleWallet();

  if (!isConnected) {
    return null;
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Coins className="h-4 w-4" />
            Token Balances
          </CardTitle>
          <Button 
            onClick={refreshBalances} 
            variant="ghost" 
            size="sm"
            disabled={isLoadingBalances}
          >
            <RefreshCw className={`h-4 w-4 ${isLoadingBalances ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-2">
        {/* ETH Balance */}
        <div className="flex justify-between items-center py-1">
          <span className="text-sm font-medium">ETH</span>
          <Badge variant="secondary">
            {balance || '0.0000'} ETH
          </Badge>
        </div>

        {/* Token Balances */}
        {isLoadingBalances ? (
          // Loading skeletons
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="flex justify-between items-center py-1">
              <Skeleton className="h-4 w-12" />
              <Skeleton className="h-5 w-20" />
            </div>
          ))
        ) : tokenBalances.length > 0 ? (
          // Actual token balances
          tokenBalances.map((tokenBalance) => (
            <div key={tokenBalance.symbol} className="flex justify-between items-center py-1">
              <span className="text-sm font-medium">{tokenBalance.symbol}</span>
              <Badge variant="outline" className="text-xs">
                {formatTokenDisplay(tokenBalance)}
              </Badge>
            </div>
          ))
        ) : (
          // No tokens found
          <div className="text-center py-4 text-sm text-muted-foreground">
            No token balances found
          </div>
        )}

        {/* Total count */}
        {tokenBalances.length > 0 && (
          <div className="pt-2 border-t">
            <div className="text-xs text-muted-foreground text-center">
              {tokenBalances.length} token{tokenBalances.length !== 1 ? 's' : ''} with balance
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
