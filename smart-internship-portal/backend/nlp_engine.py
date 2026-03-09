import spacy
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from backend.config import db

# Load spaCy model (English)
# Ensure `python -m spacy download en_core_web_sm` is run
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # A fallback if it's not downloaded yet, though in prod it should be
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

SKILLS_DATABASE = {
    "python", "java", "react", "node.js", "mongodb", "machine learning",
    "data science", "html", "css", "javascript", "docker", "aws",
    "sql", "c++", "ruby", "django", "flask", "fastapi", "express",
    "git", "kubernetes", "typescript", "c#", "php"
}

def extract_skills(text: str) -> List[str]:
    """Extracts skills from text using spaCy and keyword matching."""
    doc = nlp(text.lower())
    extracted_skills = set()
    
    # Token matching
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]
    for token in tokens:
        if token in SKILLS_DATABASE:
            extracted_skills.add(token.capitalize())
            
    # Phrases matching (multi-word skills like 'machine learning')
    for skill in SKILLS_DATABASE:
        if " " in skill and skill in text.lower():
            extracted_skills.add(skill.title())
            
    return list(extracted_skills)

def calculate_ats_score(text: str, skills: List[str]) -> float:
    """Calculates a general ATS-style score based on completeness and keywords."""
    # Simplified version for demo
    score = 0.0
    
    # Skill match 40% (based on variety and quality)
    if len(skills) >= 5: score += 40.0
    elif len(skills) >= 2: score += 20.0
    
    # Keyword match 30% (TF-IDF keywords common in resumes)
    # Placeholder: mock keyword richness
    score += min(30.0, len(text.split()) / 100.0 * 5)
    
    # Resume completeness 20%
    if "education" in text.lower(): score += 5.0
    if "experience" in text.lower(): score += 5.0
    if "projects" in text.lower(): score += 5.0
    if "contact" in text.lower() or "email" in text.lower(): score += 5.0
    
    # Experience relevance 10%
    if "year" in text.lower() or "intern" in text.lower(): score += 10.0
    
    return round(min(100.0, score), 2)

def recommend_internships(user: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Matches user skills/ATS score against internship postings."""
    internships = list(db.internships_collection.find())
    recommendations = []
    
    user_skills = set([s.lower() for s in user.get("skills", [])])
    ats_score = user.get("atsScore", 0.0)
    
    for internship in internships:
        required_skills = set([s.lower() for s in internship.get("requiredSkills", [])])
        
        # Matching formula
        # Match Score = (Skills Matched / Required Skills) * 50 + Keyword Similarity * 30 + ATS Score * 20
        
        skill_match_ratio = 0
        if required_skills:
            intersection = user_skills.intersection(required_skills)
            skill_match_ratio = len(intersection) / len(required_skills)
            
        score = (skill_match_ratio * 50) + (ats_score / 100.0 * 20)
        # Keyword matching (placeholder for 30%)
        # Here we could use TF-IDF or cosine similarity
        score += 15.0 # Mocking Keyword Similarity
        
        internship["matchScore"] = round(score, 2)
        # Convert ObjectId
        internship["_id"] = str(internship["_id"])
        recommendations.append(internship)
        
    # Sort by match score descending
    recommendations.sort(key=lambda x: x["matchScore"], reverse=True)
    return recommendations
