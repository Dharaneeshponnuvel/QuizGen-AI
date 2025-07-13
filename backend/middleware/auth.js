const jwt = require('jsonwebtoken');
const JWT_SECRET = process.env.JWT_SECRET;

function auth(requiredRole = null) {
  return function (req, res, next) {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ message: 'No token provided in Authorization header' });
    }

    const token = authHeader.split(' ')[1];

    try {
      const decoded = jwt.verify(token, JWT_SECRET);
      req.user = decoded; // decoded = { userId, studentId, role }

      // Role check (if requiredRole is specified)
      if (requiredRole && decoded.role !== requiredRole) {
        return res.status(403).json({ message: 'Forbidden: Insufficient permissions' });
      }

      next(); // Allow request to proceed
    } catch (err) {
      console.error('JWT verification error:', err.message);
      return res.status(401).json({ message: 'Invalid or expired token' });
    }
  };
}

module.exports = auth;
