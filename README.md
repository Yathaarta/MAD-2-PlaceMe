# PlaceMe — Comprehensive Placement Portal

**PlaceMe** is a multi-user placement management platform built as a decoupled Single Page Application (SPA). It connects students, companies, and institute administrators through a Vue 3 frontend and a Flask RESTful backend.

## 🔗 Project Links

[![Website](https://img.shields.io/badge/Visit_Website-733131?style=for-the-badge&logo=vercel&logoColor=white)](https://placeme-portal.vercel.app/)

| [![](https://img.shields.io/badge/View%20ERDiagram%20png-8A2BE2)](https://drive.google.com/file/d/1hQjWzMPR5LqOSq35vMXJE_Kahq9J4aIk/view?usp=drivesdk) | 
[![](https://img.shields.io/badge/View%20Report%20PDF-8A2BE2)](https://drive.google.com/file/d/1N_7gWiJ7_4kKcGszyBWP00dEaUewy_tx/view?usp=drivesdk) |
[![](https://img.shields.io/badge/View%20Demo%20Video-8A2BE2)](https://drive.google.com/file/d/1JRiAOQKH7wfCt2OsJkOMhHKQuphLn-n6/view?usp=drivesdk) |

---

## 📖 My Journey: From Conception to Production


As a standalone student in the BS Data Science degree program, I consistently strive to push the boundaries of my technical comprehension at the diploma level. I undertook this MAD-2 project with the explicit, ambitious goal of transitioning away from traditional, monolithic server-side rendered applications (like standard Jinja2 implementations) to a modern, fully decoupled Single Page Application (SPA) architecture.

My academic curiosity rarely allows me to settle for mediocre implementations, even when facing stringent deadlines. I invested a substantial amount of time in mastering advanced frontend state management, asynchronous background task processing, secure cross-origin authentication protocols, and highly reusable UI composition to build a robust, enterprise-grade platform.

To construct a project of this scale within the timeframe, I utilized AI/LLMs strictly as an advanced, interactive technical tutor for architectural guidance, debugging complex environment configurations, and learning modern API integration patterns. The final crowning achievement of this journey was taking the application from my local localhost environment and deploying it globally on a live Azure Virtual Machine. Setting up custom dynamic DNS via DuckDNS, configuring an Nginx reverse proxy to handle secure HTTPS SSL certificates, and orchestrating the background workers using systemd transformed this from an academic assignment into a production-ready system.

---

## 🚀 Project Overview

"PlaceMe" is a comprehensive, multi-user Placement Portal that bridges the critical communication and logistical gap between university students, corporate recruiters, and institute administrators. Architected as a modern SPA, the platform features a highly reactive frontend that seamlessly communicates with a robust RESTful API backend.

The architecture enforces three strict, distinct Role-Based Access Control (RBAC) tiers:

1.  **Administrators:** The governing body that oversees the system, verifies student academic records, and approves corporate placement drives to prevent spam.
    
2.  **Companies:** Corporate recruiters who draft job roles, manage eligibility criteria, and utilize an integrated Applicant Tracking System (ATS).
    
3.  **Students:** The primary end-users who maintain verified academic profiles, upload resumes, and seamlessly apply for eligible opportunities based on dynamic filtering.

---

## 🛠️ Technology Stack

### Frontend

| Technology | Purpose |
|---|---|
| **Vue.js 3** | Reactive SPA frontend and component-based UI |
| **Composition API** | Encapsulation of component and business logic |
| **Vite** | Development server, HMR, and optimized bundling |
| **Pinia** | Global state management through stores such as `authStore` and `dataStore` |
| **Vue Router** | Client-side routing and role-based route protection |
| **Axios** | Communication with the Flask REST API |
| **Bootstrap 5** | UI styling and responsive layouts |
| **Custom CSS** | Hover states, animations, and UI customization |
| **Chart.js / vue-chartjs** | Reactive dashboard visualizations |

### Backend

| Technology | Purpose |
|---|---|
| **Flask** | RESTful JSON API backend |
| **Flask-Security-Too** | Authentication, authorization, Bcrypt password hashing, and sessions |
| **Flask-SQLAlchemy** | ORM and database integration |
| **SQLite** | Transactional application database |
| **Marshmallow** | Request and data validation |

### Asynchronous Processing

| Technology | Purpose |
|---|---|
| **Celery** | Background task processing |
| **Redis** | Message broker and TTL cache |

Celery is used to keep heavy I/O operations away from the main Flask request cycle, including:

- Registration OTP email delivery
- Applicant/application CSV generation
- Email delivery of generated CSV files

### Production Infrastructure

| Technology | Purpose |
|---|---|
| **Vercel:** | Frontend hosting. |
| **Azure VM (Ubuntu):** | Backend hosting. |
| **Nginx & Gunicorn:** | Web server and reverse proxy handling HTTPS traffic. |
| **Systemd:** | Daemonizing background services for 24/7 uptime.| 
---

## 🏗️ Architecture

The application follows a decoupled SPA architecture:

```text
                         ┌─────────────────────┐
                         │        Users        │
                         │ Admin / Company /   │
                         │       Student       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Vue 3 Frontend    │
                         │ Pinia / Vue Router  │
                         │ Bootstrap / Axios   │
                         └──────────┬──────────┘
                                    │
                              REST API / JSON
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Flask Backend    │
                         │    RESTful APIs     │
                         │ Flask-Security-Too  │
                         │     Marshmallow     │
                         └──────┬────────┬─────┘
                                │        │
                    ┌───────────┘        └────────────┐
                    ▼                                 ▼
             ┌───────────────┐              ┌────────────────┐
             │ SQLite + ORM  │              │ Celery + Redis │
             │ Flask-SQLA    │              │ Background     │
             │ lchemy        │              │ Processing     │
             └───────────────┘              └────────────────┘
```

---

## 🖼️ Screenshots

Add application screenshots here as the project is documented further.

### Landing Page

<img width="48%" alt="image" src="https://github.com/user-attachments/assets/a3d0fb08-4ae9-4122-ad45-c293d0581de6" />

### Student Pages

<img width="33%" alt="image" src="https://github.com/user-attachments/assets/403a16f0-8ab5-430b-bd48-3b599b6603ee" />
<img width="33%" alt="image" src="https://github.com/user-attachments/assets/2d1b837e-017b-4cbc-9f14-65635763212b" />
<img width="33%" alt="image" src="https://github.com/user-attachments/assets/af32a343-f15f-473d-97b0-193c1def45de" />
<img width="33%" alt="image" src="https://github.com/user-attachments/assets/d9100a46-980a-4329-a529-5c11325ea2ea" />
<img width="33%" alt="image" src="https://github.com/user-attachments/assets/9a689298-1a11-4112-8b90-ec7ee791f8bb" />

### Company Pages

<img width="33%" alt="image" src="https://github.com/user-attachments/assets/0010758b-da97-47ce-9743-2d0504763d0c" />
<img width="33%" alt="image" src="https://github.com/user-attachments/assets/a6ca9b9a-daa3-4a8b-9e63-daa267fc886a" />
<img width="33%" alt="image" src="https://github.com/user-attachments/assets/bdfe50c0-8993-4d13-ad96-297afc2b5648" />
<img width="33%" alt="image" src="https://github.com/user-attachments/assets/7658b5db-b859-4e83-b470-d70b2c50148c" />
<img width="33%" alt="image" src="https://github.com/user-attachments/assets/d02efeda-ca8b-418b-aa29-dee1d6200632" />

### Admin Pages

<img width="33%" alt="image" src="https://github.com/user-attachments/assets/24ac51e6-bbb1-4d7f-b5cb-d78cf3d8c89b" />
<img width="33%" alt="image" src="https://github.com/user-attachments/assets/320fbbec-ac14-4516-9fb5-8499430ff7df" />
<img width="33%" alt="image" src="https://github.com/user-attachments/assets/c9837a3e-6223-45df-8a07-ca1de5616cd6" />
<img width="33%" alt="image" src="https://github.com/user-attachments/assets/5145701a-02eb-4518-bdf2-d499a2db5863" />

---

## 💻 Local Development Setup

### Prerequisites

 - Python installed
 - Node.js and npm installed
 - Redis Server installed and running natively on your OS


### 1. Backend

Open a terminal and navigate to the backend directory:

```bash
cd backend
```

Create and activate a Python virtual environment:

```bash
# Windows
python -m venv env
env\Scripts\activate

# macOS/Linux
python -m venv env
source env/bin/activate

```

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory and paste the following configuration, filling in your specific details:

```env
FLASK_DEBUG=true
FLASK_APP=app.py

SQLALCHEMY_DATABASE_URI=sqlite:///db.sqlite3
SQLALCHEMY_TRACK_MODIFICATIONS=False

SECRET_KEY=

ADMIN_EMAIL=
ADMIN_PASSWORD=
ADMIN_UNIQE_ID=

SECURITY_PASSWORD_SALT=

SENDER_EMAIL=
SENDER_PASSWORD=
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

FLASK_ENV=
FRONTEND_URL=
```

> **Important:** Never commit `.env` or other credentials to source control.

Start Flask:

```bash
flask run
```

### 2. Celery Worker & Beat

Open another terminal, activate the backend virtual environment, and run:

```bash
python -m celery -A app.celery_app worker --loglevel=info
```

Open another terminal and run:

```bash
python -m celery -A app.celery_app beat --loglevel=info
```

### 3. Frontend

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

The frontend normally runs on:

```text
http://localhost:5173
```

The Flask development server normally runs on:

```text
http://127.0.0.1:5000
```

---

## 🧩 Key Features

### Student

- Profile management
- Academic information management
- Resume upload
- Admin-verified education
- Dynamic placement-drive filtering
- Eligibility-based applications
- Application history
- OTP-based registration
- Application analytics

### Company

- Company profile management
- Placement-drive creation
- Eligibility criteria
- Applicant management
- Applicant Tracking System
- Application status updates
- Applicant CSV export
- Applicant analytics

### Administrator

- Student academic verification
- Company approval
- Placement-drive approval
- User blacklisting
- Platform-wide statistics
- Application analytics

---

## 👨‍💻 Author

[![](https://img.shields.io/badge/Yatharth%20Pandey%20↗-8A2BE2)](https://www.linkedin.com/in/yatharth-pandey-72bb65233/) 

BS Data Science Student @ IIT Madras 

---

## ⭐ Project Status

**Project completed and successfully deployed.** ➡️ ⌊ [![Website](https://img.shields.io/badge/Visit_Website-191970?style=for-the-badge&logo=vercel&logoColor=white)](https://placeme-portal.vercel.app/) ⌋
  

