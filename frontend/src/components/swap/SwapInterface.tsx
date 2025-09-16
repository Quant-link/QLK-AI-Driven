import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ArrowUpDown, Loader2, AlertCircle, Wallet } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useWallet } from '@/hooks/useWallet';
import { WalletButton } from '@/components/wallet/WalletButton';
import { SimpleWalletButton } from '@/components/wallet/SimpleWalletButton';
import { TokenBalances } from '@/components/wallet/TokenBalances';
import { useSimpleWallet } from '@/hooks/useSimpleWallet';
import { useSwapExecution } from '@/hooks/useSwapExecution';
import { formatGasPrice, calculateGasCost } from '@/utils/swapExecution';

interface Token {
  symbol: string;
  address: string;
  decimals: number;
  chain: string;
}

interface Quote {
  success: boolean;
  quote_id?: string;
  source?: string;
  expectedAmountOut?: number;
  execution_data?: any;
  message?: string;
  error?: string;
  supported_pairs?: string[];
  supported_dexes?: string[];
}

export function SwapInterface() {
  const [tokens, setTokens] = useState<Token[]>([]);
  const [fromToken, setFromToken] = useState<string>('');
  const [toToken, setToToken] = useState<string>('');
  const [amount, setAmount] = useState<string>('');
  const [quote, setQuote] = useState<Quote | null>(null);
  const [isLoadingTokens, setIsLoadingTokens] = useState(true);
  const [isLoadingQuote, setIsLoadingQuote] = useState(false);
  const [error, setError] = useState<string>('');

  // Wallet hooks
  const { isConnected, address, chainId } = useWallet();
  const simpleWallet = useSimpleWallet();

  // Swap execution hook
  const swapExecution = useSwapExecution();

  // Simple wallet'ı kullan (daha stabil)
  const walletConnected = simpleWallet.isConnected;
  const walletAddress = simpleWallet.address;

  // Token listesini yükle
  useEffect(() => {
    fetchTokens();
  }, []);

  const fetchTokens = async () => {
    try {
      setIsLoadingTokens(true);
      const response = await fetch('http://localhost:8000/api/tokens');
      const data = await response.json();
      
      if (data.tokens) {
        setTokens(data.tokens);
        // Varsayılan tokenları seç
        if (data.tokens.length >= 2) {
          setFromToken('USDT');
          setToToken('WETH');
        }
      }
    } catch (err) {
      setError('Token listesi yüklenemedi');
      console.error('Token fetch error:', err);
    } finally {
      setIsLoadingTokens(false);
    }
  };

  const fetchQuote = async () => {
    if (!fromToken || !toToken || !amount || parseFloat(amount) <= 0) {
      setError('Lütfen tüm alanları doldurun');
      return;
    }

    // Minimum swap amount kontrolü
    const amountNum = parseFloat(amount);
    const minimumAmounts: { [key: string]: number } = {
      'ETH': 0.001,    // 0.001 ETH minimum
      'USDT': 5,       // 5 USDT minimum
      'USDC': 5,       // 5 USDC minimum
      'DAI': 5,        // 5 DAI minimum
      'WETH': 0.001,   // 0.001 WETH minimum
    };

    const minAmount = minimumAmounts[fromToken] || 0.001;
    if (amountNum < minAmount) {
      setError(`Minimum swap amount for ${fromToken} is ${minAmount}`);
      return;
    }

    try {
      setIsLoadingQuote(true);
      setError('');
      swapExecution.resetState(); // Swap state'ini temizle

      const response = await fetch(
        `http://localhost:8000/api/quote?from_token=${fromToken}&to_token=${toToken}&amount=${amount}`,
        { method: 'POST' }
      );

      const data = await response.json();
      setQuote(data);

      if (!data.success) {
        const errorType = data.error;
        let errorMessage = data.message || 'Quote alınamadı';

        if (errorType === 'PAIR_NOT_SUPPORTED') {
          const alternatives = data.supported_pairs || [];
          if (alternatives.length > 0) {
            errorMessage += `\n\nAlternatif pair'ler:\n${alternatives.join(', ')}`;
          }
        } else if (errorType === 'NO_LIQUIDITY') {
          const supportedDexes = data.supported_dexes || [];
          if (supportedDexes.length > 0) {
            errorMessage += `\n\nDesteklenen DEX'ler: ${supportedDexes.join(', ')}`;
          }
        }

        setError(errorMessage);
      } else if (data.quote_id) {
        // Gas estimation yap
        swapExecution.estimateGas(data.quote_id);
      }
    } catch (err) {
      setError('Quote alınırken hata oluştu');
      console.error('Quote fetch error:', err);
    } finally {
      setIsLoadingQuote(false);
    }
  };

  const swapTokens = () => {
    const temp = fromToken;
    setFromToken(toToken);
    setToToken(temp);
    setQuote(null); // Quote'u temizle
  };

  const handleAmountChange = (value: string) => {
    setAmount(value);
    setQuote(null); // Amount değişince quote'u temizle
    swapExecution.resetState(); // Swap state'ini de temizle
  };

  const handleSwap = async () => {
    if (!quote?.quote_id) {
      setError('Quote bulunamadı');
      return;
    }

    await swapExecution.executeSwap(quote.quote_id, 1.0); // 1% slippage
  };

  if (isLoadingTokens) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin mr-2" />
          <span>Token listesi yükleniyor...</span>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Main Swap Interface */}
        <div className="lg:col-span-2 space-y-4">
      {/* Wallet Connection Card */}
      {!walletConnected && (
        <Card className="border-dashed">
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <Wallet className="h-12 w-12 mx-auto text-muted-foreground" />
              <div>
                <h3 className="font-semibold">Connect Your Wallet</h3>
                <p className="text-sm text-muted-foreground">
                  Connect your wallet to start swapping tokens
                </p>
              </div>
              <SimpleWalletButton />
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ArrowUpDown className="h-5 w-5" />
              Token Swap
            </div>
            {walletConnected && (
              <Badge variant="outline" className="text-xs">
                Connected
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* From Token */}
          <div className="space-y-2">
            <Label htmlFor="from-token">From</Label>
            <div className="flex gap-2">
              <Select value={fromToken} onValueChange={setFromToken}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Token" />
                </SelectTrigger>
                <SelectContent>
                  {tokens.map((token) => (
                    <SelectItem key={token.symbol} value={token.symbol}>
                      {token.symbol}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Input
                id="from-amount"
                type="number"
                placeholder="0.0"
                value={amount}
                onChange={(e) => handleAmountChange(e.target.value)}
                className="flex-1"
              />
            </div>
          </div>

          {/* Swap Button */}
          <div className="flex justify-center">
            <Button
              variant="outline"
              size="sm"
              onClick={swapTokens}
              className="rounded-full h-8 w-8 p-0"
            >
              <ArrowUpDown className="h-4 w-4" />
            </Button>
          </div>

          {/* To Token */}
          <div className="space-y-2">
            <Label htmlFor="to-token">To</Label>
            <div className="flex gap-2">
              <Select value={toToken} onValueChange={setToToken}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Token" />
                </SelectTrigger>
                <SelectContent>
                  {tokens.map((token) => (
                    <SelectItem key={token.symbol} value={token.symbol}>
                      {token.symbol}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Input
                id="to-amount"
                type="text"
                placeholder="0.0"
                value={quote?.success ? quote.expectedAmountOut?.toFixed(6) || '0.0' : '0.0'}
                disabled
                className="flex-1 bg-muted"
              />
            </div>
          </div>

          <Separator />

          {/* Get Quote Button */}
          <Button
            onClick={fetchQuote}
            disabled={isLoadingQuote || !fromToken || !toToken || !amount || !walletConnected}
            className="w-full"
          >
            {!walletConnected ? (
              'Connect Wallet First'
            ) : isLoadingQuote ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Quote Alınıyor...
              </>
            ) : (
              'Get Quote'
            )}
          </Button>

          {/* Error Display */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Quote Display */}
          {quote?.success && (
            <Card className="bg-muted/50">
              <CardContent className="pt-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Best Route:</span>
                  <Badge variant="secondary">{quote.source}</Badge>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Expected Output:</span>
                  <span className="font-medium">
                    {quote.expectedAmountOut?.toFixed(6)} {toToken}
                  </span>
                </div>

                {/* Gas Information */}
                {swapExecution.gasEstimate && swapExecution.gasPrice && (
                  <>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Gas Price:</span>
                      <span className="text-xs">
                        {formatGasPrice(swapExecution.gasPrice)} Gwei
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Est. Gas Cost:</span>
                      <span className="text-xs">
                        {calculateGasCost(swapExecution.gasEstimate, swapExecution.gasPrice)} ETH
                      </span>
                    </div>
                  </>
                )}

                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Quote ID:</span>
                  <span className="font-mono text-xs">
                    {quote.quote_id?.slice(0, 8)}...
                  </span>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Swap Button */}
          {quote?.success && (
            <div className="space-y-2">
              {/* Transaction Status */}
              {swapExecution.txHash && (
                <Card className="bg-blue-50 border-blue-200">
                  <CardContent className="pt-4">
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Transaction:</span>
                        <Badge variant={
                          swapExecution.txStatus === 'confirmed' ? 'default' :
                          swapExecution.txStatus === 'failed' ? 'destructive' : 'secondary'
                        }>
                          {swapExecution.txStatus}
                        </Badge>
                      </div>
                      <div className="text-xs font-mono break-all">
                        {swapExecution.txHash}
                      </div>
                      <a
                        href={`https://etherscan.io/tx/${swapExecution.txHash}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-blue-600 hover:underline"
                      >
                        View on Etherscan →
                      </a>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Swap Error */}
              {swapExecution.error && (
                <Card className="bg-red-50 border-red-200">
                  <CardContent className="pt-4">
                    <div className="text-sm text-red-600">
                      {swapExecution.error}
                    </div>
                  </CardContent>
                </Card>
              )}

              <Button
                className="w-full"
                size="lg"
                onClick={handleSwap}
                disabled={
                  !walletConnected ||
                  swapExecution.isExecuting ||
                  swapExecution.txStatus === 'pending'
                }
              >
                {!walletConnected
                  ? 'Connect Wallet to Swap'
                  : swapExecution.isExecuting
                  ? 'Executing Swap...'
                  : swapExecution.txStatus === 'pending'
                  ? 'Transaction Pending...'
                  : swapExecution.txStatus === 'confirmed'
                  ? 'Swap Completed ✓'
                  : 'Execute Swap'
                }
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
        </div>

        {/* Token Balances Sidebar */}
        <div className="space-y-4">
          <TokenBalances />
        </div>
      </div>
    </div>
  );
}
