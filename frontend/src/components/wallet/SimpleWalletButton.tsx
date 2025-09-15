import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Wallet, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useSimpleWallet } from '@/hooks/useSimpleWallet';

export function SimpleWalletButton() {
  const {
    isConnected,
    address,
    balance,
    isConnecting,
    error,
    connect,
    disconnect,
    refresh
  } = useSimpleWallet();

  // Hook'tan gelen fonksiyonları kullan - tüm logic hook'ta

  if (address) {
    return (
      <div className="space-y-2">
        <div className="flex gap-2 items-center">
          <Button onClick={disconnect} variant="outline" className="flex items-center gap-2">
            <Wallet className="h-4 w-4" />
            <span className="hidden sm:inline">{address.slice(0, 6)}...{address.slice(-4)}</span>
            <span className="sm:hidden">Wallet</span>
            {balance && (
              <Badge variant="secondary" className="ml-1">
                {balance} ETH
              </Badge>
            )}
          </Button>
          <Button onClick={refresh} variant="ghost" size="sm">
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <Button onClick={connect} disabled={isConnecting}>
        {isConnecting ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin mr-2" />
            Connecting...
          </>
        ) : (
          <>
            <Wallet className="h-4 w-4 mr-2" />
            Connect Wallet
          </>
        )}
      </Button>

      {error && (
        <Alert variant="destructive" className="max-w-sm">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error}
            {error.includes('Unexpected error') && (
              <Button
                onClick={() => window.location.reload()}
                variant="link"
                size="sm"
                className="ml-2 p-0 h-auto"
              >
                Refresh Page
              </Button>
            )}
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
