from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.flashcards import router as flashcard_router

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
app.include_router(flashcard_router)