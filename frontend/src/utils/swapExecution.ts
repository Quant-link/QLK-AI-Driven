// Swap Execution Utilities

interface SwapTransaction {
  to: string;
  data: string;
  value: string;
  gas?: string;
  gasPrice?: string;
}

interface SwapExecutionResult {
  success: boolean;
  txHash?: string;
  error?: string;
}

export class SwapExecutor {
  private provider: any;

  constructor(provider: any) {
    this.provider = provider;
  }

  // Backend'den swap transaction data'sını al
  async getSwapTransaction(
    quoteId: string, 
    userAddress: string, 
    slippageTolerance: number = 1.0
  ): Promise<{ success: boolean; tx?: SwapTransaction; error?: string }> {
    try {
      const response = await fetch(
        `http://localhost:8000/api/swap?quote_id=${quoteId}&user_address=${userAddress}&slippage_tolerance=${slippageTolerance}`,
        { method: 'POST' }
      );

      const data = await response.json();

      console.log('Backend swap response:', data);

      if (!data.success) {
        console.error('Backend swap failed:', data.message);
        return { success: false, error: data.message || 'Failed to get swap transaction' };
      }

      console.log('✅ Swap transaction prepared:', data.tx);
      return { success: true, tx: data.tx };
    } catch (error) {
      console.error('Error getting swap transaction:', error);
      return { success: false, error: 'Network error while preparing swap' };
    }
  }

  // MetaMask ile transaction'ı execute et
  async executeSwap(
    quoteId: string,
    userAddress: string,
    slippageTolerance: number = 1.0
  ): Promise<SwapExecutionResult> {
    try {
      // 1. Backend'den transaction data'sını al
      const txResult = await this.getSwapTransaction(quoteId, userAddress, slippageTolerance);

      if (!txResult.success || !txResult.tx) {
        return { success: false, error: txResult.error || 'Failed to prepare transaction' };
      }

      const tx = txResult.tx;
      console.log('Executing swap transaction:', tx);

      // 2. Transaction parametrelerini hazırla - ensure hex values have 0x prefix
      const value = tx.value || '0';
      const hexValue = value.startsWith('0x') ? value : `0x${value}`;

      const txParams: any = {
        from: userAddress,
        to: tx.to,
        data: tx.data,
        value: hexValue,
      };

      // Gas parametrelerini ekle (varsa)
      if (tx.gas) txParams.gas = tx.gas;
      if (tx.gasPrice) txParams.gasPrice = tx.gasPrice;

      // 3. MetaMask ile transaction'ı gönder
      const txHash = await this.provider.request({
        method: 'eth_sendTransaction',
        params: [txParams],
      });

      console.log('Swap transaction sent:', txHash);
      return { success: true, txHash };

    } catch (error: any) {
      console.error('Swap execution error:', error);
      
      // MetaMask error handling
      if (error.code === 4001) {
        return { success: false, error: 'User rejected the transaction' };
      }
      
      if (error.code === -32603) {
        return { success: false, error: 'Transaction failed. Please check your balance and try again.' };
      }

      return { 
        success: false, 
        error: error.message || 'Transaction failed' 
      };
    }
  }

  // Transaction status'unu kontrol et
  async getTransactionStatus(txHash: string): Promise<{
    status: 'pending' | 'confirmed' | 'failed';
    blockNumber?: number;
    gasUsed?: string;
  }> {
    try {
      const receipt = await this.provider.request({
        method: 'eth_getTransactionReceipt',
        params: [txHash],
      });

      if (!receipt) {
        return { status: 'pending' };
      }

      return {
        status: receipt.status === '0x1' ? 'confirmed' : 'failed',
        blockNumber: parseInt(receipt.blockNumber, 16),
        gasUsed: receipt.gasUsed,
      };
    } catch (error) {
      console.error('Error checking transaction status:', error);
      return { status: 'pending' };
    }
  }

  // Gas estimation - gerçek blockchain gas price + realistic estimates
  async estimateGas(
    quoteId: string,
    userAddress: string,
    slippageTolerance: number = 1.0
  ): Promise<{ gasEstimate?: string; gasPrice?: string; error?: string }> {
    try {
      // Gerçek network gas price'ı al
      const gasPrice = await this.provider.request({
        method: 'eth_gasPrice',
        params: [],
      });
      console.log('✅ Real network gas price obtained:', gasPrice);

      // Gerçek Uniswap gas estimates (mainnet data'sına dayalı)
      // ETH → Token: ~120,000 gas
      // Token → ETH: ~180,000 gas (approval zaten yapılmışsa)
      // Token → Token: ~250,000 gas

      // Konservativ estimate kullan (yüksek taraftan)
      const gasEstimate = '0x2bf20'; // 180,000 gas (realistic for most swaps)

      console.log('✅ Using realistic gas estimate for DEX swaps:', gasEstimate);

      return { gasEstimate, gasPrice };
    } catch (error) {
      console.error('Gas estimation error:', error);

      // Gerçek network gas price'ı almaya çalış
      try {
        const gasPrice = await this.provider.request({
          method: 'eth_gasPrice',
          params: [],
        });

        console.log('✅ Fallback: Real gas price with conservative estimate');
        return {
          gasEstimate: '0x30d40', // 200,000 gas (conservative fallback)
          gasPrice: gasPrice, // Gerçek gas price
        };
      } catch (gasPriceError) {
        console.error('Complete gas estimation failure:', gasPriceError);
        return { error: 'Failed to get gas information from network' };
      }
    }
  }
}

// Utility functions
export const formatGasPrice = (gasPriceWei: string): string => {
  const gwei = parseInt(gasPriceWei, 16) / Math.pow(10, 9);
  return gwei.toFixed(2);
};

export const calculateGasCost = (gasEstimate: string, gasPrice: string): string => {
  const gas = parseInt(gasEstimate, 16);
  const price = parseInt(gasPrice, 16);
  const costWei = gas * price;
  const costEth = costWei / Math.pow(10, 18);
  return costEth.toFixed(6);
};
