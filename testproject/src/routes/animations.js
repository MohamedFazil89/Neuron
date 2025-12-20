const express = require('express');
const router = express.Router();
const animationsController = require('../controllers/animationsController');

// ADDED: Create a route for fetching animations
router.get('/', animationsController.getAnimations);

module.exports = router;