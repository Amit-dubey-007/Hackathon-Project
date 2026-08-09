# Consensus AI

<p align="center">
  <h2 align="center">Consensus AI</h2>
  <p align="center">
    AI-Powered Practical Skill Assessment & Blockchain Verified Certification Platform
  </p>

  <p align="center">
    <b>Assess Skills • Prevent Cheating • Verify Forever</b>
  </p>
</p>

---

## 📖 Overview

**Consensus AI** is an AI-powered practical skill assessment and verification platform built to solve a fundamental hiring problem: **resumes and traditional certificates often fail to prove a candidate's actual abilities**.

Instead of relying on claims, academic credentials, or keyword-filled resumes, Consensus AI evaluates candidates through AI-generated, real-world practical assessments conducted in a secure, AI-proctored environment. Responses are assessed using Artificial Intelligence, and successful candidates receive blockchain-verifiable certificates with dynamic QR verification, allowing employers to instantly verify both authenticity and demonstrated skills.

**From resumes that claim skills to verified proof of skills.**

---

# ✨ Features

## 🔐 Secure Authentication

- Email OTP Registration
- Email OTP Login
- Secure User Authentication
- Profile Management

---

## 🏠 Personalized Dashboard

After login, users can access their personalized dashboard featuring:

- Assessment Statistics
- Recent Assessments
- Earned Certificates
- Performance Overview
- Quick Navigation

---

## 📚 Skills Catalog

Explore available practical assessments with:

- Search Skills
- Category Filters
- Difficulty Levels
- Skill Descriptions
- Passing Requirements

---

## 📝 AI-Powered Practical Assessments

Every assessment is dynamically generated using Google Gemini AI.

Features include:

- Practical Implementation-Based Questions
- Coding & Descriptive Tasks
- Difficulty-Aware Assessments
- Server-Side Timer
- Automatic Submission on Timeout
- Progress Tracking
- Multi-Step Assessment Flow

---

## 💻 Interactive Coding Workspace

Coding questions are completed directly in the browser using Monaco Editor.

Features include:

- Monaco Code Editor
- Syntax Highlighting
- Multiple Programming Languages
- Auto Save
- Smooth Coding Experience

---

## 🛡 AI Proctoring & Anti-Cheat

To maintain assessment integrity, Consensus AI continuously monitors candidates throughout the assessment.

Security measures include:

- Webcam Monitoring
- Face Detection
- TensorFlow.js COCO-SSD Mobile Phone Detection
- Clipboard Protection
- Copy & Paste Blocking
- Tab Switching Detection
- Browser Focus Monitoring
- Fullscreen Monitoring
- Multiple Warning System
- Automatic Assessment Termination after repeated violations

---

## 🧠 AI Evaluation

After submission, responses are evaluated using Google Gemini AI.

Evaluation includes:

- Practical Skill Assessment
- Rubric-Based Scoring
- AI Feedback
- Batch Evaluation
- Pass / Fail Decision

---

## 📊 Assessment Reports

Candidates receive detailed assessment reports containing:

- Final Score
- AI Feedback
- Time Taken
- Submission Type
- Integrity Score
- Previous Assessment History
- Performance Analytics (Strengths And Weakness)

---

## 🏆 Blockchain Verified Certificates

Successful candidates receive premium blockchain-verifiable certificates containing:

- Candidate Name
- Skill Name
- Assessment Score
- Passing Requirement
- Completion Date
- Certificate ID
- Wallet Address
- Token Information
- Dynamic QR Code
- Printable PDF Certificate

---

## 🔍 Public Certificate Verification

Every certificate can be verified publicly through:

- Dynamic QR Code
- Public Verification URL
- Blockchain Details
- Certificate Validation Page

---

## 📈 Performance Analytics

Users can track their progress with:

- Assessment History
- Time Analytics
- Completion Statistics
- Certificate Status
- Performance Reports

---

# 🏗 System Architecture

```text
                        User
                          │
                          ▼
                 Django Web Application
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
 Authentication    Assessment Engine   Dashboard
                          │
          ┌───────────────┼───────────────┐
          ▼                               ▼
   Google Gemini AI               AI Proctoring
          │                       TensorFlow.js
          ▼
    AI Evaluation Engine
          │
          ▼
   Assessment Result
          │
          ▼
 Certificate Generator
          │
          ▼
 Blockchain Verification
          │
          ▼
 Dynamic QR Verification
```

