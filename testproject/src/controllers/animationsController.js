const animationsModel = require('../models/animationsModel');

// ADDED: Function to handle GET request for animations
exports.getAnimations = async (req, res) => {
    try {
        const animations = await animationsModel.getAnimations();
        res.json({ animations });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Internal server error' }); // ADDED: Error handling
    }
};