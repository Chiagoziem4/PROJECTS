const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const sqlite3 = require('sqlite3').verbose();
const { check, validationResult } = require('express-validator');
const dotenv = require('dotenv');
const jwt = require('jsonwebtoken');
const ethers = require('ethers');

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Database connection
const db = new sqlite3.Database(process.env.DATABASE_URL || './data/airdrops.db', (err) => {
    if (err) {
        console.error('Error connecting to database:', err);
    } else {
        console.log('Connected to SQLite database');
    }
});

// Middleware
app.use(cors());
app.use(helmet());
app.use(express.json());

// Rate limiting
const limiter = rateLimit({
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 900000, // 15 minutes
    max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100
});
app.use(limiter);

// Auth middleware
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.status(401).json({ error: 'Authentication required' });
    }

    jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ error: 'Invalid or expired token' });
        }
        req.user = user;
        next();
    });
};

// Import routes
const airdropsRouter = require('./routes/airdrops');
app.use('/api/airdrops', airdropsRouter);

// Auth routes
app.post('/api/auth/nonce', async (req, res) => {
    const { address } = req.body;
    if (!ethers.isAddress(address)) {
        return res.status(400).json({ error: 'Invalid wallet address' });
    }

    const nonce = Math.floor(Math.random() * 1000000).toString();
    
    db.run('INSERT OR REPLACE INTO users (wallet_address, nonce) VALUES (?, ?)',
        [address, nonce],
        (err) => {
            if (err) {
                return res.status(500).json({ error: 'Database error' });
            }
            res.json({ nonce });
        }
    );
});

app.post('/api/auth/verify', async (req, res) => {
    const { address, signature } = req.body;
    
    if (!ethers.isAddress(address)) {
        return res.status(400).json({ error: 'Invalid wallet address' });
    }

    db.get('SELECT nonce FROM users WHERE wallet_address = ?',
        [address],
        async (err, row) => {
            if (err || !row) {
                return res.status(400).json({ error: 'Invalid request' });
            }

            try {
                const message = `Sign this message to verify your wallet. Nonce: ${row.nonce}`;
                const recoveredAddress = ethers.verifyMessage(message, signature);

                if (recoveredAddress.toLowerCase() === address.toLowerCase()) {
                    const token = jwt.sign({ address }, process.env.JWT_SECRET, { expiresIn: '24h' });
                    
                    // Update last login
                    db.run('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE wallet_address = ?',
                        [address]
                    );

                    res.json({ token });
                } else {
                    res.status(401).json({ error: 'Invalid signature' });
                }
            } catch (error) {
                res.status(400).json({ error: 'Signature verification failed' });
            }
        }
    );
});

// Error handling
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
