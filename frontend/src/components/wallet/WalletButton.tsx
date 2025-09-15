import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Wallet, Copy, ExternalLink, AlertCircle, Loader2 } from 'lucide-react';
import { useWallet } from '@/hooks/useWallet';

interface WalletButtonProps {
  className?: string;
}

export function WalletButton({ className }: WalletButtonProps) {
  const { 
    isConnected, 
    address, 
    chainId, 
    balance, 
    isLoading, 
    error, 
    connect, 
    disconnect,
    switchNetwork 
  } = useWallet();

  const formatAddress = (addr: string) => {
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
  };

  const copyAddress = async () => {
    if (address) {
      await navigator.clipboard.writeText(address);
      // TODO: Toast notification eklenebilir
    }
  };

  const openEtherscan = () => {
    if (address) {
      window.open(`https://etherscan.io/address/${address}`, '_blank');
    }
  };

  const handleSwitchToMainnet = () => {
    switchNetwork(1); // Ethereum mainnet
  };

  // MetaMask yüklü değilse
  if (error?.includes('MetaMask is not installed')) {
    return (
      <Alert className="max-w-sm">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          <div className="space-y-2">
            <p>MetaMask is required to use this app.</p>
            <Button 
              size="sm" 
              onClick={() => window.open('https://metamask.io/', '_blank')}
            >
              Install MetaMask
            </Button>
          </div>
        </AlertDescription>
      </Alert>
    );
  }

  // Bağlı değilse
  if (!isConnected) {
    return (
      <div className="space-y-2">
        <Button 
          onClick={connect} 
          disabled={isLoading}
          className={className}
        >
          {isLoading ? (
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
        
        {error && !error.includes('MetaMask is not installed') && (
          <Alert variant="destructive" className="max-w-sm">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
      </div>
    );
  }

  // Yanlış network'te
  if (chainId !== 1) {
    return (
      <div className="space-y-2">
        <Button 
          variant="destructive" 
          onClick={handleSwitchToMainnet}
          className={className}
        >
          <AlertCircle className="h-4 w-4 mr-2" />
          Switch to Mainnet
        </Button>
        
        <Alert variant="destructive" className="max-w-sm">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Please switch to Ethereum Mainnet to continue.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // Bağlı ve doğru network'te
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className={className}>
          <Wallet className="h-4 w-4 mr-2" />
          <span className="hidden sm:inline">{formatAddress(address!)}</span>
          <span className="sm:hidden">Wallet</span>
          {balance && (
            <Badge variant="secondary" className="ml-2 hidden md:inline">
              {balance} ETH
            </Badge>
          )}
        </Button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent align="end" className="w-64">
        <DropdownMenuLabel>
          <div className="space-y-1">
            <p className="text-sm font-medium">Connected Wallet</p>
            <p className="text-xs text-muted-foreground font-mono">
              {address}
            </p>
          </div>
        </DropdownMenuLabel>
        
        <DropdownMenuSeparator />
        
        {balance && (
          <>
            <DropdownMenuItem disabled>
              <div className="flex justify-between w-full">
                <span>Balance:</span>
                <span className="font-medium">{balance} ETH</span>
              </div>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
          </>
        )}
        
        <DropdownMenuItem onClick={copyAddress}>
          <Copy className="h-4 w-4 mr-2" />
          Copy Address
        </DropdownMenuItem>
        
        <DropdownMenuItem onClick={openEtherscan}>
          <ExternalLink className="h-4 w-4 mr-2" />
          View on Etherscan
        </DropdownMenuItem>
        
        <DropdownMenuSeparator />
        
        <DropdownMenuItem onClick={disconnect} className="text-red-600">
          Disconnect
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
