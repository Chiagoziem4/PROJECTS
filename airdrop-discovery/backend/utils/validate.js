const { check } = require('express-validator');
const ethers = require('ethers');

// Common validation chains
const validators = {
    // Wallet address validation
    walletAddress: check('address')
        .notEmpty()
        .custom(value => {
            if (!ethers.isAddress(value)) {
                throw new Error('Invalid wallet address');
            }
            return true;
        }),

    // Airdrop input validation
    airdropInput: [
        check('project_name')
            .notEmpty()
            .trim()
            .isLength({ min: 2, max: 100 })
            .withMessage('Project name must be between 2 and 100 characters'),

        check('chain')
            .notEmpty()
            .trim()
            .isIn(['Ethereum', 'Polygon', 'Optimism', 'Arbitrum', 'BSC'])
            .withMessage('Invalid chain'),

        check('token_symbol')
            .optional()
            .trim()
            .isLength({ min: 1, max: 10 })
            .withMessage('Token symbol must be between 1 and 10 characters'),

        check('description')
            .optional()
            .trim()
            .isLength({ max: 1000 })
            .withMessage('Description must not exceed 1000 characters'),

        check('eligibility_rules')
            .notEmpty()
            .trim()
            .isLength({ min: 10, max: 2000 })
            .withMessage('Eligibility rules must be between 10 and 2000 characters'),

        check('start_date')
            .optional()
            .isISO8601()
            .withMessage('Invalid start date format'),

        check('end_date')
            .optional()
            .isISO8601()
            .withMessage('Invalid end date format')
            .custom((value, { req }) => {
                if (req.body.start_date && value <= req.body.start_date) {
                    throw new Error('End date must be after start date');
                }
                return true;
            }),

        check('status')
            .isIn(['upcoming', 'active', 'ended'])
            .withMessage('Invalid status'),

        check('official_links')
            .optional()
            .custom(value => {
                if (typeof value === 'string') {
                    const links = value.split(',');
                    for (const link of links) {
                        try {
                            new URL(link.trim());
                        } catch {
                            throw new Error('Invalid URL in official links');
                        }
                    }
                }
                return true;
            }),

        check('risk_score')
            .isInt({ min: 1, max: 10 })
            .withMessage('Risk score must be between 1 and 10')
    ],

    // Comment validation
    commentInput: [
        check('content')
            .notEmpty()
            .trim()
            .isLength({ min: 1, max: 1000 })
            .withMessage('Comment must be between 1 and 1000 characters'),

        check('airdrop_id')
            .isInt({ min: 1 })
            .withMessage('Invalid airdrop ID')
    ],

    // Blog post validation
    blogPostInput: [
        check('title')
            .notEmpty()
            .trim()
            .isLength({ min: 5, max: 200 })
            .withMessage('Title must be between 5 and 200 characters'),

        check('content')
            .notEmpty()
            .trim()
            .isLength({ min: 50 })
            .withMessage('Content must be at least 50 characters'),

        check('slug')
            .optional()
            .trim()
            .matches(/^[a-z0-9-]+$/)
            .withMessage('Slug must contain only lowercase letters, numbers, and hyphens')
    ]
};

// Sanitization middleware
const sanitize = {
    // Remove potentially harmful HTML/scripts
    stripHtml: (value) => {
        if (typeof value !== 'string') return value;
        return value.replace(/<[^>]*>/g, '');
    },

    // Clean URLs
    cleanUrl: (url) => {
        try {
            const cleaned = new URL(url);
            return cleaned.toString();
        } catch {
            return '';
        }
    }
};

// Rate limiting helper
const createRateLimiter = (windowMs, max) => {
    return {
        windowMs: windowMs || 900000, // 15 minutes default
        max: max || 100, // limit each IP
        message: 'Too many requests from this IP, please try again later'
    };
};

module.exports = {
    validators,
    sanitize,
    createRateLimiter
};
