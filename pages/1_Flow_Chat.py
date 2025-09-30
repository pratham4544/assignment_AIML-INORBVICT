import streamlit as st
from pydantic import BaseModel, EmailStr, constr, conint, confloat, computed_field, ValidationError
from typing import Literal, Dict
import uuid
import json
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Flow Chat", page_icon="📝", layout="wide")

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

QUESTIONS = {
    1: {"field": "name", "question": "What is your full name?", "type": "text"},
    2: {"field": "age", "question": "What is your age?", "type": "number"},
    3: {"field": "mobile", "question": "What is your mobile number? (10 digits)", "type": "text"},
    4: {"field": "email", "question": "What is your email address?", "type": "text"},
    5: {"field": "blood_group", "question": "What is your blood group?", "type": "select"},
    6: {"field": "height", "question": "What is your height in meters? (e.g., 1.75)", "type": "number"},
    7: {"field": "weight", "question": "What is your weight in kg?", "type": "number"}
}

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'data' not in st.session_state:
    st.session_state.data = {}

def validate_field(field, value):
    try:
        data = {field: value}
        if field == "name":
            if len(value) < 2:
                return False, "Name must be at least 2 characters"
        elif field == "age":
            age = int(value)
            if not (1 <= age <= 120):
                return False, "Age must be between 1 and 120"
        elif field == "mobile":
            if len(value) != 10 or not value.isdigit():
                return False, "Mobile must be exactly 10 digits"
        elif field == "email":
            if '@' not in value or '.' not in value:
                return False, "Invalid email format"
        elif field == "height":
            height = float(value)
            if height <= 0:
                return False, "Height must be greater than 0"
        elif field == "weight":
            weight = float(value)
            if weight <= 0:
                return False, "Weight must be greater than 0"
        return True, "Valid"
    except:
        return False, "Invalid input"

def save_patient():
    try:
        patient = PatientDetails(**st.session_state.data)
        Path("patient_data").mkdir(exist_ok=True)
        file_path = Path("patient_data/patients.json")
        
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            data = []
        
        data.append({
            "session_id": st.session_state.session_id,
            "timestamp": datetime.now().isoformat(),
            "patient": patient.model_dump()
        })
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True, len(data)
    except Exception as e:
        return False, str(e)

st.title("Patient Registration")
st.write("Complete the form step by step")

step = st.session_state.step

if step <= 7:
    q = QUESTIONS[step]
    field = q["field"]
    question = q["question"]
    field_type = q["type"]
    
    st.progress((step - 1) / 7)
    st.subheader(f"Step {step} of 7")
    st.write(question)
    
    answer = None
    
    if field_type == "text":
        answer = st.text_input("Your answer:", key=f"input_{step}")
    elif field_type == "number":
        if field == "height":
            answer = st.number_input("Your answer:", min_value=0.0, max_value=3.0, step=0.01, format="%.2f", key=f"input_{step}")
        elif field == "weight":
            answer = st.number_input("Your answer:", min_value=0.0, max_value=300.0, step=0.1, format="%.1f", key=f"input_{step}")
        else:
            answer = st.number_input("Your answer:", min_value=1, max_value=120, key=f"input_{step}")
    elif field_type == "select":
        answer = st.selectbox("Your answer:", ['', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'], key=f"input_{step}")
        if not answer:
            answer = None
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if step > 1 and st.button("Back", use_container_width=True):
            st.session_state.step -= 1
            st.rerun()
    
    with col2:
        if st.button("Next", type="primary", use_container_width=True):
            if answer is not None and answer != '':
                is_valid, message = validate_field(field, answer)
                if is_valid:
                    st.session_state.data[field] = answer
                    st.session_state.step += 1
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please provide an answer")

else:
    st.success("Registration Complete")
    
    try:
        patient = PatientDetails(**st.session_state.data)
        patient_dict = patient.model_dump()
        
        st.subheader("Patient Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"Name: {patient_dict['name']}")
            st.write(f"Age: {patient_dict['age']}")
            st.write(f"Mobile: {patient_dict['mobile']}")
            st.write(f"Email: {patient_dict['email']}")
        
        with col2:
            st.write(f"Blood Group: {patient_dict['blood_group']}")
            st.write(f"Height: {patient_dict['height']} m")
            st.write(f"Weight: {patient_dict['weight']} kg")
            st.write(f"BMI: {patient.bmi}")
        
        verdict = patient.verdict
        if verdict == "Normal":
            st.success(f"Health Status: {verdict}")
        elif verdict == "UnderWeight":
            st.warning(f"Health Status: {verdict}")
        elif verdict == "Overweight":
            st.warning(f"Health Status: {verdict}")
        else:
            st.error(f"Health Status: {verdict}")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Save to File", use_container_width=True):
                success, result = save_patient()
                if success:
                    st.success("Data saved successfully")
                    st.info(f"Total patients: {result}")
                else:
                    st.error(f"Error saving: {result}")
        
        with col2:
            if st.button("New Registration", use_container_width=True):
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.step = 1
                st.session_state.data = {}
                st.rerun()
    
    except ValidationError as e:
        st.error("Validation error in patient data")
        st.write(e)