from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.flashcards import router as flashcards_router
from api.folders import router as folders_router
from api.quiz import router as quiz_router

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route registration
app.include_router(flashcards_router)
app.include_router(folders_router)
app.include_router(quiz_router)