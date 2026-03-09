const express = require('express');
const path = require('path');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000/api';

// Express config
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Mock data (replace with API calls to backend)
const mockInternships = [
  { id: 1, title: 'Frontend Developer', company: 'Google', location: 'Remote', matchScore: 85, skills: ['React', 'JavaScript', 'HTML', 'CSS'] },
  { id: 2, title: 'Backend Developer', company: 'Amazon', location: 'London', matchScore: 78, skills: ['Node.js', 'Python', 'AWS'] },
  { id: 3, title: 'AI Developer', company: 'DeepMind', location: 'Remote', matchScore: 92, skills: ['Python', 'Machine Learning', 'spaCy'] },
  { id: 4, title: 'Fullstack Intern', company: 'Meta', location: 'New York', matchScore: 72, skills: ['React', 'Node.js', 'MongoDB'] },
];

const mockUser = {
  name: 'Richa Waghmare',
  email: 'richa@example.com',
  university: 'Imperial College',
  skills: ['Python', 'FastAPI', 'React', 'MongoDB'],
  atsScore: 78
};

// Routes
app.get('/', (req, res) => {
  res.render('landing', { title: 'Smart Internship Portal | Match Your Skills' });
});

app.get('/login', (req, res) => {
  res.render('login', { title: 'Student Login' });
});

app.get('/dashboard', (req, res) => {
  res.render('dashboard', { 
    title: 'Student Dashboard',
    user: mockUser,
    internships: mockInternships.slice(0, 3)
  });
});

app.get('/upload-resume', (req, res) => {
  res.render('upload_resume', { title: 'Upload Your Resume' });
});

app.get('/internship-listings', (req, res) => {
  res.render('internships', { 
    title: 'Internship Listings',
    internships: mockInternships
  });
});

app.get('/admin', (req, res) => {
    res.render('admin_dashboard', { 
      title: 'Admin Dashboard',
      stats: { totalStudents: 450, totalInternships: 85, totalApplications: 1240 }
    });
});

app.get('/admin/create-internship', (req, res) => {
    res.render('create_internship', { title: 'Create New Internship' });
});

// Start Server
app.listen(PORT, () => {
  console.log(`Frontend running at http://localhost:${PORT}`);
});
