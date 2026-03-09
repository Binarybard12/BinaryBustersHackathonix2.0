const express = require('express');
const path = require('path');
const axios = require('axios');
const helmet = require('helmet');
const compression = require('compression');
const cookieParser = require('cookie-parser');
const multer = require('multer');
const FormData = require('form-data');
require('dotenv').config();

const upload = multer({ storage: multer.memoryStorage() });

const app = express();
const PORT = process.env.PORT || 3000;
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000/api';

// Express config
app.use(compression());
app.use(helmet({
  contentSecurityPolicy: false, // Disable for demo to allow CDNs etc.
}));
app.use(cookieParser());
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Global locals for EJS
app.use((req, res, next) => {
    res.locals.isAuthenticated = !!req.cookies.token;
    res.locals.error = null;
    res.locals.message = null;
    next();
});

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
  res.render('landing', { title: 'Smart Internship Portal | Match Your Skills', isAuthenticated: !!req.cookies.token });
});

app.get('/login', (req, res) => {
  res.render('login', { title: 'Student Login', error: null, isAuthenticated: false });
});

app.post('/login', async (req, res) => {
    try {
        const params = new URLSearchParams();
        params.append('username', req.body.email);
        params.append('password', req.body.password);

        const response = await axios.post(`${BACKEND_URL}/login`, params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });

        res.cookie('token', response.data.access_token, { httpOnly: true });
        res.redirect('/dashboard');
    } catch (error) {
        res.render('login', { title: 'Student Login', error: 'Invalid email or password' });
    }
});

app.get('/register', (req, res) => {
    res.render('register', { title: 'Create Account', error: null });
});

app.post('/register', async (req, res) => {
    try {
        const response = await axios.post(`${BACKEND_URL}/register`, req.body);
        res.cookie('token', response.data.access_token, { httpOnly: true });
        res.redirect('/dashboard');
    } catch (error) {
        res.render('register', { title: 'Create Account', error: error.response?.data?.detail || 'Registration failed' });
    }
});

app.get('/dashboard', async (req, res) => {
  try {
    const token = req.cookies.token || 'dummy-token';
    const userRes = await axios.get(`${BACKEND_URL}/user/profile`, { headers: { Authorization: `Bearer ${token}` } });
    const internshipsRes = await axios.get(`${BACKEND_URL}/recommended-internships`, { headers: { Authorization: `Bearer ${token}` } });
    
    // Fallback if no recommendations
    let internships = internshipsRes.data;
    if (!internships || internships.length === 0) {
      const allInternships = await axios.get(`${BACKEND_URL}/internships`);
      internships = allInternships.data || mockInternships;
    }

    res.render('dashboard', { 
      title: 'Student Dashboard',
      user: userRes.data || mockUser,
      internships: internships.slice(0, 3),
      isAuthenticated: true
    });
  } catch (error) {
    console.error("Dashboard API error:", error.message);
    res.render('dashboard', { 
      title: 'Student Dashboard',
      user: mockUser,
      internships: mockInternships.slice(0, 3),
      isAuthenticated: !!req.cookies.token
    });
  }
});

app.get('/upload-resume', (req, res) => {
  res.render('upload_resume', { title: 'Upload Your Resume', message: null, isAuthenticated: !!req.cookies.token });
});

app.post('/upload-resume', upload.single('resume'), async (req, res) => {
    try {
        const token = req.cookies.token;
        if (!token) return res.redirect('/login');

        const formData = new FormData();
        formData.append('file', req.file.buffer, {
            filename: req.file.originalname,
            contentType: req.file.mimetype,
        });

        await axios.post(`${BACKEND_URL}/upload-resume`, formData, {
            headers: {
                ...formData.getHeaders(),
                'Authorization': `Bearer ${token}`
            }
        });

        res.render('upload_resume', { title: 'Upload Your Resume', message: 'Resume uploaded and analyzed successfully!' });
    } catch (error) {
        console.error("Upload error:", error.message);
        res.render('upload_resume', { title: 'Upload Your Resume', message: 'Error uploading resume.' });
    }
});

app.get('/logout', (req, res) => {
    res.clearCookie('token');
    res.redirect('/');
});

app.get('/internship-listings', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/internships`);
    res.render('internships', { 
      title: 'Internship Listings',
      internships: response.data || mockInternships,
      isAuthenticated: !!req.cookies.token
    });
  } catch (error) {
    console.error("Internships API error:", error.message);
    res.render('internships', { 
      title: 'Internship Listings',
      internships: mockInternships
    });
  }
});

app.get('/admin', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/admin/stats`);
    res.render('admin_dashboard', { 
      title: 'Admin Dashboard',
      stats: response.data,
      isAuthenticated: !!req.cookies.token
    });
  } catch (error) {
    console.error("Admin API error:", error.message);
    res.render('admin_dashboard', { 
      title: 'Admin Dashboard',
      stats: { totalStudents: 450, totalInternships: 85, totalApplications: 1240 }
    });
  }
});

app.get('/admin/create-internship', (req, res) => {
    res.render('create_internship', { title: 'Create New Internship' });
});

app.post('/admin/create-internship', async (req, res) => {
    try {
        const payload = {
            title: req.body.title,
            company: req.body.company,
            description: req.body.description,
            requiredSkills: req.body.requiredSkills.split(',').map(s => s.trim()),
            keywords: [],
            location: req.body.location,
            duration: req.body.duration,
            admin_id: "dummy-admin"
        };
        await axios.post(`${BACKEND_URL}/create-internship`, payload, {
            headers: { Authorization: `Bearer admin-token` }
        });
        res.redirect('/admin');
    } catch (error) {
        console.error("Create internship error:", error.message);
        res.redirect('/admin/create-internship');
    }
});

// Start Server
app.listen(PORT, () => {
  console.log(`Frontend running at http://localhost:${PORT}`);
});
