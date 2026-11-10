from fastapi import HTTPException
from fastapi import APIRouter
from pydantic import BaseModel

players_db = []

router = APIRouter()

class Player(BaseModel):
    name: str
    team: str
    score: int

@router.get("/players")
async def players():
    return players_db

def raise404(who: str):
    raise HTTPException(
            status_code = 404,
            detail = f'{who} not found'
            )

@router.get("/players/{id}")
async def player(id: str):
    for t in players_db:
        if t["id"] == id:
            return t
    
    raise404('player')

@router.post("/players/add")
async def add(new_player_data: Player):
    from teams import teams_db
    if new_player_data.team not in [t['id'] for t in teams_db]:
        raise404('team id')
    new_player_id = len(players_db) + 1

    new_player = {
        "id": f'{new_player_id:06}',
        "Name": new_player_data.name,
        "Team": new_player_data.team,
        "Score": new_player_data.score
    }

    players_db.append(new_player)
    return new_player

import os
@router.on_event("startup")
async def main():
    if not players_db:
        await add(Player(name="Ivan", team="000001", score=20))
        await add(Player(name="John", team="000002", score=20))

@router.delete("/player/delete/{id}")
async def delete(id: str):
    for t in players_db:
        if t["id"] == id:
            players_db.remove(t)
