const express = require('express');
const authController = require('../controllers/authController');
const validateLogin = require('../middleware/validateLogin');

const router = express.Router();

// ADDED: User login route
router.post('/api/login', validateLogin, authController.login);

module.exports = router;