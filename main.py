from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.flashcards import router as flashcards_router
from api.folders import router as folders_router
from api.quiz import router as quiz_router
from api.stats import router as stats_router
from api.settings import router as settings_router
from api.review import router as review_router
from api.account import router as account_router

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
      "http://localhost:3000",
      "https://flashcard-frontend-one.vercel.app/"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route registration
app.include_router(flashcards_router)
app.include_router(folders_router)
app.include_router(quiz_router)
app.include_router(stats_router)
app.include_router(settings_router)
app.include_router(review_router)
app.include_router(account_router)