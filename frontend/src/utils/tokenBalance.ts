// ERC-20 Token Balance Utilities

// ERC-20 balanceOf function signature
const ERC20_BALANCE_OF_ABI = [
  {
    "constant": true,
    "inputs": [{"name": "_owner", "type": "address"}],
    "name": "balanceOf",
    "outputs": [{"name": "balance", "type": "uint256"}],
    "type": "function"
  }
];

interface TokenBalance {
  symbol: string;
  balance: string;
  decimals: number;
  address: string;
}

interface Token {
  symbol: string;
  address: string;
  decimals: number;
  chain: string;
}

export class TokenBalanceReader {
  private provider: any;

  constructor(provider: any) {
    this.provider = provider;
  }

  // ETH balance okuma
  async getETHBalance(address: string): Promise<string> {
    try {
      const balance = await this.provider.request({
        method: 'eth_getBalance',
        params: [address, 'latest'],
      });
      
      const ethBalance = (parseInt(balance, 16) / Math.pow(10, 18)).toFixed(4);
      return ethBalance;
    } catch (error) {
      console.error('Error fetching ETH balance:', error);
      return '0.0000';
    }
  }

  // ERC-20 token balance okuma
  async getTokenBalance(tokenAddress: string, userAddress: string, decimals: number): Promise<string> {
    try {
      // Geçersiz adres kontrolü
      if (!tokenAddress || tokenAddress === '0x0000000000000000000000000000000000000000') {
        return '0.000000';
      }

      // balanceOf function call data oluştur
      const functionSignature = '0x70a08231'; // balanceOf(address)
      const paddedAddress = userAddress.slice(2).padStart(64, '0');
      const callData = functionSignature + paddedAddress;

      const result = await this.provider.request({
        method: 'eth_call',
        params: [
          {
            to: tokenAddress,
            data: callData,
          },
          'latest'
        ],
      });

      if (result && result !== '0x' && result !== '0x0') {
        const balance = parseInt(result, 16);
        if (balance > 0) {
          const tokenBalance = (balance / Math.pow(10, decimals)).toFixed(6);
          return tokenBalance;
        }
      }

      return '0.000000';
    } catch (error) {
      // Sessizce hata logla ama kullanıcıyı rahatsız etme
      console.warn(`Token balance fetch failed for ${tokenAddress}:`, error.message || error);
      return '0.000000';
    }
  }

  // Birden fazla token balance'ını paralel olarak oku
  async getMultipleTokenBalances(tokens: Token[], userAddress: string): Promise<TokenBalance[]> {
    const balancePromises = tokens.map(async (token) => {
      let balance: string;

      if (token.symbol === 'ETH') {
        // Native ETH balance
        balance = await this.getETHBalance(userAddress);
      } else if (token.address === '0x0000000000000000000000000000000000000000') {
        // ETH with zero address
        balance = await this.getETHBalance(userAddress);
      } else {
        // ERC-20 tokenlar (WETH, USDT, vs.)
        balance = await this.getTokenBalance(token.address, userAddress, token.decimals);
      }

      return {
        symbol: token.symbol,
        balance,
        decimals: token.decimals,
        address: token.address,
      };
    });

    try {
      const results = await Promise.all(balancePromises);
      return results;
    } catch (error) {
      console.error('Error fetching multiple token balances:', error);
      return [];
    }
  }

  // Sadece sıfır olmayan balance'ları filtrele
  filterNonZeroBalances(balances: TokenBalance[]): TokenBalance[] {
    return balances.filter(balance => {
      const numBalance = parseFloat(balance.balance);
      return numBalance > 0.000001; // Minimum threshold
    });
  }
}

// Utility functions
export const formatTokenBalance = (balance: string, decimals: number = 6): string => {
  const num = parseFloat(balance);
  if (num === 0) return '0';
  if (num < 0.000001) return '< 0.000001';
  return num.toFixed(decimals);
};

export const formatTokenDisplay = (balance: TokenBalance): string => {
  const formatted = formatTokenBalance(balance.balance, 4);
  return `${formatted} ${balance.symbol}`;
};
