from fastapi import FastAPI
from teams import router as teams_router
from players import router as players_router

app = FastAPI()

app.include_router(teams_router)
app.include_router(players_router)

@app.get("/info")
async def info():
    return {"Theme": "Sport Club"}

@app.get("/about")
async def about():
    return {"course": "Web Development"}

@app.get("/")
async def root():
    return {"message": "Hello Web"}
