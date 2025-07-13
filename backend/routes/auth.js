const express = require('express');
const router = express.Router();
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();
const JWT_SECRET = process.env.JWT_SECRET;

// Register (for both admin and student)
router.post('/register', async (req, res) => {
  const { name, email, studentId, password, role } = req.body;

  try {
    const existingUser = await prisma.user.findUnique({
      where: { email },
    });
    if (existingUser) return res.status(400).json({ message: 'User already exists' });

    const hashedPassword = await bcrypt.hash(password, 10);
    const user = await prisma.user.create({
      data: {
        name,
        email,
        studentId,
        password: hashedPassword,
        role: role === 'ADMIN' ? 'ADMIN' : 'STUDENT',
      },
    });

    res.status(201).json({ message: 'User registered', user: { id: user.id, role: user.role } });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Registration failed' });
  }
});

// Login (by studentId or email)
router.post('/login', async (req, res) => {
  const { studentId, email, password } = req.body;

  try {
    const user = await prisma.user.findFirst({
      where: {
        OR: [{ studentId }, { email }],
      },
    });

    if (!user) return res.status(404).json({ message: 'User not found' });

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) return res.status(401).json({ message: 'Invalid credentials' });

    const token = jwt.sign({ userId: user.id, role: user.role }, JWT_SECRET, {
      expiresIn: '3h',
    });

    res.json({
      message: 'Login successful',
      token,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        studentId: user.studentId,
        role: user.role,
      },
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Login failed' });
  }
});

module.exports = router;
