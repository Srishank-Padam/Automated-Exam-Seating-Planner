from flask import Flask, request, jsonify, send_file, session, send_from_directory
import pandas as pd
from functools import wraps
from io import BytesIO
import os

from utils import (
    clean_dataframe,
    generate_seating_arrangement,
    generate_room_seating_pdf,
    generate_hall_ticket_pdf,
    generate_all_hall_tickets_zip
)

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
app.secret_key = "super_secret_key"

rooms_df = None
timetable_df = None
allocation_df = None

# ------------------- AUTH HELPERS -------------------
def categorize_email(email):
    if email.endswith('@cbit.ac.in'):
        return 'faculty'
    else:
        return 'invalid'

def faculty_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'role' not in session or session['role'] != 'faculty':
            return jsonify({"error": "Invalid credentials"}), 403
        return func(*args, **kwargs)
    return wrapper

# ------------------- ROUTES -------------------
@app.route('/')
def serve_login():
    return send_from_directory('../frontend', 'login.html')

@app.route('/generator')
def serve_generator():
    if 'role' in session and session['role'] == 'faculty':
        return app.send_static_file('generator.html')
    return app.send_static_file('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    if categorize_email(email) != 'faculty':
        return jsonify({"error": "Access denied. Only faculty can log in."}), 403

    try:
        creds_df = pd.read_csv('faculty_credentials.csv')
    except FileNotFoundError:
        return jsonify({"error": "Credentials file not found"}), 500

    user_row = creds_df.loc[creds_df['email'] == email]
    if user_row.empty or user_row.iloc[0]['password'] != password:
        return jsonify({"error": "Invalid email or password"}), 401

    session['email'] = email
    session['role'] = 'faculty'
    return jsonify({"message": "Login successful"}), 200

# ------------------- UPLOADS -------------------
@app.route('/upload-multiple', methods=['POST'])
@faculty_only
def upload_multiple():
    global rooms_df, timetable_df
    if 'room_data' not in request.files or 'exam_data' not in request.files:
        return jsonify({"error": "Please upload both Room and Exam CSV/XLSX files"}), 400

    room_file = request.files['room_data']
    exam_file = request.files['exam_data']

    try:
        rooms_df = pd.read_csv(room_file)
        rooms_df = clean_dataframe(rooms_df, file_type="rooms")
    except Exception as e:
        return jsonify({"error": f"Room file error: {str(e)}"}), 400

    try:
        timetable_df = pd.read_csv(exam_file)
        timetable_df = clean_dataframe(timetable_df, file_type="timetable")
    except Exception as e:
        return jsonify({"error": f"Exam file error: {str(e)}"}), 400

    return jsonify({"message": "Files uploaded successfully"}), 200

@app.route('/generate_room_seating_pdf', methods=['GET'])
@faculty_only
def generate_room_pdf():
    global allocation_df
    if timetable_df is None or rooms_df is None:
        return jsonify({"error": "Please upload both timetable and rooms CSV first"}), 400

    allocation_df = generate_seating_arrangement(timetable_df, rooms_df)
    if allocation_df.empty:
        return jsonify({"error": "No seating allocation generated"}), 400

    print("Columns in allocation_df:", allocation_df.columns.tolist())  # << Debug line

    # Try to detect the correct column names
    columns_lower = [col.lower() for col in allocation_df.columns]
    if 'date' in columns_lower:
        date_col = allocation_df.columns[columns_lower.index('date')]
    elif 'examdate' in columns_lower:
        date_col = allocation_df.columns[columns_lower.index('examdate')]
    else:
        return jsonify({"error": "Generated allocation is missing 'Date' column"}), 400

    if 'session' in columns_lower:
        session_col = allocation_df.columns[columns_lower.index('session')]
    elif 'examsession' in columns_lower:
        session_col = allocation_df.columns[columns_lower.index('examsession')]
    else:
        return jsonify({"error": "Generated allocation is missing 'Session' column"}), 400

    exam_meta = {
        "ExamDate": allocation_df.iloc[0][date_col],
        "ExamSession": allocation_df.iloc[0][session_col]
    }

    # pdf_bytes = generate_room_seating_pdf(allocation_df, exam_meta)
    # return send_file(BytesIO(pdf_bytes), mimetype='application/pdf', as_attachment=False)

    # Use BytesIO directly
    pdf_io = generate_room_seating_pdf(allocation_df, exam_meta)
    pdf_io.seek(0)
    return send_file(pdf_io, mimetype='application/pdf', as_attachment=False)

@app.route('/generate_hall_ticket/<roll_no>', methods=['GET'])
@faculty_only
def generate_hall_ticket(roll_no):
    global allocation_df
    if allocation_df is None or allocation_df.empty:
        return jsonify({"error": "Seating not generated yet"}), 400

    student = allocation_df[allocation_df["RollNo"].astype(str) == str(roll_no)]
    if student.empty:
        return jsonify({"error": f"No record found for Roll No {roll_no}"}), 404

    pdf_bytes = generate_hall_ticket_pdf(student.iloc[0])
    return send_file(BytesIO(pdf_bytes), mimetype='application/pdf', as_attachment=False)

@app.route('/download_all_halltickets', methods=['GET'])
@faculty_only
def download_all_halltickets():
    global allocation_df
    if allocation_df is None or allocation_df.empty:
        return jsonify({"error": "Seating not generated yet"}), 400

    zip_bytes = generate_all_hall_tickets_zip(allocation_df)
    return send_file(
        zip_bytes,
        mimetype='application/zip',
        as_attachment=True,
        download_name='All_HallTickets.zip'
    )

@app.route('/logout', methods=['POST'])
@faculty_only
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
