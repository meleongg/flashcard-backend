# FlashLearn Backend 🧠🧾

This is the backend for **FlashLearn**, an AI-powered flashcard app designed to help users learn new vocabulary in English, Mandarin, and French. Built with **FastAPI**, this service handles flashcard creation, user authentication, and database interaction—powering the core learning experience.

---

## ✨ Features

- ⚡ FastAPI server for handling all flashcard-related requests
- 🔄 GPT-3.5 Turbo integration for translation, example generation, and grammar explanation
- 🔡 Language-aware phonetic and part-of-speech tagging (for Mandarin, English, and French)
- 🔐 JWT-based user authentication
- 📦 PostgreSQL support via SQLAlchemy and AsyncPG
- 🌍 Language detection via `langdetect`

---

## 🛠 Tech Stack

- **Python 3.10+**
- **FastAPI**
- **SQLAlchemy (async)**
- **AsyncPG**
- **OpenAI API** (GPT-3.5 Turbo)
- **Pydantic** for request/response schemas
- **Pypinyin**, `spacy`, and `langdetect` for lightweight NLP
- **Railway** for deployment

---

## 🚀 Getting Started

1. Clone the repository

```bash
git clone https://github.com/your-username/flashcard-backend.git
cd flashcard-backend
```

2. Create .env File

```
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=your_postgres_connection_string
SECRET_KEY=your_jwt_secret
```

3. Install Dependencies
   Make sure you’re using Python 3.10+, then run:

```
pip install -r requirements.txt
```

4. Run the Development Server

```
uvicorn main:app --reload
```

---

## 📦 Deployment (via Railway)

This project is deployable on Railway:

1. Link your GitHub repo.
2. Add environment variables via Railway Dashboard.
3. Set up a PostgreSQL plugin or connect to an external DB.
4. Your API will be available at https://your-subdomain.up.railway.app
