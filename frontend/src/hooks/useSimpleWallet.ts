import { useState, useEffect, useCallback } from 'react';
import { TokenBalanceReader, TokenBalance } from '@/utils/tokenBalance';

interface SimpleWalletState {
  isConnected: boolean;
  address: string | null;
  balance: string | null;
  tokenBalances: TokenBalance[];
  isConnecting: boolean;
  isLoadingBalances: boolean;
  error: string | null;
}

interface SimpleWalletHook extends SimpleWalletState {
  connect: () => Promise<void>;
  disconnect: () => void;
  refresh: () => void;
  refreshBalances: () => Promise<void>;
}

// Global state - basit singleton pattern
let globalState: SimpleWalletState = {
  isConnected: false,
  address: null,
  balance: null,
  tokenBalances: [],
  isConnecting: false,
  isLoadingBalances: false,
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

  const fetchTokenBalances = async (address: string, provider: any) => {
    try {
      updateGlobalState({ isLoadingBalances: true });

      // Backend'den token listesini al
      const response = await fetch('http://localhost:8000/api/tokens');
      const data = await response.json();

      if (data.tokens) {
        const balanceReader = new TokenBalanceReader(provider);
        const balances = await balanceReader.getMultipleTokenBalances(data.tokens, address);
        const nonZeroBalances = balanceReader.filterNonZeroBalances(balances);

        updateGlobalState({
          tokenBalances: nonZeroBalances,
          isLoadingBalances: false
        });

        console.log('Token balances fetched:', nonZeroBalances);
      }
    } catch (err) {
      console.error('Error fetching token balances:', err);
      updateGlobalState({
        tokenBalances: [],
        isLoadingBalances: false
      });
    }
  };

  const checkExistingConnection = async () => {
    try {
      const provider = getProvider();
      if (!provider) return;

      // Network kontrolü - sadece mainnet
      const chainId = await provider.request({ method: 'eth_chainId' });
      console.log('Current Chain ID:', chainId);

      if (chainId !== '0x1') {
        console.warn(`Wrong network. Current: ${chainId}, Expected: 0x1`);
        // Otomatik olarak mainnet'e geçmeyi dene
        try {
          await provider.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: '0x1' }],
          });
          console.log('✅ Switched to Ethereum Mainnet');
        } catch (switchError: any) {
          console.error('Network switch failed:', switchError);
          updateGlobalState({
            error: 'Please manually switch to Ethereum Mainnet in MetaMask'
          });
          return;
        }
      }

      console.log('✅ Connected to Ethereum Mainnet');

      const accounts = await provider.request({ method: 'eth_accounts' });
      if (accounts && accounts.length > 0) {
        updateGlobalState({
          isConnected: true,
          address: accounts[0],
          error: null
        });
        await fetchBalance(accounts[0], provider);
        await fetchTokenBalances(accounts[0], provider);
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

      // Network kontrolü - sadece mainnet
      const chainId = await provider.request({ method: 'eth_chainId' });
      console.log('Connect Chain ID:', chainId);

      if (chainId !== '0x1') {
        // Otomatik olarak mainnet'e geçmeyi dene
        try {
          await provider.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: '0x1' }],
          });
          console.log('✅ Switched to Ethereum Mainnet');
        } catch (switchError: any) {
          if (switchError.code === 4902) {
            // Network eklenmemiş, ekle
            try {
              await provider.request({
                method: 'wallet_addEthereumChain',
                params: [{
                  chainId: '0x1',
                  chainName: 'Ethereum Mainnet',
                  nativeCurrency: {
                    name: 'Ethereum',
                    symbol: 'ETH',
                    decimals: 18,
                  },
                  rpcUrls: ['https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'],
                  blockExplorerUrls: ['https://etherscan.io'],
                }],
              });
            } catch (addError) {
              throw new Error('Please manually switch to Ethereum Mainnet in MetaMask');
            }
          } else {
            throw new Error('Please manually switch to Ethereum Mainnet in MetaMask');
          }
        }
      }

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
        await fetchTokenBalances(accounts[0], provider);
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
      tokenBalances: [],
      error: null,
    });
  };

  const refresh = () => {
    updateGlobalState({ error: null });
    checkExistingConnection();
  };

  const refreshBalances = async () => {
    if (globalState.address) {
      const provider = getProvider();
      if (provider) {
        await fetchBalance(globalState.address, provider);
        await fetchTokenBalances(globalState.address, provider);
      }
    }
  };

  return {
    ...state,
    connect,
    disconnect,
    refresh,
    refreshBalances,
  };
}

// Global type declaration
declare global {
  interface Window {
    ethereum?: any;
  }
}
