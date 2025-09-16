import { useState, useCallback } from 'react';
import { SwapExecutor, SwapExecutionResult } from '@/utils/swapExecution';
import { useSimpleWallet } from '@/hooks/useSimpleWallet';

interface SwapExecutionState {
  isExecuting: boolean;
  txHash: string | null;
  txStatus: 'idle' | 'pending' | 'confirmed' | 'failed';
  error: string | null;
  gasEstimate: string | null;
  gasPrice: string | null;
}

interface UseSwapExecutionReturn extends SwapExecutionState {
  executeSwap: (quoteId: string, slippageTolerance?: number) => Promise<void>;
  estimateGas: (quoteId: string, slippageTolerance?: number) => Promise<void>;
  resetState: () => void;
  checkTransactionStatus: (txHash: string) => Promise<void>;
}

export function useSwapExecution(): UseSwapExecutionReturn {
  const { address } = useSimpleWallet();
  
  const [state, setState] = useState<SwapExecutionState>({
    isExecuting: false,
    txHash: null,
    txStatus: 'idle',
    error: null,
    gasEstimate: null,
    gasPrice: null,
  });

  const getProvider = useCallback(() => {
    let provider = window.ethereum;
    if (!provider) return null;

    if (provider.providers && Array.isArray(provider.providers)) {
      provider = provider.providers.find((p: any) => p.isMetaMask) || provider;
    }
    
    return provider;
  }, []);

  const executeSwap = useCallback(async (quoteId: string, slippageTolerance: number = 1.0) => {
    if (!address) {
      setState(prev => ({ ...prev, error: 'Wallet not connected' }));
      return;
    }

    const provider = getProvider();
    if (!provider) {
      setState(prev => ({ ...prev, error: 'MetaMask not available' }));
      return;
    }

    try {
      setState(prev => ({ 
        ...prev, 
        isExecuting: true, 
        error: null, 
        txStatus: 'idle' 
      }));

      const executor = new SwapExecutor(provider);
      const result: SwapExecutionResult = await executor.executeSwap(
        quoteId, 
        address, 
        slippageTolerance
      );

      if (result.success && result.txHash) {
        setState(prev => ({ 
          ...prev, 
          isExecuting: false,
          txHash: result.txHash!,
          txStatus: 'pending',
          error: null 
        }));

        // Transaction status'unu takip et
        checkTransactionStatus(result.txHash);
      } else {
        setState(prev => ({ 
          ...prev, 
          isExecuting: false,
          error: result.error || 'Swap execution failed' 
        }));
      }
    } catch (error: any) {
      setState(prev => ({ 
        ...prev, 
        isExecuting: false,
        error: error.message || 'Unexpected error during swap execution' 
      }));
    }
  }, [address, getProvider]);

  const estimateGas = useCallback(async (quoteId: string, slippageTolerance: number = 1.0) => {
    if (!address) return;

    const provider = getProvider();
    if (!provider) return;

    try {
      const executor = new SwapExecutor(provider);
      const gasResult = await executor.estimateGas(quoteId, address, slippageTolerance);

      console.log('Gas estimation result:', gasResult);

      if (gasResult.gasEstimate && gasResult.gasPrice) {
        console.log('✅ Setting gas values:', {
          gasEstimate: gasResult.gasEstimate,
          gasPrice: gasResult.gasPrice
        });
        setState(prev => ({
          ...prev,
          gasEstimate: gasResult.gasEstimate!,
          gasPrice: gasResult.gasPrice!,
        }));
      } else if (gasResult.error) {
        console.log('❌ Gas estimation failed, not showing gas info');
        // Gas estimation başarısız olursa gas bilgilerini gösterme
      } else {
        console.log('❌ Gas values incomplete:', {
          hasGasEstimate: !!gasResult.gasEstimate,
          hasGasPrice: !!gasResult.gasPrice,
          hasError: !!gasResult.error
        });
      }
    } catch (error) {
      console.error('Gas estimation failed:', error);
    }
  }, [address, getProvider]);

  const checkTransactionStatus = useCallback(async (txHash: string) => {
    const provider = getProvider();
    if (!provider) return;

    try {
      const executor = new SwapExecutor(provider);
      const status = await executor.getTransactionStatus(txHash);

      setState(prev => ({ 
        ...prev, 
        txStatus: status.status 
      }));

      // Eğer hala pending ise, 5 saniye sonra tekrar kontrol et
      if (status.status === 'pending') {
        setTimeout(() => checkTransactionStatus(txHash), 5000);
      }
    } catch (error) {
      console.error('Error checking transaction status:', error);
    }
  }, [getProvider]);

  const resetState = useCallback(() => {
    setState({
      isExecuting: false,
      txHash: null,
      txStatus: 'idle',
      error: null,
      gasEstimate: null,
      gasPrice: null,
    });
  }, []);

  return {
    ...state,
    executeSwap,
    estimateGas,
    resetState,
    checkTransactionStatus,
  };
}

// Global type declaration
declare global {
  interface Window {
    ethereum?: any;
  }
}
