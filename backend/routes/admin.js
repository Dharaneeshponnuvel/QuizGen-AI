const express = require('express');
const router = express.Router();
const { PrismaClient } = require('@prisma/client');
const auth = require('../middleware/auth');

const prisma = new PrismaClient();

// GET /admin/quiz-count?adminId=22MIS7043
router.get('/quiz-count', auth('ADMIN'), async (req, res) => {
  const { adminId } = req.query;
  try {
    const count = await prisma.quiz.count({
      where: { adminId },
    });
    res.json({ count });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to fetch quiz count' });
  }
});

// GET /admin/quiz-score-graph?adminId=22MIS7043
router.get('/quiz-score-graph', auth('ADMIN'), async (req, res) => {
  const { adminId } = req.query;
  try {
    const quizzes = await prisma.quiz.findMany({
      where: { adminId },
      select: {
        id: true,
        title: true,
        attempts: {
          select: { score: true },
        },
      },
    });

    const graphData = quizzes.map(q => {
      const total = q.attempts.reduce((sum, a) => sum + a.score, 0);
      const avg = q.attempts.length ? total / q.attempts.length : 0;
      return { quizTitle: q.title, averageScore: Math.round(avg) };
    });

    res.json(graphData);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to fetch graph data' });
  }
});

// GET /admin/top-students?adminId=22MIS7043
router.get('/top-students', auth('ADMIN'), async (req, res) => {
  const { adminId } = req.query;

  try {
    const students = await prisma.attempt.findMany({
      where: {
        quiz: { adminId },
      },
      orderBy: { score: 'desc' },
      take: 5,
      select: {
        score: true,
        submittedAt: true,
        quiz: { select: { title: true } },
        user: {
          select: {
            studentId: true,
            name: true,
          },
        },
      },
    });

    const result = students.map(s => ({
      score: s.score,
      submittedAt: s.submittedAt,
      quizTitle: s.quiz.title,
      studentId: s.user.studentId,
      name: s.user.name,
    }));

    res.json(result);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Failed to fetch top students' });
  }
});

module.exports = router;