---

# ⚙ Tech Stack

| Category | Technology |
|-----------|------------|
| Backend | Django |
| Programming Language | Python |
| Frontend | HTML, Tailwind CSS, JavaScript |
| Authentication | Email OTP |
| AI Assessment | Google Gemini API |
| AI Proctoring | TensorFlow.js COCO-SSD |
| Code Editor | Monaco Editor |
| Database | PostgreSQL |
| PDF Generation | xhtml2pdf |
| QR Generation | Python qrcode |
| Blockchain | ERC-5192 Soulbound Certificates |

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone <repository-url>
```

## 2. Navigate to the project directory

```bash
cd HACKATHON
```

> Replace `HACKATHON` with your repository name if different.

## 3. Create a virtual environment (Optional if not already created)

```bash
python -m venv .venv
```

## 4. Activate the virtual environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

## 5. Install dependencies

```bash
pip install -r requirements.txt
```

## 6. Configure environment variables

Create a `.env` file in the project root and add the required variables.

```env
SECRET_KEY=YOUR_SECRET_KEY
DEBUG=True
GEMINI_API_KEY=YOUR_GEMINI_API_KEY

# Add other required variables if applicable.
```

## 7. Navigate to the Django project

```bash
cd config
```

## 8. Apply database migrations

```bash
python manage.py migrate
```

## 9. Start the development server

```bash
python manage.py runserver
```

## 10. Open the application

```
http://127.0.0.1:8000/
```
# 🔑 Environment Variables

Create a `.env` file and configure the required environment variables.

```env
SECRET_KEY=YOUR_SECRET_KEY

DEBUG=True

GEMINI_API_KEY=YOUR_GEMINI_API_KEY

# Configure other required variables if applicable.
```

---

# 📂 Project Structure

```text
ConsensusAI/

├── config/
│   ├── accounts/              # Authentication & user management
│   ├── config/                # Django project settings
│   ├── core/                  # Main application
│   │   ├── templates/
│   │   ├── static/
│   │   ├── views.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── utils.py
│   ├── media/                 # Generated certificates & uploads
│   └── manage.py
│
├── .env                       # Environment variables
├── .gitignore
├── requirements.txt
└── README.md
```


# 🎥 Demo Video

**YouTube Demo:**

> https://youtu.be/v9U4mod_6P8
---

# 🌐 Live Demo

**Website:** 

> https://hackathon-project-dxpn.onrender.com/

---

# 📈 Future Scope

- AI Mock Interviews
- Recruiter Dashboard
- Resume Analysis
- Organization Portal
- Multi-language Assessments
- Advanced AI Proctoring
- Multi-Chain Blockchain Support
- Skill Recommendation Engine

---

# 👥 Contributors

| Name | Role |
|------|------|
| **Garvita** | **Team Leader**, UI/UX Design, Frontend Development, Project Management |
| **Antara** | Frontend Development, UI Implementation |
| **Anjali** | Quality Assurance (QA), Testing & Validation |
| **Amit** | Backend Development, Database Design, AI Integration, Blockchain Integration, API Development, Security & System Architecture |

# 📄 License

This project was developed as part of a Hackathon.

---

# ⚠️ Known Limitations

This project was developed during a hackathon using free-tier AI services.

Current limitations include:

- AI proctoring accuracy (face and mobile phone detection) depends on the performance of free browser-based TensorFlow.js models.
- Detection may vary based on camera quality, lighting conditions, and device performance.
- Free-tier AI APIs have request and rate limits that can affect response times.
- The proctoring module is intended as a proof of concept and can be enhanced further using commercial vision APIs or custom-trained models for production deployments.

Despite these limitations, the platform demonstrates the complete workflow of secure AI-powered practical assessments and blockchain-verifiable certification.

# 📬 Contact

**Project:** Consensus AI

Website:  https://hackathon-project-dxpn.onrender.com

Email: amit4528990@gmail.com

GitHub: https://github.com/Amit-dubey-007/Hackathon-Project/

LinkedIn: https://www.linkedin.com/in/amit-dubey-613355371/

---

<p align="center">
<b>Consensus AI</b><br>
Practical Skills • Trusted Credentials • Verified Achievement
</p>
