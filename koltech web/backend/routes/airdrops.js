const express = require('express');
const router = express.Router();
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const db = new sqlite3.Database(path.join(__dirname, '../../data/airdrops.db'));

// Get all airdrops with filtering
router.get('/', (req, res) => {
    const { chain, status, page = 1, limit = 10 } = req.query;
    const offset = (page - 1) * limit;
    
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
    
    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?';
    params.push(limit, offset);
    
    db.all(query, params, (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json(rows);
    });
});

// Get single airdrop by ID
router.get('/:id', (req, res) => {
    const { id } = req.params;
    
    db.get('SELECT * FROM airdrops WHERE id = ?', [id], (err, row) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        if (!row) {
            res.status(404).json({ error: 'Airdrop not found' });
            return;
        }
        res.json(row);
    });
});

// Create new airdrop (protected by API key)
router.post('/', (req, res) => {
    const apiKey = req.headers['x-api-key'];
    if (apiKey !== process.env.API_KEY) {
        res.status(401).json({ error: 'Unauthorized' });
        return;
    }
    
    const {
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
    } = req.body;
    
    const query = `
        INSERT INTO airdrops (
            project_name, chain, token_symbol, description,
            eligibility_rules, official_url, status,
            start_date, end_date, risk_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;
    
    db.run(query, [
        project_name, chain, token_symbol, description,
        eligibility_rules, official_url, status,
        start_date, end_date, risk_score
    ], function(err) {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.status(201).json({
            id: this.lastID,
            message: 'Airdrop created successfully'
        });
    });
});

// Update airdrop status
router.patch('/:id/status', (req, res) => {
    const apiKey = req.headers['x-api-key'];
    if (apiKey !== process.env.API_KEY) {
        res.status(401).json({ error: 'Unauthorized' });
        return;
    }
    
    const { id } = req.params;
    const { status } = req.body;
    
    if (!['open', 'closed', 'upcoming'].includes(status)) {
        res.status(400).json({ error: 'Invalid status' });
        return;
    }
    
    db.run(
        'UPDATE airdrops SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        [status, id],
        (err) => {
            if (err) {
                res.status(500).json({ error: err.message });
                return;
            }
            res.json({ message: 'Status updated successfully' });
        }
    );
});

module.exports = router;
