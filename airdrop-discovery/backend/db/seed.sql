-- Sample seed data for development

-- Sample airdrops
INSERT INTO airdrops (
    project_name,
    chain,
    token_symbol,
    description,
    eligibility_rules,
    start_date,
    end_date,
    status,
    official_links,
    risk_score
) VALUES 
(
    'DeFi Protocol X',
    'Ethereum',
    'DFX',
    'Revolutionary DeFi protocol focusing on sustainable yield generation',
    'Must have interacted with major DeFi protocols (Uniswap, Aave, or Compound) before snapshot date',
    '2025-09-01 00:00:00',
    '2025-10-01 00:00:00',
    'upcoming',
    'https://defixprotocol.example.com,https://twitter.com/defixprotocol',
    8
),
(
    'GameFi Project Y',
    'Polygon',
    'GFY',
    'Web3 gaming platform with play-to-earn mechanics',
    'Hold at least 0.1 ETH worth of gaming NFTs on Polygon',
    '2025-08-15 00:00:00',
    '2025-09-15 00:00:00',
    'active',
    'https://gamefiproject.example.com',
    7
),
(
    'Privacy Protocol Z',
    'Optimism',
    'PPZ',
    'Zero-knowledge privacy solution for DeFi transactions',
    'Must have used zkSync or other L2 solutions before 2025',
    '2025-10-01 00:00:00',
    '2025-11-01 00:00:00',
    'upcoming',
    'https://privacyprotocol.example.com',
    9
);

-- Sample blog post
INSERT INTO blog_posts (
    title,
    slug,
    content,
    author_address
) VALUES (
    'How to Safely Participate in Airdrops',
    'safely-participate-in-airdrops',
    '# How to Safely Participate in Airdrops

Always follow these guidelines when participating in airdrops:

1. Never share your private keys
2. Always verify official links
3. Use a separate wallet for airdrops
4. Research the project thoroughly

Stay safe!',
    '0x1234567890123456789012345678901234567890'
);
