const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');

// ADDED: Route to get user data
router.get('/api/users', userController.getUsers);

module.exports = router;