from sqlalchemy.orm import Session
from fastapi import (
    FastAPI, 
    Depends,
    HTTPException
)

from schema import (
    UserGet,
    PostGet,
    FeedGet
)
from database import SessionLocal
from table_user import User
from table_post import Post


app = FastAPI()

def get_db():
    with SessionLocal() as db:
        return db

@app.get("/user/{id}", response_model=UserGet)
def get_user(id:int, db: Session = Depends(get_db)):
    response = db.query(User).filter(User.id == id).one_or_none()

    if response is None:
        print(response is None)
        raise HTTPException(404, f"No user with id {id}")

    return response

@app.get("/post/{id}", response_model=PostGet)
def get_post(id:int, db: Session = Depends(get_db)):
    response = db.query(Post).filter(Post.id == id).one_or_none()

    if response is None:
        print(response is None)
        raise HTTPException(404, f"No post with id {id}")

    return response