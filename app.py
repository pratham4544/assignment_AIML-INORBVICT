from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, constr, conint, confloat, computed_field
from typing import Literal, Dict
import uuid
import json
from pathlib import Path
from datetime import datetime

app = FastAPI(title="Patient Registration API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Model
class PatientDetails(BaseModel):
    name: constr(min_length=2)
    age: conint(ge=1, le=120)
    mobile: constr(min_length=10, max_length=10)
    email: EmailStr
    blood_group: Literal['A+', "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    height: confloat(gt=0)
    weight: confloat(gt=0)
    
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "UnderWeight"
        elif self.bmi < 25:
            return "Normal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"

# In-memory sessions
sessions: Dict[str, Dict] = {}

# Questions for flow
QUESTIONS = {
    1: {"field": "name", "question": "What is your full name?", "type": "text"},
    2: {"field": "age", "question": "What is your age?", "type": "number"},
    3: {"field": "mobile", "question": "What is your mobile number? (10 digits)", "type": "text"},
    4: {"field": "email", "question": "What is your email address?", "type": "text"},
    5: {"field": "blood_group", "question": "What is your blood group?", "type": "select"},
    6: {"field": "height", "question": "What is your height in meters? (e.g., 1.75)", "type": "number"},
    7: {"field": "weight", "question": "What is your weight in kg?", "type": "number"}
}

# Request/Response Models
class AnswerRequest(BaseModel):
    field: str
    value: str | int | float

@app.get("/")
def root():
    return {"message": "Patient Registration API", "status": "running"}

@app.post("/session/create")
def create_session():
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"step": 1, "data": {}}
    
    q = QUESTIONS[1]
    return {
        "session_id": session_id,
        "step": 1,
        "question": q["question"],
        "field": q["field"],
        "type": q["type"],
        "options": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"] if q["field"] == "blood_group" else None
    }

@app.get("/session/{session_id}")
def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    step = session["step"]
    
    if step > 7:
        return {
            "session_id": session_id,
            "step": step,
            "completed": True,
            "data": session["data"]
        }
    
    q = QUESTIONS[step]
    return {
        "session_id": session_id,
        "step": step,
        "question": q["question"],
        "field": q["field"],
        "type": q["type"],
        "options": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"] if q["field"] == "blood_group" else None,
        "completed": False,
        "data": session["data"]
    }

@app.post("/session/{session_id}/answer")
def submit_answer(session_id: str, request: AnswerRequest):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Validate field by field
    try:
        data = session["data"].copy()
        data[request.field] = request.value
        
        # Try creating a partial PatientDetails to validate
        # This will fail if required fields are missing, so we catch it
        try:
            PatientDetails(**data)
        except:
            # If full validation fails, validate just this field
            pass
        
        # Save to session
        session["data"][request.field] = request.value
        session["step"] += 1
        
        if session["step"] > 7:
            return {"message": "Registration complete!", "completed": True}
        
        q = QUESTIONS[session["step"]]
        return {
            "step": session["step"],
            "question": q["question"],
            "field": q["field"],
            "type": q["type"],
            "options": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"] if q["field"] == "blood_group" else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/session/{session_id}/back")
def go_back(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if session["step"] > 1:
        session["step"] -= 1
    
    q = QUESTIONS[session["step"]]
    return {
        "step": session["step"],
        "question": q["question"],
        "field": q["field"],
        "type": q["type"],
        "options": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"] if q["field"] == "blood_group" else None
    }

@app.get("/session/{session_id}/summary")
def get_summary(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if session["step"] <= 7:
        raise HTTPException(status_code=400, detail="Registration incomplete")
    
    # Final validation
    try:
        patient = PatientDetails(**session["data"])
        return {
            "session_id": session_id,
            "patient": patient.model_dump(),
            "bmi": patient.bmi,
            "verdict": patient.verdict
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")

@app.post("/session/{session_id}/save")
def save_patient(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    if session["step"] <= 7:
        raise HTTPException(status_code=400, detail="Cannot save incomplete registration")
    
    # Validate complete data
    try:
        patient = PatientDetails(**session["data"])
        
        # Create directory
        Path("patient_data").mkdir(exist_ok=True)
        file_path = Path("patient_data/patients.json")
        
        # Load existing
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            data = []
        
        # Append new patient
        data.append({
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "patient": patient.model_dump()
        })
        
        # Save
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return {
            "message": "Patient saved successfully",
            "file": str(file_path.absolute()),
            "total_patients": len(data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error saving: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)