from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

fields = [
    "id",
    "City",        
    "Players",
    "Score"
]

teams_dict = []

class Team(BaseModel):
    city: str
    players: int
    score: int

@app.get("/")
async def root():
    return {"message": "Hello Web"}

@app.get("/about")
async def about():
    return {"course": "Web Development"}

@app.get("/users")
async def users():
    return {"users": ["Alex", "Maria"]}

@app.get("/info")
async def info():
    return {"Theme": "Sport Club"}

@app.get("/teams")
async def teams():
    return teams_dict

def raise404():
    raise HTTPException(
            status_code = 404,
            detail = "Team not found"
            )

@app.get("/teams/{id}")
async def team(id: str):
    for t in teams_dict:
        if t["id"] == id:
            return t
    
    raise404()

new_id = 0
@app.post("/add")
async def add(new_team_data: Team):
    global new_id
    new_id += 1

    new_team = {
        "id": f'{new_id:06}',
        "City": new_team_data.city,
        "Players": new_team_data.players,
        "Score": new_team_data.score
    }

    teams_dict.append(new_team)
    return new_team

@app.on_event("startup")
async def main():
    await add(Team(city="Rostov-on-Don", players=12, score=811))
    await add(Team(city="Khabarovsk", players=13, score=1040))

@app.get("/delete/{id}")
async def delete(id: str):
    for t in teams_dict:
        if t["id"] == id:
            teams_dict.remove(t)

