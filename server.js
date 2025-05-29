import express from 'express';
import { MongoClient } from 'mongodb';
import cors from 'cors';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const mongoClient = new MongoClient('mongodb://localhost:27017');
const db = mongoClient.db('instructor');

app.post('/api/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    const collection = db.collection('access_students');
    const user = await collection.findOne({ username });

    if (!user || !bcrypt.compareSync(password, user.password)) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = jwt.sign({ username }, process.env.JWT_SECRET || 'your-secret-key', {
      expiresIn: '24h'
    });

    res.json({ token, user: { username, tokens: user.tokens, ai_tokens: user.ai_tokens } });
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

app.listen(5000, () => {
  console.log('Server running on port 5000');
});