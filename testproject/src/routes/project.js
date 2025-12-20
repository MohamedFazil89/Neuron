// src/routes/project.js
const express = require('express');
const router = express.Router();
const projectController = require('../controllers/projectController');

// ADDED: Endpoint to retrieve project status
router.get('/status', projectController.getProjectStatus);

module.exports = router;
