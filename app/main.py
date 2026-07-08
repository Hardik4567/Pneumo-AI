import app.db.base  # noqa — registers all models with SQLAlchemy
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.middleware.auth import AuthMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.routers import user_master, role_master, menu_hierarchy, config_group, config_param, disease_pred_ml, history, auth, dashboard,analytics,report

app = FastAPI(title="FastAPI Auth Boilerplate")

@app.on_event("startup")
async def startup_event():
    from app.db.init_db import init_db
    try:
        await init_db()
        print("Database tables initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize database tables: {e}")

# server static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api", tags=["Authentication"])

# app.include_router(ai_service.router, prefix="/api", tags=["AI"])
app.include_router(user_master.router, prefix="/api", tags=["Users"])
app.include_router(role_master.router, prefix="/api", tags=["Roles"])
app.include_router(menu_hierarchy.router, prefix="/api", tags=["Menu Hierarchy"])
app.include_router(config_group.router, prefix="/api", tags=["Config Groups"])
app.include_router(config_param.router, prefix="/api", tags=["Config Params"])
app.include_router(disease_pred_ml.router, prefix="/api/disease_pred_ml", tags=["Disease Prediction"])
app.include_router(history.router, prefix="/api",)
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(analytics.router, prefix="/api")
app.include_router(report.router, prefix="/api/report", tags=["Reports"])

@app.get("/")
async def root():
    return {"message": "FastAPI Boilerplate is running ✅"}
