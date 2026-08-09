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

Clone the repository

```bash
git clone <repository-url>
```

Move into the project

```bash
cd ConsensusAI
```

Create a virtual environment

```bash
python -m venv venv
```

Activate virtual environment

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run database migrations

```bash
python manage.py migrate
```

Start the development server

```bash
python manage.py runserver
```

---

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

├── core/
│   ├── templates/
│   ├── static/
│   ├── views.py
│   ├── models.py
│   ├── urls.py
│   └── utils.py
│
├── media/
├── static/
├── manage.py
├── requirements.txt
└── README.md
```

---

# 📸 Screenshots

Add screenshots of:

- Home Page
- Dashboard
- Skills Catalog
- Assessment Workspace
- AI Proctoring
- Assessment Report
- Certificate Management
- Blockchain Certificate
- Public Verification Page

---

# 🎥 Demo Video

**YouTube Demo:**

> Add your demo video link here.

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

# 📬 Contact

**Project:** Consensus AI

Website:  https://hackathon-project-dxpn.onrender.com

Email: 

GitHub: https://github.com/Amit-dubey-007/Hackathon-Project/

LinkedIn:

---

<p align="center">
<b>Consensus AI</b><br>
Practical Skills • Trusted Credentials • Verified Achievement
</p>
