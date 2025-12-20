// src/controllers/projectController.js
const projectModel = require('../models/projectModel');

// ADDED: Logic to get project status
exports.getProjectStatus = async (req, res) => {
    try {
        const projectStatus = await projectModel.getProjectStatus();
        res.status(200).json(projectStatus);
    } catch (error) {
        res.status(500).json({ message: 'Error retrieving project status' });
    }
};
