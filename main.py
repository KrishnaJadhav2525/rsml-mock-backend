from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
import time
import json
import os

app = FastAPI(
    title="RSML Mock Exam Practice Backend",
    description="Separate practice exam backend for RSML Online Exam application",
    version="1.0.0"
)

# Enable CORS for all mobile and web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "mock_data.json"

# In-memory storage with file persistence
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "exams": [
            {
                "id": 101,
                "exam_id": 101,
                "exam_name": "BSC CA - Computer Science Mock Practice Test",
                "subject": "Data Structures & Computer Applications",
                "start_time": "2026-09-24T00:00:00Z",
                "end_time": "2026-10-30T23:59:59Z",
                "duration_minutes": 60,
                "total_questions": 5,
                "status": "ONGOING",
                "passcode_required": True,
                "passcode": "123456"
            }
        ],
        "questions": {
            "101": [
                {
                    "id": 1,
                    "question_id": 1,
                    "question_text": "<p>What is the worst-case time complexity of searching an element in an unbalanced Binary Search Tree (BST)?</p>",
                    "options": [
                        {"id": "opt1_a", "label": "A", "text": "O(1)"},
                        {"id": "opt1_b", "label": "B", "text": "O(log n)"},
                        {"id": "opt1_c", "label": "C", "text": "O(n)"},
                        {"id": "opt1_d", "label": "D", "text": "O(n log n)"}
                    ]
                },
                {
                    "id": 2,
                    "question_id": 2,
                    "question_text": "<p>Evaluate the definite integral using standard calculus rules:</p><p>$$\\int_{0}^{2} (3x^2 + 2x) \\, dx$$</p>",
                    "options": [
                        {"id": "opt2_a", "label": "A", "text": "10"},
                        {"id": "opt2_b", "label": "B", "text": "12"},
                        {"id": "opt2_c", "label": "C", "text": "14"},
                        {"id": "opt2_d", "label": "D", "text": "16"}
                    ]
                },
                {
                    "id": 3,
                    "question_id": 3,
                    "question_text": "<p>In relational database management systems (RDBMS), which normal form eliminates transitive functional dependencies?</p>",
                    "options": [
                        {"id": "opt3_a", "label": "A", "text": "First Normal Form (1NF)"},
                        {"id": "opt3_b", "label": "B", "text": "Second Normal Form (2NF)"},
                        {"id": "opt3_c", "label": "C", "text": "Third Normal Form (3NF)"},
                        {"id": "opt3_d", "label": "D", "text": "Boyce-Codd Normal Form (BCNF)"}
                    ]
                },
                {
                    "id": 4,
                    "question_id": 4,
                    "question_text": "<p>Which of the following CPU scheduling algorithms in an Operating System is strictly non-preemptive?</p>",
                    "options": [
                        {"id": "opt4_a", "label": "A", "text": "Round Robin (RR)"},
                        {"id": "opt4_b", "label": "B", "text": "Shortest Job First (Non-Preemptive SJF)"},
                        {"id": "opt4_c", "label": "C", "text": "Shortest Remaining Time First (SRTF)"},
                        {"id": "opt4_d", "label": "D", "text": "Preemptive Priority Scheduling"}
                    ]
                },
                {
                    "id": 5,
                    "question_id": 5,
                    "question_text": "<p>In React Native, which hook is used to memoize expensive computations across re-renders?</p>",
                    "options": [
                        {"id": "opt5_a", "label": "A", "text": "useEffect"},
                        {"id": "opt5_b", "label": "B", "text": "useMemo"},
                        {"id": "opt5_c", "label": "C", "text": "useCallback"},
                        {"id": "opt5_d", "label": "D", "text": "useRef"}
                    ]
                }
            ]
        },
        "submissions": []
    }

DB = load_data()

def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DB, f, indent=2)
    except Exception:
        pass

# --- Pydantic Request Models ---
class LoginRequest(BaseModel):
    studentID: str
    password: str
    deviceId: Optional[str] = None
    deviceBrand: Optional[str] = None
    deviceModel: Optional[str] = None

class PasscodeRequest(BaseModel):
    exam_id: Any
    passcode: str

class SubmitRequest(BaseModel):
    exam_id: Any
    student_id: str
    responses: Dict[str, str] = Field(default_factory=dict)
    violation_count: int = 0
    submitBehavior: str = "normal"
    submitted_at: Optional[str] = None

class QuestionOption(BaseModel):
    id: str
    label: str
    text: str

class QuestionModel(BaseModel):
    id: Any
    question_id: Optional[Any] = None
    question_text: str
    options: List[QuestionOption]

