-- Schema for Airdrop Discovery Platform

-- Users table (for wallet-based authentication)
CREATE TABLE users (
    wallet_address TEXT PRIMARY KEY,
    nonce TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Airdrops table
CREATE TABLE airdrops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    chain TEXT NOT NULL,
    token_symbol TEXT,
    description TEXT,
    eligibility_rules TEXT NOT NULL,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    status TEXT CHECK(status IN ('upcoming', 'active', 'ended')) DEFAULT 'upcoming',
    official_links TEXT,
    risk_score INTEGER CHECK(risk_score BETWEEN 1 AND 10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Comments table
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    airdrop_id INTEGER,
    wallet_address TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(airdrop_id) REFERENCES airdrops(id),
    FOREIGN KEY(wallet_address) REFERENCES users(wallet_address)
);

-- Watchlist table
CREATE TABLE watchlist (
    wallet_address TEXT,
    airdrop_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(wallet_address, airdrop_id),
    FOREIGN KEY(wallet_address) REFERENCES users(wallet_address),
    FOREIGN KEY(airdrop_id) REFERENCES airdrops(id)
);

-- Blog posts table
CREATE TABLE blog_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,
    author_address TEXT,
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(author_address) REFERENCES users(wallet_address)
);

-- Create indexes
CREATE INDEX idx_airdrops_status ON airdrops(status);
CREATE INDEX idx_airdrops_chain ON airdrops(chain);
CREATE INDEX idx_comments_airdrop ON comments(airdrop_id);
CREATE INDEX idx_blog_posts_slug ON blog_posts(slug);
