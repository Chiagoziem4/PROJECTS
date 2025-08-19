const express = require('express');
const router = express.Router();
const { check, validationResult } = require('express-validator');
const sqlite3 = require('sqlite3').verbose();
const { authenticateToken } = require('../utils/auth');

// Database connection
const db = new sqlite3.Database(process.env.DATABASE_URL || '../data/airdrops.db');

// Input validation middleware
const validateAirdrop = [
    check('project_name').notEmpty().trim(),
    check('chain').notEmpty().trim(),
    check('eligibility_rules').notEmpty(),
    check('status').isIn(['upcoming', 'active', 'ended']),
    check('risk_score').isInt({ min: 1, max: 10 })
];

// Get all airdrops with filtering
router.get('/', async (req, res) => {
    const {
        chain,
        status,
        search,
        page = 1,
        limit = 10
    } = req.query;

    let query = 'SELECT * FROM airdrops WHERE 1=1';
    const params = [];

    if (chain) {
        query += ' AND chain = ?';
        params.push(chain);
    }

    if (status) {
        query += ' AND status = ?';
        params.push(status);
    }

    if (search) {
        query += ' AND (project_name LIKE ? OR description LIKE ?)';
        params.push(`%${search}%`, `%${search}%`);
    }

    const offset = (page - 1) * limit;
    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?';
    params.push(limit, offset);

    db.all(query, params, (err, rows) => {
        if (err) {
            console.error('Database error:', err);
            return res.status(500).json({ error: 'Database error' });
        }
        res.json(rows);
    });
});

// Get single airdrop
router.get('/:id', (req, res) => {
    const { id } = req.params;

    db.get('SELECT * FROM airdrops WHERE id = ?', [id], (err, row) => {
        if (err) {
            return res.status(500).json({ error: 'Database error' });
        }
        if (!row) {
            return res.status(404).json({ error: 'Airdrop not found' });
        }
        res.json(row);
    });
});

// Add new airdrop (protected route)
router.post('/',
    authenticateToken,
    validateAirdrop,
    (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ errors: errors.array() });
        }

        const {
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
        } = req.body;

        const query = `
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `;

        db.run(query,
            [
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
            ],
            function(err) {
                if (err) {
                    console.error('Error adding airdrop:', err);
                    return res.status(500).json({ error: 'Database error' });
                }
                res.status(201).json({
                    id: this.lastID,
                    message: 'Airdrop added successfully'
                });
            }
        );
    }
);

// Update airdrop status (protected route)
router.patch('/:id/status',
    authenticateToken,
    [check('status').isIn(['upcoming', 'active', 'ended'])],
    (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ errors: errors.array() });
        }

        const { id } = req.params;
        const { status } = req.body;

        db.run('UPDATE airdrops SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            [status, id],
            function(err) {
                if (err) {
                    return res.status(500).json({ error: 'Database error' });
                }
                if (this.changes === 0) {
                    return res.status(404).json({ error: 'Airdrop not found' });
                }
                res.json({ message: 'Status updated successfully' });
            }
        );
    }
);

// Add to watchlist (protected route)
router.post('/:id/watchlist',
    authenticateToken,
    (req, res) => {
        const { id } = req.params;
        const wallet_address = req.user.address;

        db.run('INSERT INTO watchlist (wallet_address, airdrop_id) VALUES (?, ?)',
            [wallet_address, id],
            function(err) {
                if (err) {
                    if (err.code === 'SQLITE_CONSTRAINT') {
                        return res.status(400).json({ error: 'Already in watchlist' });
                    }
                    return res.status(500).json({ error: 'Database error' });
                }
                res.status(201).json({ message: 'Added to watchlist' });
            }
        );
    }
);

// Get watchlist for user (protected route)
router.get('/watchlist/user',
    authenticateToken,
    (req, res) => {
        const wallet_address = req.user.address;

        db.all(`
            SELECT a.* FROM airdrops a
            JOIN watchlist w ON w.airdrop_id = a.id
            WHERE w.wallet_address = ?
            ORDER BY a.created_at DESC
        `,
        [wallet_address],
        (err, rows) => {
            if (err) {
                return res.status(500).json({ error: 'Database error' });
            }
            res.json(rows);
        });
    }
);

module.exports = router;
