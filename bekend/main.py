from fastapi import FastAPI, HTTPException, Request, APIRouter
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
from database import Database

app = FastAPI()
router = APIRouter()
db = Database()

@app.post('/play/')
def new_session():
    session_id = db.new_session()
    return {"id": session_id}

@app.get("/get-hungry/{session_id}")
def get_hungry(session_id: int):
    hng = db.get_hungry(session_id)
    return {"hungry": hng}

@app.get("/get-wash/{session_id}")
def get_wash(session_id: int):
    wash = db.get_wash(session_id)
    return {"wash": wash}

@router.patch('/feed-fish/{fish_id}')
def feed_fish(fish_id: int):
    new_hungry = db.feed_fish_by_id(fish_id)
    if new_hungry is None:
        raise HTTPException(status_code=404, detail="Риба не знайдена")
    # Оновлення значення голоду у базі даних
    db.update_hungry(fish_id, new_hungry)
    return {"fish_id": fish_id, "new_hungry": new_hungry}

@app.patch('/wash-aqua/{session_id}')
def wash_aqua(session_id: int):
    wash_aq = db.wash_aqua(session_id)
    return {"wash aqua": wash_aq}

@app.get("/ready-to-love/{session_id}")
def ready_to_love(session_id: int):
    r_love = db.ready_to_love(session_id)
    return{"r_love": r_love}

@app.put("/love/{fish_id1}/{fish_id2}")
def love(fish_id: int, fish_id2: int):
    fm = db.love(fish_id, fish_id2)
    return {"love": fm}

@app.post("/by-fish/{session_id}/{fish_name}")
def buy_fish(session_id: int,fish_name):
    bf = db.buy_fish(session_id,fish_name)
    if bf is None:
        raise HTTPException(status_code=404, detail="Недостатньо коштів")
    return {"fish_id": bf }

@app.get("/sell-fish/{fish_id}")
def sell_fish(fish_id: int):
    t_money = db.sell_fish(fish_id)
    return {"sell_fish": t_money}

@app.get("/is-alive/{fish_id}")
def is_alive(fish_id:int):
    alive = db.is_alive(fish_id)
    return {"is_alive": alive}





