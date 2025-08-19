import { ethers } from 'ethers';
import { createConfig, configureChains, mainnet } from 'wagmi';
import { publicProvider } from 'wagmi/providers/public';
import { MetaMaskConnector } from 'wagmi/connectors/metaMask';
import { WalletConnectConnector } from 'wagmi/connectors/walletConnect';

// Configure chains for the wallet
const { chains, publicClient } = configureChains(
    [mainnet],
    [publicProvider()]
);

// Create wagmi config with connectors
const config = createConfig({
    autoConnect: true,
    connectors: [
        new MetaMaskConnector({ chains }),
        new WalletConnectConnector({
            chains,
            options: {
                projectId: process.env.NEXT_PUBLIC_WEB3_MODAL_PROJECT_ID,
            },
        }),
    ],
    publicClient,
});

// Helper function to get ethers provider
export const getProvider = () => {
    if (typeof window !== 'undefined' && window.ethereum) {
        return new ethers.BrowserProvider(window.ethereum);
    }
    return new ethers.JsonRpcProvider(process.env.ETHEREUM_RPC_URL);
};

// Helper function to get signer
export const getSigner = async () => {
    const provider = getProvider();
    return await provider.getSigner();
};

// Function to verify message signature
export const verifySignature = async (message, signature, address) => {
    try {
        const signerAddr = ethers.verifyMessage(message, signature);
        return signerAddr.toLowerCase() === address.toLowerCase();
    } catch (error) {
        console.error('Signature verification failed:', error);
        return false;
    }
};

// Function to generate nonce for authentication
export const generateNonce = () => {
    return Math.floor(Math.random() * 1000000).toString();
};

export { config, chains };
