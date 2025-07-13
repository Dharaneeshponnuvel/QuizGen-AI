const express = require('express');
const router = express.Router();
const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();
const auth = require('../middleware/auth');

router.get('/', auth('ADMIN'), async (req, res) => {
  try {
    const adminId = req.user.studentId;

    const quizzes = await prisma.quiz.findMany({
      where: { adminId },
      orderBy: { startAt: 'desc' },
      select: {
        id: true,
        title: true,
        startAt: true,
        endAt: true,
        status: true,
        adminId: true,
      },
    });

    res.json(quizzes);
  } catch (err) {
    console.error('Error fetching quizzes:', err);
    res.status(500).json({ error: 'Failed to fetch quizzes' });
  }
});

/**
 * GET /quizzes/:id
 * Returns detailed quiz info with all questions
 */
router.get('/:id', async (req, res) => {
  const quizId = parseInt(req.params.id, 10);

  if (isNaN(quizId)) {
    return res.status(400).json({ error: 'Invalid quiz ID format' });
  }

  try {
    const quiz = await prisma.quiz.findUnique({
      where: { id: quizId },
      include: {
        questions: {
          select: {
            body: true,
            options: true,
            correct: true,
          },
        },
      },
    });

    if (!quiz) {
      return res.status(404).json({ error: 'Quiz not found' });
    }

    res.json(quiz);
  } catch (err) {
    console.error('Error fetching quiz:', err);
    res.status(500).json({ error: 'Error retrieving quiz' });
  }
});

module.exports = router;
