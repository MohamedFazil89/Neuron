const User = require('../models/User');
const jwt = require('jsonwebtoken');

// ADDED: Login controller functionfvbef
exports.login = async (req, res) => {
    const { email, password } = req.body;
    try {
        const user = await User.findOne({ email });
        if (!user || !(await user.comparePassword(password))) {
            return res.status(400).json({ message: 'Invalid email or password' }); // ADDED: Error handling
        }
        const token = jwt.sign({ id: user._id, email: user.email }, process.env.JWT_SECRET, { expiresIn: '1h' });
        res.json({ token, user: { id: user._id, email: user.email } }); // ADDED: Successful response
    } catch (error) {
        res.status(500).json({ message: 'Internal server error' }); // ADDED: Error handling
    }
};