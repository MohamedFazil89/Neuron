// Import necessary modules
const express = require('express');
const router = express.Router();
const stylesController = require('../controllers/stylesController');

// ADDED: Create a route for fetching styles
router.get('/', stylesController.getStyles);

module.exports = router;