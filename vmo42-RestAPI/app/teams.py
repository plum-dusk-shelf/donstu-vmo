from fastapi import HTTPException
from fastapi import APIRouter
from pydantic import BaseModel


    "id",
    "City",        
    "Players",
    "Score"
]

teams_db = []

router = APIRouter()

class Team(BaseModel):
    city: str
    players: int
    score: int

@router.get("/teams")
async def teams():
    return teams_db

def raise404():
    raise HTTPException(
            status_code = 404,
            detail = "Team not found"
            )

@router.get("/teams/{id}")
async def team(id: str):
    for t in teams_db:
        if t["id"] == id:
            return t
    
    raise404()

@router.post("/teams/add")
async def add(new_team_data: Team):
    new_team_id = len(teams_db) + 1

    new_team = {
        "id": f'{new_team_id:06}',
        "City": new_team_data.city,
        "Players": new_team_data.players,
        "Score": new_team_data.score
    }

    teams_db.append(new_team)
    return new_team

@router.on_event("startup")
async def main():
    await add(Team(city="Rostov-on-Don", players=12, score=811))
    await add(Team(city="Khabarovsk", players=13, score=1040))

@router.delete("/teams/delete/{id}")
async def delete(id: str):
    for t in teams_db:
        if t["id"] == id:
            teams_db.remove(t)
