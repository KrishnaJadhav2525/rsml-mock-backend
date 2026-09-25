import argparse
import urllib.request
import json
import sys

def upload_mock_exam(base_url: str, json_file: str):
    base = base_url.rstrip("/")
    if base.endswith("/api"):
        base = base[:-4]
    
    print(f"Reading mock exam from: {json_file}")
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    exam = data.get("exam")
    questions = data.get("questions", [])

    if not exam:
        print("Error: JSON must contain an 'exam' object.")
        sys.exit(1)

    exam_id = exam.get("id") or exam.get("exam_id")
    print(f"Target Render Backend: {base}")
    print(f"Uploading Exam #{exam_id}: '{exam.get('exam_name')}'...")

    # 1. Upload Exam metadata
    exam_url = f"{base}/api/admin/exams"
    req1 = urllib.request.Request(
        exam_url,
        data=json.dumps(exam).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req1) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            print("  Exam metadata saved successfully.")
    except Exception as e:
        print(f"  Error uploading exam: {e}")
        sys.exit(1)

    # 2. Upload Questions
    if questions:
        print(f"Uploading {len(questions)} questions for Exam #{exam_id}...")
        q_url = f"{base}/api/admin/exams/{exam_id}/questions"
        req2 = urllib.request.Request(
            q_url,
            data=json.dumps(questions).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req2) as resp:
                res_q = json.loads(resp.read().decode("utf-8"))
                print(f"  {res_q.get('message', 'Questions saved successfully.')}")
        except Exception as e:
            print(f"  Error uploading questions: {e}")
            sys.exit(1)

    print("\nSUCCESS! Your mock exam is now live on Render.")
    print(f"Students can take this exam immediately at: {base}/api/mobile/exams/today")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload mock exam to Render backend from your laptop")
    parser.add_argument("--url", default="http://127.0.0.1:3000", help="Render service URL (e.g. https://my-mock-backend.onrender.com)")
    parser.add_argument("--file", default="sample_exam.json", help="Path to exam JSON file (default: sample_exam.json)")
    args = parser.parse_args()

    upload_mock_exam(args.url, args.file)
