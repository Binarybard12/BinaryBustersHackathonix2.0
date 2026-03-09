from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import db, students_collection, internships_collection, applications_collection, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from .utils.resume_parser import parse_resume
from .nlp_engine import extract_skills, calculate_ats_score, recommend_internships

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

# ----- Pydantic Schemas -----
class RegisterRequest(BaseModel):
    name: str = Field(..., example="John Doe")
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None
    university: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ResumeUploadResponse(BaseModel):
    skills: List[str]
    ats_score: float

class InternshipCreateRequest(BaseModel):
    title: str
    company: str
    description: str
    requiredSkills: List[str]
    keywords: List[str]
    location: str
    duration: str
    admin_id: Optional[str] = None

class ApplicationCreateRequest(BaseModel):
    internship_id: str

# ----- Helper Functions -----
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # For hackathon/demo, allow "dummy-token"
        if token == "dummy-token":
            user = students_collection.find_one({"email": "dummy@example.com"})
            if not user:
                 # Seed if missing
                 students_collection.insert_one({"name": "Richa Waghmare", "email": "dummy@example.com", "skills": [], "resumeText": "", "atsScore": 0.0})
                 user = students_collection.find_one({"email": "dummy@example.com"})
            return user

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = students_collection.find_one({"email": email})
    if user is None:
        raise credentials_exception
    return user

# ----- Auth Endpoints -----
@router.post("/register", response_model=LoginResponse)
async def register_user(payload: RegisterRequest):
    if students_collection.find_one({"email": payload.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(payload.password)
    user = payload.dict()
    user["password"] = hashed_password
    user["skills"] = []
    user["resumeText"] = ""
    user["atsScore"] = 0.0
    students_collection.insert_one(user)
    
    access_token = create_access_token(data={"sub": payload.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=LoginResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user = students_collection.find_one({"email": form_data.username})
    if not user or not pwd_context.verify(form_data.password, user.get("password", "")):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

# ----- Resume Upload -----
@router.post("/upload-resume", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    content = await file.read()
    text = parse_resume(file.filename, content)
    skills = extract_skills(text)
    ats = calculate_ats_score(text, skills)
    # Update user record
    students_collection.update_one({"_id": current_user["_id"]}, {"$set": {"resumeText": text, "skills": skills, "atsScore": ats}})
    return {"skills": skills, "ats_score": ats}

# ----- Internship Endpoints -----
@router.post("/create-internship")
async def create_internship(payload: InternshipCreateRequest, token: str = Depends(oauth_scheme)):
    # Verify admin token in real implementation
    internship = payload.dict()
    internship["matchScore"] = 0
    internships_collection.insert_one(internship)
    return {"detail": "Internship created"}

@router.get("/admin-internships/{admin_id}")
async def get_admin_internships(admin_id: str):
    """Get all internships created by a specific admin"""
    internships = list(internships_collection.find({"admin_id": admin_id}))
    if not internships:
        raise HTTPException(status_code=404, detail="No internships found for this admin")
    return {"admin_id": admin_id, "count": len(internships), "internships": internships}

@router.get("/recommended-internships")
async def get_recommendations(token: str = Depends(oauth_scheme)):
    # Placeholder: fetch current user
    user = students_collection.find_one({"email": "dummy@example.com"})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    recommendations = recommend_internships(user)
    return recommendations

@router.post("/apply")
async def apply_internship(payload: ApplicationCreateRequest, token: str = Depends(oauth_scheme)):
    # Placeholder user ID
    application = {
        "studentId": "dummy_student_id",
        "internshipId": payload.internship_id,
        "status": "Applied",
        "matchScore": 0,
    }
    applications_collection.insert_one(application)
    return {"detail": "Application submitted"}

@router.get("/applications")
async def view_applications(token: str = Depends(oauth_scheme)):
    # Return all applications for admin (placeholder)
    apps = list(applications_collection.find())
    return apps

@router.get("/internships")
async def list_internships():
    internships = list(internships_collection.find())
    
    # Auto-seed some data if DB is empty for the hackathon prototype
    if not internships:
        seed_data = [
            { "title": "Frontend Developer", "company": "Google", "location": "Remote", "duration": "3 Months", "requiredSkills": ["React", "JavaScript", "HTML", "CSS"], "matchScore": 85 },
            { "title": "Backend Developer", "company": "Amazon", "location": "London", "duration": "6 Months", "requiredSkills": ["Node.js", "Python", "AWS"], "matchScore": 78 },
            { "title": "AI Developer", "company": "DeepMind", "location": "Remote", "duration": "4 Months", "requiredSkills": ["Python", "Machine Learning", "spaCy"], "matchScore": 92 },
            { "title": "Fullstack Intern", "company": "Meta", "location": "New York", "duration": "6 Months", "requiredSkills": ["React", "Node.js", "MongoDB"], "matchScore": 72 }
        ]
        internships_collection.insert_many(seed_data)
        internships = list(internships_collection.find())
        
    for internship in internships:
        internship["_id"] = str(internship["_id"])
        if "skills" not in internship and "requiredSkills" in internship:
            # alias requiredSkills to skills to match frontend EJS
            internship["skills"] = internship["requiredSkills"]

    return internships

@router.get("/user/profile")
async def get_user_profile(token: str = Depends(oauth_scheme)):
    user = students_collection.find_one({"email": "dummy@example.com"})
    if not user:
        students_collection.insert_one({
            "name": "Richa Waghmare",
            "email": "dummy@example.com",
            "university": "Imperial College",
            "skills": ["Python", "FastAPI", "React", "MongoDB"],
            "atsScore": 78,
            "resumeText": ""
        })
        user = students_collection.find_one({"email": "dummy@example.com"})
    user["_id"] = str(user["_id"])
    # Do not expose password
    user.pop("password", None)
    return user

@router.get("/admin/stats")
async def get_admin_stats():
    total_students = students_collection.count_documents({})
    total_internships = internships_collection.count_documents({})
    total_applications = applications_collection.count_documents({})
    
    # default mock numbers for demo empty db
    if total_students == 0: total_students = 1
    if total_internships == 0: total_internships = 4
    if total_applications == 0: total_applications = 12

    return {
        "totalStudents": total_students,
        "totalInternships": total_internships,
        "totalApplications": total_applications
    }

