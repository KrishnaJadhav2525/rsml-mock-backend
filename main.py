from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
import time
import json
import os

app = FastAPI(
    title="RSML Mock Exam Practice Backend",
    description="Separate practice exam backend for RSML Online Exam application with device and session tracking",
    version="1.1.0"
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
                data = json.load(f)
                if "devices" not in data:
                    data["devices"] = {}
                return data
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
        "devices": {},
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
        "registered_phones": len(DB.get("devices", {})),
        "admin_dashboard": "/admin/devices",
        "swagger_docs": "/docs"
    }

@app.get("/api/mobile/server-time")
def get_server_time():
    now_ms = int(time.time() * 1000)
    return {
        "timestamp": now_ms,
        "iso": datetime.now(timezone.utc).isoformat()
    }

@app.post("/api/mobile/auth/login")
def student_login(payload: LoginRequest, request: Request):
    sid = payload.studentID.strip() if payload.studentID else "2406319"
    
    # Capture client IP (accounting for Render reverse proxies)
    client_ip = request.client.host if request.client else "unknown"
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    
    dev_id = (payload.deviceId or f"dev_{int(time.time())}").strip()
    now_str = datetime.now(timezone.utc).isoformat()
    
    # Record or update phone in device tracker
    if "devices" not in DB:
        DB["devices"] = {}
        
    if dev_id in DB["devices"]:
        d = DB["devices"][dev_id]
        d["last_seen"] = now_str
        d["student_id"] = sid
        d["ip_address"] = client_ip
        d["login_count"] = d.get("login_count", 1) + 1
        d["status"] = "Active / Logged In"
    else:
        DB["devices"][dev_id] = {
            "device_id": dev_id,
            "student_id": sid,
            "student_name": "KARANDE HARSHAD MAHADEV",
            "device_brand": payload.deviceBrand or "Android Device",
            "device_model": payload.deviceModel or "Android Mobile",
            "ip_address": client_ip,
            "first_seen": now_str,
            "last_seen": now_str,
            "login_count": 1,
            "status": "Active / Logged In"
        }
    
    save_data()

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
    
    # Update phone status
    if "devices" in DB:
        for d in DB["devices"].values():
            if d.get("student_id") == str(payload.student_id):
                d["last_seen"] = datetime.now(timezone.utc).isoformat()
                d["status"] = f"Submitted Exam #{exam_id}"
                
    save_data()
    return {
        "success": True,
        "message": "Exam responses recorded successfully",
        "exam_id": exam_id
    }

# --- Admin & Device Tracking Endpoints ---

@app.get("/api/admin/devices")
def admin_get_devices():
    return list(DB.get("devices", {}).values())

@app.delete("/api/admin/devices/{device_id}")
def admin_delete_device(device_id: str):
    if "devices" in DB and device_id in DB["devices"]:
        deleted = DB["devices"].pop(device_id)
        save_data()
        return {"success": True, "message": f"Device {device_id} removed", "device": deleted}
    raise HTTPException(status_code=404, detail="Device not found")

@app.get("/admin/devices", response_class=HTMLResponse)
def admin_devices_web_dashboard():
    devices = list(DB.get("devices", {}).values())
    total_devs = len(devices)
    total_subs = len(DB.get("submissions", []))
    
    rows_html = ""
    for idx, d in enumerate(devices, 1):
        status_color = "#10b981" if "Active" in d.get("status", "") else "#6366f1"
        rows_html += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">{idx}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;"><strong>{d.get('student_id')}</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">{d.get('device_brand', 'Android')} - <strong>{d.get('device_model', 'Phone')}</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; font-family: monospace; font-size: 12px;">{d.get('device_id')}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; font-family: monospace;">{d.get('ip_address')}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;"><span style="background: {status_color}20; color: {status_color}; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px;">{d.get('status', 'Online')}</span></td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; font-size: 13px; color: #6b7280;">{d.get('last_seen', '').replace('T', ' ')[:19]}</td>
            <td style="padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: center;">{d.get('login_count', 1)}</td>
        </tr>
        """
        
    if not rows_html:
        rows_html = """<tr><td colspan="8" style="text-align: center; padding: 30px; color: #9ca3af;">No student phones registered yet. Once students open and log into the app, their devices will automatically appear here.</td></tr>"""

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>RSML App Device & Session Monitor</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f3f4f6; margin: 0; padding: 24px; color: #1f2937; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }}
            .card {{ background: #fff; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 24px; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
            .stat-box {{ background: #fff; padding: 20px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            .stat-val {{ font-size: 28px; font-weight: bold; color: #023c69; margin-top: 4px; }}
            table {{ width: 100%; border-collapse: collapse; text-align: left; }}
            th {{ padding: 12px; background: #f9fafb; font-weight: 600; color: #4b5563; font-size: 13px; text-transform: uppercase; border-bottom: 2px solid #e5e7eb; }}
            .refresh-btn {{ background: #023c69; color: #fff; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div>
                    <h1 style="margin: 0; color: #023c69;">📱 Student Phone & Device Monitor</h1>
                    <p style="margin: 4px 0 0 0; color: #6b7280;">Real-time device tracking for RSML Online Exam App</p>
                </div>
                <div>
                    <a href="/admin/devices" class="refresh-btn">🔄 Refresh</a>
                    <a href="/docs" class="refresh-btn" style="background: #4b5563; margin-left: 8px;">⚙️ API Docs</a>
                </div>
            </div>

            <div class="stats-grid">
                <div class="stat-box">
                    <div style="color: #6b7280; font-size: 13px; font-weight: 600;">INSTALLED PHONES</div>
                    <div class="stat-val">{total_devs}</div>
                </div>
                <div class="stat-box">
                    <div style="color: #6b7280; font-size: 13px; font-weight: 600;">ACTIVE EXAMS</div>
                    <div class="stat-val">{len(DB.get('exams', []))}</div>
                </div>
                <div class="stat-box">
                    <div style="color: #6b7280; font-size: 13px; font-weight: 600;">SUBMISSIONS RECORDED</div>
                    <div class="stat-val">{total_subs}</div>
                </div>
            </div>

            <div class="card" style="padding: 0; overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Student ID</th>
                            <th>Phone Brand & Model</th>
                            <th>Unique Installation ID</th>
                            <th>Client IP</th>
                            <th>Session Status</th>
                            <th>Last Active</th>
                            <th style="text-align: center;">Logins</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

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