class ExamModel(BaseModel):
    id: Any
    exam_id: Optional[Any] = None
    exam_name: str
    subject: Optional[str] = None
    start_time: str
    end_time: str
    duration_minutes: int
    total_questions: int
    status: str = "ONGOING"
    passcode_required: bool = False
    passcode: Optional[str] = None

# --- Mobile Application Endpoints (Matched 1:1) ---

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "RSML Mock Exam Backend",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_exams": len(DB["exams"]),
        "admin_docs": "/docs"
    }

@app.get("/api/mobile/server-time")
def get_server_time():
    now_ms = int(time.time() * 1000)
    return {
        "timestamp": now_ms,
        "iso": datetime.now(timezone.utc).isoformat()
    }

@app.post("/api/mobile/auth/login")
def student_login(payload: LoginRequest):
    # Mock backend accepts any student ID for practice testing
    sid = payload.studentID.strip() if payload.studentID else "2406319"
    return {
        "token": f"mock_jwt_session_{sid}_{int(time.time())}",
        "user": {
            "student_id": 687,
            "studentID": sid,
            "studentname": "KARANDE HARSHAD MAHADEV",
            "gender": "MALE",
            "course": {
                "class_id": 67,
                "class_name": "BSC CA - III"
            }
        }
    }

@app.post("/api/mobile/auth/logout")
def student_logout():
    return {"success": True, "message": "Logged out successfully"}

@app.get("/api/mobile/exams/today")
def get_today_exams():
    return DB["exams"]

@app.post("/api/mobile/exams/verify-passcode")
def verify_passcode(payload: PasscodeRequest):
    target_id = str(payload.exam_id)
    matched_exam = next((e for e in DB["exams"] if str(e.get("id")) == target_id or str(e.get("exam_id")) == target_id), None)
    
    if not matched_exam or not matched_exam.get("passcode_required"):
        return {"success": True, "valid": True}
    
    required_passcode = str(matched_exam.get("passcode", "")).strip()
    if payload.passcode.strip() == required_passcode or payload.passcode.strip() in ["123456", ""]:
        return {"success": True, "valid": True}
    
    raise HTTPException(status_code=400, detail={"success": False, "valid": False, "message": "Invalid passcode"})

@app.get("/api/online-exams/{exam_id}/questions")
def get_exam_questions(exam_id: str):
    questions = DB["questions"].get(str(exam_id))
    if not questions:
        # Fallback to first available question set
        first_key = next(iter(DB["questions"]), None)
        questions = DB["questions"][first_key] if first_key else []
    return questions

@app.post("/api/online-exams/{exam_id}/submit")
def submit_exam_responses(exam_id: str, payload: SubmitRequest):
    record = {
        "exam_id": exam_id,
        "student_id": payload.student_id,
        "responses": payload.responses,
        "violation_count": payload.violation_count,
        "submit_behavior": payload.submitBehavior,
        "submitted_at": payload.submitted_at or datetime.now(timezone.utc).isoformat(),
        "received_at": datetime.now(timezone.utc).isoformat()
    }
    DB["submissions"].append(record)
    save_data()
    return {
        "success": True,
        "message": "Exam responses recorded successfully",
        "exam_id": exam_id
    }

# --- Admin Endpoints (For Populating & Reviewing from Your Laptop) ---

@app.post("/api/admin/exams")
def admin_create_or_update_exam(exam: ExamModel):
    exam_dict = exam.model_dump()
    exam_dict["id"] = exam.id
    exam_dict["exam_id"] = exam.id
    
    existing_idx = next((i for i, e in enumerate(DB["exams"]) if str(e.get("id")) == str(exam.id)), None)
    if existing_idx is not None:
        DB["exams"][existing_idx] = exam_dict
    else:
        DB["exams"].append(exam_dict)
    
    save_data()
    return {"success": True, "message": f"Exam {exam.id} saved", "exam": exam_dict}

@app.post("/api/admin/exams/{exam_id}/questions")
def admin_upload_questions(exam_id: str, questions: List[QuestionModel]):
    q_list = [q.model_dump() for q in questions]
    DB["questions"][str(exam_id)] = q_list
    
    # Update total questions on matching exam
    matched = next((e for e in DB["exams"] if str(e.get("id")) == str(exam_id)), None)
    if matched:
        matched["total_questions"] = len(q_list)
    
    save_data()
    return {"success": True, "message": f"Uploaded {len(q_list)} questions for exam {exam_id}"}

@app.get("/api/admin/submissions")
def admin_view_submissions(exam_id: Optional[str] = None):
    if exam_id:
        return [s for s in DB["submissions"] if str(s["exam_id"]) == str(exam_id)]
    return DB["submissions"]

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)
