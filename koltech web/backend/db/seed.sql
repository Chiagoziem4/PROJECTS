-- Sample seed data for Web3 Airdrop Discovery Platform

-- Sample airdrops
INSERT INTO airdrops (
    project_name,
    chain,
    token_symbol,
    description,
    eligibility_rules,
    official_url,
    status,
    start_date,
    end_date,
    risk_score
) VALUES 
(
    'Example Protocol',
    'Ethereum',
    'EXP',
    'Example Protocol is a decentralized exchange aggregator focusing on optimal swap routes.',
    'Must have traded at least $100 worth of tokens on major DEXes between January and June 2023.',
    'https://example-protocol.io',
    'upcoming',
    '2023-09-01 00:00:00',
    '2023-10-01 00:00:00',
    3
),
(
    'DeFi Rewards',
    'Arbitrum',
    'DFR',
    'DeFi Rewards is a yield optimization protocol for Layer 2 networks.',
    'Must have provided liquidity on Arbitrum for at least 30 days.',
    'https://defi-rewards.io',
    'open',
    '2023-08-01 00:00:00',
    '2023-12-31 23:59:59',
    5
),
(
    'NFT Marketplace',
    'Polygon',
    'NFTM',
    'A community-driven NFT marketplace with focus on digital art.',
    'Must have minted or traded NFTs worth at least 1 ETH on Polygon.',
    'https://nft-marketplace.io',
    'closed',
    '2023-06-01 00:00:00',
    '2023-07-31 23:59:59',
    4
);

-- Sample users (wallet addresses are examples, replace with real ones)
INSERT INTO users (wallet_address, nonce) VALUES 
('0x1234567890123456789012345678901234567890', 'abc123'),
('0x0987654321098765432109876543210987654321', 'def456');

-- Sample comments
INSERT INTO comments (user_id, airdrop_id, content) VALUES 
(1, 1, 'Looks promising! The team has a good track record.'),
(2, 1, 'Make sure to check the eligibility requirements carefully.'),
(1, 2, 'Already qualified for this one. The requirements are reasonable.');

-- Sample watchlist entries
INSERT INTO watchlist (user_id, airdrop_id) VALUES 
(1, 1),
(1, 2),
(2, 2);
