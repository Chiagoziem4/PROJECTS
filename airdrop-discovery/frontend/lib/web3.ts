import { createConfig, configureChains, mainnet, polygonMainnet, optimism } from 'wagmi';
import { publicProvider } from 'wagmi/providers/public';
import { infuraProvider } from 'wagmi/providers/infura';
import { MetaMaskConnector } from 'wagmi/connectors/metaMask';
import { WalletConnectConnector } from 'wagmi/connectors/walletConnect';
import { CoinbaseWalletConnector } from 'wagmi/connectors/coinbaseWallet';

// Configure chains
const { chains, publicClient, webSocketPublicClient } = configureChains(
    [mainnet, polygonMainnet, optimism],
    [
        infuraProvider({ apiKey: process.env.NEXT_PUBLIC_INFURA_ID! }),
        publicProvider(),
    ]
);

// Configure connectors
const connectors = [
    new MetaMaskConnector({ chains }),
    new WalletConnectConnector({
        chains,
        options: {
            projectId: process.env.NEXT_PUBLIC_WALLET_CONNECT_PROJECT_ID!,
        },
    }),
    new CoinbaseWalletConnector({
        chains,
        options: {
            appName: 'Airdrop Discovery',
        },
    }),
];

// Create wagmi config
export const config = createConfig({
    autoConnect: true,
    connectors,
    publicClient,
    webSocketPublicClient,
});

// Authentication helpers
export const generateNonceMessage = (nonce: string) => {
    return `Sign this message to verify your wallet. Nonce: ${nonce}`;
};

export const fetchNonce = async (address: string): Promise<string> => {
    const response = await fetch('/api/auth/nonce', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ address }),
    });

    if (!response.ok) {
        throw new Error('Failed to fetch nonce');
    }

    const data = await response.json();
    return data.nonce;
};

export const verifySignature = async (
    address: string,
    signature: string
): Promise<string> => {
    const response = await fetch('/api/auth/verify', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ address, signature }),
    });

    if (!response.ok) {
        throw new Error('Signature verification failed');
    }

    const data = await response.json();
    return data.token;
};

// Chain helpers
export const getChainName = (chainId: number): string => {
    const chains: Record<number, string> = {
        1: 'Ethereum',
        137: 'Polygon',
        10: 'Optimism',
        42161: 'Arbitrum',
        56: 'BSC',
    };
    return chains[chainId] || 'Unknown Chain';
};

export const getChainExplorer = (chainId: number): string => {
    const explorers: Record<number, string> = {
        1: 'https://etherscan.io',
        137: 'https://polygonscan.com',
        10: 'https://optimistic.etherscan.io',
        42161: 'https://arbiscan.io',
        56: 'https://bscscan.com',
    };
    return explorers[chainId] || '';
};

// Token helpers
export interface TokenInfo {
    address: string;
    symbol: string;
    decimals: number;
}

export const getTokenInfo = async (
    tokenAddress: string,
    chainId: number
): Promise<TokenInfo> => {
    // This would typically interact with the blockchain to get token info
    // For now, we'll return mock data
    return {
        address: tokenAddress,
        symbol: 'TOKEN',
        decimals: 18,
    };
};

// ENS helpers
export const resolveEns = async (
    address: string
): Promise<string | null> => {
    try {
        const response = await fetch(
            `https://api.ensideas.com/ens/resolve/${address}`
        );
        if (!response.ok) return null;
        const data = await response.json();
        return data.name || null;
    } catch {
        return null;
    }
};

// Error handler
export const handleWeb3Error = (error: any): string => {
    if (error.code === 4001) {
        return 'Transaction rejected by user';
    }
    if (error.code === -32002) {
        return 'Please unlock your wallet';
    }
    return error.message || 'An error occurred';
};
