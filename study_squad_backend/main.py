from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models  # noqa: F401
from routers import (
    auth,
    users,
    ai_coach,
    squads,
    coins,
    subscriptions,
    progress,
    tasks,
    onboarding,
    profile,
    chat,
    chat_ws,
)
from scheduler import start_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Study Squad API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(ai_coach.router)
app.include_router(squads.router)
app.include_router(coins.router)
app.include_router(subscriptions.router)
app.include_router(progress.router)
app.include_router(tasks.router)
app.include_router(onboarding.router)
app.include_router(profile.router)
app.include_router(chat.router)
app.include_router(chat_ws.router)


@app.on_event("startup")
def on_startup():
    start_scheduler()


@app.get("/")
def root():
    return {"status": "ok", "message": "Study Squad API ishlayapti"}


@app.get("/health")
def health():
    return {"status": "healthy"}
