from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from ..config import db
from ..utils.resume_parser import parse_resume
from ..nlp_engine import extract_skills, calculate_ats_score, recommend_internships

router = APIRouter()

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

class ApplicationCreateRequest(BaseModel):
    internship_id: str

# ----- Helper Functions -----
def get_current_user(token: str = Depends(auth_scheme)):
    # Placeholder for token verification
    # In a real implementation, decode JWT and fetch user from DB
    raise HTTPException(status_code=401, detail="Authentication required")

# ----- Auth Endpoints -----
@router.post("/register", response_model=LoginResponse)
async def register_user(payload: RegisterRequest):
    if db.students_collection.find_one({"email": payload.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    # Password hashing omitted for brevity; store plain for now (replace with bcrypt)
    user = payload.dict()
    user["password"] = payload.password
    user["skills"] = []
    user["resumeText"] = ""
    user["atsScore"] = 0.0
    db.students_collection.insert_one(user)
    # Return dummy token
    return {"access_token": "dummy-token", "token_type": "bearer"}

@router.post("/login", response_model=LoginResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.students_collection.find_one({"email": form_data.username})
    if not user or user.get("password") != form_data.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"access_token": "dummy-token", "token_type": "bearer"}

# ----- Resume Upload -----
@router.post("/upload-resume", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...), token: str = Depends(auth_scheme)):
    # In real scenario, verify token and fetch user ID
    content = await file.read()
    text = parse_resume(file.filename, content)
    skills = extract_skills(text)
    ats = calculate_ats_score(text, skills)
    # Update user record (placeholder ID)
    db.students_collection.update_one({"email": "dummy@example.com"}, {"$set": {"resumeText": text, "skills": skills, "atsScore": ats}})
    return {"skills": skills, "ats_score": ats}

# ----- Internship Endpoints -----
@router.post("/create-internship")
async def create_internship(payload: InternshipCreateRequest, token: str = Depends(auth_scheme)):
    # Verify admin token in real implementation
    internship = payload.dict()
    internship["matchScore"] = 0
    db.internships_collection.insert_one(internship)
    return {"detail": "Internship created"}

@router.get("/recommended-internships")
async def get_recommendations(token: str = Depends(auth_scheme)):
    # Placeholder: fetch current user
    user = db.students_collection.find_one({"email": "dummy@example.com"})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    recommendations = recommend_internships(user)
    return recommendations

@router.post("/apply")
async def apply_internship(payload: ApplicationCreateRequest, token: str = Depends(auth_scheme)):
    # Placeholder user ID
    application = {
        "studentId": "dummy_student_id",
        "internshipId": payload.internship_id,
        "status": "Applied",
        "matchScore": 0,
    }
    db.applications_collection.insert_one(application)
    return {"detail": "Application submitted"}

@router.get("/applications")
async def view_applications(token: str = Depends(auth_scheme)):
    # Return all applications for admin (placeholder)
    apps = list(db.applications_collection.find())
    return apps
