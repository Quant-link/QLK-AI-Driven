import { useState, useEffect, useCallback } from 'react';

interface SimpleWalletState {
  isConnected: boolean;
  address: string | null;
  balance: string | null;
  isConnecting: boolean;
  error: string | null;
}

interface SimpleWalletHook extends SimpleWalletState {
  connect: () => Promise<void>;
  disconnect: () => void;
  refresh: () => void;
}

// Global state - basit singleton pattern
let globalState: SimpleWalletState = {
  isConnected: false,
  address: null,
  balance: null,
  isConnecting: false,
  error: null,
};

const listeners: Set<(state: SimpleWalletState) => void> = new Set();

const updateGlobalState = (newState: Partial<SimpleWalletState>) => {
  globalState = { ...globalState, ...newState };
  listeners.forEach(listener => listener(globalState));
};

export function useSimpleWallet(): SimpleWalletHook {
  const [state, setState] = useState<SimpleWalletState>(globalState);

  useEffect(() => {
    const listener = (newState: SimpleWalletState) => {
      setState(newState);
    };
    
    listeners.add(listener);
    
    return () => {
      listeners.delete(listener);
    };
  }, []);

  // Sayfa yüklendiğinde mevcut bağlantıyı kontrol et
  useEffect(() => {
    checkExistingConnection();
  }, []);

  const getProvider = useCallback(() => {
    let provider = window.ethereum;
    if (!provider) return null;

    if (provider.providers && Array.isArray(provider.providers)) {
      provider = provider.providers.find((p: any) => p.isMetaMask) || provider;
    }
    
    return provider;
  }, []);

  const fetchBalance = async (address: string, provider: any) => {
    try {
      const balance = await provider.request({
        method: 'eth_getBalance',
        params: [address, 'latest'],
      });
      
      const ethBalance = (parseInt(balance, 16) / Math.pow(10, 18)).toFixed(4);
      updateGlobalState({ balance: ethBalance });
    } catch (err) {
      console.error('Error fetching balance:', err);
      updateGlobalState({ balance: null });
    }
  };

  const checkExistingConnection = async () => {
    try {
      const provider = getProvider();
      if (!provider) return;

      const accounts = await provider.request({ method: 'eth_accounts' });
      if (accounts && accounts.length > 0) {
        updateGlobalState({ 
          isConnected: true, 
          address: accounts[0], 
          error: null 
        });
        await fetchBalance(accounts[0], provider);
      }
    } catch (err) {
      console.log('No existing connection');
    }
  };

  const connect = async () => {
    const provider = getProvider();
    if (!provider) {
      updateGlobalState({ error: 'MetaMask is not installed' });
      return;
    }

    try {
      updateGlobalState({ isConnecting: true, error: null });

      // Önce mevcut hesapları kontrol et
      let accounts = await provider.request({ method: 'eth_accounts' });
      
      // Eğer hesap yoksa yeni bağlantı iste
      if (!accounts || accounts.length === 0) {
        accounts = await provider.request({
          method: 'eth_requestAccounts'
        }).catch((error: any) => {
          if (error.code === 4001) {
            throw new Error('User rejected the connection');
          }
          if (error.code === -32002) {
            throw new Error('MetaMask is busy. Please check MetaMask and try again.');
          }
          throw new Error(`Connection failed: ${error.message || 'Unknown error'}`);
        });
      }

      if (accounts && accounts.length > 0) {
        updateGlobalState({ 
          isConnected: true, 
          address: accounts[0], 
          isConnecting: false,
          error: null 
        });
        await fetchBalance(accounts[0], provider);
      }
    } catch (err: any) {
      updateGlobalState({ 
        isConnecting: false, 
        error: err.message || 'Failed to connect' 
      });
    }
  };

  const disconnect = () => {
    updateGlobalState({
      isConnected: false,
      address: null,
      balance: null,
      error: null,
    });
  };

  const refresh = () => {
    updateGlobalState({ error: null });
    checkExistingConnection();
  };

  return {
    ...state,
    connect,
    disconnect,
    refresh,
  };
}

// Global type declaration
declare global {
  interface Window {
    ethereum?: any;
  }
}
