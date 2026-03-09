from backend.nlp_engine import extract_skills, calculate_ats_score

def test_extract_skills():
    resume_text = "Experienced software engineer with strong proficiency in Python, React, and Machine Learning."
    skills = extract_skills(resume_text)
    
    # Skills are capitalized based on NLP engine logic
    assert "Python" in skills
    assert "React" in skills
    assert "Machine Learning" in skills
    assert "Java" not in skills

def test_calculate_ats_score():
    resume_text = "I have 1 year of experience as an intern working on projects in education."
    skills = ["Python", "React", "Node.js", "Machine Learning", "MongoDB"]
    
    score = calculate_ats_score(resume_text, skills)
    
    # 5 skills gives 40
    # keywords logic adds some points based on length
    # experience (intern/year) adds 10, projects 5, education 5
    assert score > 50.0
    assert score <= 100.0
