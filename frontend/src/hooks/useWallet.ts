import { useState, useEffect, useCallback } from 'react';

interface WalletState {
  isConnected: boolean;
  address: string | null;
  chainId: number | null;
  balance: string | null;
  isLoading: boolean;
  error: string | null;
}

interface WalletHook extends WalletState {
  connect: () => Promise<void>;
  disconnect: () => void;
  switchNetwork: (chainId: number) => Promise<void>;
}

// Ethereum mainnet
const ETHEREUM_CHAIN_ID = 1;
const ETHEREUM_CHAIN_HEX = '0x1';

export function useWallet(): WalletHook {
  const [state, setState] = useState<WalletState>({
    isConnected: false,
    address: null,
    chainId: null,
    balance: null,
    isLoading: false,
    error: null,
  });

  // Ethereum provider'ını güvenli şekilde al
  const getEthereumProvider = useCallback(() => {
    if (typeof window === 'undefined') {
      console.log('Window is undefined');
      return null;
    }

    const { ethereum } = window;
    console.log('Ethereum object:', {
      exists: !!ethereum,
      isMetaMask: ethereum?.isMetaMask,
      hasProviders: !!ethereum?.providers,
      providersLength: ethereum?.providers?.length
    });

    if (!ethereum) return null;

    // Eğer birden fazla provider varsa MetaMask'ı bul
    if (ethereum.providers) {
      const metamaskProvider = ethereum.providers.find((provider: any) => provider.isMetaMask);
      console.log('Found MetaMask provider in providers array:', !!metamaskProvider);
      return metamaskProvider || ethereum;
    }

    return ethereum;
  }, []);

  // MetaMask varlığını kontrol et
  const isMetaMaskInstalled = useCallback(() => {
    const provider = getEthereumProvider();
    return provider && (provider.isMetaMask || typeof provider.request === 'function');
  }, [getEthereumProvider]);

  // Account değişikliklerini dinle
  useEffect(() => {
    if (!isMetaMaskInstalled()) return;

    const provider = getEthereumProvider();
    if (!provider) return;

    const handleAccountsChanged = (accounts: string[]) => {
      console.log('Accounts changed:', accounts);
      if (accounts.length === 0) {
        // Kullanıcı disconnect etti
        setState(prev => ({
          ...prev,
          isConnected: false,
          address: null,
          balance: null,
          error: null,
        }));
      } else {
        // Yeni account seçildi
        setState(prev => ({
          ...prev,
          address: accounts[0],
          isConnected: true,
          error: null,
        }));
        fetchBalance(accounts[0]);
      }
    };

    const handleChainChanged = (chainId: string) => {
      console.log('Chain changed:', chainId);
      const newChainId = parseInt(chainId, 16);
      setState(prev => ({
        ...prev,
        chainId: newChainId,
        error: newChainId !== ETHEREUM_CHAIN_ID ? 'Please switch to Ethereum Mainnet' : null,
      }));
    };

    // Event listener'ları ekle
    provider.on('accountsChanged', handleAccountsChanged);
    provider.on('chainChanged', handleChainChanged);

    // Cleanup
    return () => {
      if (provider.removeListener) {
        provider.removeListener('accountsChanged', handleAccountsChanged);
        provider.removeListener('chainChanged', handleChainChanged);
      }
    };
  }, [isMetaMaskInstalled, getEthereumProvider]);

  // Sayfa yüklendiğinde mevcut connection'ı kontrol et
  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    if (!isMetaMaskInstalled()) {
      setState(prev => ({ ...prev, error: 'MetaMask is not installed' }));
      return;
    }

    try {
      const provider = getEthereumProvider();
      if (!provider) {
        setState(prev => ({ ...prev, error: 'MetaMask is not available' }));
        return;
      }

      const accounts = await provider.request({ method: 'eth_accounts' });
      const chainId = await provider.request({ method: 'eth_chainId' });

      if (accounts.length > 0) {
        const address = accounts[0];
        const numericChainId = parseInt(chainId, 16);

        setState(prev => ({
          ...prev,
          isConnected: true,
          address,
          chainId: numericChainId,
          error: numericChainId !== ETHEREUM_CHAIN_ID ? 'Please switch to Ethereum Mainnet' : null,
        }));

        await fetchBalance(address);
      }
    } catch (error) {
      console.error('Error checking wallet connection:', error);
      setState(prev => ({ ...prev, error: 'Failed to check wallet connection' }));
    }
  };

  const fetchBalance = async (address: string) => {
    try {
      const provider = getEthereumProvider();
      if (!provider) return;

      const balance = await provider.request({
        method: 'eth_getBalance',
        params: [address, 'latest'],
      });

      // Wei'den ETH'ye çevir
      const ethBalance = (parseInt(balance, 16) / Math.pow(10, 18)).toFixed(4);
      setState(prev => ({ ...prev, balance: ethBalance }));
    } catch (error) {
      console.error('Error fetching balance:', error);
      setState(prev => ({ ...prev, balance: null }));
    }
  };

  const connect = async () => {
    if (!isMetaMaskInstalled()) {
      setState(prev => ({ ...prev, error: 'MetaMask is not installed. Please install MetaMask.' }));
      return;
    }

    try {
      setState(prev => ({ ...prev, isLoading: true, error: null }));

      // Güvenli provider al
      const provider = getEthereumProvider();
      if (!provider) {
        throw new Error('MetaMask provider is not available');
      }

      console.log('Connecting to MetaMask...', { provider: !!provider, isMetaMask: provider.isMetaMask });

      // Daha güvenli request yöntemi
      const accounts = await provider.request({
        method: 'eth_requestAccounts',
      }).catch((error: any) => {
        console.error('MetaMask request error:', error);
        if (error.code === 4001) {
          throw new Error('User rejected the connection request');
        }
        if (error.code === -32002) {
          throw new Error('MetaMask is already processing a request. Please check MetaMask.');
        }
        throw error;
      });

      if (!accounts || accounts.length === 0) {
        throw new Error('No accounts found');
      }

      const chainId = await provider.request({ method: 'eth_chainId' });
      const numericChainId = parseInt(chainId, 16);
      const address = accounts[0];

      console.log('Connected successfully:', { address, chainId: numericChainId });

      setState(prev => ({
        ...prev,
        isConnected: true,
        address,
        chainId: numericChainId,
        isLoading: false,
        error: numericChainId !== ETHEREUM_CHAIN_ID ? 'Please switch to Ethereum Mainnet' : null,
      }));

      await fetchBalance(address);

    } catch (error: any) {
      console.error('Error connecting wallet:', error);
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error.message || 'Failed to connect wallet',
      }));
    }
  };

  const disconnect = () => {
    setState({
      isConnected: false,
      address: null,
      chainId: null,
      balance: null,
      isLoading: false,
      error: null,
    });
  };

  const switchNetwork = async (targetChainId: number) => {
    if (!isMetaMaskInstalled()) return;

    try {
      const provider = getEthereumProvider();
      if (!provider) return;

      await provider.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: `0x${targetChainId.toString(16)}` }],
      });
    } catch (error: any) {
      console.error('Error switching network:', error);
      setState(prev => ({ ...prev, error: 'Failed to switch network' }));
    }
  };

  return {
    ...state,
    connect,
    disconnect,
    switchNetwork,
  };
}

// Global type declaration for window.ethereum
declare global {
  interface Window {
    ethereum?: {
      isMetaMask?: boolean;
      request: (args: { method: string; params?: any[] }) => Promise<any>;
      on: (event: string, handler: (...args: any[]) => void) => void;
      removeListener: (event: string, handler: (...args: any[]) => void) => void;
    };
  }
}
