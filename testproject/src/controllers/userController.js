const User = require('../models/User'); // Assuming there's a User model

// ADDED: Controller to handle fetching users
exports.getUsers = async (req, res) => {
  try {
    const users = await User.find(); // Fetch users from the database
    res.status(200).json({ users });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Internal Server Error - Unexpected error' }); // ADDED: Error handling
  }
};