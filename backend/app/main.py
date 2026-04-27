from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
import app.models.user
from app.database import engine, Base
from app.api.analyze import router as analyze_router
from app.api.history import router as history_router
from app.api.multi_analyze import router as multi_analyze_router
from app.api.rdp_analyze import router as rdp_analyze_router
import app.models.result
import app.models.multi_result

app = FastAPI(
    title="CodeTrace",
    description="A Code Plagiarism and Duplication Detection System",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(analyze_router)
app.include_router(history_router)
app.include_router(multi_analyze_router)
app.include_router(auth_router)
app.include_router(rdp_analyze_router)

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "app": "CodeTrace"}
