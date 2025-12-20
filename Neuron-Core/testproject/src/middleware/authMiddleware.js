const jwt = require('jsonwebtoken');

// ADDED: Middleware to protect routes
exports.verifyToken = (req, res, next) => {
    const token = req.headers['authorization'] && req.headers['authorization'].split(' ')[1];
    if (!token) {
        return res.status(403).json({ message: 'No token provided!' }); // ADDED: No token error
    }
    jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
        if (err) {
            return res.status(401).json({ message: 'Unauthorized!' }); // ADDED: Unauthorized error
        }
        req.userId = decoded.id;
        next();
    });
};