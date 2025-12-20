const express = require('express');
const { login } = require('../controllers/authController');

const router = express.Router();

// ADDED: User login with email and password
router.post('/login', login);

module.exports = router;