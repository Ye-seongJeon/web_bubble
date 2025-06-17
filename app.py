import os
import json
import tempfile
import subprocess
import requests
from flask import Flask, request, jsonify

# Environment variables for Bubble API configuration
BUBBLE_API_TOKEN = os.environ.get("BUBBLE_API_TOKEN")  # your private API token
BUBBLE_API_URL = os.environ.get("BUBBLE_API_URL")      # e.g. https://yourapp.bubbleapps.io/api/1.1/obj
BUBBLE_TYPE = os.environ.get("BUBBLE_TYPE")            # Data type to create

app = Flask(__name__)

ANALYSIS_START = "=== ANALYSIS_RESULT_START ==="
ANALYSIS_END = "=== ANALYSIS_RESULT_END ==="


def run_stp_grading(student_path, answer_path=None, student_id=None, assignment_id=None):
    """Run the stp_grading script and return the parsed JSON result."""
    env = os.environ.copy()
    env["STUDENT_FILE_PATH"] = student_path
    env["STUDENT_ID"] = student_id or "unknown"
    env["ASSIGNMENT_ID"] = assignment_id or "unknown"
    if answer_path:
        env["ANSWER_FILE_PATH"] = answer_path
    with tempfile.TemporaryDirectory() as tmpdir:
        env["RESULT_PATH"] = tmpdir
        proc = subprocess.run(
            ["python", "code_ver402/source/stp_grading.py"],
            capture_output=True,
            text=True,
            env=env,
        )
    output = proc.stdout
    start = output.find(ANALYSIS_START)
    end = output.find(ANALYSIS_END, start)
    if start == -1 or end == -1:
        raise RuntimeError(f"Failed to parse analysis output: {output}")
    json_str = output[start + len(ANALYSIS_START):end].strip()
    return json.loads(json_str)


def save_to_bubble(data):
    """Send the result to Bubble DB using the Data API."""
    if not (BUBBLE_API_TOKEN and BUBBLE_API_URL and BUBBLE_TYPE):
        raise RuntimeError("Bubble API configuration is missing")
    url = f"{BUBBLE_API_URL}/{BUBBLE_TYPE}"
    headers = {
        "Authorization": f"Bearer {BUBBLE_API_TOKEN}",
        "Content-Type": "application/json",
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


@app.route("/grade", methods=["POST"])
def grade():
    """Receive STP files, run grading and store result in Bubble DB."""
    if "stp_file" not in request.files:
        return jsonify({"error": "stp_file is required"}), 400

    student_id = request.form.get("student_id")
    assignment_id = request.form.get("assignment_id")

    stp_file = request.files["stp_file"]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stp") as tmp:
        stp_file.save(tmp.name)
        student_path = tmp.name

    answer_path = None
    if "answer_file" in request.files:
        answer_file = request.files["answer_file"]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".stp") as tmp:
            answer_file.save(tmp.name)
            answer_path = tmp.name

    try:
        result = run_stp_grading(student_path, answer_path, student_id, assignment_id)
    finally:
        os.remove(student_path)
        if answer_path:
            os.remove(answer_path)

    try:
        bubble_response = save_to_bubble(result)
    except Exception as e:
        return jsonify({"error": str(e), "analysis": result}), 500

    return jsonify({"bubble": bubble_response, "analysis": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
