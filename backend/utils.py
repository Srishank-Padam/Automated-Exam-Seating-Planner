import pandas as pd
import random
from io import BytesIO
from fpdf import FPDF
import io
import zipfile


# ----------------------------------------------------------
# Data Cleaning Utility
# ----------------------------------------------------------
def clean_dataframe(df, file_type=None):
    df = df.copy()
    df = df.dropna(how="all")

    # Normalize column names
    df.columns = [c.strip().replace(" ", "") for c in df.columns]

    # Trim spaces from string fields
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()

    # Drop complete duplicates
    df = df.drop_duplicates()

    # Enforce unique RoomNo or RollNo
    if file_type == "rooms" and "RoomNo" in df.columns:
        df = df.drop_duplicates(subset=["RoomNo"], keep="first")
    elif file_type == "timetable" and "RollNo" in df.columns:
        df = df.drop_duplicates(subset=["RollNo"], keep="first")

    return df


# ----------------------------------------------------------
# Seat allocation logic (randomized)
# ----------------------------------------------------------
def _separate_adjacent_prefixes(roll_list):
    prefix_map = {}
    for roll in roll_list:
        prefix = ''.join(filter(str.isalpha, str(roll)))
        prefix_map.setdefault(prefix, []).append(roll)
    for prefix in prefix_map:
        random.shuffle(prefix_map[prefix])
    separated = []
    while any(prefix_map.values()):
        for prefix, rolls in list(prefix_map.items()):
            if rolls:
                separated.append(rolls.pop())
    return separated


def generate_seating_arrangement(timetable_df, rooms_df):
    timetable_df = timetable_df.copy()
    rooms_df = rooms_df.copy()

    timetable_df["RollNo"] = timetable_df["RollNo"].astype(str).str.strip()
    room_list = list(rooms_df["RoomNo"].unique())
    room_capacities = dict(zip(rooms_df["RoomNo"], rooms_df["Capacity"]))

    seating_records = []
    grouped = timetable_df.groupby(["ExamDate", "ExamSession"])

    for (exam_date, exam_session), group in grouped:
        students = group.sample(frac=1).reset_index(drop=True)
        roll_numbers = _separate_adjacent_prefixes(students["RollNo"].tolist())

        student_idx = 0
        for room_no in room_list:
            capacity = int(room_capacities[room_no])
            for seat_no in range(1, capacity + 1):
                if student_idx >= len(roll_numbers):
                    break
                roll = roll_numbers[student_idx]
                student = students[students["RollNo"] == roll].iloc[0]
                seating_records.append({
                    "RollNo": student["RollNo"],
                    "StudentName": student["StudentName"],
                    "Department": student["Department"],
                    "Subject": student["Subject"],
                    "ExamDate": student["ExamDate"],
                    "ExamSession": student["ExamSession"],
                    "RoomNo": room_no,
                    "SeatNo": seat_no
                })
                student_idx += 1

    return pd.DataFrame(seating_records)


# ----------------------------------------------------------
# Room Seating PDF Generator (Professional look)
# ----------------------------------------------------------
class StyledPDF(FPDF):
    pass


def generate_room_seating_pdf(allocation_df, exam_meta=None):
    pdf = StyledPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for room_no, room_group in allocation_df.groupby("RoomNo"):
        pdf.add_page()

        # Header bar
        pdf.set_fill_color(240, 245, 250)
        pdf.rect(0, 0, 210, 25, "F")

        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(20, 50, 80)
        pdf.cell(0, 15, f"Room Seating Arrangement", ln=True, align="C")

        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 8, f"Room: {room_no}", ln=True, align="C")
        if exam_meta:
            pdf.cell(0, 8,
                     f"Date: {exam_meta.get('ExamDate', '')}   |   Session: {exam_meta.get('ExamSession', '')}",
                     ln=True, align="C")

        pdf.ln(10)

        # Table header
        headers = ["Seat No", "Roll No", "Student Name", "Department", "Subject"]
        col_widths = [20, 35, 55, 35, 45]

        pdf.set_font("Helvetica", "B", 11)
        pdf.set_fill_color(225, 230, 235)
        pdf.set_text_color(0, 0, 0)
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 9, header, border=1, align="C", fill=True)
        pdf.ln()

        # Table rows
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.set_fill_color(248, 250, 252)
        fill = False

        for _, row in room_group.iterrows():
            pdf.cell(col_widths[0], 8, str(row["SeatNo"]), border=1, align="C", fill=fill)
            pdf.cell(col_widths[1], 8, str(row["RollNo"]), border=1, align="C", fill=fill)
            pdf.cell(col_widths[2], 8, str(row["StudentName"]), border=1, fill=fill)
            pdf.cell(col_widths[3], 8, str(row["Department"]), border=1, fill=fill)
            pdf.cell(col_widths[4], 8, str(row["Subject"]), border=1, fill=fill)
            pdf.ln()
            fill = not fill  # alternate row background

    pdf_bytes = pdf.output(dest="S")
    bio = BytesIO(pdf_bytes)
    bio.seek(0)
    return bio



# ----------------------------------------------------------
# Hall Ticket PDF Generator (Professional Layout)
# ----------------------------------------------------------
def generate_hall_ticket_pdf(student):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    title_color = (30, 60, 100)
    box_bg = (245, 247, 250)
    border_color = (180, 180, 180)

    pdf.set_fill_color(235, 240, 245)
    pdf.rect(0, 0, 210, 25, "F")

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*title_color)
    pdf.cell(0, 15, "EXAM HALL TICKET", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    pdf.set_draw_color(*border_color)
    pdf.set_fill_color(*box_bg)
    pdf.set_font("Helvetica", "", 12)

    details = [
        ("Name", student["StudentName"]),
        ("Roll No", student["RollNo"]),
        ("Department", student["Department"]),
        ("Subject", student["Subject"]),
        ("Exam Date", student["ExamDate"]),
        ("Exam Session", student["ExamSession"]),
        ("Room No", student["RoomNo"]),
    ]

    col1_width, col2_width, line_height = 50, 120, 10
    for key, val in details:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(col1_width, line_height, key, border=1, fill=True)
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(col2_width, line_height, str(val), border=1, ln=True, fill=True)

    pdf.ln(12)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(90, 90, 90)
    pdf.multi_cell(0, 8,
                   "Please bring this hall ticket and a valid ID card to the examination hall.\n"
                   "Ensure you are present at least 15 minutes before the scheduled start time.",
                   align="C")

    pdf.ln(15)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 10, "Signature of Controller of Examinations", ln=True, align="R")

    pdf_bytes = pdf.output(dest="S")
    return pdf_bytes


# ----------------------------------------------------------
# Generate all hall tickets ZIP
# ----------------------------------------------------------
def generate_all_hall_tickets_zip(allocation_df):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for _, student in allocation_df.iterrows():
            pdf_bytes = generate_hall_ticket_pdf(student)
            roll_no_safe = str(student['RollNo']).strip().replace(' ', '_')
            zipf.writestr(f"hall_ticket_{roll_no_safe}.pdf", pdf_bytes)
    zip_buffer.seek(0)
    return zip_buffer
