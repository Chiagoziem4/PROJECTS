const validateAirdrop = (data) => {
    const errors = [];

    // Required fields
    const requiredFields = ['project_name', 'chain', 'status'];
    for (const field of requiredFields) {
        if (!data[field]) {
            errors.push(`${field} is required`);
        }
    }

    // Status validation
    if (data.status && !['open', 'closed', 'upcoming'].includes(data.status)) {
        errors.push('Invalid status value');
    }

    // Risk score validation
    if (data.risk_score !== undefined) {
        const score = parseInt(data.risk_score);
        if (isNaN(score) || score < 1 || score > 10) {
            errors.push('Risk score must be between 1 and 10');
        }
    }

    // URL validation
    if (data.official_url) {
        try {
            new URL(data.official_url);
        } catch (e) {
            errors.push('Invalid official URL format');
        }
    }

    // Date validation
    if (data.start_date && data.end_date) {
        const start = new Date(data.start_date);
        const end = new Date(data.end_date);
        
        if (isNaN(start.getTime())) {
            errors.push('Invalid start date format');
        }
        if (isNaN(end.getTime())) {
            errors.push('Invalid end date format');
        }
        if (start > end) {
            errors.push('End date must be after start date');
        }
    }

    return {
        isValid: errors.length === 0,
        errors
    };
};

const sanitizeInput = (input) => {
    if (typeof input !== 'string') return input;
    
    // Remove HTML tags
    input = input.replace(/<[^>]*>/g, '');
    
    // Convert special characters to HTML entities
    input = input
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    
    return input;
};

const sanitizeAirdropData = (data) => {
    const sanitized = {};
    
    for (const [key, value] of Object.entries(data)) {
        sanitized[key] = sanitizeInput(value);
    }
    
    return sanitized;
};

module.exports = {
    validateAirdrop,
    sanitizeInput,
    sanitizeAirdropData
};
