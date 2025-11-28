# 📘 Examzy – Automated Exam Seating Planner

A full‑stack web application that automates exam seating allocation, generates room‑wise seating PDFs, and produces individual or bulk hall tickets. This project streamlines exam management for institutions through simple dataset uploads and automatic PDF generation.

---

## 🚀 Features

### ✅ Backend (Flask + Python)
- Automated seating allocation based on room capacities  
- Randomized seating with roll‑number prefix separation  
- Professional **Room‑wise Seating PDF Generator**  
- **Individual Hall Ticket PDF Generator**  
- **Bulk Hall Ticket ZIP Export**  
- Data cleaning & preprocessing tools  
- Faculty authentication (restricted to `@cbit.ac.in` emails)

### 🎨 Frontend (HTML/CSS/JS)
- Modern animated UI  
- Secure Login  
- Dataset upload dashboard  
- Embedded PDF preview  
- Hall‑ticket download tools  

---

## 🧩 Tech Stack

| Component | Technology / Library | Purpose |
| :--- | :--- | :--- |
| **Frontend** | **HTML5** | Builds the structure for the login page, seating generator UI, and hall ticket tools. |
| **Frontend** | **CSS3** | Provides all visual styling, responsive layouts, gradients, animations, and modern UI design. |
| **Frontend** | **JavaScript (Vanilla JS)** | Handles client-side interactivity, file uploads, API calls using Fetch, real-time form validation, and PDF preview rendering. |
| **Frontend Service** | **Google Fonts (Poppins)** | Ensures a clean, consistent, modern font across UI pages. |
| **Backend Framework** | **Flask (Python)** | Powers the backend server, routing, authentication, PDF generation endpoints, and hall-ticket/room-chart logic. |
| **Data Processing** | **Pandas** | Reads, cleans, processes, and transforms the uploaded CSV/XLSX datasets (rooms + student timetable). |
| **PDF Generation** | **FPDF & fpdf2** | Creates polished Room Seating PDFs and Hall Ticket PDFs programmatically. |
| **File Handling** | **ZipFile (Python stdlib)** | Bundles all generated hall tickets into a single downloadable `.zip` file. |
| **Document Read/Write** | **openpyxl** | Enables reading Excel (`.xlsx`) files uploaded by the user. |
| **Session & Auth** | **Flask Session** | Maintains secure, faculty-only login using institutional email. |
| **Core Language** | **Python 3.x** | Used for all backend logic, data workflows, and generation pipelines. |

---

## 📁 Folder Structure

```
Examzy/
│
├── backend/
│   ├── main.py
│   ├── utils.py
│   ├── faculty_credentials.csv
│   ├── requirements.txt
│
├── frontend/
│   ├── login.html
│   ├── generator.html
│
├── README.md
└── Uploads/
    ├── Rooms.csv
    ├── StudentData.csv
```

---

## 📥 Input File Formats

### **1️⃣ Rooms Dataset (`Rooms.csv`)**

Columns:
- RoomNo  
- Capacity  
- (Optional) Block  

### **2️⃣ Student Exam Data (`StudentData.csv`)**

Columns:
- RollNo  
- Subject / SubjectName  
- ExamDate  
- ExamSession  
- (Optional) StudentName, Department  

---

## ⚙️ Installation & Setup

### 1. Clone the Project
```bash
git clone https://github.com/yourusername/examzy.git
cd examzy/backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Start Backend Server
```bash
python main.py
```

Server runs at:
```
http://127.0.0.1:5000/
```

Open browser to access frontend.

---

## 🔐 Authentication

Only faculty using:
```
@cbit.ac.in
```
can log in.  
Credentials stored in `faculty_credentials.csv`.

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login` | Faculty Login |
| POST | `/logout` | Logout |

### File Uploads
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload-multiple` | Upload rooms + exam data |

### PDF / ZIP Generation
| Method | Endpoint | Description |
|--------|-----------|--------------|
| GET | `/generate_room_seating_pdf` | Room seating PDF |
| GET | `/generate_hall_ticket/<rollno>` | Single hall ticket |
| GET | `/download_all_halltickets` | ZIP of all hall tickets |

---

## 📄 Core Logic

### ✔ Seating Allocation  
- Group by ExamDate & ExamSession  
- Shuffle students & separate prefixes  
- Fill rooms sequentially  

### ✔ Room Seating PDF  
Professional tables including:
- Roll No  
- Student Name  
- Department  
- Subject  
- Seat No  

### ✔ Hall Ticket PDF  
Includes:
- Student details  
- Exam schedule  
- Room & Seat number  
- Controller signature placeholder  

---

## 🧪 Sample Data

Two sample files included:
- Rooms.csv  
- StudentData.csv  

---

## 🧻 Deployment Options

- **Render** (recommended)
- **Railway**
- **Gunicorn + Nginx** for production  

---

## 👨‍💻 Author

**Srishank Padam**  
B.Tech AI & DS  
Chaitanya Bharathi Institute of Technology  

---

## ⭐ Contribute

Pull requests & issues welcome!

---

## 📜 License
MIT License 

