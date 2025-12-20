const User = require('../models/User');
const jwt = require('jsonwebtoken');

// ADDED: User login with email and password
exports.login = async (req, res) => {
    const { email, password } = req.body;

    // Validate request body
    if (!email || !password) {
        return res.status(400).json({ message: 'Email and password are required.' }); // ADDED: Validation error handling
    }

    try {
        const user = await User.findOne({ email }); // Check for user in database
        if (!user) {
            return res.status(401).json({ message: 'Unauthorized - user not found or password incorrect' }); // ADDED: User not found error
        }

        const isMatch = await user.comparePassword(password); // Compare provided password with stored hashed password
        if (!isMatch) {
            return res.status(401).json({ message: 'Unauthorized - user not found or password incorrect' }); // ADDED: Password mismatch error
        }

        const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: '1h' }); // Generate JWT token
        res.json({ token, user: { id: user._id, email: user.email } }); // Return token and user details
    } catch (error) {
        res.status(500).json({ message: 'Server error' }); // ADDED: General server error handling
    }
};