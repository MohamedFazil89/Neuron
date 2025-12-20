const { body, validationResult } = require('express-validator');

// ADDED: Middleware to validate login input
exports.validateLogin = [
    body('email').isEmail().withMessage('Invalid email format'),
    body('password').isLength({ min: 6 }).withMessage('Password must be at least 6 characters long'),
    (req, res, next) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ errors: errors.array() }); // ADDED: Error handling
        }
        next();
    }
];