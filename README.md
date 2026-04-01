<div align="center">

# 🔍 CodeTrace

### Code Plagiarism & Duplication Detection System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-4-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

*Detect plagiarism and code duplication across codebases using AST-based analysis powered by Tree-sitter.*

</div>

---

## 📖 Overview

**CodeTrace** is a full-stack web application that analyzes source code for plagiarism and structural duplication. It leverages AST (Abstract Syntax Tree) parsing via Tree-sitter to detect similarities across C, C++, Java, and Python files — going beyond simple text matching to catch structural clones even after renaming or reformatting.

### ✨ Key Features

- 🧠 **AST-based Analysis** — Detects structural similarities, not just text matches
- 🌐 **Multi-language Support** — C, C++, Java (Tree-sitter) + Python (built-in `ast`)
- 📊 **Visual Reports** — Score-based similarity results with interactive charts
- 🗂️ **History Tracking** — Persistent analysis history stored in PostgreSQL
- ⚡ **Fast API** — Async FastAPI backend with auto-generated Swagger docs
- 🎨 **Modern UI** — React + Tailwind with Monaco Editor for in-browser code editing

---

## 🗂️ Project Structure

```
codetrace/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── api/                # Route handlers (analyze, history)
│   │   ├── core/               # Core analysis logic (AST, similarity)
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── config.py           # Environment & app configuration
│   │   ├── database.py         # DB engine & session setup
│   │   └── main.py             # FastAPI app entry point
│   ├── .env                    # Environment variables (do NOT commit)
│   ├── requirements.txt        # Python dependencies
│   └── venv/                   # Python virtual environment
│
├── frontend/                   # React + Vite application
│   ├── src/
│   │   ├── api/                # Axios instance & API calls
│   │   ├── components/         # Reusable UI components (Navbar, Footer, etc.)
│   │   ├── pages/              # Page-level components (Home, Analyze, History)
│   │   ├── App.jsx             # Root component & routing
│   │   ├── main.jsx            # React entry point
│   │   └── index.css           # Global styles & Tailwind directives
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── start_project.py            # 🚀 One-command launcher for both servers
├── .gitignore
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite 4, Tailwind CSS 3, Shadcn/ui, Monaco Editor |
| **Backend** | FastAPI 0.111, Uvicorn, Pydantic v2 |
| **Database** | PostgreSQL, SQLAlchemy 2, Alembic |
| **AST Analysis** | Tree-sitter (C, C++, Java), Python `ast` module |
| **HTTP Client** | Axios |
| **Charts** | Recharts |

---

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed:

- [Python 3.11+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/) & npm
- [PostgreSQL 15+](https://www.postgresql.org/download/)

---

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/codetrace.git
cd codetrace
```

---

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Configure Environment Variables:**

Create or edit `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/codetrace
DB_USER=postgres
DB_PASSWORD=YOUR_PASSWORD
DB_HOST=localhost
DB_PORT=5432
DB_NAME=codetrace
```

**Create the PostgreSQL Database:**

```sql
CREATE DATABASE codetrace;
```

---

### 3. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install
```

---

### 4. Run Both Servers

#### ⚡ Option A — One Command (Recommended)

```bash
# From the project root
python start_project.py
```

This launches both the FastAPI backend and the Vite dev server simultaneously.

#### 🔧 Option B — Manual

```bash
# Terminal 1 — Backend
cd backend
venv\Scripts\activate          # Windows
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

---

### 5. Open in Browser

| Service | URL |
|---|---|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **Swagger Docs** | http://localhost:8000/docs |
| **Redoc** | http://localhost:8000/redoc |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/analyze` | Submit code for analysis |
| `GET` | `/history` | Retrieve past analysis results |
| `GET` | `/history/{id}` | Get a specific analysis result |

Full interactive documentation available at **`/docs`** (Swagger UI).

---

## 🧪 Development

### Running Backend Tests

```bash
cd backend
pytest
```

### Linting & Formatting

```bash
# Backend
black app/
isort app/

# Frontend
npm run lint
```

### Database Migrations (Alembic)

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "your message"

# Apply migrations
alembic upgrade head
```

---

## 📦 Environment Variables Reference

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | Full PostgreSQL connection string | — |
| `DB_USER` | Database username | `postgres` |
| `DB_PASSWORD` | Database password | — |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `codetrace` |

> ⚠️ Never commit your `.env` file. It is already listed in `.gitignore`.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'feat: add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">
Made with ❤️ — CodeTrace
</div>
